"""DAG 工作流图 - 节点+有向边; Kahn 拓扑排序 + 校验。"""
from typing import Dict, List, Optional
from collections import deque
from workflow.node import WorkflowNode, NodeType
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

    def topological_order(self) -> Optional[List[str]]:
        """Kahn: 逐个找入度0的节点, 生成一个合法拓扑序(有环返回 None)"""
        in_deg = {nid: len(n.inputs) for nid, n in self.nodes.items()}
        q = deque(nid for nid, d in in_deg.items() if d == 0)
        order = []
        while q:
            nid = q.popleft()
            order.append(nid)
            for o in self.nodes[nid].outputs:
                in_deg[o] -= 1
                if in_deg[o] == 0:
                    q.append(o)
        return order if len(order) == len(self.nodes) else None

    def validate(self) -> bool:
        return self.topological_order() is not None

    @classmethod
    def from_definition(cls, definition: Dict) -> "WorkflowGraph":
        g = cls()
        for n in definition.get("nodes", []):
            g.add_node(WorkflowNode(n["id"], NodeType(n.get("type", "agent")), n))
        for e in definition.get("edges", []):
            g.add_edge(e["from"], e["to"])
        return g
