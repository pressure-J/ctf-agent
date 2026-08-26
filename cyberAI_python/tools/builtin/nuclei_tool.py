"""
Nuclei 漏洞模板扫描工具
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def nuclei_scan(url: str, severity: str = "", tags: str = "", templates: str = "") -> str:
    raise NotImplementedError

__all__ = ["nuclei_scan"]
