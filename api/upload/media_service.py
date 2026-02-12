import os
from fastapi import UploadFile, HTTPException, status
from .S3_utils import upload_file
from ..config import get, get_int
from .media_response_model import MediaUploadResponse
from ..error_constant import ErrorConstants

def upload_file_service(token: str, file: UploadFile) -> MediaUploadResponse:
    validate_file(file)
    return upload_file(bucket_name=get("AWS_BUCKET_NAME"), s3_key=file.filename, file=file)


def validate_file(file: UploadFile) -> None:
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    if file_extension not in get("ALLOWED_EXTENSIONS"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.INVALID_FILE_FORMAT)

    if hasattr(file, 'size') and file.size and file.size > get_int("MAX_FILE_SIZE"):
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=ErrorConstants.FILE_TOO_LARGE)