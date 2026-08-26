"""
工作流执行器 - 按拓扑序执行节点
TODO: 条件分支/并行执行/失败处理
"""
from typing import Dict, Any
from workflow.graph import WorkflowGraph
from workflow.state import WorkflowState
import logging
logger = logging.getLogger(__name__)

class WorkflowExecutor:
    def __init__(self):
        self.agents = {}  # agent_id -> Agent

    def execute(self, graph: WorkflowGraph, initial_data: Dict = None) -> Dict[str, Any]:
        raise NotImplementedError

    def _execute_node(self, node, state: WorkflowState) -> Any:
        raise NotImplementedError
