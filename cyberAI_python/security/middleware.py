"""
安全中间件 - 安全头/统一错误/敏感脱敏
"""
import logging
logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        raise NotImplementedError
