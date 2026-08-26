"""
LLM接口层 - 统一封装 OpenAI 兼容 API
原理：所有 LLM 提供商(DeepSeek/OpenAI/本地vLLM)都走 OpenAI 协议，
    通过 base_url + api_key + model 即可切换。
"""
from typing import Dict, Any, List, Optional
from openai import OpenAI
import logging
logger = logging.getLogger(__name__)

class LLMClient:
    """OpenAI 兼容客户端封装"""
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "deepseek-chat", **kwargs):
        self.model = model
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        # TODO: 多模型配置 {"chat": "...", "reasoning": "..."}

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """普通对话(无工具)"""
        raise NotImplementedError

    def chat_with_tools(self, messages: List[Dict], tools: List[Dict], tool_choice: str = "auto") -> Dict:
        """带工具调用的对话(Agent循环核心)"""
        raise NotImplementedError

    def stream_chat(self, messages: List[Dict]):
        """流式对话(Web前端打字机效果)"""
        raise NotImplementedError

    def embed(self, text: str) -> List[float]:
        """文本向量化(知识库RAG用)"""
        raise NotImplementedError
