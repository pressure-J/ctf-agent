"""多 Agent 测试: supervisor 子Agent-as-tool 派发 + plan_execute 继承 + orchestrator 缓存。"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMultiAgent(unittest.TestCase):
    def test_supervisor_dispatch(self):
        from agents.supervisor_agent import SupervisorAgent
        class MockSub:
            description = "d"
            def __init__(s): s.calls = []
            def think(s, task, context=None): s.calls.append(task); return "r"
        sub = MockSub(); sup = SupervisorAgent(sub_agents={"x": sub})
        lc = []
        def fake():
            lc.append(1)
            if len(lc) == 1:
                return {"choices": [{"message": {"role": "assistant", "content": None,
                    "tool_calls": [{"id": "t", "type": "function",
                        "function": {"name": "x", "arguments": '{"task":"do"}'}}]}}]}
            return {"choices": [{"message": {"role": "assistant", "content": "done"}}]}
        sup.core._call_llm = fake
        self.assertEqual(sup.think("t"), "done")   # 主管汇总
        self.assertEqual(sub.calls, ["do"])        # 子Agent被当工具调用
        self.assertEqual(len(sup.core.tools), 1)   # 注册为工具

    def test_plan_execute_inherits(self):
        from agents.plan_execute_agent import PlanExecuteAgent
        self.assertTrue(PlanExecuteAgent.__bases__[0].__name__ == "SupervisorAgent")

    def test_orchestrator_cache(self):
        from agents.orchestrator import Orchestrator
        o = Orchestrator(); a = o.get_or_create("s")
        self.assertIs(a, o.get_or_create("s"))


if __name__ == "__main__":
    unittest.main()
