"""日志中间件"""
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        logger.info(f"{request.method} {request.url.path} -> {response.status_code} "
                    f"({time.time()-start:.3f}s)")
        return response
