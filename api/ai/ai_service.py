import asyncio
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator

from api.Assistant.assistant_repository import get_assistant_by_id_repository
from api.Assistant.assistant_response_model import ContextRequest
from api.langgraph.workflow_init import run_workflow
from api.langgraph.workflow_stream import stream_workflow_events
from api.ai.ai_response_model import (
    WorkflowRequest, 
    StreamResponse, 
    WorkflowResult, 
    ResponseMetadata,
    AvailableModelsResponse,
    ModelInfo,
    EnhanceResponse,
    FuzzyMatch,
)
from api.db.pg_database import SessionLocal
from api.llm.router import get_model_router
from api.external_api import get_related_segment_ids, get_segment_content
from api.ai.prompts import ENHANCE_META_PROMPT
from api.translation_memory.tm_model import TranslationMemory
from api.translation_memory.tm_repository import (
    find_exact_match,
    find_fuzzy_matches,
    batch_create_tm_entries,
)
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def build_workflow_request(db_session, assistant_id, target_language, prompt, segments, model, instruction=None) -> WorkflowRequest:
    assistant_detail = get_assistant_by_id_repository(db_session, assistant_id)

    variables = assistant_detail.variables or []
    instance_ids = [
        v.get("instanceId") for v in variables
        if isinstance(v, dict) and v.get("instanceId")
    ] if isinstance(variables, list) else []

    return WorkflowRequest(
        assistant_name=assistant_detail.name,
        assistant_system_prompt=assistant_detail.system_prompt,
        assistant_user_prompt=assistant_detail.user_prompt,
        assistant_variables=assistant_detail.variables,
        instance_ids=instance_ids,
        segments=segments,
        contexts=[
            ContextRequest(
                content=context.content,
                pecha_title=context.pecha_title,
                pecha_text_id=context.pecha_text_id
            ) 
            for context in assistant_detail.contexts
        ],
        target_language=target_language,
        text=prompt,
        model=model,
        instruction=instruction,
    )


def validate_model(model: str) -> None:
    model_router = get_model_router()
    if not model_router.validate_model_availability(model):
        available_models = model_router.available_models()
        raise HTTPException(
            status_code=400, 
            detail=f"Model not available: Select from this list: {list(available_models.keys())}"
        )


def _lookup_translation_memory(assistant_id, prompt, target_language, created_by, model_name):
    tm_hits = {}
    fuzzy_cache = {}
    texts_for_llm = []

    if target_language:
        with SessionLocal() as db_session:
            for idx, source_text in enumerate(prompt):
                exact = find_exact_match(
                    db_session, assistant_id, source_text, target_language, created_by, model_name
                )
                if exact:
                    tm_hits[idx] = exact.target_text
                    continue

                rows = find_fuzzy_matches(
                    db_session, assistant_id, source_text, target_language, created_by
                )
                fuzzy_cache[idx] = [
                    FuzzyMatch(
                        source_text=row.source_text,
                        target_text=row.target_text,
                        score=round(float(row.score), 4),
                        model_name=row.model_name,
                    )
                    for row in rows
                ]
                texts_for_llm.append((idx, source_text))
    else:
        texts_for_llm = list(enumerate(prompt))

    return tm_hits, fuzzy_cache, texts_for_llm


def _save_translations_to_memory(assistant_id, target_language, texts_for_llm, llm_results, created_by, model_name):
    try:
        with SessionLocal() as db_session:
            new_entries = [
                TranslationMemory(
                    assistant_id=assistant_id,
                    source_text=source_text,
                    target_text=result.output_text,
                    target_language=target_language,
                    model_name=model_name,
                    created_by=created_by,
                )
                for (_, source_text), result in zip(texts_for_llm, llm_results)
            ]
            batch_create_tm_entries(db_session, new_entries)
    except Exception as e:
        logger.warning(f"Failed to save translations to TM: {e}")


def _merge_tm_and_llm_results(prompt, tm_hits, fuzzy_cache, llm_results):
    llm_iter = iter(llm_results)
    merged = []
    for idx in range(len(prompt)):
        if idx in tm_hits:
            merged.append(
                WorkflowResult(output_text=tm_hits[idx], from_memory=True)
            )
        else:
            llm_result = next(llm_iter)
            merged.append(
                WorkflowResult(
                    output_text=llm_result.output_text,
                    from_memory=False,
                    fuzzy_matches=fuzzy_cache.get(idx, []),
                )
            )
    return merged


async def run_workflow_service(assistant_id, target_language, prompt, segments, model, offset=0, instruction=None, created_by=None):
    validate_model(model)

    tm_hits, fuzzy_cache, texts_for_llm = _lookup_translation_memory(
        assistant_id, prompt, target_language, created_by, model
    )

    if not texts_for_llm:
        now = datetime.now(timezone.utc).isoformat()
        return StreamResponse(
            results=[
                WorkflowResult(
                    output_text=tm_hits[idx], from_memory=True
                )
                for idx in range(len(prompt))
            ],
            metadata=ResponseMetadata(
                initialized_at=now,
                total_batches=0,
                completed_at=now,
                total_processing_time=0.0,
            ),
            errors=[],
        )

    llm_prompts = [text for _, text in texts_for_llm]

    with SessionLocal() as db_session:
        workflow_request = build_workflow_request(
            db_session, assistant_id, target_language, llm_prompts, segments, model, instruction
        )
    if workflow_request.instance_ids and workflow_request.segments:
        all_segment_ids = []
        for instance_id in workflow_request.instance_ids:
            segment_ids = await get_related_segment_ids(
                instance_id=instance_id,
                span_start=max(0, workflow_request.segments.start - offset),
                span_end=workflow_request.segments.end + offset,
            )
            all_segment_ids.extend(segment_ids)

        segment_contents = await asyncio.gather(
            *[get_segment_content(sid) for sid in all_segment_ids],
            return_exceptions=True
        )

        collected_contents = []
        for sid, result in zip(all_segment_ids, segment_contents):
            if isinstance(result, Exception):
                continue
            elif result:
                collected_contents.append(result)

        if collected_contents:
            for content in collected_contents:
                workflow_request.contexts.append(
                    ContextRequest(content=content)
                )

    workflow_response = await run_workflow(workflow_request)
    llm_results = workflow_response.get("final_results", [])

    if target_language and llm_results:
        _save_translations_to_memory(
            assistant_id, target_language, texts_for_llm, llm_results, created_by, model
        )

    merged_results = _merge_tm_and_llm_results(
        prompt, tm_hits, fuzzy_cache, llm_results
    )

    workflow_metadata = workflow_response.get("metadata", {})
    return StreamResponse(
        results=merged_results,
        metadata=ResponseMetadata(
            initialized_at=workflow_metadata.get("initialized_at"),
            total_batches=workflow_metadata.get("total_batches"),
            completed_at=workflow_metadata.get("completed_at"),
            total_processing_time=workflow_metadata.get("total_processing_time"),
        ),
        errors=workflow_response.get("errors", []),
    )


async def stream_workflow_service(
    assistant_id, 
    target_language, 
    prompt, 
    model,
    instruction=None,
) -> AsyncGenerator[str, None]:
    validate_model(model)
    
    with SessionLocal() as db_session:
        workflow_request = build_workflow_request(
            db_session, assistant_id, target_language, prompt, None, model, instruction
        )
    
    async for event in stream_workflow_events(
        request=workflow_request,
        target_language=target_language,
        model=model
    ):
        yield event

def get_available_models_service() -> AvailableModelsResponse:
    model_router = get_model_router()
    available_models_dict = model_router.available_models()
    
    models = {}
    for model_name, model_data in available_models_dict.items():
        models[model_name] = ModelInfo(
            name=model_data["name"],
            provider=model_data["provider"],
            description=model_data["description"],
            is_thinking=model_data["is_thinking"],
            capabilities=model_data["capabilities"],
            context_window=model_data.get("context_window")
        )
    
    return AvailableModelsResponse(models=models)

async def enhance_prompt_service(prompt: str, model: str = "claude-sonnet-4-20250514") -> EnhanceResponse:
    model_router = get_model_router()
    print(model)
    if not model_router.validate_model_availability(model):
        raise HTTPException(
            status_code=503,
            detail=f"Model '{model}' is not available. Check API key configuration."
        )

    llm = model_router.get_model(model, temperature=0.7, max_tokens=4096)
    response = await llm.ainvoke(ENHANCE_META_PROMPT.format(prompt=prompt))
    enhanced_text = response.content if hasattr(response, "content") else str(response)

    return EnhanceResponse(enhanced_prompt=enhanced_text)