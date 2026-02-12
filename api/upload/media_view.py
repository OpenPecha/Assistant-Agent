from fastapi import APIRouter, UploadFile, File, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .media_service import upload_file_service
from .media_response_model import MediaUploadResponse
from typing import Annotated

oauth2_scheme = HTTPBearer()

media_router = APIRouter(
    prefix="/media",
    tags=["media"]
)


@media_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media_image(authentication_credential: Annotated[HTTPAuthorizationCredentials, Depends(oauth2_scheme)], file: UploadFile = File(...)) -> MediaUploadResponse:
    return upload_file_service(token=authentication_credential.credentials, file=file)