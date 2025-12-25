from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app import models
from app.api import deps
from app.services.llm import llm_service
from app.services import rag # Will implement later

router = APIRouter()

class ChatRequest(BaseModel):
    agent_id: str
    message: str
    history: Optional[List[dict]] = [] # [{"role": "user", "content": "..."}]

@router.post("/message")
async def chat_message(
    request: ChatRequest,
    db: Session = Depends(deps.get_db)
):
    agent = db.query(models.Agent).filter(models.Agent.id == request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    # TODO: Fetch RAG context if enabled (future step)
    
    return StreamingResponse(
        llm_service.chat_stream(
            agent=agent, 
            history=request.history or [], 
            user_input=request.message
        ), 
        media_type="text/event-stream"
    )
