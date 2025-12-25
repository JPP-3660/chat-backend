from sqlalchemy import Column, String, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    name = Column(String, index=True)
    role = Column(String)
    description = Column(String)
    system_prompt = Column(Text)
    model_config_data = Column(JSON, default={}) # e.g. {"model": "gpt-4", "temperature": 0.7}
    tools_config = Column(JSON, default=[]) # e.g. ["web_search", "calculator"]
    is_public = Column(Boolean, default=False)

    user = relationship("User", backref="agents")
