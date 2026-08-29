"""工作流状态 - 共享输入 + 各节点结果, 支持 ${node.output} 引用解析。"""
from typing import Dict, Any


class WorkflowState:
    def __init__(self, initial: Dict = None):
        self.data: Dict[str, Any] = dict(initial or {})
        self.node_results: Dict[str, Any] = {}

    def set_node_result(self, node_id: str, result: Any):
        self.node_results[node_id] = result

    def get_node_result(self, node_id: str) -> Any:
        return self.node_results.get(node_id)

    def resolve_variable(self, expr: str) -> Any:
        """解析 ${node_id.output} / ${key} 引用"""
        s = (expr or "").strip()
        if s.startswith("${") and s.endswith("}"):
            s = s[2:-1].strip()
        if "." in s:                                   # ${node.字段}
            nid, _, key = s.partition(".")
            val = self.node_results.get(nid)
            return val.get(key) if isinstance(val, dict) else None
        if s in self.node_results:
            return self.node_results[s]
        return self.data.get(s)

    def snapshot(self) -> Dict:
        return {"data": self.data, "node_results": self.node_results}
