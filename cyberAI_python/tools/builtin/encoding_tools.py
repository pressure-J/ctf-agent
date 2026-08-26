"""
编码工具族(约15个)
"""
import logging
logger = logging.getLogger(__name__)

def encode_base64(data: str) -> str:
    raise NotImplementedError

def decode_base64(data: str) -> str:
    raise NotImplementedError

def encode_hex(data: str) -> str:
    raise NotImplementedError

def decode_hex(data: str) -> str:
    raise NotImplementedError

def url_encode(data: str) -> str:
    raise NotImplementedError

def url_decode(data: str) -> str:
    raise NotImplementedError

def auto_detect(data: str) -> str:
    """自动识别编码类型"""
    raise NotImplementedError

__all__ = ["encode_base64", "decode_base64", "encode_hex", "decode_hex",
           "url_encode", "url_decode", "auto_detect"]
