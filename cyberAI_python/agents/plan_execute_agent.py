"""Plan-Execute 模式 - 先规划后执行(串行步骤)。
复用 Supervisor 的子Agent-as-tool 机制, 只换引导提示词让主管先规划再按步骤派发。
对齐 Go multiagent 的 plan_execute(planner ↔ executor)。
"""
from agents.supervisor_agent import SupervisorAgent


class PlanExecuteAgent(SupervisorAgent):
    _SYSTEM = ("你是一个 Plan-Execute 规划执行 Agent。先给出清晰的执行计划(步骤序号), "
               "然后按步骤逐个调用专业子Agent/工具执行, 每一步参考上一步结果, 最后汇总汇报。")
