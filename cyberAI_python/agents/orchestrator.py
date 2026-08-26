"""
多 Agent 编排器 - 管理 Agent 实例生命周期(全局单例)
"""
from typing import Dict
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}

    def get_or_create(self, agent_id: str = None, config: Dict = None) -> BaseAgent:
        raise NotImplementedError

    def destroy(self, agent_id: str):
        raise NotImplementedError

    def list_active(self) -> list:
        raise NotImplementedError
