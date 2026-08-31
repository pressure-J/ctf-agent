"""AI 通道配置设置 API(管理页: 多通道/提供商/模型/测试连接)。"""
from fastapi import APIRouter, HTTPException
from typing import Dict
from core.ai_channels import AiChannelManager

router = APIRouter(prefix="/api/settings", tags=["settings"])
_mgr = AiChannelManager()


@router.get("/ai-channels")
def list_channels():
    return {"channels": _mgr.list()}


@router.post("/ai-channels")
def add_channel(cfg: Dict):
    return _mgr.add(cfg)


@router.put("/ai-channels/{ch_id}")
def update_channel(ch_id: str, cfg: Dict):
    try:
        return _mgr.update(ch_id, cfg)
    except KeyError:
        raise HTTPException(404, "通道不存在")


@router.delete("/ai-channels/{ch_id}")
def delete_channel(ch_id: str):
    _mgr.delete(ch_id)
    return {"ok": True}


@router.post("/ai-channels/{ch_id}/default")
def make_default(ch_id: str):
    _mgr.set_default(ch_id)
    return {"ok": True}


@router.post("/ai-channels/test")
def test_channel(cfg: Dict):
    return _mgr.test_connection(cfg)


@router.post("/ai-channels/models")
def list_models(cfg: Dict):
    """按当前填的 base_url+api_key 拉取可用模型下拉"""
    return _mgr.list_models(cfg)