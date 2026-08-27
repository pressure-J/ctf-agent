"""
Agent 循环与 LLM 封装接线的单元测试(mock 掉网络, 不联网)。
验证 core/agent.py 经 self.llm 的:
  - 完整工具调用循环: 调LLM -> tool_call -> 执行工具 -> 回填 -> 终答
  - Agent.chat() 无工具对话走 self.llm
  - LLMClient.chat_with_tools 正确透传 tools 参数并返回 dict
运行: python -m unittest tests.unit.test_agent_loop -v
"""
import os
import sys
import unittest

# 让 OpenAI 客户端能构造(不联网)。必须在 import core 之前设置。
os.environ["OPENAI_API_KEY"] = "sk-test-mock"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-mock"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core.agent import Agent
from core.llm import LLMClient


class TestAgentLoop(unittest.TestCase):

    def test_tool_calling_loop(self):
        """第一次LLM要求调工具 -> 执行 -> 第二次LLM给终答"""
        calls = []

        def fake_chat_with_tools(messages, tools, tool_choice="auto",
                                 temperature=None, max_tokens=None):
            calls.append((list(messages), tools))
            if len(calls) == 1:
                return {"choices": [{"message": {
                    "role": "assistant", "content": None,
                    "tool_calls": [{"id": "c1", "type": "function",
                                    "function": {"name": "echo_tool",
                                                 "arguments": '{"text": "hi"}'}}]}}]}
            return {"choices": [{"message": {"role": "assistant", "content": "FLAG{done}"}}]}

        def echo_tool(text):
            return "echo:" + text

        a = Agent(name="T")
        a.llm.chat_with_tools = fake_chat_with_tools
        a.register_tool("echo_tool", "echo", echo_tool,
                        {"type": "object", "properties": {"text": {"type": "string"}},
                         "required": ["text"]})

        result = a.think("t")
        self.assertEqual(result, "FLAG{done}")
        self.assertEqual(len(a.state.tool_calls), 1, "应执行 1 次工具")
        self.assertEqual(len(calls[0][1]), 1, "第1轮应把工具schema传给LLM")
        self.assertIn("tool", [m["role"] for m in calls[1][0]], "第2轮应回填 role=tool")

    def test_chat_via_llm(self):
        """无工具对话: Agent.chat() 走 self.llm.chat"""
        a = Agent(name="T")
        original = a.llm.chat
        a.llm.chat = lambda messages, temperature=None: "hi back"
        try:
            self.assertEqual(a.chat("hello"), "hi back")
        finally:
            a.llm.chat = original

    def test_llm_client_tool_pass_through(self):
        """LLMClient.chat_with_tools 把 tools 透传并返回 dict"""

        class MD:
            def model_dump(self):
                return {"choices": [{"message": {"content": "r"}}]}

        class Comp:
            def __init__(self):
                self.last = None

            def create(self, **kw):
                self.last = kw
                return MD()

        class Chat:
            def __init__(self):
                self.completions = Comp()

        class Client:
            def __init__(self):
                self.chat = Chat()

        c = LLMClient(api_key="sk-t", base_url="http://x")
        c.client = Client()
        out = c.chat_with_tools([{"role": "user", "content": "hi"}], tools=[{"t": 1}])
        self.assertEqual(out, {"choices": [{"message": {"content": "r"}}]})
        self.assertEqual(c.client.chat.completions.last["tools"], [{"t": 1}])


if __name__ == "__main__":
    unittest.main()