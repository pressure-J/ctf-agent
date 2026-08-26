
"""Pwn Agent: 二进制漏洞/栈溢出/ROP
TODO: 定制 system_prompt + 注册专业工具 + 知识检索
"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class PwnAgent(BaseAgent):
    def __init__(self, name: str = "pwn", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 注册 Pwn 相关工具
