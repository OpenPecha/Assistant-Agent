from fastapi import APIRouter
from starlette import status
from api.Assistant.assistant_response_model import AssistantResponse, AssistantRequest
from fastapi import Query, Depends
from api.Assistant.assistant_service import create_assistant_service, get_assistants
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

oauth2_scheme = HTTPBearer()

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
async def create_assistant(assistant_request: AssistantRequest, authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]):
    return create_assistant_service(token=authentication_credential.credentials, assistant_request=assistant_request)