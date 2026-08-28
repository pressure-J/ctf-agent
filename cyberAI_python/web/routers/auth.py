"""认证路由"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from web.deps import auth_manager, security, LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    user = auth_manager.authenticate(request.username, request.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    return LoginResponse(access_token=auth_manager.create_access_token(user),
                         token_type="bearer", user_id=user["id"])

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    auth_manager.revoke_token(credentials.credentials)
    return {"message": "已登出"}
