"""Agent 路由"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any
from web.deps import database, security

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("")
async def list_agents(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"agents": database.list_agents()}

@router.post("")
async def create_agent(agent_config: Dict[str, Any],
                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"agent_id": database.create_agent(agent_config)}

@router.get("/{agent_id}")
async def get_agent(agent_id: str,
                    credentials: HTTPAuthorizationCredentials = Depends(security)):
    agent = database.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    return agent
