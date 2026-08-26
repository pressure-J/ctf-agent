"""认证路由 /api/auth"""
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

@router.post("/login")
async def login(username: str, password: str):
    """登录, 返回 access_token (TODO: Pydantic模型接收)"""
    raise NotImplementedError

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """登出"""
    raise NotImplementedError

@router.post("/register")
async def register(username: str, password: str, email: str = None):
    """注册"""
    raise NotImplementedError
