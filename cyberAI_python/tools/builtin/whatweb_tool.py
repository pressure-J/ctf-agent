"""
WhatWeb 指纹识别工具
"""
import subprocess
import json
import logging
logger = logging.getLogger(__name__)

def whatweb_scan(url: str) -> str:
    raise NotImplementedError

__all__ = ["whatweb_scan"]
