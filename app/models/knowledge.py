from sqlalchemy import Column, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime
from app.core.database import Base

class SourceType(str, enum.Enum):
    PDF = "pdf"
    URL = "url"
    TEXT = "text"

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"))
    source_type = Column(String) # Store enum as string
    source_name = Column(String) # Title or filename
    content_hash = Column(String) # For duplicate detection
    status = Column(String, default="pending") # pending, indexed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent", backref="knowledge_sources")
