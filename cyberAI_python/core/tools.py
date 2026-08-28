"""
工具系统门面 - 对 Agent 暴露统一工具入口
职责：
  1. load_all()        把 tools/configs/*.yaml 批量灌进注册表(数据→能力)
  2. attach_to_agent() 把注册表里的工具桥接给 Agent(能力→Agent)
  3. execute/aexecute  给工具执行加统一入口(同步/异步)
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

    def load_all(self, config_dir: str) -> List[str]:
        """从 YAML 目录批量加载工具, 返回工具名列表。
        原理: 遍历目录下所有 *.yaml, 逐个交给 registry 自动生成函数+schema。
        这样"加一个工具=加一个 YAML", 而不用碰任何 Python。
        """
        from pathlib import Path
        names: List[str] = []
        for yaml_file in sorted(Path(config_dir).glob("*.yaml")):
            try:
                name = self.registry.register_from_yaml(str(yaml_file))
                names.append(name)
            except Exception as e:
                logger.error(f"加载工具失败 {yaml_file}: {e}")
        logger.info(f"已从 {config_dir} 加载工具: {names}")
        return names

    def attach_to_agent(self, agent) -> None:
        """把注册表里的全部工具桥接给 Agent。
        原理: registry 每条工具存 {function, schema};
             Agent 需要两份 — schema 给LLM(self.tools) + func 执行(self.tool_functions)。
             Agent.register_tool(name, description, func, parameters) 会同时填好这两份,
             所以这里把每条工具的 schema 拆开调用它即可。
        """
        for _name, tool in self.registry.tools.items():
            fdef = tool["schema"]["function"]
            agent.register_tool(
                name=fdef["name"],
                description=fdef["description"],
                func=tool["function"],
                parameters=fdef["parameters"],
            )
        logger.info(f"已把 {len(self.registry.tools)} 个工具接入 Agent")

    def list_tools(self, category: str = None, enabled_only: bool = True) -> List[str]:
        """列出工具"""
        return self.registry.list_tools(category, enabled_only)

    def get_schemas(self) -> List[Dict]:
        """给 LLM 用的工具 schema 列表"""
        return self.registry.get_schemas()

    def execute(self, name: str, args: Dict[str, Any]) -> str:
        """同步执行工具(Agent循环内)"""
        return self.registry.execute(name, args)

    async def aexecute(self, name: str, args: Dict[str, Any]) -> str:
        """异步执行工具(Web API 场景)。
        原理: 扫描工具(sync)直接 await 会卡住事件循环;
              用 run_in_executor 丢进线程池, 让其他请求不被阻塞。
        """
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self.execute, name, args)