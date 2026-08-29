"""Supervisor 模式 - 主管调度子 Agent(对齐 Go multiagent 的 supervisor)。
实现: 每个子Agent.think 包装成一个"调度工具"(schema+call)注册进主管的 core 循环。
      主管 LLM 决策"派给哪个子Agent"(当作工具调用), 子Agent 结果回填, 主管汇总。
"""
from typing import Dict, Callable
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    _SYSTEM = ("你是一个 CTF 安全专家团队的主管。把任务拆解后交给最合适的专业子Agent执行"
               "(把它们当作工具调用, 传入具体 task)。等各子Agent结果返回后, 汇总成最终报告。")

    def __init__(self, name: str = "Supervisor", sub_agents: Dict[str, BaseAgent] = None, **kwargs):
        kwargs.setdefault("system_prompt", self._SYSTEM)
        kwargs["auto_load"] = False          # 主管不重复加载通用工具, 由子Agent代劳
        super().__init__(name=name, **kwargs)
        self.sub_agents = sub_agents or {}
        self._register_sub_agents()

    def _register_sub_agents(self):
        for an, sub in self.sub_agents.items():
            desc = getattr(sub, "description", "") or f"专业能力: {an}"
            schema = {"type": "function",
                      "function": {"name": an, "description": desc,
                                   "parameters": {"type": "object",
                                                  "properties": {"task": {"type": "string",
                                                                          "description": f"交给 {an} 的具体任务"}},
                                                  "required": ["task"]}}}
            # 与 attach_to_agent 一致: 填 core.tools(schema) + tool_functions(执行)
            self.core.tools.append(schema)
            self.core.tool_functions[an] = self._make_dispatch(an)
        logger.info("Supervisor '%s' 注册子Agent工具 %d 个", self.name, len(self.sub_agents))

    def _make_dispatch(self, agent_name: str) -> Callable:
        def dispatch(task: str):
            return self.sub_agents[agent_name].think(task, context={"supervisor": self.name})
        return dispatch

    def _dispatch(self, agent_name: str, task: str) -> str:
        return self._make_dispatch(agent_name)(task)

    def think(self, task: str, context: Dict = None) -> str:
        return self.core.think(task, context)
