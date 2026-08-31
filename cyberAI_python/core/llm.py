"""
LLM接口层 - 完整版
统一封装 OpenAI 兼容 API。所有提供商(DeepSeek/OpenAI/本地vLLM/mimo)都走 OpenAI 协议,
通过 base_url + api_key + model 即可切换。换模型只改这一个文件, 上层不动。
"""
import os
from typing import Dict, List, Optional
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """OpenAI 兼容客户端封装"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        # 优先用已配置的"默认 AI 通道"(管理页可加/改), 配置项缺省回退 .env
        ch = None
        try:
            from core.ai_channels import AiChannelManager
            ch = AiChannelManager().default()
        except Exception:
            ch = None
        ch = ch or {}

        # 模型: 构造参数(非占位默认) > 默认通道 model > env LLM_MODEL
        # 注意 Agent 默认传 "deepseek-chat"(占位), 须被默认通道的 model(如 gpt-5.6-luna)覆盖,
        # 否则会用错误的模型名去打通道(404 model not found)
        self.model = (model if model and model not in ("deepseek-chat", "") else None) \
            or ch.get("model") or os.getenv("LLM_MODEL", "deepseek-chat")
        self.temperature = temperature
        self.max_tokens = max_tokens or ch.get("max_output") or 2000

        # 核心: OpenAI 官方客户端, 但 base_url 可指向任何兼容服务
        self.client = OpenAI(
            api_key=api_key or ch.get("api_key") or os.getenv("DEEPSEEK_API_KEY"),
            base_url=base_url or ch.get("base_url") or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        logger.debug(f"LLMClient 初始化: model={self.model}")

    def chat(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> str:
        """普通对话(无工具), 直接返回最终文本字符串"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        return resp.choices[0].message.content

    def chat_with_tools(
        self,
        messages: List[Dict],
        tools: List[Dict],
        tool_choice: str = "auto",
        temperature: float = None,
        max_tokens: int = None,
    ) -> Dict:
        """
        带工具调用的对话 —— Agent 循环的核心。
        传 tools 给 LLM 让它知道能干什么; 它可能返回 tool_calls(要调工具)
        而不是 content(直接回答)。返回完整响应 dict(等价 model_dump)。
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or None,
            tool_choice=tool_choice if tools else None,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        return resp.model_dump()

    def stream_chat(self, messages: List[Dict], **kwargs):
        """流式对话(Web前端打字机效果用), 逐段 yield 文本"""
        stream = self.client.chat.completions.create(
            model=self.model, messages=messages, stream=True, **kwargs
        )
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def embed(self, text: str) -> List[float]:
        """文本向量化(知识库RAG用), 依赖服务商支持 embeddings 接口"""
        resp = self.client.embeddings.create(
            model=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
            input=text,
        )
        return resp.data[0].embedding