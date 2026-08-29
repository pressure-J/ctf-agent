"""MCPClient 演示: 连本地 stdio MCP server -> 列出/异步调用外部工具 -> 生成 schema 桥进 registry。"""
import asyncio, os, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE); os.chdir(BASE)
from tools.mcp_client import MCPClient
from tools.registry import ToolRegistry

MOCK = os.path.join(BASE, "examples", "mcp_mock_server.py")

async def main():
    client = MCPClient()
    await client.connect_stdio("demo", sys.executable, [MOCK])
    tools = await client.list_tools("demo")
    print("外部 MCP 工具:", [t["name"] for t in tools])
    print("call add(2,3) ->", await client.call_tool("demo", "add", {"a": 2, "b": 3}))
    print("call echo    ->", await client.call_tool("demo", "echo", {"text": "hi"}))

    reg = ToolRegistry()
    for t in tools:
        schema, fn = client.make_sync_tool("demo", t)
        reg.register(t["name"], fn, schema, category="external")
    print("registry 外部工具:", reg.list_tools("external"), "| schema keys:", list(reg.get_schemas()[0].keys()))
    await client.close()
    print("DONE: 连接外部MCP + 发现 + 调用 + schema桥进registry 全通")

asyncio.run(main())
