"""管理路由 /api/admin"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats")
async def get_stats():
    raise NotImplementedError

@router.get("/audit")
async def get_audit_logs(limit: int = 100):
    raise NotImplementedError

@router.get("/system")
async def system_status():
    raise NotImplementedError
