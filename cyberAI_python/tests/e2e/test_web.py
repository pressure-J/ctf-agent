"""e2e: 模拟真实用户完整流程(登录->页面->工具->工作流->知识库->对话->统计)。
所有耗钱环节用 mock(假Agent/condition节点), 不连真 LLM。"""
import os, sys, time, unittest
os.environ["OPENAI_API_KEY"] = "sk-test-mock"; os.environ["DEEPSEEK_API_KEY"] = "sk-test-mock"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from starlette.testclient import TestClient
from web import deps
import web.app as appmod


class TestE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = TestClient(appmod.app)
        from web.routers import chat as cr
        class FA:
            system_prompt = "t"
            llm = type("L", (), {"stream_chat": lambda s, m: (x for x in ["hi"])})()
            def __init__(s): s.state = type("S", (), {"tool_calls": []})()
            def think(s, task, context=None): return "答复:" + task
        cr.get_or_create_agent = lambda agent_id=None: FA()   # 对话走假Agent

    def test_full_user_journey(self):
        c = self.c
        u = f"e2e{int(time.time()) % 100000}"
        deps.auth_manager.register(u, "pw", u + "@x.com")
        # 1 登录
        tok = c.post("/api/auth/login", json={"username": u, "password": "pw"}).json()["access_token"]
        h = {"Authorization": f"Bearer {tok}"}
        # 2 前端页面(多页签壳)
        self.assertEqual(c.get("/").status_code, 200)
        # 3 工具列表
        self.assertGreater(c.get("/api/tools", headers=h).json()["count"], 50)
        # 4 建工作流并执行(condition节点, 免LLM)
        wid = c.post("/api/workflows", headers=h,
                     json={"name": "e2eWF", "description": "",
                           "nodes": [{"id": "a", "type": "condition", "then": "ok"}], "edges": []}).json()["workflow_id"]
        self.assertEqual(c.post(f"/api/workflows/{wid}/execute", headers=h, json={}).json()["result"], {"a": "ok"})
        # 5 知识库检索(向量)
        r = c.post("/api/knowledge/search", params={"query": "SQL 注入", "top_k": 3}, headers=h)
        self.assertEqual(r.status_code, 200); self.assertIn("results", r.json())
        # 6 对话(假Agent)
        self.assertEqual(c.post("/api/chat", headers=h, json={"message": "hi"}).json()["response"], "答复:hi")
        # 7 系统统计
        self.assertIn("registered_tools", c.get("/api/admin/stats", headers=h).json())
        print("e2e 通过: 登录→页面→工具→工作流→知识库→对话→统计")


if __name__ == "__main__":
    unittest.main()
