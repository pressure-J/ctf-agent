"""工具路由 /api/tools"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/tools", tags=["tools"])

@router.get("")
async def list_tools(category: str = None):
    raise NotImplementedError

@router.get("/{tool_name}")
async def get_tool(tool_name: str):
    raise NotImplementedError

@router.post("/{tool_name}/execute")
async def execute_tool(tool_name: str, args: dict):
    raise NotImplementedError
