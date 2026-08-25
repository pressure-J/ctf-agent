from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import requests

load_dotenv()

class BaseAgent:
    """基础Agent类，提供与OpenAI API的交互功能"""
    def __init__(self,name:str,system_prompt:str):
        self.name=name
        self.system_prompt=system_prompt
        self.client=OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.system_prompt=system_prompt
        self.tools=[]
        # ✅ 修复：统一变量名 tool_funcs
        self.tool_funcs = {}

    def register_tool(self, name, desc, func, params):
        """注册工具"""
        # ✅ 修复：使用正确的属性名 tool_funcs
        self.tool_funcs[name] = func
        self.tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": desc,
                "parameters": params
            }
        })

    def think(self,task:str,context:dict=None)->str:
        """
        Agent思考并执行
        
        参数:
            task: 任务描述
            context: 上下文（来自前一个Agent的结果）
        
        返回:
            执行结果
        """
        messages=[{"role":"system","content":self.system_prompt}]
        if context:
            messages.append({"role":"user","content": f"已知信息:\n{json.dumps(context, ensure_ascii=False, indent=2)}"})
        messages.append({"role":"user","content":task})
        print(f"\n{'='*50}")
        print(f"[{self.name}] 开始工作")
        print(f"{'='*50}")

        for i in range(10):
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                max_tokens=2000
            )
            msg=response.choices[0].message

            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    print(f"  调用工具: {name}({json.dumps(args, ensure_ascii=False)})")
                    # ✅ 修复：使用 self.tool_funcs
                    if name in self.tool_funcs:
                        try:
                            result = self.tool_funcs[name](**args)
                        except Exception as e:
                            result = f"工具调用失败: {str(e)}"
                    else:
                        result = f"未知工具: {name}"
                    print(f"  工具输出:\n{result}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result)
                    })
            else:
                content = msg.content.strip()
                print(f"  AI回复:\n{content}")
                return content
        return "未能完成任务"

class Pipeline:
    """Agent管道类，用于协调多个Agent的工作"""

    def __init__(self, agents:list):
        """
        参数:
            agents: Agent列表，按执行顺序排列
        """
        self.agents=agents

    def run(self, initial_task:str)->dict:
        """
        执行流水线
        
        参数:
            initial_task: 初始任务
        
        返回:
            所有Agent的结果
        """
        print(f"\n{'#'*60}")
        print(f"流水线启动")
        print(f"\n{'#'*60}")
       
        
        context = {"task": initial_task}
        results = {}

        for agent in self.agents:
            # 执行Agent
            result = agent.think(
                task=f"基于上下文完成任务: {context.get('task', initial_task)}",
                context=context
            ) 

             # 保存结果
            results[agent.name] = result
            context[agent.name] = result
            context["task"] = f"基于 {agent.name} 的结果继续"
        print(f"\n{'#'*60}")
        print(f"流水线完成")
        print(f"{'#'*60}")
        
        return results

# ========== 使用示例 ==========

if __name__ == "__main__":
    
    # Agent 1: 信息收集
    recon_agent = BaseAgent(
        name="侦察Agent",
        system_prompt="""你是一个信息收集专家。
你的任务是收集目标的基本信息。
使用send_request工具访问目标URL，分析响应。
返回结构化的信息收集结果。"""
    )
    
    recon_agent.register_tool(
        name="send_request",
        desc="发送HTTP请求",
        func=lambda url, method="GET": requests.request(method, url, timeout=10).text[:2000],
        params={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"}
            },
            "required": ["url"]
        }
    )
    
    # Agent 2: 漏洞分析
    vuln_agent = BaseAgent(
        name="漏洞Agent",
        system_prompt="""你是一个漏洞分析专家。
根据收集的信息，分析可能存在的漏洞。
重点关注Web漏洞：SQL注入、XSS、命令注入等。
给出漏洞利用建议。"""
    )
    
    # Agent 3: 漏洞利用
    exploit_agent = BaseAgent(
        name="利用Agent",
        system_prompt="""你是一个漏洞利用专家。
根据漏洞分析结果，尝试利用漏洞获取flag。
使用send_request工具测试payload。
flag格式：FLAG{...} 或 flag{...}"""
    )
    
    exploit_agent.register_tool(
        name="send_request",
        desc="发送HTTP请求",
        func=lambda url, method="GET": requests.request(method, url, timeout=10).text[:2000],
        params={
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"}
            },
            "required": ["url"]
        }
    )
    
    # 创建流水线
    pipeline = Pipeline([recon_agent, vuln_agent, exploit_agent])
    
    # 执行任务
    results = pipeline.run("http://testphp.vulnweb.com/")
    
    # 打印结果
    print("\n\n最终结果:")
    for agent_name, result in results.items():
        print(f"\n{agent_name}:")
        print(result[:500])
