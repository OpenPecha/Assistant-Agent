

from api.db.pg_database import SessionLocal
from api.Assistant.assistant_repository import get_all_assistants, get_assistant_by_id_repository, delete_assistant_repository, update_assistant_repository
from api.Assistant.assistant_response_model import AssistantRequest, AssistantResponse, AssistantInfoResponse, ContextResponse, UpdateAssistantRequest
from api.Assistant.assistant_repository import create_assistant_repository
from typing import List, Optional
from api.Assistant.assistant_model import Assistant, Context
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status
from api.error_constant import ErrorConstants
from api.Auth.auth_repository import get_current_user_email


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
                file_url=context.file_url,
                pecha_title=context.pecha_title,
                pecha_text_id=context.pecha_text_id
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

def create_assistant_service(token: Optional[str], assistant_request: AssistantRequest):
    current_user_email = get_current_user_email(token=token)

    with SessionLocal() as db_session:
        assistant = Assistant(
        name=assistant_request.name,
        source_type=assistant_request.source_type,
        description=assistant_request.description,
        system_prompt=assistant_request.system_prompt,
        system_assistance=assistant_request.system_assistance,
        created_by=current_user_email,
        contexts=[
            Context(content=ctx.content, file_url=ctx.file_url, pecha_title=ctx.pecha_title, pecha_text_id=ctx.pecha_text_id)
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
                file_url=context.file_url,
                pecha_title=context.pecha_title,
                pecha_text_id=context.pecha_text_id
            ) for context in assistant.contexts],
            created_by=assistant.created_by,
            system_assistance=assistant.system_assistance
        )

def delete_assistant_service(assistant_id: UUID, token: Optional[str]):
    current_user_email = get_current_user_email(token=token)
    with SessionLocal() as db_session:
        assistant = get_assistant_by_id_repository(db=db_session, assistant_id=assistant_id)
        if current_user_email != assistant.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.UNAUTHORIZED_ERROR_MESSAGE)
        if assistant.system_assistance:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.FORBIDDEN_ERROR_MESSAGE)
        delete_assistant_repository(db=db_session, assistant_id=assistant_id)

def update_assistant_service(assistant_id: UUID, update_request: UpdateAssistantRequest, token: Optional[str]) -> AssistantInfoResponse:
    current_user_email = get_current_user_email(token=token)
    with SessionLocal() as db_session:
        assistant = get_assistant_by_id_repository(db=db_session, assistant_id=assistant_id)
        if current_user_email != assistant.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.UNAUTHORIZED_ERROR_MESSAGE)
        if update_request.name is not None:
            assistant.name = update_request.name
        if update_request.source_type is not None:
            assistant.source_type = update_request.source_type
        if update_request.description is not None:
            assistant.description = update_request.description
        if update_request.system_prompt is not None:
            assistant.system_prompt = update_request.system_prompt
        if update_request.system_assistance is not None:
            assistant.system_assistance = update_request.system_assistance
        if update_request.contexts is not None:
            for context in assistant.contexts:
                db_session.delete(context)
            assistant.contexts = [
                Context(content=ctx.content, file_url=ctx.file_url, pecha_title=ctx.pecha_title, pecha_text_id=ctx.pecha_text_id)
                for ctx in update_request.contexts
            ]
        
        assistant.updated_at = datetime.now(timezone.utc)
        
        assistant = update_assistant_repository(db=db_session, assistant=assistant)
        
        return AssistantInfoResponse(
            id=assistant.id,
            name=assistant.name,
            source_type=assistant.source_type,
            description=assistant.description,
            system_prompt=assistant.system_prompt,
            contexts=[ContextResponse(
                id=context.id,
                content=context.content,
                file_url=context.file_url,
                pecha_title=context.pecha_title,
                pecha_text_id=context.pecha_text_id
            ) for context in assistant.contexts],
            created_by=assistant.created_by,
            system_assistance=assistant.system_assistance
        )