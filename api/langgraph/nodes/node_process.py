import time
from datetime import datetime
from langchain_core.messages import HumanMessage
from api.langgraph.workflow_type import WorkflowState, Result, BatchResult
from api.llm.router import get_model_router
from api.ai.prompts import get_specialized_prompt
from api.ai.utils import clean_translation_text


async def process_batch(state: WorkflowState) -> WorkflowState:
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

        item_results = []

        for input_text in current_batch.texts:
            prompt = get_specialized_prompt(
                source_text=input_text,
                target_language=current_batch.target_language,
                text_type=current_batch.text_type,
                user_rules=current_batch.user_rules,
                contexts=current_batch.contexts,
            )
            message = HumanMessage(content=prompt)
            response = await model.ainvoke([message])
            output_text = clean_translation_text(response.content)

            result = Result(
                input_text=input_text,
                output_text=output_text,
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
