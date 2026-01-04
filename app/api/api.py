from fastapi import APIRouter
from app.api.endpoints import agents, chat, files

api_router = APIRouter()
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
