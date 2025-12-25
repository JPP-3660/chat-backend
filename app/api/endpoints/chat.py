from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from app import models
from app.api import deps
from app.services.llm import llm_service
from app.schemas.chat import ChatRequest, Message as MessageSchema, Session as SessionSchema
import json

router = APIRouter()

@router.get("/sessions/{agent_id}", response_model=List[SessionSchema])
def get_sessions(
    agent_id: str,
    db: DBSession = Depends(deps.get_db)
):
    sessions = db.query(models.Session).filter(models.Session.agent_id == agent_id).order_by(models.Session.created_at.desc()).all()
    return sessions

@router.get("/messages/{session_id}", response_model=List[MessageSchema])
def get_messages(
    session_id: str,
    db: DBSession = Depends(deps.get_db)
):
    messages = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.asc()).all()
    return messages

@router.post("/message")
async def chat_message(
    request: ChatRequest,
    db: DBSession = Depends(deps.get_db)
):
    agent = db.query(models.Agent).filter(models.Agent.id == request.agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
        
    # Get or create session
    if request.session_id:
        chat_session = db.query(models.Session).filter(models.Session.id == request.session_id).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        chat_session = models.Session(agent_id=request.agent_id)
        db.add(chat_session)
        db.commit()
        db.refresh(chat_session)

    # Save user message
    user_msg = models.Message(
        session_id=chat_session.id,
        role="user",
        content=request.message
    )
    db.add(user_msg)
    db.commit()

    async def stream_and_save():
        full_response = ""
        # Yield a space for keep-alive and also to send the session ID in a headers-compatible way if needed
        # But for StreamingResponse we can use headers.
        
        async for chunk in llm_service.chat_stream(
            agent=agent, 
            history=request.history or [], 
            user_input=request.message
        ):
            if chunk:
                full_response += chunk
                yield chunk
        
        # Save assistant message once done
        if full_response.strip():
            assistant_msg = models.Message(
                session_id=chat_session.id,
                role="assistant",
                content=full_response
            )
            db.add(assistant_msg)
            db.commit()

    return StreamingResponse(
        stream_and_save(),
        media_type="text/event-stream",
        headers={"X-Session-ID": chat_session.id}
    )
