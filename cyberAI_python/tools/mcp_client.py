"""
MCP客户端 - 连接外部 MCP 工具服务器(Burp MCP / Claude mcp-servers / 自建等)。
能力:
  - connect_stdio: 启动外部 stdio MCP server 子进程 -> JSON-RPC 通信
  - connect_sse:    连外部 SSE/HTTP MCP server(如 Burp MCP)
  - list_tools:     列出外部服务器暴露的工具(schema)
  - call_tool:      调用外部工具
  - make_sync_tool: 把外部工具包装成可注册进 ToolRegistry/Agent 的同步函数(schema+func)
用途: 把外部工具生态并入本项目 Agent 的可用清单(对齐 Go 的外部 MCP 能力)。
"""
import asyncio
import threading
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self):
        self.sessions: Dict[str, Any] = {}   # server_name -> ClientSession
        self._bases: Dict[str, Any] = {}     # 保持 transport 上下文存活
        self.tools: Dict[str, List[Dict]] = {}  # server_name -> 工具清单
        self._cms: Dict[str, Any] = {}   # 保持 transport context manager 存活(防GC关闭)

    async def connect_stdio(self, name: str, command: str, args: Optional[list] = None,
                            env: Optional[dict] = None) -> str:
        """连一个 stdio 外部 MCP server(子进程)"""
        from mcp.client.stdio import stdio_client
        from mcp import ClientSession, StdioServerParameters
        params = StdioServerParameters(command=command, args=args or [], env=env)
        cm = stdio_client(params)
        self._cms[f"stdio:{name}"] = cm       # 保留引用, 防 GC 关闭 transport
        read, write = await cm.__aenter__()
        session = await ClientSession(read, write).__aenter__()
        await session.initialize()
        self._bases[f"stdio:{name}"] = (read, write)
        self.sessions[name] = session
        logger.info("MCP stdio 已连接: %s", name)
        return name

    async def connect_sse(self, name: str, url: str, headers: Optional[dict] = None) -> str:
        """连一个 SSE/HTTP 外部 MCP server(如 Burp MCP)"""
        from mcp.client.sse import sse_client
        from mcp import ClientSession
        cm = sse_client(url, headers=headers)
        self._cms[f"sse:{name}"] = cm         # 保留引用, 防 GC 关闭 transport
        read, write = await cm.__aenter__()
        session = await ClientSession(read, write).__aenter__()
        await session.initialize()
        self._bases[f"sse:{name}"] = (read, write)
        self.sessions[name] = session
        logger.info("MCP SSE 已连接: %s @ %s", name, url)
        return name

    async def list_tools(self, name: str) -> List[Dict]:
        """列出外部服务器暴露的工具"""
        res = await self.sessions[name].list_tools()
        tools = [{"name": t.name, "description": t.description, "inputSchema": t.inputSchema}
                 for t in res.tools]
        self.tools[name] = tools
        return tools

    async def call_tool(self, name: str, tool_name: str, arguments: dict = None) -> str:
        """调用外部工具, 把返回的 content 块拼成文本"""
        res = await self.sessions[name].call_tool(tool_name, arguments or {})
        parts = []
        for c in (res.content or []):
            d = c if isinstance(c, dict) else getattr(c, "model_dump", lambda: {})()
            if d.get("type") == "text":
                parts.append(d.get("text", ""))
            else:
                parts.append(str(c))
        return "\n".join(parts)

    async def close(self, name: Optional[str] = None):
        """关闭 session, 并退出 transport context manager(关闭子进程, 让事件循环能退出)"""
        names = [name] if name else list(self.sessions.keys())
        for nm in names:
            if nm not in self.sessions:
                continue
            try:
                await self.sessions[nm].close()
            except Exception:
                pass
            # 退出对应 transport CM
            for key in [k for k in self._cms if k.endswith(":" + nm)]:
                try:
                    await self._cms[key].__aexit__(None, None, None)
                except Exception:
                    pass
                del self._cms[key]
            del self.sessions[nm]
        if not name:
            self.sessions.clear()

    def make_sync_tool(self, name: str, tool: Dict):
        """把外部 MCP 工具包装成 (schema, 同步可调用) 对, 可直接注册进 ToolRegistry / Agent。
        MCP call 是 async, 这里用独立线程跑一个 loop, 保证在同步的 Agent 循环里也能调用。
        """
        schema = {
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool.get("inputSchema") or {"type": "object", "properties": {}},
            },
        }

        def call(**args):
            # sync 上下文(无 running loop, 如 Agent think 循环)直接用新 loop 跑;
            # 若在 web async 场景, 请直接 await call_tool, 不要用本 sync 包装
            import asyncio
            return asyncio.run(self.call_tool(name, tool["name"], args))

        return schema, call