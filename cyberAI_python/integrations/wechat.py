"""微信 机器人 - 复用 Bot 基类的 Agent 处理; 平台收发待配置。"""
from integrations.base import Bot
import logging
logger = logging.getLogger(__name__)


class 微信Bot(Bot):
    def __init__(self, token: str = "", webhook_url: str = "", **kw):
        super().__init__(name="微信", **kw)
        self.token = token
        self.webhook_url = webhook_url

    def handle_message(self, text: str) -> str:
        return super().handle_message(text)

    def start(self):
        # TODO: 企业微信/公众号 webhook 回推(需真实地址)
        raise NotImplementedError("配置平台收发参数后实现")
