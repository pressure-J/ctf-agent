"""
检索器 - RAG 查询流程: 查询向量化 -> 相似检索 -> 拼装上下文
"""
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)

class Retriever:
    def __init__(self, vector_store, embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        raise NotImplementedError

    def build_context(self, query: str, top_k: int = 5, max_chars: int = 4000) -> str:
        raise NotImplementedError
