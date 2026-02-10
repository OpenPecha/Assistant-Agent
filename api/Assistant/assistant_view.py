from fastapi import APIRouter
from starlette import status
from api.Assistant.assistant_response_model import AssistantResponse, AssistantRequest, AssistantInfoResponse, UpdateAssistantRequest
from fastapi import Query, Depends
from api.Assistant.assistant_service import create_assistant_service, get_assistant_by_id_service, get_assistants, delete_assistant_service, update_assistant_service
from api.Auth.auth_repository import get_optional_token
from typing import Annotated, Optional
from uuid import UUID
from api.constant import Constant

assistant_router=APIRouter(
    prefix="/assistant",
    tags=["assistant"]
)

@assistant_router.get("", status_code=status.HTTP_200_OK)
async def get_all_assistants(   
    skip: int = Query(default=0),
    limit: int = Query(default=10))  -> AssistantResponse:
    return get_assistants(skip=skip, limit=limit)

@assistant_router.post("", status_code=status.HTTP_201_CREATED)
async def create_assistant(
    assistant_request: AssistantRequest,
    token: Annotated[Optional[str], Depends(get_optional_token)]
):
    create_assistant_service(token=token, assistant_request=assistant_request)
    return {"message": Constant.CREATED_ASSISTANT_MESSAGE}

@assistant_router.get("/{assistant_id}", status_code=status.HTTP_200_OK)
async def get_assistant_by_id(
    assistant_id: UUID,
    token: Annotated[Optional[str], Depends(get_optional_token)]
) -> AssistantInfoResponse:
    return get_assistant_by_id_service(assistant_id=assistant_id)

@assistant_router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assistant(
    assistant_id: UUID,
    token: Annotated[Optional[str], Depends(get_optional_token)]
):
    return delete_assistant_service(assistant_id=assistant_id, token=token)

@assistant_router.put("/{assistant_id}", status_code=status.HTTP_200_OK)
async def update_assistant(
    assistant_id: UUID,
    update_request: UpdateAssistantRequest,
    token: Annotated[Optional[str], Depends(get_optional_token)]
) -> AssistantInfoResponse:
    return update_assistant_service(
        assistant_id=assistant_id,
        update_request=update_request,
        token=token
    )