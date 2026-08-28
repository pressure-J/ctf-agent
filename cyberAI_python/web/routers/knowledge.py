"""知识库路由"""
from pathlib import Path
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from typing import Dict
from web.deps import security, search_knowledge_base

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

@router.get("")
async def list_knowledge(credentials: HTTPAuthorizationCredentials = Depends(security)):
    docs = sorted(f.name for f in Path("knowledge/docs").glob("*.md"))
    return {"knowledge": docs}

@router.post("/search")
async def search_knowledge(query: str, top_k: int = 5,
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"results": search_knowledge_base(query, top_k)}
