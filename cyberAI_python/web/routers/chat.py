"""对话路由 /api/chat /api/conversations"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api", tags=["chat"])
security = HTTPBearer()

@router.post("/chat")
async def chat(message: str, conversation_id: str = None, agent_id: str = None):
    """与 Agent 对话 (TODO: Pydantic + 异步执行)"""
    raise NotImplementedError

@router.get("/conversations")
async def list_conversations():
    raise NotImplementedError

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    raise NotImplementedError
