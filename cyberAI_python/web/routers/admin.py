"""管理路由"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from web.deps import database, tool_registry, security, get_active_agents
from knowledge.retriever import get_kb
from core.ai_channels import AiChannelManager

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
async def get_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        kb_chunks = len(get_kb().store)
    except Exception:
        kb_chunks = 0
    return {
        "total_conversations": database.count_conversations(),
        "total_messages": database.count_messages(),
        "total_tool_executions": database.count_tool_executions(),
        "active_agents": len(get_active_agents()),
        "registered_tools": len(tool_registry.tools),
        # B: 仪表盘对标 Go 补充的统计
        "total_users": database.count_users(),
        "total_agents": len(database.list_agents()),
        "total_workflows": database.count_workflows(),
        "knowledge_chunks": kb_chunks,
        "ai_channels": len(AiChannelManager().list()),
    }

@router.get("/audit")
async def get_audit_logs(limit: int = 100,
                         credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"logs": database.get_audit_logs(limit)}
