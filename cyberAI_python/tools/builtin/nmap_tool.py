"""
Nmap 扫描工具 - subprocess 调用系统 nmap, 解析输出
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def nmap_scan(target: str, ports: str = "", scan_type: str = "-sV", extra_args: str = "") -> str:
    raise NotImplementedError

def nmap_os_detect(target: str) -> str:
    raise NotImplementedError

def nmap_script(target: str, script: str) -> str:
    raise NotImplementedError

__all__ = ["nmap_scan", "nmap_os_detect", "nmap_script"]
