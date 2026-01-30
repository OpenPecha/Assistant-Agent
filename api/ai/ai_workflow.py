"""
LangGraph workflow for LLM text processing.

This module implements a flexible, extensible workflow for running
LLM-powered text tasks (currently translation) with support for batch processing
and multiple models.

Glossary extraction removed, and model_params forwarding removed.
"""

import time
import uuid
from datetime import datetime

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

# Keep existing translation types, but alias them locally to generic names
from api.ai.translation_types import (
    TranslationWorkflowState as WorkflowState,
    TranslationBatch as WorkBatch,
    TranslationResult as WorkResult,
    BatchResult,
)

from api.llm.router import get_model_router
from api.ai.prompts import get_translation_prompt  # still translation-specific for now
from api.ai.utils import clean_translation_text
from api.ai.ai_response_model import WorkflowRequest
from api.ai.cache import get_cache
from api import config

DEFAULT_MAX_BATCH_SIZE = 50
DEFAULT_MIN_BATCH_SIZE = 1


def initialize_workflow(state: WorkflowState) -> WorkflowState:
    """
    Initialize the workflow state.

    Prepares the workflow by:
    - Setting up initial state
    - Creating batches from input texts
    - Initializing counters and metadata
    """
    request = state["original_request"]

    batches = []
    texts = request.text
    max_batch_size = int(config.get("MAX_BATCH_SIZE") or DEFAULT_MAX_BATCH_SIZE)
    batch_size = min(int(config.get("MIN_BATCH_SIZE") or DEFAULT_MIN_BATCH_SIZE), max_batch_size)

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch = WorkBatch(
            batch_id=str(uuid.uuid4()),
            texts=batch_texts,
            target_language=request.target_language,
            text_type=request.assistant_source_type,
            model_name=request.model,
            user_rules=request.assistant_system_prompt,
        )
        batches.append(batch)

    state.update(
        {
            "batches": batches,
            "current_batch_index": 0,
            "batch_results": [],
            "final_results": [],
            "total_texts": len(texts),
            "processed_texts": 0,
            "workflow_start_time": time.time(),
            "workflow_status": "running",
            "errors": [],
            "retry_count": 0,
            "model_name": request.model,
            "custom_steps": {},
            "metadata": {
                "initialized_at": datetime.now().isoformat(),
                "total_batches": len(batches),
            },
        }
    )

    return state


def process_batch(state: WorkflowState) -> WorkflowState:
    """
    Process a single batch.

    Core processing node that:
    - Takes the current batch
    - Uses the selected model to produce outputs
    - Handles errors and updates processing state

    NOTE: Implementation is currently translation-specific (prompt + cache keys),
    but naming here is task-generic so you can extend later.
    """
    current_index = state["current_batch_index"]
    batches = state["batches"]

    if current_index >= len(batches):
        state["workflow_status"] = "completed"
        return state

    current_batch = batches[current_index]
    batch_start_time = time.time()

    try:
        model_router = get_model_router()
        model = model_router.get_model(current_batch.model_name)

        cache = get_cache()
        item_results = []

        for input_text in current_batch.texts:
            # Cache wrapper stays translation-based internally, but naming is generic here
            cache_key = cache.get_translation_cache_key(
                input_text,
                current_batch.target_language,
                current_batch.text_type,
                current_batch.model_name,
                current_batch.user_rules,
            )
            cached_output = cache.get_translation(cache_key)

            if cached_output:
                output_text = cached_output
            else:
                prompt = get_translation_prompt(
                    source_text=input_text,
                    target_language=current_batch.target_language,
                    text_type=current_batch.text_type,
                    user_rules=current_batch.user_rules,
                )
                message = HumanMessage(content=prompt)
                response = model.invoke([message])
                output_text = clean_translation_text(response.content)
                cache.set_translation(cache_key, output_text)

            result = WorkResult(
                original_text=input_text,
                translated_text=output_text,
                metadata={
                    "batch_id": current_batch.batch_id,
                    "model_used": current_batch.model_name,
                    "text_type": current_batch.text_type,
                },
            )
            item_results.append(result)

        processing_time = time.time() - batch_start_time
        batch_result = BatchResult(
            batch_id=current_batch.batch_id,
            results=item_results,
            processing_time=processing_time,
            model_used=current_batch.model_name,
            success=True,
        )

        state["batch_results"].append(batch_result)
        state["final_results"].extend(item_results)
        state["processed_texts"] += len(current_batch.texts)
        state["current_batch_index"] += 1

    except Exception as e:
        processing_time = time.time() - batch_start_time
        error_result = BatchResult(
            batch_id=current_batch.batch_id,
            results=[],
            processing_time=processing_time,
            model_used=current_batch.model_name,
            success=False,
            error_message=str(e),
        )

        state["batch_results"].append(error_result)
        state["errors"].append(
            {
                "batch_id": current_batch.batch_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
        )
        state["current_batch_index"] += 1

    return state


def check_completion(state: WorkflowState) -> str:
    """
    Check if workflow is complete or should continue processing.
    """
    current_index = state["current_batch_index"]
    total_batches = len(state["batches"])

    return "finalize" if current_index >= total_batches else "continue"


def finalize_workflow(state: WorkflowState) -> WorkflowState:
    """
    Finalize the workflow.

    Calculates final statistics, sets completion status, prepares final output.
    """
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


def create_workflow() -> StateGraph:
    """
    Create the LangGraph workflow.
    (Glossary extraction removed, model_params forwarding removed.)
    """
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