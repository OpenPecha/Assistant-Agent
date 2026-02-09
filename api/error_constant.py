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

class ResponseError(BaseModel):
    error: str
    message: str