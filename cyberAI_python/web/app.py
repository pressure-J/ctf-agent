"""
FastAPI Web后端 - 完整版
与Go版CyberStrikeAI的Web界面对齐
"""

from fastapi import FastAPI, HTTPException, WebSocket, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

# 本地模块
from core.agent import Agent, AgentMode
from core.tools import ToolRegistry
from security.auth import AuthManager
from database.db import Database

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="CyberStrikeAI Python",
    description="AI驱动的CTF安全测试平台",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局实例
tool_registry = ToolRegistry()
auth_manager = AuthManager()
database = Database()

# 安全认证
security = HTTPBearer()


# ========== 数据模型 ==========

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user_id: str

class ChatRequest(BaseModel):
    """对话请求"""
    message: str
    conversation_id: Optional[str] = None
    agent_id: Optional[str] = None

class ChatResponse(BaseModel):
    """对话响应"""
    response: str
    conversation_id: str
    tool_calls: List[Dict[str, Any]] = []

class ToolDefinition(BaseModel):
    """工具定义"""
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str = "general"

class WorkflowDefinition(BaseModel):
    """工作流定义"""
    name: str
    description: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


# ========== 认证路由 ==========

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录"""
    
    user = auth_manager.authenticate(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 生成Token
    access_token = auth_manager.create_access_token(
        data={"sub": user["id"], "username": user["username"]}
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user["id"]
    )

@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登出"""
    auth_manager.revoke_token(credentials.credentials)
    return {"message": "已登出"}


# ========== 对话路由 ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """与Agent对话"""
    
    # 验证Token
    user = auth_manager.verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的Token"
        )
    
    # 获取或创建对话
    conversation_id = request.conversation_id
    if not conversation_id:
        conversation_id = database.create_conversation(user["id"])
    
    # 获取Agent
    agent = get_or_create_agent(request.agent_id)
    
    # 执行任务
    response = agent.think(
        task=request.message,
        context={"user_id": user["id"], "conversation_id": conversation_id}
    )
    
    # 保存消息
    database.save_message(
        conversation_id=conversation_id,
        role="user",
        content=request.message
    )
    
    database.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=response,
        metadata={"tool_calls": agent.state.tool_calls}
    )
    
    return ChatResponse(
        response=response,
        conversation_id=conversation_id,
        tool_calls=agent.state.tool_calls
    )

@app.get("/api/conversations")
async def list_conversations(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """列出对话"""
    
    user = auth_manager.verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(status_code=401, detail="未授权")
    
    conversations = database.list_conversations(user["id"])
    
    return {"conversations": conversations}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """获取对话详情"""
    
    user = auth_manager.verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(status_code=401, detail="未授权")
    
    conversation = database.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return conversation


# ========== 工具路由 ==========

@app.get("/api/tools")
async def list_tools(
    category: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """列出所有工具"""
    
    tools = tool_registry.list_tools(category=category)
    
    return {"tools": tools, "count": len(tools)}

@app.get("/api/tools/{tool_name}")
async def get_tool(
    tool_name: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """获取工具详情"""
    
    tool_info = tool_registry.get_tool_info(tool_name)
    
    if not tool_info:
        raise HTTPException(status_code=404, detail="工具不存在")
    
    return tool_info

@app.post("/api/tools/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    args: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """执行工具"""
    
    result = tool_registry.execute(tool_name, args)
    
    return {"result": result}


# ========== Agent路由 ==========

@app.get("/api/agents")
async def list_agents(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """列出所有Agent"""
    
    agents = database.list_agents()
    
    return {"agents": agents}

@app.post("/api/agents")
async def create_agent(
    agent_config: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """创建Agent"""
    
    agent_id = database.create_agent(agent_config)
    
    return {"agent_id": agent_id}

@app.get("/api/agents/{agent_id}")
async def get_agent(
    agent_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """获取Agent详情"""
    
    agent = database.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent不存在")
    
    return agent


# ========== 工作流路由 ==========

@app.get("/api/workflows")
async def list_workflows(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """列出所有工作流"""
    
    workflows = database.list_workflows()
    
    return {"workflows": workflows}

@app.post("/api/workflows")
async def create_workflow(
    workflow: WorkflowDefinition,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """创建工作流"""
    
    workflow_id = database.create_workflow(workflow.dict())
    
    return {"workflow_id": workflow_id}

@app.post("/api/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    input_data: Dict[str, Any],
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """执行工作流"""
    
    workflow = database.get_workflow(workflow_id)
    
    if not workflow:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 执行工作流
    result = execute_workflow_engine(workflow, input_data)
    
    return {"result": result}


# ========== 知识库路由 ==========

@app.get("/api/knowledge")
async def list_knowledge(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """列出知识库"""
    
    knowledge = database.list_knowledge()
    
    return {"knowledge": knowledge}

@app.post("/api/knowledge/search")
async def search_knowledge(
    query: str,
    top_k: int = 5,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """搜索知识库"""
    
    results = search_knowledge_base(query, top_k)
    
    return {"results": results}


# ========== 管理路由 ==========

@app.get("/api/admin/stats")
async def get_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """获取系统统计"""
    
    stats = {
        "total_conversations": database.count_conversations(),
        "total_messages": database.count_messages(),
        "total_tool_executions": database.count_tool_executions(),
        "active_agents": len(get_active_agents()),
        "registered_tools": len(tool_registry.tools)
    }
    
    return stats

@app.get("/api/admin/audit")
async def get_audit_logs(
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """获取审计日志"""
    
    logs = database.get_audit_logs(limit)
    
    return {"logs": logs}


# ========== WebSocket路由 ==========

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket实时通信"""
    
    await websocket.accept()
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            if message["type"] == "chat":
                # 异步处理对话
                response = await handle_websocket_chat(message)
                await websocket.send_json(response)
            
            elif message["type"] == "ping":
                await websocket.send_json({"type": "pong"})
    
    except Exception as e:
        logger.error(f"WebSocket错误: {e}")
    finally:
        await websocket.close()


# ========== 辅助函数 ==========

def get_or_create_agent(agent_id: str = None) -> Agent:
    """获取或创建Agent"""
    
    if agent_id:
        agent_config = database.get_agent(agent_id)
        if agent_config:
            return Agent(
                name=agent_config["name"],
                mode=AgentMode(agent_config.get("mode", "single")),
                system_prompt=agent_config.get("system_prompt"),
                model=agent_config.get("model", "deepseek-chat")
            )
    
    # 默认Agent
    return Agent(name="CTF专家")

async def handle_websocket_chat(message: Dict) -> Dict:
    """处理WebSocket对话"""
    
    agent = get_or_create_agent(message.get("agent_id"))
    
    response = agent.think(message["content"])
    
    return {
        "type": "chat_response",
        "response": response,
        "tool_calls": agent.state.tool_calls
    }

def execute_workflow_engine(workflow: Dict, input_data: Dict) -> Dict:
    """执行工作流引擎"""
    
    # 简化实现，实际需要完整的DAG执行逻辑
    results = {}
    
    for node in workflow.get("nodes", []):
        agent = get_or_create_agent(node.get("agent_id"))
        result = agent.think(
            task=node.get("task", ""),
            context={**input_data, **results}
        )
        results[node["id"]] = result
    
    return results

def search_knowledge_base(query: str, top_k: int) -> List[Dict]:
    """搜索知识库"""
    
    # 简化实现，实际需要向量检索
    knowledge = database.list_knowledge()
    
    # 简单的关键词匹配
    results = []
    for item in knowledge:
        if query.lower() in item.get("content", "").lower():
            results.append(item)
    
    return results[:top_k]


# ========== 启动事件 ==========

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    
    logger.info("CyberStrikeAI Python 启动中...")
    
    # 初始化数据库
    await database.init()
    
    # 加载工具
    load_tools()
    
    # 加载Agent
    load_agents()
    
    logger.info("CyberStrikeAI Python 启动完成")

def load_tools():
    """加载所有工具"""
    
    tools_dir = Path("tools/configs")
    
    for yaml_file in tools_dir.glob("*.yaml"):
        try:
            tool_registry.register_from_yaml(str(yaml_file))
        except Exception as e:
            logger.error(f"加载工具失败 {yaml_file}: {e}")

def load_agents():
    """加载所有Agent"""
    
    # 加载Agent配置
    pass


# ========== 主程序入口 ==========

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "web.app:app",
        host="0.0.0.0",
        port=8080,
        reload=True
    )
