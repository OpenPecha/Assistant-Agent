

from api.db.pg_database import SessionLocal
from api.Assistant.assistant_repository import get_all_assistants
from api.Assistant.assistant_response_model import AssistantResponse, AssistantInfoResponse, ContextResponse
from typing import List


def get_assistants(skip: 0, limit: 20) -> List[AssistantResponse]:
    with SessionLocal() as db_session:
        assistants, total = get_all_assistants(db=db_session, skip=skip, limit=limit)
        assistants_response = [AssistantInfoResponse(
            id=assistant.id,
            name=assistant.name,
            source_type=assistant.source_type,
            description=assistant.description,
            system_prompt=assistant.system_prompt,
            contexts=[ContextResponse(
                id=context.id,
                content=context.content,
                file_url=context.file_url
            ) for context in assistant.contexts],
            created_by=assistant.created_by,
            system_assistance=assistant.system_assistance
        ) for assistant in assistants]

        return AssistantResponse(
            assistants=assistants_response,
            skip=skip,
            limit=limit,
            total=total
        )