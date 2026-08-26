"""WebSocket路由 /ws 实时对话"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["websocket"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # TODO: -> 调 Agent -> 流式返回
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        pass
