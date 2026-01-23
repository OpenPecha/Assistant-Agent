from fastapi import APIRouter
from starlette import status
from api.Assistant.assistant_response_model import AssistantResponse
from fastapi import Query
from api.Assistant.assistant_service import get_assistants

assistant_router=APIRouter(
    prefix="/assistant",
    tags=["assistant"]
)

@assistant_router.get("", status_code=status.HTTP_200_OK)
async def get_all_assistants(   
    skip: int = Query(default=0),
    limit: int = Query(default=10))  -> AssistantResponse:
    return get_assistants(skip=skip, limit=limit)
