"""对话路由"""
import json
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
from starlette.concurrency import run_in_threadpool
from web.deps import (database, auth_manager, security,
                      ChatRequest, ChatResponse, get_or_create_agent)

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的Token")
    conversation_id = request.conversation_id or database.create_conversation(user["sub"])
    agent = get_or_create_agent(request.agent_id)
    # 异步化: 丢线程池, 避免阻塞事件循环
    response = await run_in_threadpool(agent.think, request.message,
                                       {"user_id": user["sub"], "conversation_id": conversation_id})
    database.save_message(conversation_id, "user", request.message)
    database.save_message(conversation_id, "assistant", response,
                          metadata={"tool_calls": agent.state.tool_calls})
    return ChatResponse(response=response, conversation_id=conversation_id,
                        tool_calls=agent.state.tool_calls)

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的Token")
    conversation_id = request.conversation_id or database.create_conversation(user["sub"])
    agent = get_or_create_agent(request.agent_id)

    def gen():
        try:
            # 带工具循环的事件流式: LLM 增量 + 工具调用过程 实时回传
            for ev in agent.stream_think(request.message,
                                         {"user_id": user["sub"], "conversation_id": conversation_id}):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    database.save_message(conversation_id, "user", request.message)
    return StreamingResponse(gen(), media_type="text/event-stream")

@router.get("/conversations")
async def list_conversations(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="未授权")
    return {"conversations": database.list_conversations(user["sub"])}

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str,
                           credentials: HTTPAuthorizationCredentials = Depends(security)):
    user = auth_manager.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="未授权")
    conversation = database.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation
