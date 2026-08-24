# ctf_agent.py
# 最终终极版：工具输出发现FLAG立即结束
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import subprocess
import requests
import base64
import re

load_dotenv()

class CTFAgent:
    """能解CTF题目的AI Agent"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.tools = []
        self.tool_funcs = {}
        self._setup_tools()
    
    def _setup_tools(self):
        tools_config = [
            {
                "name": "send_request",
                "desc": "发送HTTP请求",
                "func": self._send_request,
                "params": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"},
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "execute_command",
                "desc": "执行系统命令",
                "func": self._execute_command,
                "params": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    },
                    "required": ["command"]
                }
            }
        ]
        
        for tool in tools_config:
            self.tool_funcs[tool["name"]] = tool["func"]
            self.tools.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["desc"],
                    "parameters": tool["params"]
                }
            })
    
    def _send_request(self, url, method="GET", data=None):
        try:
            r = requests.request(method, url, timeout=10, verify=False)
            return f"Status: {r.status_code}\nContent:\n{r.text[:3000]}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _execute_command(self, command):
        try:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return r.stdout + r.stderr
        except Exception as e:
            return f"Error: {str(e)}"

    def _has_flag(self, s):
        return re.search(r'flag\{.*?\}|NSSCTF\{.*?\}|ctf\{.*?\}', s, re.I) is not None
    
    def solve(self, task: str) -> str:
        messages = [
            {"role": "system", "content": """你是专业CTF选手。
只要得到flag，立刻停止，输出flag。
必须调用工具获取结果。"""},
            {"role": "user", "content": task}
        ]
        
        print(f"\n{'='*60}")
        print(f"🎯 CTF Agent 开始解题")
        print(f"{'='*60}")
        
        for i in range(50):
            print(f"\n📝 第{i+1}轮...")
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1500
            )
            
            msg = response.choices[0].message
            
            if msg.tool_calls:
                messages.append(msg)
                for tc in msg.tool_calls:
                    name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    
                    print(f"  🔧 调用: {name}")
                    
                    result = self.tool_funcs[name](**args)
                    
                    # =============== 核心修复：工具输出有flag直接结束 ===============
                    if self._has_flag(result):
                        print("\n🎉🎉🎉 成功拿到FLAG！！！")
                        print("="*60)
                        print(result)
                        print("="*60)
                        return result
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(result)[:2000]
                    })
            else:
                content = msg.content
                if self._has_flag(content):
                    print("\n🎉🎉🎉 成功拿到FLAG！")
                    print(content)
                    return content
                messages.append({"role": "assistant", "content": content})
        
        return "❌ 未找到flag"

if __name__ == "__main__":
    agent = CTFAgent()
    target_url = input("请输入CTF目标网址：").strip()
    task = f"目标网址：{target_url}，找到flag"
    result = agent.solve(task)
