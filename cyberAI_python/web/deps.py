"""
共享依赖与全局单例 - 供各 router 使用, 避免 routers<->app 循环 import。
全局实例集中在此: database / auth_manager / tool_registry / security。
"""
from typing import Dict, Any, List, Optional
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from pathlib import Path

from database.db import Database
from security.auth import AuthManager
from tools.registry import ToolRegistry
from core.agent import Agent, AgentMode

# ---------- 全局单例 ----------
database = Database()
auth_manager = AuthManager(db=database)
tool_registry = ToolRegistry()
# 加载 YAML 工具(与 CLI 一致)
for _y in sorted(Path("tools/configs").glob("*.yaml")):
    try:
        tool_registry.register_from_yaml(str(_y))
    except Exception:
        pass
security = HTTPBearer()

# ---------- Pydantic schemas ----------
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    agent_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tool_calls: List[Dict] = []

class WorkflowDefinition(BaseModel):
    name: str
    description: str
    nodes: List[Dict[Any, Any]]
    edges: List[Dict[Any, Any]]

# ---------- 辅助函数 ----------
def get_or_create_agent(agent_id: str = None) -> Agent:
    """获取或创建 Agent(按数据库配置或默认)"""
    if agent_id:
        cfg = database.get_agent(agent_id)
        if cfg:
            return Agent(name=cfg["name"],
                         mode=AgentMode(cfg.get("mode", "single")),
                         system_prompt=cfg.get("system_prompt"),
                         model=cfg.get("model", "deepseek-chat"))
    return Agent(name="CTF专家")

def execute_workflow_engine(workflow: Dict, input_data: Dict) -> Dict:
    """执行工作流(简化为按 nodes 顺序调 agent; 完整 DAG 见 workflow/ 包)"""
    results = {}
    for node in workflow.get("nodes", []):
        agent = get_or_create_agent(node.get("agent_id"))
        results[node["id"]] = agent.think(node.get("task", ""), context={**input_data, **results})
    return results

def search_knowledge_base(query: str, top_k: int = 5) -> List[Dict]:
    """向量检索知识库(docs+skills): 余弦 TopK, 对齐 Go internal/knowledge 的纯向量检索"""
    from knowledge.retriever import retrieve
    return retrieve(query, top_k=top_k)

def get_active_agents() -> List:
    """当前活跃 Agent(占位, 后续与 orchestrator 对接)"""
    return []

def handle_websocket_chat(message: Dict) -> Dict:
    agent = get_or_create_agent(message.get("agent_id"))
    response = agent.think(message["content"])
    return {"type": "chat_response", "response": response, "tool_calls": agent.state.tool_calls}
