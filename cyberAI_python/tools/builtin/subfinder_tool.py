"""
Subfinder 子域名被动枚举工具
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def subfinder_enum(domain: str, silent: bool = True) -> str:
    raise NotImplementedError

__all__ = ["subfinder_enum"]
