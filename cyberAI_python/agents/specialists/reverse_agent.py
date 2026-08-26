
"""逆向 Agent: 静态/动态分析/脱壳
TODO: 定制 system_prompt + 注册专业工具 + 知识检索
"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class ReverseAgent(BaseAgent):
    def __init__(self, name: str = "reverse", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 注册 Reverse 相关工具
