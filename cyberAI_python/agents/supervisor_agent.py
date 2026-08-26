"""
Supervisor 模式 - 主管调度子 Agent
原理: 主管拆分任务 -> 分发给专业子Agent -> 汇总结果
实现: 每个子Agent的 think 注册为主管的一个"调度工具"
"""
from agents.base_agent import BaseAgent
from typing import Dict
import logging
logger = logging.getLogger(__name__)

class SupervisorAgent(BaseAgent):
    def __init__(self, name: str = "Supervisor", sub_agents: Dict[str, BaseAgent] = None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.sub_agents = sub_agents or {}
        # TODO: 把子Agent.think 包装成工具注册到 core

    def _dispatch(self, agent_name: str, task: str) -> str:
        raise NotImplementedError

    def _aggregate(self, results: Dict[str, str]) -> str:
        raise NotImplementedError
