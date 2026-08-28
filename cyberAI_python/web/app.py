"""
CyberStrikeAI Python Web 后端 - 精简版。
路由已拆分到 web/routers/, 全局单例在 web/deps.py。
本文件只负责: 创建 app + CORS + 挂载 routers + 启动事件。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
logger = logging.getLogger(__name__)

app = FastAPI(title="CyberStrikeAI Python",
              description="AI驱动的CTF安全测试平台", version="1.0.0")

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

from web.deps import database
from web.routers import auth, chat, tools, agent, workflow, knowledge, admin, websocket
for _r in (auth, chat, tools, agent, workflow, knowledge, admin, websocket):
    app.include_router(_r.router)


@app.on_event("startup")
async def startup_event():
    logger.info("CyberStrikeAI Python 启动中...")
    await database.init()
    logger.info("CyberStrikeAI Python 启动完成")
