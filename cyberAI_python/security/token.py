"""
Token 管理 - JWT(pyjwt), payload 含 sub/exp/role
"""
from typing import Dict, Optional
import jwt
import logging
logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self, secret: str, expire_minutes: int = 1440):
        self.secret = secret
        self.expire_minutes = expire_minutes

    def create_token(self, user_id: str, username: str, role: str = "user") -> str:
        raise NotImplementedError

    def verify_token(self, token: str) -> Optional[Dict]:
        raise NotImplementedError

    def revoke_token(self, token: str):
        raise NotImplementedError
