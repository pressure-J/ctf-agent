"""
记忆系统 - Agent 跨会话经验存储
两层: 短期(会话内消息) + 长期(SQLite持久化经验条目)
"""
from typing import List, Dict, Optional
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class MemoryEntry:
    def __init__(self, content: str, kind: str = "experience", tags: List[str] = None):
        self.id = None
        self.content = content
        self.kind = kind
        self.tags = tags or []
        self.created_at = datetime.utcnow()

class Memory:
    """长期记忆管理器"""
    def __init__(self, db=None):
        self.db = db
        # TODO: 初始化记忆表

    def remember(self, content: str, kind: str = "experience", tags: List[str] = None):
        """存入一条记忆"""
        raise NotImplementedError

    def recall(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """按相关性召回"""
        raise NotImplementedError

    def forget(self, entry_id: str):
        raise NotImplementedError
