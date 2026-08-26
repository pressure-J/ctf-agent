"""
FFuf 模糊测试工具
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def ffuf_dir(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", match_codes: str = "200,204,301,302,307,401,403") -> str:
    raise NotImplementedError

def ffuf_vhost(domain: str, wordlist: str) -> str:
    raise NotImplementedError

def ffuf_param(url: str, wordlist: str) -> str:
    raise NotImplementedError

__all__ = ["ffuf_dir", "ffuf_vhost", "ffuf_param"]
