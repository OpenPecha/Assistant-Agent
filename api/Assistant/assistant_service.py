

from api.Users.user_service import validate_and_extract_user_email
from api.db.pg_database import SessionLocal
from api.Assistant.assistant_repository import get_all_assistants, get_assistant_by_id_repository, delete_assistant_repository
from api.Assistant.assistant_response_model import AssistantRequest, AssistantResponse, AssistantInfoResponse, ContextResponse
from api.Assistant.assistant_repository import create_assistant_repository
from typing import List
from api.Assistant.assistant_model import Assistant, Context
from uuid import UUID


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

def create_assistant_service(token: str, assistant_request: AssistantRequest):
    current_user_email=validate_and_extract_user_email(token=token)
    with SessionLocal() as db_session:
        assistant = Assistant(
        name=assistant_request.name,
        source_type=assistant_request.source_type,
        description=assistant_request.description,
        system_prompt=assistant_request.system_prompt,
        system_assistance=assistant_request.system_assistance,
        created_by=current_user_email,
        contexts=[
            Context(content=ctx.content, file_url=ctx.file_url)
            for ctx in assistant_request.contexts
        ]
    )
        create_assistant_repository(db=db_session, assistant=assistant)

def get_assistant_by_id_service(assistant_id: UUID) -> AssistantInfoResponse:
    with SessionLocal() as db_session:
        assistant = get_assistant_by_id_repository(db=db_session, assistant_id=assistant_id)
        return AssistantInfoResponse(
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
        )

def delete_assistant_service(assistant_id: UUID):
    with SessionLocal() as db_session:
        delete_assistant_repository(db=db_session, assistant_id=assistant_id)