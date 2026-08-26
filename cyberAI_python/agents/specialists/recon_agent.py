
"""侦察 Agent: 子域名/端口/指纹/技术栈
TODO: 定制 system_prompt + 注册专业工具 + 知识检索
"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class ReconAgent(BaseAgent):
    def __init__(self, name: str = "recon", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 注册 Recon 相关工具
