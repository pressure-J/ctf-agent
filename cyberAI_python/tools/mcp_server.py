"""
MCP服务器 - 把自己暴露成 Model Context Protocol 服务
原理: MCP 是 Anthropic 提出的工具发现/调用标准协议。
     本模块把 ToolRegistry 注册成 MCP 服务端(stdio/sse)。
"""
import logging
logger = logging.getLogger(__name__)

class MCPServer:
    def __init__(self, registry, transport: str = "stdio"):
        self.registry = registry
        self.transport = transport
        # TODO: 初始化 mcp 库 Server 实例

    def start(self):
        raise NotImplementedError

    def _handle_list_tools(self) -> list:
        raise NotImplementedError

    def _handle_call_tool(self, name: str, arguments: dict) -> dict:
        raise NotImplementedError
