from api.ai.ai_response_model import AIResponse
from uuid import UUID

def get_stream_response_service(assistant_id: UUID) -> AIResponse:
    print(assistant_id)