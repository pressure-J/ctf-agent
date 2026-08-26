"""
Agent 基类 - 组合优于继承: 持有 core.agent.Agent(核心循环)+自己的策略
"""
from typing import Dict, Any, List, Optional
from core.agent import Agent
import logging
logger = logging.getLogger(__name__)

class BaseAgent:
    def __init__(self, name: str, system_prompt: str = None, model: str = "deepseek-chat",
                 tools: List[str] = None, config: Dict = None):
        self.name = name
        self.core = Agent(name=name, system_prompt=system_prompt, model=model, config=config)
        self.tools = tools or []
        # TODO: 从 ToolManager 注册工具

    def think(self, task: str, context: Dict = None) -> str:
        return self.core.think(task, context)

    def get_state(self) -> Dict:
        return self.core.get_state()

    def reset(self):
        self.core.state.clear()
