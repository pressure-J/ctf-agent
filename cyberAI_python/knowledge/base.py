"""
知识库基类 - 存储后端可替换(JSON/SQLite/向量库)
"""
from typing import List, Dict, Optional
import logging
logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self, storage_path: str = "knowledge/docs"):
        self.storage_path = storage_path

    def add_document(self, title: str, content: str, tags: List[str] = None, source: str = "") -> str:
        raise NotImplementedError

    def get_document(self, doc_id: str) -> Optional[Dict]:
        raise NotImplementedError

    def list_documents(self, tag: str = None) -> List[Dict]:
        raise NotImplementedError

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        raise NotImplementedError

    def delete_document(self, doc_id: str):
        raise NotImplementedError
