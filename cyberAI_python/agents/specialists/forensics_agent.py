
"""取证 Agent: 文件/隐写/流量/内存
TODO: 定制 system_prompt + 注册专业工具 + 知识检索
"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class ForensicsAgent(BaseAgent):
    def __init__(self, name: str = "forensics", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 注册 Forensics 相关工具
