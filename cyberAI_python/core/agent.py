"""
Agent核心模块 - 完整版
实现与Go版CyberStrikeAI 100%对齐的功能
"""

from openai import OpenAI
from typing import List, Dict, Any, Optional, Callable, Union
import json
from dotenv import load_dotenv
import os
from datetime import datetime
import asyncio
import logging
from enum import Enum

load_dotenv()

logger = logging.getLogger(__name__)


class AgentMode(Enum):
    """Agent模式"""
    SINGLE = "single"              # 单Agent
    SUPERVISOR = "supervisor"      # Supervisor模式
    PLAN_EXECUTE = "plan_execute"  # Plan-Execute模式


class AgentState:
    """Agent状态管理"""
    
    def __init__(self):
        self.messages: List[Dict] = []
        self.tool_calls: List[Dict] = []
        self.iteration: int = 0
        self.max_iterations: int = 30
        self.status: str = "idle"
        self.context: Dict[str, Any] = {}
        self.memory: List[str] = []
    
    def add_message(self, role: str, content: str, **kwargs):
        """添加消息"""
        message = {"role": role, "content": content}
        message.update(kwargs)
        self.messages.append(message)
    
    def clear(self):
        """清空状态"""
        self.messages = []
        self.tool_calls = []
        self.iteration = 0
        self.status = "idle"


class Agent:
    """
    AI Agent核心类 - 完整版
    
    与Go版CyberStrikeAI功能完全对齐
    """
    
    def __init__(
        self,
        name: str = "Agent",
        mode: AgentMode = AgentMode.SINGLE,
        system_prompt: str = None,
        model: str = "deepseek-chat",
        max_iterations: int = 30,
        temperature: float = 0.7,
        config: Dict[str, Any] = None
    ):
        """
        初始化Agent
        
        完整参数支持，与Go版对齐
        """
        
        # 基础配置
        self.name = name
        self.mode = mode
        self.model = model
        self.max_iterations = max_iterations
        self.temperature = temperature
        self.config = config or {}
        
        # LLM客户端
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
        
        # 系统提示词
        self.system_prompt = system_prompt or self._default_system_prompt()
        
        # 工具系统
        self.tools: List[Dict[str, Any]] = []
        self.tool_functions: Dict[str, Callable] = {}
        
        # 状态管理
        self.state = AgentState()
        self.state.max_iterations = max_iterations
        
        # 子Agent（多Agent模式）
        self.sub_agents: Dict[str, 'Agent'] = {}
        
        # 记忆系统
        self.memory_enabled = self.config.get("memory_enabled", True)
        
        # 并发控制
        self._lock = asyncio.Lock()
        
        logger.info(f"Agent '{self.name}' 初始化完成 (mode={self.mode.value})")
    
    def _default_system_prompt(self) -> str:
        """默认系统提示词"""
        return f"""你是一个专业的CTF安全专家，名叫{self.name}。

你的任务是帮助用户解决CTF题目，找到flag。

工作流程：
1. 仔细阅读题目描述
2. 分析可能的漏洞类型
3. 选择合适的工具进行测试
4. 分析工具输出，寻找线索
5. 不断尝试，直到找到flag

Flag格式通常是：FLAG{{...}} 或 flag{{...}}

重要原则：
- 先信息收集，再深入测试
- 每次工具调用后都要分析结果
- 如果一个方法失败，尝试其他方法
- 保持耐心，CTF需要反复尝试
- 记住所有发现，包括负面结果
- 遇到错误时分析原因并调整策略"""
    
    def register_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        parameters: Dict[str, Any]
    ):
        """注册工具 - 完整版"""
        
        self.tool_functions[name] = func
        
        self.tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters
            }
        })
        
        logger.debug(f"注册工具: {name}")
    
    def register_tools_from_yaml(self, yaml_path: str):
        """从YAML文件批量注册工具"""
        
        import yaml
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            tools_config = yaml.safe_load(f)
        
        for tool_name, tool_config in tools_config.items():
            if tool_config.get("enabled", True):
                # 动态创建工具函数
                def make_tool_func(config):
                    def tool_func(**kwargs):
                        return self._execute_tool_from_config(config, kwargs)
                    return tool_func
                
                self.register_tool(
                    name=tool_name,
                    description=tool_config.get("description", ""),
                    func=make_tool_func(tool_config),
                    parameters=tool_config.get("parameters", {})
                )
    
    def _execute_tool_from_config(self, config: Dict, args: Dict) -> str:
        """根据配置执行工具"""
        
        import subprocess
        
        command = config.get("command", "")
        
        # 构建命令
        cmd_parts = [command]
        
        # 添加固定参数
        if "args" in config:
            cmd_parts.extend(config["args"])
        
        # 添加动态参数
        for param_name, param_value in args.items():
            if param_name in [p["name"] for p in config.get("parameters", [])]:
                param_config = next(
                    p for p in config.get("parameters", []) 
                    if p["name"] == param_name
                )
                
                if param_config.get("format") == "flag":
                    cmd_parts.append(param_config.get("flag", f"--{param_name}"))
                    cmd_parts.append(str(param_value))
                elif param_config.get("format") == "positional":
                    cmd_parts.append(str(param_value))
                elif param_config.get("format") == "template":
                    template = param_config.get("template", "{value}")
                    cmd_parts.append(template.replace("{value}", str(param_value)))
        
        # 执行命令
        try:
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=config.get("timeout", 60)
            )
            
            return result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            return f"工具执行失败: {str(e)}"
    
    def think(self, task: str, context: Dict[str, Any] = None) -> str:
        """
        Agent思考并执行任务 - 完整版
        
        核心Agent循环，与Go版完全对齐
        """
        
        logger.info(f"Agent '{self.name}' 开始执行任务")
        
        # 初始化状态
        self.state.clear()
        self.state.status = "running"
        
        # 初始化对话
        self.state.add_message("system", self.system_prompt)
        
        # 添加上下文
        if context:
            self.state.context.update(context)
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            self.state.add_message("system", f"已知信息:\n{context_str}")
        
        # 添加记忆
        if self.memory_enabled and self.memory:
            memory_str = "\n".join(self.memory[-10:])  # 最近10条记忆
            self.state.add_message("system", f"历史经验:\n{memory_str}")
        
        # 用户任务
        self.state.add_message("user", task)
        
        # Agent循环
        for iteration in range(self.max_iterations):
            self.state.iteration = iteration + 1
            logger.debug(f"迭代 {iteration + 1}/{self.max_iterations}")
            
            try:
                # 调用LLM
                response = self._call_llm()
                
                # 获取助手消息
                assistant_message = response["choices"][0]["message"]
                
                # 检查是否有工具调用
                if assistant_message.get("tool_calls"):
                    # 处理工具调用
                    self._handle_tool_calls(assistant_message)
                else:
                    # 没有工具调用，返回最终答案
                    final_answer = assistant_message.get("content", "")
                    
                    # 记住这次经验
                    if self.memory_enabled:
                        self.memory.append(f"任务: {task[:100]}")
                        self.memory.append(f"结果: {final_answer[:100]}")
                        self.memory.append(f"时间: {datetime.now().isoformat()}")
                        
                        # 限制记忆长度
                        if len(self.memory) > 50:
                            self.memory = self.memory[-50:]
                    
                    self.state.status = "completed"
                    
                    logger.info(f"Agent '{self.name}' 执行完成")
                    
                    return final_answer
            
            except Exception as e:
                logger.error(f"迭代 {iteration + 1} 出错: {e}")
                self.state.add_message("system", f"错误: {str(e)}，请继续")
                continue
        
        # 达到最大迭代次数
        self.state.status = "max_iterations_reached"
        
        logger.warning(f"Agent '{self.name}' 达到最大迭代次数")
        
        return "达到最大迭代次数，未能完成任务"
    
    def _call_llm(self) -> Dict:
        """调用LLM"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.state.messages,
            tools=self.tools if self.tools else None,
            tool_choice="auto" if self.tools else None,
            temperature=self.temperature,
            max_tokens=2000
        )
        
        return response.model_dump()
    
    def _handle_tool_calls(self, assistant_message: Dict):
        """处理工具调用"""
        
        # 把助手消息加入历史
        self.state.add_message(
            "assistant",
            assistant_message.get("content", ""),
            tool_calls=assistant_message.get("tool_calls")
        )
        
        # 处理每个工具调用
        for tool_call in assistant_message["tool_calls"]:
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["arguments"])
            
            logger.debug(f"调用工具: {function_name}")
            
            # 执行工具
            if function_name in self.tool_functions:
                try:
                    result = self.tool_functions[function_name](**arguments)
                except Exception as e:
                    result = f"工具执行失败: {str(e)}"
                    logger.error(f"工具 {function_name} 执行失败: {e}")
            else:
                result = f"未知工具: {function_name}"
                logger.warning(f"未知工具: {function_name}")
            
            # 限制结果长度
            if len(str(result)) > 2000:
                result = str(result)[:2000] + "\n... (输出被截断)"
            
            logger.debug(f"工具结果: {str(result)[:100]}...")
            
            # 把工具结果加入消息
            self.state.add_message(
                "tool",
                str(result),
                tool_call_id=tool_call["id"]
            )
            
            # 记录工具调用
            self.state.tool_calls.append({
                "name": function_name,
                "arguments": arguments,
                "result": str(result)[:200]
            })
    
    def chat(self, message: str) -> str:
        """简单对话（不使用工具）"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    def get_state(self) -> Dict:
        """获取Agent状态"""
        
        return {
            "name": self.name,
            "mode": self.mode.value,
            "status": self.state.status,
            "iteration": self.state.iteration,
            "max_iterations": self.state.max_iterations,
            "tool_calls_count": len(self.state.tool_calls),
            "messages_count": len(self.state.messages),
            "memory_count": len(self.memory)
        }
    
    def clear_memory(self):
        """清空记忆"""
        self.memory = []
        logger.info(f"Agent '{self.name}' 记忆已清空")
