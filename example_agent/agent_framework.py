from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import subprocess
import requests  # 补上缺失的导入

load_dotenv()

class CTFagent:
    def __init__(self):  # 修复：__init__ 必须双下划线！！！
        self.client=OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.tools=[]

        self.tools_functions = {}  # 修复：改成字典，方便映射工具名
        self.system_prompt="你是一个专业的CTF（Capture The Flag）安全竞赛选手。你的任务是帮助用户解决CTF题目，找到flag。工作流程：1. 分析题目描述，理解题目类型2. 选择合适的工具进行测试3. 分析工具输出，寻找线索4. 不断尝试，直到找到flag。Flag格式通常是：FLAG{...} 或 flag{...} 或 CTF{...}。重要原则：- 先信息收集，再深入测试- 每次工具调用后都要分析结果- 如果一个方法失败，尝试其他方法- 保持耐心，CTF需要反复尝试"

        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """注册内置工具"""
        self.register_tool(
            name="execute_command",
            description="执行系统命令",
            func=self.execute_command,
            parameters={
                "type":"object",
                "properties":{
                    "command":{
                        "type":"string",
                        "description":"要执行的系统命令，如nmap -sV 192.168.1.100"
                    }
                },
                "required":["command"]
            }
        )
        self.register_tool(
            name="send_request",
            description="发送HTTP请求",
            func=self.send_request,
            parameters={
                "type":"object",
                "properties":{
                    "url":{
                        "type":"string",
                        "description":"要发送请求的URL，如http://example.com"
                    },
                    "method":{
                        "type":"string",
                        "description":"HTTP方法，如GET、POST等"
                    },
                    "data":{
                        "type":"string",
                        "description":"HTTP请求体数据"
                    }
                },
                "required":["url"]
            }
        )

        self.register_tool(
            name="read_file",
            description="读取文件内容",
            func=self.read_file,
            parameters={
                "type":"object",
                "properties":{
                    "path":{
                        "type":"string",
                        "description":"要读取的文件路径，如/var/log/syslog"
                    }
                },
                "required":["path"]
            }
        )

    def register_tool(self, name:str, description:str, func:callable, parameters:dict):
        """注册工具"""
        # 保存工具函数（字典映射）
        self.tools_functions[name] = func
        self.tools.append({
            "type":"function",
            "function":{
                "name":name,
                "description":description,
                "parameters":parameters
            }
        })
        print(f"[+] 注册工具: {name}")

    def execute_command(self, command: str) -> str:  # 修复：函数名统一
        try:
            result=subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            output=result.stdout
            if result.stderr:
                output+=f"\n[错误]: {result.stderr}"
            return output if output else "命令执行完成，但没有输出。"
        except subprocess.TimeoutExpired:
            return "命令执行超时。"
        except Exception as e:
            return f"命令执行错误: {e}"

    def send_request(self, url: str, method: str = "GET", data: str = None) -> str:  # 修复：函数名统一
        try:
            if method == "GET":
                response = requests.get(url, timeout=10, verify=False)
            elif method == "POST":
                response = requests.post(url, json=json.loads(data) if data else None, timeout=10, verify=False)
            else:
                return f"不支持的HTTP方法: {method}"
            return f"HTTP响应状态码: {response.status_code}\n响应内容:\n{response.text}"
        except Exception as e:
            return f"HTTP请求错误: {e}"

    def read_file(self, path: str) -> str:  # 新增：补上缺失的函数
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"读取文件失败: {str(e)}"

    def solve(self,task:str)->str:
        messages=[{"role":"system","content":self.system_prompt},{"role":"user","content":task}]
        print(f"\n{'='*60}")
        print(f"CTFagent开始解题:")
        print(f"{'='*60}")
        print(f"\n题目描述: {task}\n")

        for iteration in range(30):
            print(f"\n--- 第{iteration + 1}轮 ---")

            response=self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",  # 修复：补上逗号
                max_tokens=2048
            )

            assistant_message=response.choices[0].message

            if assistant_message.tool_calls:
                messages.append(assistant_message)
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    print(f"  调用工具: {function_name}({arguments})")

                    # 修复：正确调用工具
                    if function_name in self.tools_functions:
                        result = self.tools_functions[function_name](**arguments)
                    else:
                        result = f"未知工具: {function_name}"

                    if len(result) > 2048:
                        result = result[:2048] + "... [输出过长，已截断]"

                    print(f"  工具输出:\n{result}")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result
                    })

            else:
                print(f"  AI回复: {assistant_message.content}")
                return assistant_message.content
        return "解题失败"

if __name__ == "__main__":
    
    agent = CTFagent()
    
    # 示例题目1：Web SQL注入
    task1 = """
    题目：Login Bypass
    难度：Easy
    描述：http://target.ctf.com/login.php
    提示：这个登录页面可能存在SQL注入漏洞
    """
    
    # 运行Agent
    result = agent.solve(task1) 
