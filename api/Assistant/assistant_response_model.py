from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

class ContextRequest(BaseModel):
    content: Optional[str] = None
    file_url: Optional[str] = None

class ContextResponse(BaseModel):
    id: UUID
    content: Optional[str] = None
    file_url: Optional[str] = None

class AssistantInfoResponse(BaseModel):
    id: UUID
    name: str
    source_type: Optional[str] = None
    description: Optional[str] = None
    system_prompt: str
    contexts: List[ContextResponse]
    created_by: Optional[str] = None
    system_assistance: bool = False

class AssistantResponse(BaseModel):
    assistants: List[AssistantInfoResponse]
    skip: int
    limit: int
    total: int

class AssistantRequest(BaseModel):
    name: str
    source_type: Optional[str] = None
    description: Optional[str] = None
    system_prompt: str
    contexts: List[ContextRequest]
    system_assistance: bool = False