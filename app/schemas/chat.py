from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str
    metadata: Optional[dict] = Field(default={}, validation_alias="metadata_")

class MessageCreate(MessageBase):
    session_id: str

class Message(MessageBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    created_at: datetime

class SessionBase(BaseModel):
    agent_id: str
    user_id: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    messages: List[Message] = []

class ChatRequest(BaseModel):
    agent_id: str
    message: str
    session_id: Optional[str] = None
    history: Optional[List[dict]] = []
