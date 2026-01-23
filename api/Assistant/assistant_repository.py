from sqlalchemy.orm import Session
from api.Assistant.assistant_model import Assistant
from typing import List, Tuple

def get_all_assistants(db: Session, skip: int, limit: int) -> Tuple[List[Assistant], int]:
    db_query = db.query(Assistant)
    total = db_query.count()
    assistants = db_query.offset(skip).limit(limit).all()
    return assistants, total