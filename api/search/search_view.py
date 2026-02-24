from __future__ import annotations

from fastapi import APIRouter
from starlette import status
from api.search.search_service import get_search_texts_details
from api.search.search_response_model import SearchTextsDetailsResponse

search_router = APIRouter(
    prefix="/search",
    tags=["search"]
)


@search_router.get("/{text_id}", status_code=status.HTTP_200_OK, response_model=list[SearchTextsDetailsResponse])
async def read_texts_details(
        text_id: str
)->list[SearchTextsDetailsResponse]:
    return await get_search_texts_details(
        text_id=text_id
    )