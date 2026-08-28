"""工具路由"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from web.deps import tool_registry, security

router = APIRouter(prefix="/api/tools", tags=["tools"])

@router.get("")
async def list_tools(category: Optional[str] = None,
                     credentials: HTTPAuthorizationCredentials = Depends(security)):
    tools = tool_registry.list_tools(category=category)
    return {"tools": tools, "count": len(tools)}

@router.get("/{tool_name}")
async def get_tool(tool_name: str,
                   credentials: HTTPAuthorizationCredentials = Depends(security)):
    info = tool_registry.get_tool_info(tool_name)
    if not info:
        raise HTTPException(status_code=404, detail="工具不存在")
    return info

@router.post("/{tool_name}/execute")
async def execute_tool(tool_name: str, args: Dict[str, Any],
                       credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"result": tool_registry.execute(tool_name, args)}
