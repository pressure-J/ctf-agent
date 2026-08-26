"""
Gobuster 目录/子域爆破
"""
import subprocess
import logging
logger = logging.getLogger(__name__)

def gobuster_dir(url: str, wordlist: str = "/usr/share/wordlists/dirb/common.txt", extensions: str = "") -> str:
    raise NotImplementedError

def gobuster_dns(domain: str, wordlist: str = "") -> str:
    raise NotImplementedError

__all__ = ["gobuster_dir", "gobuster_dns"]
