from typing import List, Any, Optional, Dict
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


class ModelInfo(BaseModel):
    name: str
    provider: str
    description: str
    is_thinking: bool
    capabilities: List[str]
    context_window: Optional[int] = None


class AvailableModelsResponse(BaseModel):
    models: Dict[str, ModelInfo]


class StreamRequest(BaseModel):
    assistant_id: UUID
    target_language: Optional[str] = None
    prompt: List[str] = Field(min_length=1)
    model: str = Field(min_length=1)

class WorkflowResult(BaseModel):
    output_text: str


class ResponseMetadata(BaseModel):
    initialized_at: str
    total_batches: int
    completed_at: str
    total_processing_time: float


class StreamResponse(BaseModel):
    results: List[WorkflowResult]
    metadata: ResponseMetadata
    errors: List[Any]