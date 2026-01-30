from typing import List
from api.Assistant.assistant_response_model import ContextRequest
from pydantic import BaseModel, Field
from uuid import UUID

class WorkflowRequest(BaseModel):
    assistant_name: str
    assistant_source_type: str
    assistant_system_prompt: str
    contexts: List[ContextRequest]
    target_language: str
    text: List[str]
    model: str


class StreamRequest(BaseModel):
    assistant_id: UUID
    target_language: str = Field(min_length=2)
    prompt: str = Field(min_length=1)
    model: str = Field(min_length=1)