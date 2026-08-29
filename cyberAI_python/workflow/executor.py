"""工作流执行器 - 按拓扑序执行节点(agent/tool/condition), 结果写入共享状态。"""
from typing import Dict, Any, Callable, Optional
from workflow.graph import WorkflowGraph
from workflow.node import NodeType
from workflow.state import WorkflowState
import logging
logger = logging.getLogger(__name__)


class WorkflowExecutor:
    def __init__(self, agent_factory: Optional[Callable] = None):
        self.agent_factory = agent_factory   # agent_id -> Agent(便于 mock)

    def execute(self, graph: WorkflowGraph, initial_data: Dict = None) -> Dict[str, Any]:
        order = graph.topological_order()
        if not order:
            raise ValueError("工作流无法执行(存在环)")
        state = WorkflowState(initial_data)
        for nid in order:
            result = self._execute_node(graph.nodes[nid], state)
            state.set_node_result(nid, result)
        return state.node_results

    def _default_agent(self, agent_id):
        from agents.base_agent import BaseAgent
        return BaseAgent(name=agent_id or "workflow-agent")

    def _execute_node(self, node, state: WorkflowState) -> Any:
        cfg = node.config
        if node.type == NodeType.AGENT:
            agent = (self.agent_factory(cfg.get("agent_id")) if self.agent_factory
                     else self._default_agent(cfg.get("agent_id")))
            if agent is None:
                return f"(no agent) {cfg.get('task', '')}"
            return agent.think(cfg.get("task", ""), context={**state.data, **state.node_results})
        if node.type == NodeType.TOOL:
            try:
                from web.deps import tool_registry
                return tool_registry.execute(cfg.get("tool", ""), cfg.get("args", {}))
            except Exception as e:
                return f"tool err: {e}"
        if node.type == NodeType.CONDITION:
            return cfg.get("then", "")
        return ""  # START/END/MERGE 无操作(结果经 state 透传)
