"""
Agent 基类 - 组合优于继承: 持有 core.agent.Agent(核心循环) + 自动加载 YAML 工具库。
原理: Agent 不自己下楼拿工具; 这里用 ToolManager 做"自动上弹药"——
      __init__ 时 load_all(tools/configs) + attach_to_agent(core),
      于是"在 tools/configs 放一个 YAML, 任何 BaseAgent 天生就用得上"。
"""
from typing import Dict, Any, List, Optional
from core.agent import Agent
from core.tools import ToolManager
import logging
logger = logging.getLogger(__name__)


class BaseAgent:
    def __init__(self, name: str, system_prompt: str = None, model: str = "deepseek-chat",
                 tools: List[str] = None, config: Dict = None, auto_load: bool = True):
        self.name = name
        self.core = Agent(name=name, system_prompt=system_prompt, model=model, config=config)
        self.tools = list(tools or [])          # 工具白名单(空=加载全部)
        if auto_load:
            self._load_tools()

    def _load_tools(self):
        """自动加载 YAML 工具库, 并按 self.tools 白名单桥接进核心 Agent。
        self.tools 为空/None = 加载全部(向后兼容)。
        """
        tm = ToolManager()
        tm.load_all("tools/configs")
        limit = self.tools if self.tools else None
        n = tm.attach_to_agent(self.core, names=limit)
        tool_names = [t["function"]["name"] for t in self.core.tools]
        logger.info(f"BaseAgent '{self.name}' 加载工具 {n} 个({tool_names})")

    def think(self, task: str, context: Dict = None) -> str:
        return self.core.think(task, context)

    def get_state(self) -> Dict:
        return self.core.get_state()

    def reset(self):
        self.core.state.clear()
