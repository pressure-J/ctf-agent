"""
取证工具族(约10个) - file/binwalk/foremost/strings/exiftool
"""
import logging
logger = logging.getLogger(__name__)

def file_type(path: str) -> str:
    raise NotImplementedError

def strings_extract(path: str, min_len: int = 4) -> str:
    raise NotImplementedError

def exif_extract(path: str) -> str:
    raise NotImplementedError

def hexdump(path: str, length: int = 256) -> str:
    raise NotImplementedError

__all__ = ["file_type", "strings_extract", "exif_extract", "hexdump"]
