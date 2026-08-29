"""工作流引擎 - 对外统一入口: 构建->校验->按拓扑执行。"""
from typing import Dict, Any, Tuple
from workflow.graph import WorkflowGraph
from workflow.executor import WorkflowExecutor
import logging
logger = logging.getLogger(__name__)


class WorkflowEngine:
    def __init__(self, executor: WorkflowExecutor = None):
        self.executor = executor or WorkflowExecutor()

    def execute(self, definition: Dict, input_data: Dict = None) -> Dict:
        graph = WorkflowGraph.from_definition(definition)
        if not graph.validate():
            raise ValueError("工作流定义无效(存在环)")
        return self.executor.execute(graph, input_data)

    def validate_definition(self, definition: Dict) -> Tuple:
        try:
            graph = WorkflowGraph.from_definition(definition)
            order = graph.topological_order()
            return (True, order) if order else (False, "存在环")
        except Exception as e:
            return (False, str(e))
