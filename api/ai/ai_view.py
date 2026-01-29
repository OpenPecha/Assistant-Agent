from api.ai.ai_service import get_stream_response_service
from fastapi import APIRouter
from starlette import status
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from uuid import UUID
oauth2_scheme = HTTPBearer()

ai_router=APIRouter(
    prefix="/ai",
    tags=["ai"]
)

@ai_router.get("/", status_code=status.HTTP_200_OK)
async def get_stream_response(
    assistant_id: UUID,
    target_language:str,
    prompt:str,
    model:str,
    authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)]
):
    return await get_stream_response_service(assistant_id=assistant_id, target_language=target_language, prompt=prompt, model=model)
