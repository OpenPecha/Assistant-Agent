from api.ai.ai_response_model import WorkflowRequest
from api.ai.translation_types import (
    TranslationWorkflowState as WorkflowState
)
from api.langgraph.workflow_create import create_workflow

async def run_workflow(request: WorkflowRequest) -> WorkflowState:
    workflow = create_workflow()
    app = workflow.compile()

    initial_state: WorkflowState = {
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
        "custom_steps": {},
        "metadata": {},
    }

    final_state = await app.ainvoke(initial_state)
    return final_state