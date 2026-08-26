
"""单 Agent - 最简模式, 适合简单问答/单工具链"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class SingleAgent(BaseAgent):
    def __init__(self, name: str = "SingleAgent", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 默认注册通用工具集(http/编码/文件)
