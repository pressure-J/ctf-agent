"""
ToolManager 桥接链路单元测试(网络部分mock)。
覆盖: load_all(注册名) -> attach_to_agent -> think 里调用 YAML 工具。
运行: python -m unittest tests.unit.test_tools_manager -v
"""
import os, sys, unittest
from unittest import mock

os.environ["OPENAI_API_KEY"] = "sk-test-mock"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-mock"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from core.tools import ToolManager
from core.agent import Agent


class TestToolManager(unittest.TestCase):

    def test_load_all_and_attach(self):
        """load_all 返回注册名, attach_to_agent 把工具桥接进 Agent"""
        m = ToolManager()
        names = m.load_all("tools/configs")
        self.assertIn("dns_lookup", names)   # 注册名(来自 YAML 的 name:), 不是文件名
        self.assertIn("nmap_scan", names)
        a = Agent(name="V")
        m.attach_to_agent(a)
        self.assertIn("dns_lookup", a.tool_functions)                      # 执行侧
        self.assertIn("dns_lookup", [t["function"]["name"] for t in a.tools])  # schema侧

    def test_think_calls_yaml_tool(self):
        """Agent 在 think 循环里真的调用了来自 YAML 的 dns_lookup"""
        m = ToolManager(); m.load_all("tools/configs")
        a = Agent(name="V"); m.attach_to_agent(a)
        calls = []

        def fake(messages, tools, **kw):
            calls.append(list(messages))
            if not any(x["role"] == "tool" for x in messages):
                return {"choices": [{"message": {"role": "assistant", "content": None,
                    "tool_calls": [{"id": "c1", "type": "function",
                        "function": {"name": "dns_lookup",
                                     "arguments": '{"target": "example.com"}'}}]}}]}
            return {"choices": [{"message": {"role": "assistant", "content": "done"}}]}

        a.llm.chat_with_tools = fake
        fake_run = type("R", (), {"returncode": 0, "stdout": "1.2.3.4", "stderr": ""})
        with mock.patch("subprocess.run", return_value=fake_run()):
            ans = a.think("查 dns")
        self.assertEqual(ans, "done")
        self.assertEqual(a.state.tool_calls[0]["name"], "dns_lookup")


if __name__ == "__main__":
    unittest.main()
