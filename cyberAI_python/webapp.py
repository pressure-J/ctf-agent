"""
Web应用入口 - 启动 FastAPI + 静态前端
TODO: 把编译后的 React 产物挂到 /static, 单端口访问
"""
import uvicorn

if __name__ == "__main__":
    # TODO: 静态目录挂载 frontend/react-app/dist
    uvicorn.run("web.app:app", host="0.0.0.0", port=8080, reload=True)
