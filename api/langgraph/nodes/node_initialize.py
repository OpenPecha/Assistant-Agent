import time
import uuid
from datetime import datetime

from api.langgraph.workflow_type import WorkflowState,Batch
from api.utils import Utils
from api import config

DEFAULT_MAX_BATCH_SIZE = 2

def initialize_workflow(state: WorkflowState) -> WorkflowState:
    request = state["original_request"]

    batches = []
    texts = request.text
    init_size = int(config.get("MAX_BATCH_SIZE") or DEFAULT_MAX_BATCH_SIZE)
    batch_size = init_size


    processed_contexts = Utils.process_contexts(request.contexts) if request.contexts else None

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch = Batch(
            batch_id=str(uuid.uuid4()),
            texts=batch_texts,
            target_language=request.target_language,
            text_type=request.assistant_source_type,
            model_name=request.model,
            user_rules=request.assistant_system_prompt,
            contexts=processed_contexts,
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