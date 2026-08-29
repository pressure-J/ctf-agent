"""多 Agent 编排器 - 按 mode 创建 Agent(single/supervisor/plan_execute), 全局缓存。
对齐 Go multiagent: 管理者按 mode 派发; 子Agent从 agents/roles 角色池构建。
"""
from typing import Dict, Optional
from agents.base_agent import BaseAgent
from agents.single_agent import SingleAgent
from agents.supervisor_agent import SupervisorAgent
from agents.plan_execute_agent import PlanExecuteAgent
from agents.roles_loader import load_roles, build_role_agent
import logging
logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def get_or_create(self, agent_id: str = None, config: Dict = None) -> BaseAgent:
        config = config or {}
        mode = config.get("mode", "single")
        name = agent_id or config.get("name", mode.capitalize())
        if name in self.agents:
            return self.agents[name]
        if mode == "supervisor":
            sub = self._build_role_pool(config.get("role_tools"))
            agent = SupervisorAgent(name=name, sub_agents=sub)
        elif mode == "plan_execute":
            agent = PlanExecuteAgent(name=name,
                                     sub_agents=self._build_role_pool(config.get("role_tools")))
        else:
            agent = SingleAgent(name=name)
        self.agents[name] = agent
        return agent

    def _build_role_pool(self, role_tools: Optional[list] = None) -> Dict[str, BaseAgent]:
        pool = {}
        for r in load_roles():
            if not r.get("enabled", True):
                continue
            pool[r["name"]] = build_role_agent(r["name"], tools=role_tools)
        return pool

    def destroy(self, agent_id: str):
        return self.agents.pop(agent_id, None)

    def list_active(self) -> list:
        return list(self.agents.keys())

    def clear(self):
        self.agents.clear()
