"""
SQLMap 注入检测工具
注意: --batch 自动应答, 输出截断后返回。
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def sqlmap_check(url: str, data: str = "", level: int = 1, risk: int = 1, threads: int = 4) -> str:
    raise NotImplementedError

def sqlmap_dump(url: str, db: str = "", table: str = "", columns: str = "") -> str:
    raise NotImplementedError

__all__ = ["sqlmap_check", "sqlmap_dump"]
