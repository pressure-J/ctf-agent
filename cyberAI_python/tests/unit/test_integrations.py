"""集成通道测试: Bot 基类处理 + 各通道继承复用(mock Agent)。"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from integrations.dingtalk import 钉钉Bot
from integrations.feishu import 飞书Bot
from integrations.telegram import TelegramBot
from integrations.wechat import 微信Bot


class _FakeAgent:
    def think(self, task, context=None): return "reply:" + task


class TestIntegrations(unittest.TestCase):
    def test_base_bot_handles_via_agent(self):
        from integrations.base import Bot
        b = Bot(agent_factory=lambda: _FakeAgent())
        self.assertEqual(b.handle_message("hi"), "reply:hi")

    def test_channels_inherit_agent_handling(self):
        for cls in (钉钉Bot, 飞书Bot, TelegramBot, 微信Bot):
            b = cls(agent_factory=lambda: _FakeAgent())
            self.assertEqual(b.handle_message("扫描"), "reply:扫描")


if __name__ == "__main__":
    unittest.main()
