"""Agent 高级能力: 上下文预算压缩 + checkpoint存储 + 中断恢复(resume_from)。"""
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.agent import Agent
from core.checkpoint import CheckpointStore


class TestAgentAdvanced(unittest.TestCase):
    def setUp(self):
        self.store = CheckpointStore(tempfile.mkdtemp("cyck"))

    def test_context_budget_compress(self):
        a = Agent(name="b").set_context_budget(10)
        a.state.messages = ([{"role": "system", "content": "s"}] +
                            [{"role": "user", "content": "很长" * 50},
                             {"role": "assistant", "content": "结果" * 30}] * 5)
        n = len(a.state.messages); a._maybe_compress()
        self.assertLess(len(a.state.messages), n)

    def test_checkpoint_save(self):
        a = Agent(name="c").set_checkpoint(self.store, "run")
        a.state.iteration = 3; a._maybe_checkpoint()
        d, ok = self.store.load("run")
        self.assertTrue(ok); self.assertEqual(d["iteration"], 3)

    def test_resume_from(self):
        a = Agent(name="r")
        a.state.from_dict({"messages": [{"role": "user", "content": "已有"}],
                           "tool_calls": [], "iteration": 2,
                           "status": "running", "context": {}})
        self.store.save("ckr", a.state.to_dict())
        lc = []
        def flm():
            lc.append(1); return {"choices": [{"message": {"role": "assistant", "content": "续跑完成"}}]}
        a._call_llm = flm
        self.assertEqual(a.resume_from("ckr", self.store), "续跑完成")
        self.assertGreaterEqual(a.state.iteration, 3)


if __name__ == "__main__":
    unittest.main()
