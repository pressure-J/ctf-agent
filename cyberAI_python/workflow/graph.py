"""
DAG 工作流图 - 节点+有向边, 拓扑排序定执行顺序
"""
from typing import Dict, List
from workflow.node import WorkflowNode
import logging
logger = logging.getLogger(__name__)

class WorkflowGraph:
    def __init__(self):
        self.nodes: Dict[str, WorkflowNode] = {}
        self.start_node: str = None

    def add_node(self, node: WorkflowNode):
        self.nodes[node.id] = node

    def add_edge(self, from_id: str, to_id: str):
        if from_id in self.nodes and to_id in self.nodes:
            self.nodes[from_id].add_output(to_id)
            self.nodes[to_id].add_input(from_id)

    def topological_order(self) -> List[str]:
        """Kahn 拓扑排序"""
        raise NotImplementedError

    @classmethod
    def from_definition(cls, definition: Dict):
        """从 {nodes:[...], edges:[{from,to}]} 构建"""
        raise NotImplementedError

    def validate(self) -> bool:
        raise NotImplementedError
