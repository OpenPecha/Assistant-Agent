from api.ai.ai_response_model import StreamRequest
from api.ai.ai_service import get_translation_response_service
from fastapi import APIRouter
from starlette import status
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
oauth2_scheme = HTTPBearer()

ai_router=APIRouter(
    prefix="/ai",
    tags=["ai"]
)

@ai_router.post("", status_code=status.HTTP_200_OK)
async def get_translation_response(
    payload: StreamRequest, 
    authentication_credential: Annotated[
        HTTPAuthorizationCredentials, Depends(oauth2_scheme)
    ],
):
    return await get_translation_response_service(
        assistant_id=payload.assistant_id,
        target_language=payload.target_language,
        prompt=payload.prompt,
        model=payload.model,
    )
