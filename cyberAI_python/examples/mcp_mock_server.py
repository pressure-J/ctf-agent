"""本地 MCP 演示服务器(FastMCP 1.x, stdio): 暴露 add/echo。"""
from mcp.server.fastmcp import FastMCP

server = FastMCP("py-demo")

@server.tool()
def add(a: int, b: int) -> int:
    """两个整数相加"""
    return a + b

@server.tool()
def echo(text: str) -> str:
    """原样返回文本"""
    return f"echo: {text}"

if __name__ == "__main__":
    server.run()  # 默认 stdio transport
