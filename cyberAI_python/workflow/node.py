"""
工作流节点定义
"""
from typing import Dict, List
from enum import Enum
import logging
logger = logging.getLogger(__name__)

class NodeType(Enum):
    AGENT = "agent"
    TOOL = "tool"
    CONDITION = "condition"
    MERGE = "merge"
    START = "start"
    END = "end"

class WorkflowNode:
    def __init__(self, node_id: str, node_type: NodeType, config: Dict = None):
        self.id = node_id
        self.type = node_type
        self.config = config or {}
        self.inputs: List[str] = []
        self.outputs: List[str] = []

    def add_input(self, node_id: str):
        self.inputs.append(node_id)

    def add_output(self, node_id: str):
        self.outputs.append(node_id)

    def to_dict(self) -> Dict:
        return {"id": self.id, "type": self.type.value, "config": self.config}
