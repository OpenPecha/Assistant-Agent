
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from api.ai.ai_response_model import WorkflowRequest

class Batch(BaseModel):
    """A batch of texts for processing."""
    batch_id: str = Field(..., description="Unique identifier for the batch")
    texts: List[str] = Field(..., description="Texts in this batch")
    target_language: Optional[str] = Field(None, description="Target language for translation tasks")
    model_name: str = Field(..., description="Model to use")
    user_rules: Optional[str] = Field(None, description="Optional custom translation rules")
    user_prompt: Optional[str] = Field(None, description="User-defined prompt instructions from assistant")
    contexts: Optional[List[str]] = Field(None, description="Additional context for processing")


class Result(BaseModel):
    """Result for a single text processing (translation or Q&A response)."""
    input_text: str
    output_text: str
    metadata: Dict[str, Any]


class BatchResult(BaseModel):
    """Result of processing a batch."""
    batch_id: str = Field(..., description="Batch identifier")
    results: List[Result] = Field(..., description="Translation results")
    processing_time: float = Field(..., description="Time taken to process batch in seconds")
    model_used: str = Field(..., description="Model used for translation")
    success: bool = Field(True, description="Whether batch processing was successful")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")


class WorkflowState(TypedDict):
    """Represents the state of the translation workflow."""
    original_request: WorkflowRequest
    batches: List[Batch]
    current_batch_index: int
    batch_results: List[BatchResult]
    final_results: List[Result]
    total_texts: int
    processed_texts: int
    workflow_start_time: float
    workflow_status: str
    errors: List[Dict[str, Any]]
    retry_count: int
    model_name: str
    model_params: Dict[str, Any]
    custom_steps: Dict[str, Any]
    metadata: Dict[str, Any]    