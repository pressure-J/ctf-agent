# workflow.py
# 工作流引擎：定义和执行复杂任务流程

from enum import Enum
from typing import Dict
import json
import time

class NodeType(Enum):
    """节点类型"""
    AGENT = "agent"         # Agent节点
    CONDITION = "condition" # 条件分支
    PARALLEL = "parallel"   # 并行执行
    MERGE = "merge"         # 合并结果


# ======================
# 新增：模拟AI代理类（必须加）
# ======================
class BaseAgent:
    def __init__(self, name, role):
        self.name = name
        self.role = role
    
    def think(self, task, context=None):
        """模拟Agent思考执行任务"""
        time.sleep(0.5)  # 模拟执行耗时
        return f"【{self.name} - {self.role}】已完成：{task}"


class Node:
    """工作流节点"""
    
    def __init__(self, id: str, type: NodeType, config: dict):
        self.id = id
        self.type = type
        self.config = config
        self.next_nodes = []  # 下一个节点列表
    
    def connect(self, node, condition: str = None):
        """连接到下一个节点"""
        self.next_nodes.append({
            "node": node,
            "condition": condition
        })
    
    def execute(self, state: dict) -> str:
        """执行节点（根据类型分发）"""
        if self.type == NodeType.AGENT:
            return self._execute_agent(state)
        elif self.type == NodeType.CONDITION:
            return self._evaluate_condition(state)
        elif self.type == NodeType.PARALLEL:
            return self._execute_parallel(state)
        elif self.type == NodeType.MERGE:
            return self._merge_results(state)
    
    def _execute_agent(self, state: dict) -> str:
        """执行单个Agent"""
        agent = self.config["agent"]
        task = self.config.get("task", "完成任务")
        context = state.get("context", {})
        return agent.think(task, context)
    
    def _evaluate_condition(self, state: dict) -> str:
        """条件判断：返回 true / false"""
        condition = self.config["condition"]
        if eval(condition, {"state": state}):
            return "true"
        return "false"
    
    def _execute_parallel(self, state: dict) -> str:
        """多Agent并行执行"""
        import concurrent.futures
        agents = self.config["agents"]
        task = self.config.get("task", "完成任务")
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(agents)) as executor:
            futures = {
                executor.submit(agent.think, task): name
                for name, agent in agents.items()
            }
            for future in concurrent.futures.as_completed(futures):
                name = futures[future]
                results[name] = future.result()
        
        return json.dumps(results, ensure_ascii=False)
    
    def _merge_results(self, state: dict) -> str:
        """合并所有节点结果"""
        results = []
        for key, value in state.items():
            if key.startswith("result_"):
                results.append(f"### {key}\n{value}")
        return "\n\n".join(results)


class Workflow:
    """工作流总控制器"""
    
    def __init__(self, name: str):
        self.name = name
        self.nodes: Dict[str, Node] = {}  # 节点字典
        self.start_node: Node = None      # 开始节点
    
    def add_node(self, node: Node):
        """添加节点到工作流"""
        self.nodes[node.id] = node
    
    def set_start(self, node_id: str):
        """设置从哪个节点开始执行"""
        self.start_node = self.nodes[node_id]
    
    def execute(self, initial_state: dict = None) -> dict:
        """执行整个工作流（核心）"""
        print(f"\n{'#'*60}")
        print(f"工作流启动: {self.name}")
        print(f"{'#'*60}")
        
        state = initial_state or {}
        current_node = self.start_node
        
        # 循环执行节点
        while current_node:
            print(f"\n执行节点: {current_node.id}")
            
            # 1. 执行当前节点
            result = current_node.execute(state)
            
            # 2. 把结果存入全局状态
            state[f"result_{current_node.id}"] = result
            state["context"] = state.get("context", {})
            state["context"][current_node.id] = result
            
            print(f"节点完成: {current_node.id}")
            
            # 3. 寻找下一个节点
            current_node = self._next_node(current_node, state)
        
        print(f"\n{'#'*60}")
        print(f"工作流完成: {self.name}")
        print(f"{'#'*60}")
        
        return state
    
    def _next_node(self, node: Node, state: dict) -> Node:
        """根据条件自动选择下一个节点"""
        for next_config in node.next_nodes:
            condition = next_config.get("condition")
            
            # 无条件 → 直接走
            if condition is None:
                return next_config["node"]
            
            # 有条件 → 匹配节点执行结果
            if condition == state.get(f"result_{node.id}"):
                return next_config["node"]
        
        # 没有匹配的节点 → 工作流结束
        return None


# ========== 使用示例：CTF 自动化解题工作流 ==========
if __name__ == "__main__":
    
    # 1. 创建3个AI代理
    recon_agent = BaseAgent("侦察", "信息收集专家")
    vuln_agent = BaseAgent("漏洞", "漏洞分析专家")
    exploit_agent = BaseAgent("利用", "漏洞利用专家")
    
    # 2. 创建工作流节点
    recon_node = Node("recon", NodeType.AGENT, {
        "agent": recon_agent,
        "task": "收集目标信息"
    })
    
    check_node = Node("check", NodeType.CONDITION, {
        "condition": "len(state.get('result_recon', '')) > 100"
    })
    
    vuln_node = Node("vuln", NodeType.AGENT, {
        "agent": vuln_agent,
        "task": "分析漏洞"
    })
    
    exploit_node = Node("exploit", NodeType.AGENT, {
        "agent": exploit_agent,
        "task": "利用漏洞获取flag"
    })
    
    # 3. 连接节点 → 构建流程
    recon_node.connect(check_node)                  # 侦察完 → 进入判断
    check_node.connect(vuln_node, condition="true") # 判断为真 → 漏洞分析
    check_node.connect(None, condition="false")    # 判断为假 → 结束
    vuln_node.connect(exploit_node)                # 漏洞分析完 → 利用
    
    # 4. 创建工作流并添加所有节点
    workflow = Workflow("CTF解题")
    workflow.add_node(recon_node)
    workflow.add_node(check_node)
    workflow.add_node(vuln_node)
    workflow.add_node(exploit_node)
    workflow.set_start("recon")  # 设置起点
    
    # 5. 启动工作流
    final_state = workflow.execute({"target": "http://example.com"})
    
    # 6. 打印最终结果
    print("\n【工作流最终结果】")
    print(final_state)
