"""
密码哈希 - 绝不明文/单MD5存储。用 passlib 的 pbkdf2_sha256(内置, 无需bcrypt C依赖)。
原理: 加盐 + 密钥拉伸, 每次 hash 带随机盐, 即使相同密码结果也不同。
"""
from passlib.hash import pbkdf2_sha256


def hash_password(password: str) -> str:
    """生成带盐的密码哈希(默认 py 字面量; 存储到 DB)"""
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """安全比对: 从 hash 中取出盐, 重算并恒时比较"""
    try:
        return pbkdf2_sha256.verify(password, password_hash)
    except Exception:
        return False
