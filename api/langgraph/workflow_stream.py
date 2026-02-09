from typing import AsyncGenerator, Dict, Any
from datetime import datetime
import json
import time

from api.ai.ai_response_model import WorkflowRequest
from api.langgraph.workflow_type import WorkflowState
from api.langgraph.workflow_create import create_workflow


def create_initial_state(request: WorkflowRequest) -> WorkflowState:
    return {
        "original_request": request,
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
        "model_name": request.model,
        "model_params": {},
        "custom_steps": {},
        "metadata": {},
    }


def create_event(event_type: str, data: Dict[str, Any]) -> str:
    event = {
        "timestamp": datetime.now().isoformat(),
        "type": event_type,
        **data
    }
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


async def stream_workflow_events(
    request: WorkflowRequest,
    target_language: str,
    model: str
) -> AsyncGenerator[str, None]:
    workflow = create_workflow()
    app = workflow.compile()
    initial_state = create_initial_state(request)
    
    workflow_start_time = time.time()
    current_batch_info = {"batch_id": None, "batch_index": -1}
    accumulated_text = ""
    
    try:
        async for event in app.astream_events(initial_state, version="v2"):
            kind = event.get("event")
            
            if kind == "on_chain_start":
                node_name = event.get("name")
                if node_name == "initialize":
                    yield create_event("initialization", {
                        "status": "starting",
                        "target_language": target_language,
                        "model": model
                    })
            
            elif kind == "on_chain_end":
                node_name = event.get("name")
                
                if node_name == "initialize":
                    output = event.get("data", {}).get("output", {})
                    batches = output.get("batches", [])
                    total_texts = output.get("total_texts", 0)
                    batch_size = len(batches[0].texts) if batches else 0
                    
                    yield create_event("planning", {
                        "status": "batches_created",
                        "total_batches": len(batches),
                        "total_texts": total_texts,
                        "batch_size": batch_size
                    })
                
                elif node_name == "finalize":
                    output = event.get("data", {}).get("output", {})
                    final_results = output.get("final_results", [])
                    total_texts = output.get("total_texts", 0)
                    total_processing_time = time.time() - workflow_start_time
                    
                    results_data = [
                        {"output_text": result.output_text}
                        for result in final_results
                    ]
                    
                    yield create_event("completion", {
                        "status": "completed",
                        "total_texts": total_texts,
                        "successful_translations": len(final_results),
                        "total_processing_time": round(total_processing_time, 2),
                        "results": results_data
                    })
            
            elif kind == "on_chat_model_start":
                metadata = event.get("metadata", {})
                langgraph_node = metadata.get("langgraph_node")
                
                if langgraph_node == "process_batch":
                    batch_index = metadata.get("langgraph_step", 0)
                    current_batch_info["batch_index"] = batch_index
                    accumulated_text = ""
                    
                    yield create_event("batch_start", {
                        "status": "processing",
                        "batch_index": batch_index
                    })
            
            elif kind == "on_chat_model_stream":
                metadata = event.get("metadata", {})
                langgraph_node = metadata.get("langgraph_node")
                
                if langgraph_node == "process_batch":
                    chunk = event.get("data", {}).get("chunk")
                    if chunk and hasattr(chunk, "content") and chunk.content:
                        token = chunk.content
                        accumulated_text += token
                        
                        yield create_event("token", {
                            "data": token,
                            "batch_index": current_batch_info["batch_index"]
                        })
            
            elif kind == "on_chat_model_end":
                metadata = event.get("metadata", {})
                langgraph_node = metadata.get("langgraph_node")
                
                if langgraph_node == "process_batch" and accumulated_text:
                    yield create_event("text_complete", {
                        "status": "text_completed",
                        "batch_index": current_batch_info["batch_index"],
                        "output_text": accumulated_text
                    })
                    accumulated_text = ""
        
        yield create_event("done", {"status": "stream_ended"})
        
    except Exception as e:
        yield create_event("error", {"message": str(e)})
