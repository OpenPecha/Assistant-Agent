from typing import AsyncGenerator

from api.Assistant.assistant_repository import get_assistant_by_id_repository
from api.Assistant.assistant_response_model import ContextRequest
from api.langgraph.workflow_init import run_workflow
from api.langgraph.workflow_stream import stream_workflow_events
from api.ai.ai_response_model import WorkflowRequest, StreamResponse, TranslationResult, ResultMetadata, ResponseMetadata
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
            ContextRequest(content=context.content, file_url=context.file_url) 
            for context in assistant_detail.contexts
        ],
        target_language=target_language,
        text=prompt,
        model=model
    )


def validate_model(model: str) -> None:
    model_router = get_model_router()
    if not model_router.validate_model_availability(model):
        available_models = model_router.available_models()
        raise HTTPException(
            status_code=400, 
            detail=f"Model not available: Select from this list: {list(available_models.keys())}"
        )


async def run_workflow_service(assistant_id, target_language, prompt, model):
    validate_model(model)
    
    with SessionLocal() as db_session:
        workflow_request = build_workflow_request(
            db_session, assistant_id, target_language, prompt, model
        )
    
    workflow_response = await run_workflow(workflow_request)
    
    results = [
        TranslationResult(
            original_text=result.original_text,
            translated_text=result.translated_text,
            metadata=ResultMetadata(
                batch_id=result.metadata.get("batch_id"),
                model_used=result.metadata.get("model_used"),
                text_type=result.metadata.get("text_type")
            )
        )
        for result in workflow_response.get("final_results", [])
    ]
    
    workflow_metadata = workflow_response.get("metadata", {})
    response_metadata = ResponseMetadata(
        initialized_at=workflow_metadata.get("initialized_at"),
        total_batches=workflow_metadata.get("total_batches"),
        completed_at=workflow_metadata.get("completed_at"),
        total_processing_time=workflow_metadata.get("total_processing_time")
    )
    
    response = StreamResponse(
        results=results,
        metadata=response_metadata,
        errors=workflow_response.get("errors", [])
    )
    
    return response


async def stream_workflow_service(
    assistant_id, 
    target_language, 
    prompt, 
    model
) -> AsyncGenerator[str, None]:
    validate_model(model)
    
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
