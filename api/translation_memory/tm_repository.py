from sqlalchemy.orm import Session
from sqlalchemy import text
from api.translation_memory.tm_model import TranslationMemory
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


def find_exact_match(
    db: Session, assistant_id: UUID, source_text: str, target_language: str, created_by: str, model_name: str
) -> Optional[TranslationMemory]:
    return db.query(TranslationMemory).filter(
        TranslationMemory.assistant_id == assistant_id,
        TranslationMemory.source_text == source_text,
        TranslationMemory.target_language == target_language,
        TranslationMemory.created_by == created_by,
        TranslationMemory.model_name == model_name,
    ).first()


def find_fuzzy_matches(
    db: Session,
    assistant_id: UUID,
    source_text: str,
    target_language: str,
    created_by: str,
    model_name: str,
    limit: int = 5,
    threshold: float = 0.3,
) -> list:
    results = db.execute(
        text("""
            SELECT source_text, target_text, model_name,
                   similarity(source_text, :source_text) AS score
            FROM translation_memory
            WHERE assistant_id = :assistant_id
              AND target_language = :target_language
              AND created_by = :created_by
              AND model_name = :model_name
              AND similarity(source_text, :source_text) > :threshold
              AND source_text != :source_text
            ORDER BY score DESC
            LIMIT :limit
        """),
        {
            "assistant_id": str(assistant_id),
            "source_text": source_text,
            "target_language": target_language,
            "created_by": created_by,
            "model_name": model_name,
            "threshold": threshold,
            "limit": limit,
        },
    ).fetchall()
    return results

def batch_create_tm_entries(
    db: Session, entries: List[TranslationMemory]
) -> List[TranslationMemory]:
    try:
        db.add_all(entries)
        db.commit()
        for entry in entries:
            db.refresh(entry)
        return entries
    except Exception as e:
        db.rollback()
        logger.error(f"Error batch creating TM entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to batch create translation memory entries",
        )
