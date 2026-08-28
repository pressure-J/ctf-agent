"""
认证管理 - 注册 / 登录 / 令牌。串联: db(取用户) + password(哈希比) + token(JWT)。
"""
from typing import Optional, Dict
from security.password import hash_password, verify_password
from security.token import TokenManager
import logging
logger = logging.getLogger(__name__)


class AuthManager:
    def __init__(self, db, secret: str = "CHANGE_ME_TO_RANDOM", expire_minutes: int = 1440):
        self.db = db
        self.tokens = TokenManager(secret, expire_minutes)

    def register(self, username: str, password: str, email: str = None) -> Optional[Dict]:
        """注册(返回不含 hash 的用户信息); 用户名已存在返回 None"""
        if self.db.get_user(username):
            return None
        uid = self.db.create_user(username, hash_password(password), email)
        return self.db.get_user(username)

    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """校验用户名密码, 成功返回 {id, username, role}, 失败返回 None"""
        row = self.db.get_user_with_password(username)
        if not row or not verify_password(password, row["password_hash"]):
            return None
        return {"id": row["id"], "username": row["username"], "role": row["role"]}

    def create_access_token(self, user: Dict) -> str:
        return self.tokens.create_token(user["id"], user["username"], user.get("role", "user"))

    def verify_token(self, token: str):
        return self.tokens.verify_token(token)

    def bootstrap_admin(self, password: Optional[str] = None) -> Optional[str]:
        """对齐 Go 首启 bootstrap: 无 admin 用户则创建内置 admin 账号(随机密码), 返回密码; 已存在返回 None"""
        if self.db.get_user("admin"):
            return None
        import secrets, time
        pwd = password or secrets.token_urlsafe(16)
        self.db.create_user("admin", hash_password(pwd), "admin@local")
        logger.info("[bootstrap] 已创建内置 admin 账号 (role=admin), 初始密码: %s", pwd)
        return pwd
