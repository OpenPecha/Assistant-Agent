import asyncio
from typing import AsyncGenerator, List

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
    MultiModelResponse,
)
from api.db.pg_database import SessionLocal
from api.llm.router import get_model_router
from fastapi import HTTPException


def build_workflow_request(db_session, assistant_id, target_language, prompt, model) -> WorkflowRequest:
    assistant_detail = get_assistant_by_id_repository(db_session, assistant_id)
    return WorkflowRequest(
        assistant_name=assistant_detail.name,
        assistant_source_type=assistant_detail.source_type,
        assistant_system_prompt=assistant_detail.system_prompt,
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
        model=model
    )


def validate_models(models: List[str]) -> None:
    model_router = get_model_router()
    invalid_models = [m for m in models if not model_router.validate_model_availability(m)]
    if invalid_models:
        available_models = model_router.available_models()
        raise HTTPException(
            status_code=400,
            detail=f"Models not available: {invalid_models}. Select from: {list(available_models.keys())}"
        )


async def _run_single_workflow(assistant_id, target_language, prompt, model: str) -> StreamResponse:
    with SessionLocal() as db_session:
        workflow_request = build_workflow_request(
            db_session, assistant_id, target_language, prompt, model
        )

    workflow_response = await run_workflow(workflow_request)

    results = [
        WorkflowResult(output_text=result.output_text)
        for result in workflow_response.get("final_results", [])
    ]

    workflow_metadata = workflow_response.get("metadata", {})
    response_metadata = ResponseMetadata(
        initialized_at=workflow_metadata.get("initialized_at"),
        total_batches=workflow_metadata.get("total_batches"),
        completed_at=workflow_metadata.get("completed_at"),
        total_processing_time=workflow_metadata.get("total_processing_time")
    )

    return StreamResponse(
        model=model,
        results=results,
        metadata=response_metadata,
        errors=workflow_response.get("errors", [])
    )


async def run_workflow_service(
    assistant_id, target_language, prompt, models: List[str]
) -> MultiModelResponse:
    validate_models(models)

    responses = await asyncio.gather(
        *[
            _run_single_workflow(assistant_id, target_language, prompt, model)
            for model in models
        ]
    )

    return MultiModelResponse(responses=list(responses))


async def stream_workflow_service(
    assistant_id, 
    target_language, 
    prompt, 
    model: str
) -> AsyncGenerator[str, None]:
    validate_models([model])
    
    with SessionLocal() as db_session:
        workflow_request = build_workflow_request(
            db_session, assistant_id, target_language, prompt, model
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