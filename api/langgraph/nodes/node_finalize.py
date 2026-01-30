import time
from datetime import datetime

from api.langgraph.workflow_type import WorkflowState

def finalize_workflow(state: WorkflowState) -> WorkflowState:
    total_time = time.time() - state["workflow_start_time"]
    successful_batches = len([r for r in state["batch_results"] if r.success])
    failed_batches = len([r for r in state["batch_results"] if not r.success])

    state["workflow_status"] = "completed"
    state["metadata"].update(
        {
            "completed_at": datetime.now().isoformat(),
            "total_processing_time": total_time,
            "successful_batches": successful_batches,
            "failed_batches": failed_batches,
            "total_outputs": len(state["final_results"]),
            "success_rate": (
                len(state["final_results"]) / state["total_texts"] if state["total_texts"] > 0 else 0
            ),
        }
    )

    return state