from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AgentBase(BaseModel):
    name: str
    role: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model_config_data: Optional[Dict[str, Any]] = {}
    tools_config: Optional[List[str]] = []
    is_public: Optional[bool] = False

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    pass

class AgentInDBBase(AgentBase):
    id: str
    user_id: Optional[str] = None

    class Config:
        from_attributes = (
            True  # Pydantic V2 config to support ORM mode (orm_mode in V1)
        )

class Agent(AgentInDBBase):
    pass
