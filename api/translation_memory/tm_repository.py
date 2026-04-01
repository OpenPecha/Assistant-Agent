from sqlalchemy.orm import Session
from sqlalchemy import text
from api.translation_memory.tm_model import TranslationMemory
from uuid import UUID
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


def find_exact_match(
    db: Session, assistant_id: UUID, source_text: str, target_language: str
) -> Optional[TranslationMemory]:
    return db.query(TranslationMemory).filter(
        TranslationMemory.assistant_id == assistant_id,
        TranslationMemory.source_text == source_text,
        TranslationMemory.target_language == target_language,
    ).first()


def find_fuzzy_matches(
    db: Session,
    assistant_id: UUID,
    source_text: str,
    target_language: str,
    limit: int = 5,
    threshold: float = 0.3,
) -> list:
    results = db.execute(
        text("""
            SELECT source_text, target_text,
                   similarity(source_text, :source_text) AS score
            FROM translation_memory
            WHERE assistant_id = :assistant_id
              AND target_language = :target_language
              AND similarity(source_text, :source_text) > :threshold
              AND source_text != :source_text
            ORDER BY score DESC
            LIMIT :limit
        """),
        {
            "assistant_id": str(assistant_id),
            "source_text": source_text,
            "target_language": target_language,
            "threshold": threshold,
            "limit": limit,
        },
    ).fetchall()
    return results


def create_tm_entry(db: Session, tm: TranslationMemory) -> TranslationMemory:
    try:
        db.add(tm)
        db.commit()
        db.refresh(tm)
        return tm
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating TM entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create translation memory entry",
        )


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


def get_tm_entries(
    db: Session,
    assistant_id: UUID,
    target_language: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[TranslationMemory], int]:
    query = db.query(TranslationMemory).filter(
        TranslationMemory.assistant_id == assistant_id
    )
    if target_language:
        query = query.filter(TranslationMemory.target_language == target_language)
    total = query.count()
    entries = query.order_by(TranslationMemory.created_at.desc()).offset(skip).limit(limit).all()
    return entries, total


def delete_tm_entry(db: Session, tm_id: UUID) -> None:
    entry = db.query(TranslationMemory).filter(TranslationMemory.id == tm_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation memory entry not found",
        )
    try:
        db.delete(entry)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting TM entry: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete translation memory entry",
        )
