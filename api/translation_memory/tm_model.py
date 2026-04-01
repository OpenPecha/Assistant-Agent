from sqlalchemy.orm import relationship
from sqlalchemy import Column,DateTime,String,ForeignKey,UUID,Text
from datetime import datetime,timezone
from uuid import uuid4
from api.db.pg_database import Base

class TranslationMemory(Base):
    __tablename__="translation_memory"

    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    assistant_id=Column(UUID(as_uuid=True),ForeignKey("assistant.id",ondelete="CASCADE"),nullable=False)
    source_text=Column(Text,nullable=False)
    target_text=Column(Text,nullable=False)
    target_language=Column(String(255),nullable=False)
    created_at=Column(DateTime(timezone=True),default=datetime.now(timezone.utc),nullable=False)

    assistant=relationship("Assistant",back_populates="translation_memories")