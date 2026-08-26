"""
工作流状态管理 - 每个节点结果写入共享状态, 下游读取
"""
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

class WorkflowState:
    def __init__(self, initial: Dict = None):
        self.data: Dict[str, Any] = dict(initial or {})
        self.node_results: Dict[str, Any] = {}

    def set_node_result(self, node_id: str, result: Any):
        self.node_results[node_id] = result

    def get_node_result(self, node_id: str) -> Any:
        return self.node_results.get(node_id)

    def resolve_variable(self, expr: str) -> Any:
        """解析 ${node_id.output} 引用"""
        raise NotImplementedError

    def snapshot(self) -> Dict:
        return {"data": self.data, "node_results": self.node_results}
