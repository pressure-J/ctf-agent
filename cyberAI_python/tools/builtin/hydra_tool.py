"""
Hydra 在线口令爆破工具
注意: 默认低并发(-t 4)防止锁账号。
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def hydra_brute(target: str, service: str, user: str = "", userlist: str = "", passlist: str = "/usr/share/wordlists/rockyou.txt", threads: int = 4) -> str:
    raise NotImplementedError

__all__ = ["hydra_brute"]
