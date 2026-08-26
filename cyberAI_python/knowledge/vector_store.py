"""
向量存储 - RAG 索引层
实现选择: chromadb(内嵌最简单) / faiss(高性能) / sqlite-vec(轻量)
"""
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, backend: str = "chromadb", persist_dir: str = "data/vectors"):
        self.backend = backend
        # TODO: 初始化对应后端

    def add(self, doc_id: str, text: str, vector: List[float], metadata: Dict = None):
        raise NotImplementedError

    def query(self, vector: List[float], top_k: int = 5) -> List[Dict]:
        raise NotImplementedError

    def delete(self, doc_id: str):
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError
