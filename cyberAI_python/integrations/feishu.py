
"""飞书 机器人集成 - 接收消息->Agent处理->回复(TODO)
原理: 通过webhook/长轮询接收消息, 调用Agent处理, 回推结果
"""
import logging
logger = logging.getLogger(__name__)

class 飞书Bot:
    def __init__(self, token: str = "", webhook_url: str = ""):
        self.token = token
        self.webhook_url = webhook_url

    def handle_message(self, text: str):
        """处理收到的消息, 返回Agent回复"""
        raise NotImplementedError

    def start(self):
        """启动接收循环"""
        raise NotImplementedError
