from sqlalchemy.orm import Session, load_only
from sqlalchemy.exc import IntegrityError
from api.Assistant.assistant_model import Assistant
from typing import List, Tuple
from uuid import UUID
from fastapi import HTTPException, status
import logging
from api.error_constant import ErrorConstants

def get_all_assistants(db: Session, skip: int, limit: int) -> Tuple[List[Assistant], int]:
    db_query = db.query(Assistant).options(
        load_only(
            Assistant.id,
            Assistant.name,
            Assistant.source_type,
            Assistant.description,
            Assistant.created_by,
            Assistant.system_assistance
        )
    )
    total = db_query.count()
    assistants = db_query.offset(skip).limit(limit).all()
    return assistants, total

def create_assistant_repository(db: Session, assistant: Assistant):
    db.add(assistant)
    db.commit()
    db.refresh(assistant)

def get_assistant_by_id_repository(db: Session, assistant_id: UUID) -> Assistant:
    assistant = db.query(Assistant).filter(Assistant.id == assistant_id).first()
    if not assistant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorConstants.ASSISTANT_NOT_FOUND
        )
    return assistant

def delete_assistant_repository(db: Session, assistant_id: UUID):
    try:
        assistant = get_assistant_by_id_repository(db, assistant_id)
        db.delete(assistant)
        db.commit()
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting assistant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorConstants.FAILED_TO_DELETE_ASSISTANT
        )

def update_assistant_repository(db: Session, assistant: Assistant) -> Assistant:
    try:
        db.add(assistant)
        db.commit()
        db.refresh(assistant)
        return assistant
    except IntegrityError as e:
        db.rollback()
        logging.error(f"Integrity error while updating assistant: {e.orig}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{ErrorConstants.FAILED_TO_UPDATE_ASSISTANT}: {e.orig}"
        )
    except Exception as e:
        db.rollback()
        logging.error(f"Error updating assistant: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorConstants.FAILED_TO_UPDATE_ASSISTANT
        )