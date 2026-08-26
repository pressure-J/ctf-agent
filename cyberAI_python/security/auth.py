"""
认证管理 - 登录/注册/会话
"""
from typing import Dict, Optional
from security.token import TokenManager
import logging
logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self, db=None):
        self.db = db
        self.tokens = TokenManager(secret="CHANGE_ME")  # TODO: 从.env读
        # TODO: 登录失败计数

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        raise NotImplementedError

    def register(self, username: str, password: str, email: str = None) -> Optional[Dict]:
        raise NotImplementedError

    def create_access_token(self, data: Dict) -> str:
        return self.tokens.create_token(data.get("sub"), data.get("username"), data.get("role", "user"))

    def verify_token(self, token: str) -> Optional[Dict]:
        return self.tokens.verify_token(token)

    def revoke_token(self, token: str):
        self.tokens.revoke_token(token)
