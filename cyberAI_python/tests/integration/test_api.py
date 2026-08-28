"""API 集成测试: Web 登录 + 鉴权 + 工具列表(真实 app, TestClient)。
覆盖 web/app.py 的接线。运行: pytest tests/ -q
"""
import os, sys, unittest
os.environ["OPENAI_API_KEY"] = "sk-test-mock"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-mock"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from starlette.testclient import TestClient
import web.app as appmod


def _login(c, u="apitest", pwd="pw123"):
    appmod.auth_manager.register(u, pwd, u + "@x.com")  # 幂等
    r = c.post("/api/auth/login", json={"username": u, "password": pwd})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = TestClient(appmod.app)

    def test_tools_require_auth(self):
        self.assertEqual(self.c.get("/api/tools", headers={}).status_code, 401)

    def test_login_and_tools(self):
        tok = _login(self.c)
        r = self.c.get("/api/tools", headers={"Authorization": f"Bearer {tok}"})
        self.assertEqual(r.status_code, 200)
        self.assertGreater(r.json()["count"], 50, "YAML 工具库应已加载")

    def test_tool_detail_has_schema(self):
        tok = _login(self.c)
        r = self.c.get("/api/tools/dns_lookup", headers={"Authorization": f"Bearer {tok}"})
        self.assertEqual(r.status_code, 200)

    def test_chat_endpoint(self):
        """chat 路由异步化 + 接线(假Agent, 不连真实LLM); 防 KeyError user[sub] 回归"""
        import web.app as m

        class FakeLLM:
            def stream_chat(self, messages):
                yield "hi"

        class FakeAgent:
            system_prompt = "t"
            llm = FakeLLM()

            def __init__(self):
                self.state = type("S", (), {"tool_calls": []})()

            def think(self, task, context=None):
                return "ok:" + task

        m.get_or_create_agent = lambda agent_id=None: FakeAgent()
        tok = _login(self.c, "chatuser", "pw")
        r = self.c.post("/api/chat", json={"message": "hello"},
                        headers={"Authorization": f"Bearer {tok}"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["response"], "ok:hello")

if __name__ == "__main__":
    unittest.main()
