"""
Plan-Execute 模式 - 先规划后执行, 执行失败可修订
对比 Supervisor: Plan-Execute 串行步骤, Supervisor 并行分工
"""
from agents.base_agent import BaseAgent
from typing import Dict, List
import logging
logger = logging.getLogger(__name__)

class PlanExecuteAgent(BaseAgent):
    def __init__(self, name: str = "PlanExecute", **kwargs):
        super().__init__(name=name, **kwargs)

    def _plan(self, task: str) -> List[Dict]:
        """LLM 生成执行计划 [{step, action, params}]"""
        raise NotImplementedError

    def _execute_step(self, step: Dict) -> str:
        raise NotImplementedError

    def _revise(self, task: str, plan: List[Dict], results: List[str]) -> List[Dict]:
        raise NotImplementedError

    def think(self, task: str, context: Dict = None) -> str:
        raise NotImplementedError
