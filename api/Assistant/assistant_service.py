from api.Users.user_service import validate_and_extract_user_email
from api.db.pg_database import SessionLocal
from api.Assistant.assistant_repository import get_all_assistants, get_assistant_by_id_repository, delete_assistant_repository, update_assistant_repository
from api.Assistant.assistant_response_model import AssistantRequest, AssistantResponse, AssistantInfoResponse, AssistantListItemResponse, ContextResponse, UpdateAssistantRequest
from api.search.search_service import get_search_texts_details
from api.Assistant.assistant_repository import create_assistant_repository
from typing import List
from api.Assistant.assistant_model import Assistant, Context
from uuid import UUID
from datetime import datetime, timezone
from fastapi import HTTPException, status, UploadFile
from api.config import get
from api.llm.token_counter import TokenCounter
from api.error_constant import ErrorConstants
from api.cache.cache_enums import CacheType
from api.Assistant.assistant_cache_service import (
    get_assistant_detail_cache,
    set_assistant_detail_cache,
    delete_assistant_detail_cache,
)
from api.utils import Utils
import re

token_counter = TokenCounter(api_key=get("GEMINI_API_KEY"))


def _sync_variables_with_prompt(user_prompt: str, variables: list) -> list:
    if not variables:
        return variables
    referenced_ids = set(re.findall(r"\{\{(.+?)\}\}", user_prompt or ""))
    return [v for v in variables if v.get("instanceId") in referenced_ids]


def _build_context_responses(contexts) -> List[ContextResponse]:
    return [
        ContextResponse(
            id=context.id,
            content=context.content,
            pecha_title=context.pecha_title,
            pecha_text_id=context.pecha_text_id
        ) for context in contexts
    ]


def _build_assistant_list_item_response(assistant) -> AssistantListItemResponse:
    return AssistantListItemResponse(
        id=assistant.id,
        name=assistant.name,
        description=assistant.description,
        language=assistant.language,
        model=assistant.model,
        created_by=assistant.created_by,
        system_assistance=assistant.system_assistance
    )


def _build_assistant_info_response(assistant) -> AssistantInfoResponse:
    return AssistantInfoResponse(
        id=assistant.id,
        name=assistant.name,
        description=assistant.description,
        language=assistant.language,
        model=assistant.model,
        user_prompt=assistant.user_prompt,
        variables=assistant.variables,
        system_prompt=assistant.system_prompt,
        contexts=_build_context_responses(assistant.contexts),
        created_by=assistant.created_by,
        system_assistance=assistant.system_assistance
    )


def get_assistants(skip: 0, limit: 20) -> AssistantResponse:
    with SessionLocal() as db_session:
        assistants, total = get_all_assistants(db=db_session, skip=skip, limit=limit)
        assistants_response = [
            _build_assistant_list_item_response(assistant)
            for assistant in assistants
        ]

        assistant_response = AssistantResponse(
            assistants=assistants_response,
            skip=skip,
            limit=limit,
            total=total
        )

    return assistant_response


async def create_assistant_service(token: str, assistant_request: AssistantRequest, files: List[UploadFile] = None):
    current_user_email = validate_and_extract_user_email(token=token)
    contexts_list = []
    for ctx in assistant_request.contexts:
        if ctx.pecha_text_id:
            search_details = await get_search_texts_details(ctx.pecha_text_id)
            content = "\n\n".join([detail.content for detail in search_details]) if search_details else ""
        else:
            content = ctx.content
        token_count = token_counter.count_tokens(content)
        contexts_list.append(
            Context(content=content, pecha_title=ctx.pecha_title, pecha_text_id=ctx.pecha_text_id, token_count=token_count)
        )
    if files:
        for file in files:
            if file.filename:
                file_bytes = await file.read()
                try:
                    Utils.validate_file(file.filename, len(file_bytes))
                    extracted_content = Utils.extract_content_from_file(file_bytes, file.filename)
                    file_token_count = token_counter.count_tokens(extracted_content)
                    contexts_list.append(Context(content=extracted_content, token_count=file_token_count))
                except ValueError as e:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    with SessionLocal() as db_session:
        assistant = Assistant(
            name=assistant_request.name,
            description=assistant_request.description,
            language=assistant_request.language,
            model=assistant_request.model,
            user_prompt=assistant_request.user_prompt,
            variables=assistant_request.variables,
            system_prompt=assistant_request.system_prompt,
            system_assistance=assistant_request.system_assistance,
            created_by=current_user_email,
            contexts=contexts_list
        )
        create_assistant_repository(db=db_session, assistant=assistant)

async def get_assistant_by_id_service(assistant_id: UUID) -> AssistantInfoResponse:
    cached_data = await get_assistant_detail_cache(
        assistant_id=str(assistant_id),
        cache_type=CacheType.ASSISTANT_DETAIL
    )

    if cached_data:
        return cached_data

    with SessionLocal() as db_session:
        assistant = get_assistant_by_id_repository(db=db_session, assistant_id=assistant_id)
        assistant_info = _build_assistant_info_response(assistant)

    await set_assistant_detail_cache(
        assistant_id=str(assistant_id),
        data=assistant_info,
        cache_type=CacheType.ASSISTANT_DETAIL
    )

    return assistant_info

async def delete_assistant_service(assistant_id: UUID, token: str):
    current_user_email = validate_and_extract_user_email(token=token)
    with SessionLocal() as db_session:
        assistant = get_assistant_by_id_repository(db=db_session, assistant_id=assistant_id)
        if current_user_email != assistant.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.UNAUTHORIZED_ERROR_MESSAGE)
        if assistant.system_assistance:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.FORBIDDEN_ERROR_MESSAGE)
        
        delete_assistant_repository(db=db_session, assistant_id=assistant_id)

    await delete_assistant_detail_cache(
        assistant_id=str(assistant_id),
        cache_type=CacheType.ASSISTANT_DETAIL
    )


async def update_assistant_service(assistant_id: UUID, update_request: UpdateAssistantRequest, token: str) -> AssistantInfoResponse:
    current_user_email=validate_and_extract_user_email(token=token)
    with SessionLocal() as db_session:
        assistant = get_assistant_by_id_repository(db=db_session, assistant_id=assistant_id)
        if current_user_email != assistant.created_by:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=ErrorConstants.UNAUTHORIZED_ERROR_MESSAGE)
        if update_request.name is not None:
            assistant.name = update_request.name
        if update_request.description is not None:
            assistant.description = update_request.description
        if update_request.language is not None:
            assistant.language = update_request.language
        if update_request.model is not None:
            assistant.model = update_request.model
        if update_request.user_prompt is not None:
            assistant.user_prompt = update_request.user_prompt
        if update_request.variables is not None:
            assistant.variables = update_request.variables
        if update_request.system_prompt is not None:
            assistant.system_prompt = update_request.system_prompt
        if update_request.system_assistance is not None:
            assistant.system_assistance = update_request.system_assistance
        assistant.variables = _sync_variables_with_prompt(
            assistant.user_prompt, assistant.variables
        )
        if update_request.contexts is not None:
            for context in assistant.contexts:
                db_session.delete(context)
            new_contexts = []
            for ctx in update_request.contexts:
                if ctx.pecha_text_id:
                    search_details = await get_search_texts_details(ctx.pecha_text_id)
                    content = "\n\n".join([detail.content for detail in search_details]) if search_details else ""
                else:
                    content = ctx.content
                token_count = token_counter.count_tokens(content)
                new_contexts.append(
                    Context(content=content, pecha_title=ctx.pecha_title, pecha_text_id=ctx.pecha_text_id, token_count=token_count)
                )
            assistant.contexts = new_contexts
        
        assistant.updated_at = datetime.now(timezone.utc)
        
        assistant = update_assistant_repository(db=db_session, assistant=assistant)
        
        assistant_info = _build_assistant_info_response(assistant)

    await delete_assistant_detail_cache(
        assistant_id=str(assistant_id),
        cache_type=CacheType.ASSISTANT_DETAIL
    )

    return assistant_info
