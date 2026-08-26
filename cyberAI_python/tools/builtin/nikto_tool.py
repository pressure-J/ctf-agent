
"""Nikto Web 漏洞扫描工具 - subprocess 调用 nikto"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def nikto_scan(url: str, ssl: bool = False, extra_args: str = "") -> str:
    raise NotImplementedError

__all__ = ["nikto_scan"]
