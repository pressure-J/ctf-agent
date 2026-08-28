"""验证 BaseAgent 构造时自动从 tools/configs 加载 YAML 工具(网络mock)。"""
import os, sys, unittest
os.environ["OPENAI_API_KEY"]="sk-test-mock"; os.environ["DEEPSEEK_API_KEY"]="sk-test-mock"
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,BASE)
from agents.base_agent import BaseAgent

class TestBaseAgentAutoLoad(unittest.TestCase):
    def test_auto_load_yaml_tools(self):
        a=BaseAgent(name="B")
        names=[t["function"]["name"] for t in a.core.tools]
        self.assertIn("dns_lookup", names)
        self.assertIn("nmap_scan", names)
        self.assertIn("dns_lookup", a.core.tool_functions)

    def test_whitelist_filter(self):
        """BaseAgent(tools=[...]) 只桥接白名单工具, 避免全量撑爆 context"""
        a = BaseAgent(name="R", tools=["dns_lookup", "nmap_scan"])
        names = sorted(t["function"]["name"] for t in a.core.tools)
        self.assertEqual(names, ["dns_lookup", "nmap_scan"])
        self.assertNotIn("angr", names)

if __name__=="__main__":
    unittest.main()
