"""知识库路由 /api/knowledge"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.get("")
async def list_knowledge(tag: str = None):
    raise NotImplementedError

@router.post("/search")
async def search_knowledge(query: str, top_k: int = 5):
    raise NotImplementedError

@router.post("")
async def add_document(title: str, content: str, tags: list = None):
    raise NotImplementedError
