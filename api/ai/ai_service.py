from api.Assistant.assistant_repository import get_assistant_by_id_repository
from api.Assistant.assistant_response_model import ContextRequest
from api.langgraph.workflow_init import run_workflow
from api.ai.ai_response_model import WorkflowRequest, StreamResponse, TranslationResult, ResultMetadata, ResponseMetadata
from api.db.pg_database import SessionLocal
from api.llm.router import get_model_router
from api.langgraph.workflow_create import create_workflow
from fastapi import HTTPException
from datetime import datetime
import json
import time

async def get_translation_response_service(assistant_id, target_language, prompt, model):
    model_router = get_model_router()
    if not model_router.validate_model_availability(model):
        available_models = model_router.available_models()
        raise HTTPException(status_code=400, detail=f"Model not available: Select from this list: {list(available_models.keys())}")
    
    with SessionLocal() as db_session:
        assistant_detail=get_assistant_by_id_repository(db_session, assistant_id)

        workflow_request = WorkflowRequest(
        assistant_name=assistant_detail.name,
        assistant_source_type=assistant_detail.source_type,
        assistant_system_prompt=assistant_detail.system_prompt,
        contexts=[ContextRequest(content=context.content, file_url=context.file_url) for context in assistant_detail.contexts],
        target_language=target_language,
        text=prompt,
        model=model
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


async def get_translation_response_stream_service(assistant_id, target_language, prompt, model):
    model_router = get_model_router()
    if not model_router.validate_model_availability(model):
        available_models = model_router.available_models()
        raise HTTPException(status_code=400, detail=f"Model not available: Select from this list: {list(available_models.keys())}")
    
    with SessionLocal() as db_session:
        assistant_detail = get_assistant_by_id_repository(db_session, assistant_id)

        workflow_request = WorkflowRequest(
            assistant_name=assistant_detail.name,
            assistant_source_type=assistant_detail.source_type,
            assistant_system_prompt=assistant_detail.system_prompt,
            contexts=[ContextRequest(content=context.content, file_url=context.file_url) for context in assistant_detail.contexts],
            target_language=target_language,
            text=prompt,
            model=model
        )
    
    workflow = create_workflow()
    app = workflow.compile()

    initial_state = {
        "original_request": workflow_request,
        "batches": [],
        "current_batch_index": 0,
        "batch_results": [],
        "final_results": [],
        "total_texts": 0,
        "processed_texts": 0,
        "workflow_start_time": 0.0,
        "workflow_status": "initializing",
        "errors": [],
        "retry_count": 0,
        "model_name": workflow_request.model,
        "custom_steps": {},
        "metadata": {},
    }

    workflow_start_time = time.time()
    last_batch_index = -1
    
    async for node_output in app.astream(initial_state):
        for node_name, state in node_output.items():
            
            if node_name == "initialize":
                batches = state.get("batches", [])
                total_texts = state.get("total_texts", 0)
                batch_size = len(batches[0].texts) if batches else 0
                
                init_event = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "initialization",
                    "status": "starting",
                    "total_texts": total_texts,
                    "target_language": target_language,
                    "model": model,
                    "batch_size": batch_size
                }
                yield f"data: {json.dumps(init_event)}\n\n"
                
                planning_event = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "planning",
                    "status": "batches_created",
                    "total_batches": len(batches),
                    "batch_size": batch_size
                }
                yield f"data: {json.dumps(planning_event)}\n\n"
            
            elif node_name == "process_batch":
                batches = state.get("batches", [])
                batch_results = state.get("batch_results", [])
                current_batch_index = state.get("current_batch_index", 0) - 1
                total_texts = state.get("total_texts", 0)
                processed_texts = state.get("processed_texts", 0)
                
                if current_batch_index > last_batch_index and batch_results:
                    last_batch_index = current_batch_index
                    current_batch_result = batch_results[-1]
                    
                    batch_start_event = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "batch_start",
                        "status": "processing_batch",
                        "batch_number": current_batch_index + 1,
                        "batch_id": current_batch_result.batch_id,
                        "texts_in_batch": len(current_batch_result.results),
                        "progress_percent": int((processed_texts - len(current_batch_result.results)) / total_texts * 100) if total_texts > 0 else 0
                    }
                    yield f"data: {json.dumps(batch_start_event)}\n\n"
                    
                    batch_results_data = [
                        {
                            "original_text": result.original_text,
                            "translated_text": result.translated_text,
                            "metadata": {
                                "batch_id": result.metadata.get("batch_id"),
                                "model_used": result.metadata.get("model_used"),
                                "text_type": result.metadata.get("text_type"),
                                "batch_index": current_batch_index
                            }
                        }
                        for result in current_batch_result.results
                    ]
                    
                    batch_completed_event = {
                        "timestamp": datetime.now().isoformat(),
                        "type": "batch_completed",
                        "status": "batch_completed",
                        "batch_number": current_batch_index + 1,
                        "batch_id": current_batch_result.batch_id,
                        "processing_time": current_batch_result.processing_time,
                        "texts_processed": len(current_batch_result.results),
                        "cumulative_progress": int(processed_texts / total_texts * 100) if total_texts > 0 else 0,
                        "batch_results": batch_results_data
                    }
                    yield f"data: {json.dumps(batch_completed_event)}\n\n"
            
            elif node_name == "finalize":
                total_processing_time = time.time() - workflow_start_time
                final_results = state.get("final_results", [])
                total_texts = state.get("total_texts", 0)
                
                results_data = [
                    {
                        "original_text": result.original_text,
                        "translated_text": result.translated_text,
                        "metadata": {
                            "batch_id": result.metadata.get("batch_id"),
                            "model_used": result.metadata.get("model_used"),
                            "text_type": result.metadata.get("text_type"),
                            "batch_index": idx
                        }
                    }
                    for idx, result in enumerate(final_results)
                ]
                
                completion_event = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "completion",
                    "status": "completed",
                    "total_texts": total_texts,
                    "successful_translations": len(final_results),
                    "total_processing_time": round(total_processing_time, 2),
                    "average_time_per_text": round(total_processing_time / len(final_results), 2) if final_results else 0,
                    "results": results_data
                }
                yield f"data: {json.dumps(completion_event)}\n\n"
