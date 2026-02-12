import os
import uuid
from fastapi import UploadFile, HTTPException, status
from .S3_utils import upload_file, generate_presigned_access_url
from ..config import get, get_int
from .media_response_model import MediaUploadResponse
from ..error_constant import ErrorConstants


def validate_file(file: UploadFile) -> None:
    file_extension = os.path.splitext(file.filename.lower())[1] if file.filename else ''
    if file_extension not in get("ALLOWED_EXTENSIONS"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=ErrorConstants.INVALID_FILE_FORMAT
        )

    max_file_size_bytes = get_int("MAX_FILE_SIZE_MB") * 1024 * 1024
    if hasattr(file, 'size') and file.size and file.size > max_file_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, 
            detail=ErrorConstants.FILE_TOO_LARGE
        )


def prepare_file_upload(file: UploadFile, document_path_full: str) -> tuple[str, str]:
    file_name = file.filename if file.filename else "uploaded_file"
    s3_key = f"{document_path_full}/{file_name}"
    
    upload_key = upload_file(
        bucket_name=get("AWS_BUCKET_NAME"),
        s3_key=s3_key,
        file=file
    )
    
    file_url = generate_presigned_access_url(
        bucket_name=get("AWS_BUCKET_NAME"),
        s3_key=upload_key
    )
    
    return upload_key, file_url


def upload_file_service(token: str, file: UploadFile) -> MediaUploadResponse:
    validate_file(file)
    unique_id = str(uuid.uuid4())
    path = "documents/context"
    document_path_full = f"{path}/{unique_id}"
    
    upload_key, file_url = prepare_file_upload(
        file=file,
        document_path_full=document_path_full
    )
    
    return MediaUploadResponse(
        file_url=file_url,
        key=upload_key,
        path=document_path_full
    )
