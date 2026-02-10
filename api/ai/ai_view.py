from api.ai.ai_response_model import StreamRequest, AvailableModelsResponse
from api.ai.ai_service import run_workflow_service, stream_workflow_service, get_available_models_service
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from starlette import status
from api.Auth.auth_repository import get_optional_token
from typing import Annotated, Optional
from api.config import get
from api.error_constant import ErrorConstants, ResponseError

ai_router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no"
}


@ai_router.get("/models", status_code=status.HTTP_200_OK, response_model=AvailableModelsResponse)
async def get_available_models():
    return get_available_models_service()

@ai_router.post("", status_code=status.HTTP_200_OK)
async def run_workflow(
    payload: StreamRequest, 
    token: Annotated[Optional[str], Depends(get_optional_token)],
):
    max_query_length = get("MAX_QUERY_LENGTH")
    total_prompt_length = sum(len(p) for p in payload.prompt)
    if total_prompt_length > int(max_query_length):
        raise HTTPException(
            status_code=400, 
            detail=ResponseError(
                error=ErrorConstants.BAD_REQUEST, 
                message=ErrorConstants.MAX_QUERY_LENGTH_ERROR
            ).model_dump()
        )

    return await run_workflow_service(
        assistant_id=payload.assistant_id,
        target_language=payload.target_language,
        prompt=payload.prompt,
        model=payload.model,
    )


@ai_router.post("/stream", status_code=status.HTTP_200_OK)
async def stream_workflow(
    payload: StreamRequest, 
    token: Annotated[Optional[str], Depends(get_optional_token)],
):
    max_query_length = get("MAX_QUERY_LENGTH")
    total_prompt_length = sum(len(p) for p in payload.prompt)
    if total_prompt_length > int(max_query_length):
        raise HTTPException(
            status_code=400, 
            detail=ResponseError(
                error=ErrorConstants.BAD_REQUEST, 
                message=ErrorConstants.MAX_QUERY_LENGTH_ERROR
            ).model_dump()
        )

    return StreamingResponse(
        stream_workflow_service(
            assistant_id=payload.assistant_id,
            target_language=payload.target_language,
            prompt=payload.prompt,
            model=payload.model,
        ),
        media_type="text/event-stream",
        headers=SSE_HEADERS
    )
