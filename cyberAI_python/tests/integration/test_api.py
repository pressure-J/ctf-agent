"""API 集成测试: 登录/鉴权/工具/chat(真实 app + deps, TestClient)。"""
import os, sys, unittest
os.environ["OPENAI_API_KEY"] = "sk-test-mock"
os.environ["DEEPSEEK_API_KEY"] = "sk-test-mock"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

from starlette.testclient import TestClient
from web import deps
import web.app as appmod


def _login(c, pwd="pw12"):
    import time
    u = f"u{time.time_ns() % 100000000}"   # 每次唯一用户名, 避免跨运行密码冲突
    deps.auth_manager.register(u, pwd, u + "@x.com")
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
        self.assertIn("schema", r.json())

    def test_chat_endpoint(self):
        """chat 异步化接线(假Agent); 防 verify_token用sub 回归"""
        from web.routers import chat as chat_router

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

        chat_router.get_or_create_agent = lambda agent_id=None: FakeAgent()
        tok = _login(self.c, "pw")
        r = self.c.post("/api/chat", json={"message": "hello"},
                        headers={"Authorization": f"Bearer {tok}"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["response"], "ok:hello")


if __name__ == "__main__":
    unittest.main()
