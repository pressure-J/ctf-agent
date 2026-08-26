"""
MCP客户端 - 连接外部 MCP 工具服务器
用途: 调用 HexStrike/Burp MCP 等外部工具,扩展工具生态。
"""
import logging
logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.connections = {}
        # TODO: config.yaml external_mcp.servers 驱动

    async def connect_stdio(self, name: str, command: str, args: list):
        raise NotImplementedError

    async def connect_sse(self, name: str, url: str):
        raise NotImplementedError

    async def list_remote_tools(self, name: str) -> list:
        raise NotImplementedError

    async def call_tool(self, name: str, tool: str, args: dict):
        raise NotImplementedError

    def merge_into_registry(self, registry):
        raise NotImplementedError
