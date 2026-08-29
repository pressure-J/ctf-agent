"""
检索器 - 便捷入口(懒加载单例索引 docs+skills)。
"""
from knowledge.base import KnowledgeBase

_kb = None


def get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
        _kb.index_dir("knowledge/docs")
        _kb.index_dir("knowledge/skills")
    return _kb


def retrieve(query, top_k: int = 3, threshold: float = 0.0):
    return get_kb().retrieve_context(query, top_k, threshold)
