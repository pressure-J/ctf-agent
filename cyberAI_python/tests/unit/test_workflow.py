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

    def test_parallel_execution(self):
        """同一层(无依赖)节点应并发: 各 sleep0.25 -> 总耗时 <串行和"""
        import time
        DEF_P = {"nodes": [
            {"id": "a", "type": "agent", "agent_id": "A", "task": "t"},
            {"id": "b", "type": "agent", "agent_id": "B", "task": "t"},
            {"id": "c", "type": "agent", "agent_id": "C", "task": "t"}],
            "edges": [{"from": "a", "to": "b"}, {"from": "a", "to": "c"}]}
        class Slow:
            def think(s, task, context=None): time.sleep(0.25); return task
        st = time.time()
        WorkflowEngine(WorkflowExecutor(lambda aid: Slow())).execute(DEF_P)
        self.assertLess(time.time() - st, 0.6)   # 串行~0.75, 并行~0.5


if __name__ == "__main__":    unittest.main()
