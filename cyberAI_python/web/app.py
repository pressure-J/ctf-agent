"""
CyberStrikeAI Python Web 后端 - 精简版。
路由已拆分到 web/routers/, 全局单例在 web/deps.py。
本文件只负责: 创建 app + CORS + 挂载 routers + 启动事件。
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os, logging
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

# ---------- 轻量单页前端(静态托管, 对齐 Go 的 web/templates+static) ----------
_FRONT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
app.mount("/static", StaticFiles(directory=os.path.join(_FRONT, "static")), name="static")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(os.path.join(_FRONT, "index.html"))


@app.on_event("startup")
async def startup_event():
    logger.info("CyberStrikeAI Python 启动中...")
    await database.init()
    logger.info("CyberStrikeAI Python 启动完成")
