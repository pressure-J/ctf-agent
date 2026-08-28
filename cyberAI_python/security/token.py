"""
Token 管理 - JWT(python-jose)。payload 含 sub(user_id)/username/role/exp。
原理: 服务端用 secret 签名, 客户端带回来, 服务端验签(篡改即失败)。
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
from jose import jwt, JWTError


class TokenManager:
    def __init__(self, secret: str, expire_minutes: int = 1440, algorithm: str = "HS256"):
        self.secret = secret
        self.expire_minutes = expire_minutes
        self.algorithm = algorithm

    def create_token(self, user_id: str, username: str, role: str = "user") -> str:
        payload = {
            "sub": user_id,
            "username": username,
            "role": role,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[Dict]:
        """校验+解码, 失败(过期/篡改/伪造)返回 None"""
        try:
            return jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except JWTError:
            return None
