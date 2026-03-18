from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional, Any

class ContextRequest(BaseModel):
    content: Optional[str] = None
    pecha_title: Optional[str] = None
    pecha_text_id: Optional[str] = None

class ContextResponse(BaseModel):
    id: UUID
    content: Optional[str] = None
    pecha_title: Optional[str] = None
    pecha_text_id: Optional[str] = None

class AssistantInfoResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    user_prompt: Optional[str] = None
    variables: Optional[Any] = None
    system_prompt: str
    contexts: List[ContextResponse]
    created_by: Optional[str] = None
    system_assistance: bool = False

class AssistantListItemResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    created_by: Optional[str] = None
    system_assistance: bool = False

class AssistantResponse(BaseModel):
    assistants: List[AssistantListItemResponse]
    skip: int
    limit: int
    total: int

class AssistantRequest(BaseModel):
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    user_prompt: Optional[str] = None
    variables: Optional[Any] = None
    system_prompt: str
    contexts: List[ContextRequest]
    system_assistance: bool = False

class UpdateAssistantRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    model: Optional[str] = None
    user_prompt: Optional[str] = None
    variables: Optional[Any] = None
    system_prompt: Optional[str] = None
    contexts: Optional[List[ContextRequest]] = None
    system_assistance: Optional[bool] = None