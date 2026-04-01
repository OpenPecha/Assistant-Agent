from typing import List, Any, Optional, Dict
from api.Assistant.assistant_response_model import ContextRequest
from pydantic import BaseModel, Field
from uuid import UUID

class SegmentRequest(BaseModel):
    start: int
    end: int


class WorkflowRequest(BaseModel):
    assistant_name: str
    assistant_system_prompt: str
    assistant_user_prompt: Optional[str] = None
    assistant_variables: Optional[Any] = None
    instance_ids: List[str] = []
    segments: Optional[SegmentRequest] = None
    contexts: List[ContextRequest]
    target_language: Optional[str] = None
    text: List[str]
    model: str
    instruction: Optional[str] = None


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
    segments: Optional[SegmentRequest] = None
    model: str = Field(min_length=1)
    offset: int = 0
    instruction: Optional[str] = None

class FuzzyMatch(BaseModel):
    source_text: str
    target_text: str
    score: float


class WorkflowResult(BaseModel):
    output_text: str
    from_memory: bool = False
    fuzzy_matches: List[FuzzyMatch] = []


class ResponseMetadata(BaseModel):
    initialized_at: str
    total_batches: int
    completed_at: str
    total_processing_time: float


class StreamResponse(BaseModel):
    results: List[WorkflowResult]
    metadata: ResponseMetadata
    errors: List[Any]

class EnhanceRequest(BaseModel):
    prompt: str
    model: str = "claude-sonnet-4-20250514"

class EnhanceResponse(BaseModel):
    enhanced_prompt: str