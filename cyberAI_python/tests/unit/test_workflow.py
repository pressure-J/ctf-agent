"""工作流 DAG 引擎测试: 拓扑执行顺序 + 环检测。"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from workflow.graph import WorkflowGraph
from workflow.engine import WorkflowEngine
from workflow.executor import WorkflowExecutor

DEF = {"nodes": [
    {"id": "a", "type": "agent", "agent_id": "A", "task": "scan"},
    {"id": "b", "type": "agent", "agent_id": "B", "task": "web"},
    {"id": "c", "type": "agent", "agent_id": "C", "task": "crypto"},
    {"id": "d", "type": "agent", "agent_id": "D", "task": "report"}],
    "edges": [{"from": "a", "to": "b"}, {"from": "a", "to": "c"},
              {"from": "b", "to": "d"}, {"from": "c", "to": "d"}]}


class TestWorkflow(unittest.TestCase):
    def test_topological_execution(self):
        calls = []
        class MockAgent:
            def __init__(s, aid): s.aid = aid
            def think(s, task, context=None): calls.append(s.aid); return f"{s.aid}:{task}"
        eng = WorkflowEngine(WorkflowExecutor(lambda aid: MockAgent(aid)))
        res = eng.execute(DEF, {"target": "x"})
        self.assertEqual(calls[0], "A"); self.assertEqual(calls[-1], "D")
        self.assertLess(calls.index("B"), calls.index("D"))
        self.assertLess(calls.index("C"), calls.index("D"))
        self.assertIn("D:report", res["d"])

    def test_cycle_rejected(self):
        ring = {"nodes": [{"id": "a", "type": "agent"}, {"id": "b", "type": "agent"}],
                "edges": [{"from": "a", "to": "b"}, {"from": "b", "to": "a"}]}
        self.assertIsNone(WorkflowGraph.from_definition(ring).topological_order())
        self.assertFalse(WorkflowGraph.from_definition(ring).validate())


if __name__ == "__main__":
    unittest.main()
