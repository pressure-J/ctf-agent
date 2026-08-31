"""
通用机器人基类 - 各通道共用的"消息 -> Agent 处理 -> 回复"。
平台子类(钉钉/飞书/Telegram/微信)只负责自己的收发(webhook/轮询), 处理逻辑统一在这。
"""
from typing import Optional, Callable


class Bot:
    def __init__(self, name: str = "bot", agent_factory: Optional[Callable] = None):
        self.name = name
        self.agent_factory = agent_factory   # () -> Agent; 便于注入/mock

    def _agent(self):
        if self.agent_factory:
            return self.agent_factory()
        from web.deps import get_or_create_agent   # 默认平台主 Agent
        return get_or_create_agent()

    def handle_message(self, text: str) -> str:
        """处理收到的消息: 交 Agent.think, 返回回复(所有通道复用)"""
        try:
            agent = self._agent()
            return agent.think(text) if agent else f"(无Agent配置) {text}"
        except Exception as e:
            return f"处理失败: {e}"
