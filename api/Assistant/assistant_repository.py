from sqlalchemy.orm import Session
from api.Assistant.assistant_model import Assistant
from typing import List, Tuple
from uuid import UUID

def get_all_assistants(db: Session, skip: int, limit: int) -> Tuple[List[Assistant], int]:
    db_query = db.query(Assistant)
    total = db_query.count()
    assistants = db_query.offset(skip).limit(limit).all()
    return assistants, total

def create_assistant_repository(db: Session, assistant: Assistant):
    db.add(assistant)
    db.commit()
    db.refresh(assistant)

def get_assistant_by_id_repository(db: Session, assistant_id: UUID) -> Assistant:
    return db.query(Assistant).filter(Assistant.id == assistant_id).first()