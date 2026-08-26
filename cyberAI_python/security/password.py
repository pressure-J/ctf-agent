
"""密码加密 - passlib pbkdf2_sha256, 绝不明文/单MD5存储"""
import logging
logger = logging.getLogger(__name__)

def hash_password(password: str) -> str:
    raise NotImplementedError

def verify_password(password: str, password_hash: str) -> bool:
    raise NotImplementedError
