"""
密码哈希 - 对齐 Go 版: 用 bcrypt(默认成本=10, 同 Go bcrypt.DefaultCost)。
兼容验证明文 vs 两种存储格式:
  1) bcrypt  ($2a/$2b/$2y 前缀)
  2) Go 老格式 "sha256$<salthex>$<sha256(salt+pass)hex>"
"""
import bcrypt, hashlib, hmac, secrets

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=10)).decode()

def _verify_sha256legacy(password: str, encoded: str) -> bool:
    parts = encoded.split("$")
    if len(parts) != 3:
        return False
    try:
        salt = bytes.fromhex(parts[1]); expected = bytes.fromhex(parts[2])
    except ValueError:
        return False
    dig = hashlib.sha256(salt + password.encode()).digest()
    return hmac.compare_digest(dig, expected)

def verify_password(password: str, encoded: str) -> bool:
    encoded = (encoded or "").strip()
    if not encoded:
        return False
    if encoded.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(password.encode(), encoded.encode())
        except Exception:
            return False
    if encoded.startswith("sha256$"):
        return _verify_sha256legacy(password, encoded)
    return False
