"""
工作流门面 - 对上层暴露 DAG 工作流接口
"""
from typing import Dict, Any
from workflow.engine import WorkflowEngine
from workflow.graph import WorkflowGraph
import logging
logger = logging.getLogger(__name__)

class WorkflowManager:
    def __init__(self):
        self.engine = WorkflowEngine()
        # TODO: 加载预定义模板 (workflow/templates/*.yaml)

    def run(self, definition: Dict, input_data: Dict[str, Any]) -> Dict:
        graph = WorkflowGraph.from_definition(definition)
        return self.engine.execute(graph, input_data)

    def list_templates(self) -> list:
        raise NotImplementedError

    def load_template(self, name: str) -> Dict:
        raise NotImplementedError
