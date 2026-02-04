from api.ai.ai_response_model import StreamRequest
from api.ai.ai_service import get_translation_response_service
from fastapi import APIRouter,HTTPException,Depends
from starlette import status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from api.config import get
from api.error_constant import ErrorConstants, ResponseError

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
    max_query_length = get("MAX_QUERY_LENGTH")
    if len(payload.prompt) > int(max_query_length):
        raise HTTPException(status_code=400, detail=ResponseError(error=ErrorConstants.BAD_REQUEST, message=ErrorConstants.MAX_QUERY_LENGTH_ERROR).model_dump())

    return await get_translation_response_service(
        assistant_id=payload.assistant_id,
        target_language=payload.target_language,
        prompt=payload.prompt,
        model=payload.model,
    )
