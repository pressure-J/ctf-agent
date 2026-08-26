"""
嵌入模型封装 - 文本转向量
可用: LLM embed 接口 / sentence-transformers / hash占位
"""
from typing import List
import logging
logger = logging.getLogger(__name__)

class Embedder:
    def __init__(self, provider: str = "llm", model: str = "text-embedding-3-small"):
        self.provider = provider
        self.model = model

    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError
