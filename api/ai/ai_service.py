from api.Assistant.assistant_repository import get_assistant_by_id_repository
from api.db.pg_database import SessionLocal
from api.llm.router import get_model_router
from fastapi import HTTPException

def get_stream_response_service(assistant_id, target_language, prompt, model):
    model_router = get_model_router()
    if not model_router.validate_model_availability(model):
        raise HTTPException(status_code=400, detail="Model not available")
    
    # old agent was validating batchsize but we are not as we are not getting it from the request

    with SessionLocal() as db_session:
        assistant_detail=get_assistant_by_id_repository(db_session, assistant_id)

    #     workflow_request = TranslationWorkflowRequest(
        
    #     contexts=assistant_detail.contexts,
    #     target_language=target_language,
    #     prompt=prompt,
    #     model=model
    # )

    # workflow_response = translate_workflow(workflow_request)
    # return workflow_response