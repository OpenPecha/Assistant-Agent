from typing import List, Any, Optional
from api.Assistant.assistant_response_model import ContextRequest
from pydantic import BaseModel, Field
from uuid import UUID

class WorkflowRequest(BaseModel):
    assistant_name: str
    assistant_source_type: str
    assistant_system_prompt: str
    contexts: List[ContextRequest]
    target_language: Optional[str] = None
    text: List[str]
    model: str


class StreamRequest(BaseModel):
    assistant_id: UUID
    target_language: Optional[str] = None
    prompt: List[str] = Field(min_length=1)
    model: str = Field(min_length=1)

class ResultMetadata(BaseModel):
    batch_id: str
    model_used: str
    text_type: str


class TranslationResult(BaseModel):
    input_text: str
    output_text: str
    metadata: ResultMetadata


class ResponseMetadata(BaseModel):
    initialized_at: str
    total_batches: int
    completed_at: str
    total_processing_time: float


class StreamResponse(BaseModel):
    results: List[TranslationResult]
    metadata: ResponseMetadata
    errors: List[Any]