from langgraph.graph import StateGraph, END

from api.ai.translation_types import (
    TranslationWorkflowState as WorkflowState
)

from api.langgraph.nodes.node_initialize import initialize_workflow
from api.langgraph.nodes.node_process import process_batch
from api.langgraph.nodes.node_finalize import finalize_workflow

def check_completion(state: WorkflowState) -> str:
    current_index = state["current_batch_index"]
    total_batches = len(state["batches"])

    return "finalize" if current_index >= total_batches else "continue"

def create_workflow() -> StateGraph:
    workflow = StateGraph(WorkflowState)

    workflow.add_node("initialize", initialize_workflow)
    workflow.add_node("process_batch", process_batch)
    workflow.add_node("finalize", finalize_workflow)

    workflow.set_entry_point("initialize")
    workflow.add_edge("initialize", "process_batch")

    workflow.add_conditional_edges(
        "process_batch",
        check_completion,
        {
            "continue": "process_batch",
            "finalize": "finalize",
        },
    )

    workflow.add_edge("finalize", END)
    return workflow