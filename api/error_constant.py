from pydantic import BaseModel

class ErrorConstants:
    BAD_REQUEST = "Bad Request"
    MAX_QUERY_LENGTH_ERROR = "Query length exceeds the maximum allowed length"
    TOKEN_ERROR_MESSAGE = "Invalid or no token found"
    INVALID_UUID_MESSAGE="Invalid UUID"
    FORBIDDEN_ERROR_MESSAGE="Forbidden action"
    ASSISTANT_NOT_FOUND="Assistant not found"
    FAILED_TO_DELETE_ASSISTANT="Failed to delete assistant"
    FAILED_TO_UPDATE_ASSISTANT="Failed to update assistant"
    UNAUTHORIZED_ERROR_MESSAGE="Unauthorized, your email does not match the assistant creator's email"
    INVALID_FILE_FORMAT="Invalid file format"
    FILE_TOO_LARGE="File size exceeds the maximum allowed size"
    FILE_NOT_FOUND="File not found"
    FAILED_TO_DOWNLOAD_FILE_FROM_S3="Failed to download file from S3"
    AN_UNEXPECTED_ERROR_OCCURRED_WHILE_DOWNLOADING_FILE="An unexpected error occurred while downloading file"
    FAILED_TO_UPLOAD_FILE_TO_S3="Failed to upload file to S3"
    AN_UNEXPECTED_ERROR_OCCURRED="An unexpected error occurred"
    FAILED_TO_UPLOAD_BYTES_TO_S3="Failed to upload bytes to S3"
    AN_UNEXPECTED_ERROR_OCCURRED_WHILE_UPLOADING_BYTES="An unexpected error occurred while uploading bytes"
    FAILED_TO_DELETE_FILE="Failed to delete file"

class ResponseError(BaseModel):
    error: str
    message: str