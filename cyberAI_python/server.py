"""
API服务器入口 - 启动 FastAPI 后端
用法: python server.py  (默认 0.0.0.0:8080)
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("web.app:app", host="0.0.0.0", port=8080, reload=True)
