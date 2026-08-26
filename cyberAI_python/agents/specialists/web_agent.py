
"""Web 安全 Agent: 目录爆破/注入/XSS/SSRF/上传
TODO: 定制 system_prompt + 注册专业工具 + 知识检索
"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class WebAgent(BaseAgent):
    def __init__(self, name: str = "web", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 注册 Web 相关工具
