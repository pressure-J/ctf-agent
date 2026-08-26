"""认证中间件"""
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # TODO: 白名单路径跳过
        raise NotImplementedError
