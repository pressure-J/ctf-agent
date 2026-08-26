
"""Crypto Agent: 加密破解/编码/古典密码
TODO: 定制 system_prompt + 注册专业工具 + 知识检索
"""
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class CryptoAgent(BaseAgent):
    def __init__(self, name: str = "crypto", model: str = "deepseek-chat", **kwargs):
        super().__init__(name=name, model=model, **kwargs)
        # TODO: 注册 Crypto 相关工具
