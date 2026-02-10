from sqlalchemy.orm import relationship
from sqlalchemy import Column,DateTime,String,ForeignKey,Boolean,UUID,Text
from datetime import datetime,timezone
from uuid import uuid4
from api.db.pg_database import Base

class Assistant(Base):
    __tablename__="assistant"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)    
    name=Column(String(255),nullable=False)
    source_type=Column(String(255),nullable=True)
    description=Column(Text,nullable=True)
    system_prompt=Column(Text,nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc),nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    created_by=Column(String(255),nullable=True)
    system_assistance=Column(Boolean,default=False)

    contexts = relationship(
        "Context",
        back_populates="assistant",
        cascade="all, delete-orphan"
    )

class Context(Base):
    __tablename__="context"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    content=Column(Text,nullable=True)
    file_url=Column(Text,nullable=True)
    pecha_title = Column(String(255), nullable=True)
    pecha_text_id = Column(String(255), nullable=True)
    assistant_id = Column(UUID(as_uuid=True),ForeignKey("assistant.id", ondelete="CASCADE"),nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc),nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    assistant = relationship("Assistant",back_populates="contexts")
