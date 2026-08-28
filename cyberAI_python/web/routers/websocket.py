"""WebSocket 实时路由"""
import json
from fastapi import APIRouter, WebSocket
from starlette.concurrency import run_in_threadpool
from web.deps import handle_websocket_chat

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["type"] == "chat":
                resp = await run_in_threadpool(handle_websocket_chat, msg)
                await websocket.send_json(resp)
            elif msg["type"] == "ping":
                await websocket.send_json({"type": "pong"})
    except Exception:
        pass
    finally:
        await websocket.close()
