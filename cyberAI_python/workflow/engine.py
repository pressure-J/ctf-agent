"""
工作流引擎 - 对外统一入口: 构建->校验->执行
"""
from typing import Dict, Any
from workflow.graph import WorkflowGraph
from workflow.executor import WorkflowExecutor
import logging
logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(self):
        self.executor = WorkflowExecutor()

    def execute(self, definition: Dict, input_data: Dict = None) -> Dict:
        graph = WorkflowGraph.from_definition(definition)
        if not graph.validate():
            raise ValueError("工作流定义无效")
        return self.executor.execute(graph, input_data)

    def validate_definition(self, definition: Dict) -> tuple:
        raise NotImplementedError
