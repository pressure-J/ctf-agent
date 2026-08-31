"""API 集成测试补全: agents / workflows / knowledge / admin 端点(真实 app + deps)。"""
import os, sys, time, unittest
os.environ["OPENAI_API_KEY"] = "sk-test-mock"; os.environ["DEEPSEEK_API_KEY"] = "sk-test-mock"
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from starlette.testclient import TestClient
from web import deps
import web.app as appmod


def _tok(c):
    u = f"u{time.time_ns() % 100000000}"
    deps.auth_manager.register(u, "pw", u + "@x.com")
    r = c.post("/api/auth/login", json={"username": u, "password": "pw"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


class TestAPIExtend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = TestClient(appmod.app)

    def test_agents_crud(self):
        tok = _tok(self.c); h = {"Authorization": f"Bearer {tok}"}
        self.assertEqual(self.c.get("/api/agents", headers=h).status_code, 200)
        r = self.c.post("/api/agents", headers=h, json={"name": "a", "mode": "single"})
        aid = r.json()["agent_id"]
        self.assertEqual(self.c.get(f"/api/agents/{aid}", headers=h).status_code, 200)

    def test_workflow_create_exec(self):
        """建工作流 + 执行(condition节点免LLM) -> DAG引擎返回 {'a':'ok'}"""
        tok = _tok(self.c); h = {"Authorization": f"Bearer {tok}"}
        wf = {"name": "w", "description": "d",
              "nodes": [{"id": "a", "type": "condition", "then": "ok"}], "edges": []}
        wid = self.c.post("/api/workflows", headers=h, json=wf).json()["workflow_id"]
        res = self.c.post(f"/api/workflows/{wid}/execute", headers=h, json={}).json()
        self.assertEqual(res["result"], {"a": "ok"})

    def test_knowledge_search(self):
        tok = _tok(self.c); h = {"Authorization": f"Bearer {tok}"}
        self.assertEqual(self.c.get("/api/knowledge", headers=h).status_code, 200)
        r = self.c.post("/api/knowledge/search", params={"query": "SQL 注入", "top_k": 3}, headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertIn("results", r.json())

    def test_admin_stats_audit(self):
        tok = _tok(self.c); h = {"Authorization": f"Bearer {tok}"}
        s = self.c.get("/api/admin/stats", headers=h).json()
        for k in ("total_conversations", "total_messages", "registered_tools"):
            self.assertIn(k, s)
        self.assertEqual(self.c.get("/api/admin/audit?limit=5", headers=h).status_code, 200)


if __name__ == "__main__":
    unittest.main()
