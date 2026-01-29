from typing import List
from api.Assistant.assistant_response_model import ContextRequest
from pydantic import BaseModel

class WorkflowRequest(BaseModel):
    assistant_name: str
    assistant_source_type: str
    assistant_system_prompt: str
    contexts: List[ContextRequest]
    target_language: str
    text: List[str]
    model: str