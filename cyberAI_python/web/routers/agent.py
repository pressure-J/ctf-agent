"""Agent路由 /api/agents"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("")
async def list_agents():
    raise NotImplementedError

@router.post("")
async def create_agent(config: dict):
    raise NotImplementedError

@router.get("/{agent_id}")
async def get_agent(agent_id: str):
    raise NotImplementedError

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str):
    raise NotImplementedError
