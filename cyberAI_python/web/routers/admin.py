"""管理路由"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from web.deps import database, tool_registry, security, get_active_agents

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
async def get_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {
        "total_conversations": database.count_conversations(),
        "total_messages": database.count_messages(),
        "total_tool_executions": database.count_tool_executions(),
        "active_agents": len(get_active_agents()),
        "registered_tools": len(tool_registry.tools),
    }

@router.get("/audit")
async def get_audit_logs(limit: int = 100,
                         credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"logs": database.get_audit_logs(limit)}
