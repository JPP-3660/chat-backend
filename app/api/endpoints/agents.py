from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app import models
from app.api import deps
from app.schemas import agent as agent_schema
from app.services.rag import rag_service

router = APIRouter()

@router.get("/", response_model=List[agent_schema.Agent])
def read_agents(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve agents.
    """
    agents = db.query(models.Agent).offset(skip).limit(limit).all()
    return agents

@router.post("/", response_model=agent_schema.Agent)
def create_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_in: agent_schema.AgentCreate,
) -> Any:
    """
    Create new agent.
    """
    # Simply create with no user for MVP or create a default user if needed
    db_agent = models.Agent(
        name=agent_in.name,
        role=agent_in.role,
        description=agent_in.description,
        system_prompt=agent_in.system_prompt,
        model_config_data=agent_in.model_config_data,
        tools_config=agent_in.tools_config,
        is_public=agent_in.is_public,
        # user_id goes here if auth enabled
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

@router.get("/{agent_id}", response_model=agent_schema.Agent)
def read_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: str,
) -> Any:
    """
    Get agent by ID.
    """
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    return agent

@router.put("/{agent_id}", response_model=agent_schema.Agent)
def update_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: str,
    agent_in: agent_schema.AgentUpdate,
) -> Any:
    """
    Update an agent.
    """
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        update_data = agent_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
            
        db.add(agent)
        db.commit()
        db.refresh(agent)
        return agent
    except Exception as e:
        import logging
        logging.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/knowledge/upload")
async def upload_knowledge(
    agent_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
):
    """
    Upload a file to agent knowledge base.
    """
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    content = await file.read()
    # Decode if text
    text_content = ""
    try:
        text_content = content.decode("utf-8")
        rag_service.add_text(agent_id, text_content, {"filename": file.filename})
    except:
        # If binary (pdf), handled by service later
        pass

    # Record in DB
    kb = models.KnowledgeBase(
        agent_id=agent_id,
        source_type="text", # Simplified
        source_name=file.filename,
        status="indexed"
    )
    db.add(kb)
    db.commit()
    
    return {"status": "success", "filename": file.filename}
