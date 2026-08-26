"""
工具系统门面 - 对 Agent 暴露统一工具入口
职责：把 tools/registry.py 的 ToolRegistry 包装给 Agent,并提供异步执行。
"""
from typing import Dict, Any, List
from tools.registry import ToolRegistry
from tools.executor import ToolExecutor
import logging
logger = logging.getLogger(__name__)

class ToolManager:
    """统一工具管理：注册表 + 执行器"""
    def __init__(self):
        self.registry = ToolRegistry()
        self.executor = ToolExecutor(self.registry)
        # TODO: MCP 客户端接入(外部工具服务器)

    def load_all(self, config_dir: str):
        """从 YAML 目录批量加载工具"""
        raise NotImplementedError

    def get_schemas(self) -> List[Dict]:
        """给 LLM 用的工具 schema 列表"""
        return self.registry.get_schemas()

    def execute(self, name: str, args: Dict[str, Any]) -> str:
        """同步执行工具(Agent循环内)"""
        return self.registry.execute(name, args)

    async def aexecute(self, name: str, args: Dict[str, Any]) -> str:
        """异步执行工具(Web API)"""
        raise NotImplementedError
