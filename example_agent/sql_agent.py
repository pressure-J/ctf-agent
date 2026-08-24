from openai import OpenAI
from dotenv import load_dotenv
import os
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

def solve_sqli_challenge():
    """
    CTF题目：SQL Injection
    URL: http://node7.anna.nssctf.cn:25440/
    提示：登录可能存在SQL注入
    """
    
    # 题目描述
    task = """
    CTF题目：SQL Injection 100分
    URL: http://node7.anna.nssctf.cn:25440/
    描述：这是一个简单sql题目，请找到SQL注入漏洞并提取flag。
    Flag格式：flag{...}
    
    提示：
    1. 先测试用户名密码注入
    2. 如果登录成功，检查URL参数
    3. 尝试使用sqlmap工具
    """
    
    messages = [
        {"role": "system", "content": """你是一个CTF选手，擅长Web安全。
请帮我解决这个SQL注入题目。

可用工具：
1. send_request(url, method, data) - 发送HTTP请求
2. execute_command(command) - 执行系统命令（如sqlmap）

步骤：
1. 先访问登录页面，分析表单
2. 测试SQL注入
3. 提取数据找flag"""},
        {"role": "user", "content": task}
    ]
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "send_request",
                "description": "发送HTTP请求",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "method": {"type": "string", "enum": ["GET", "POST"]},
                        "data": {"type": "string"}
                    },
                    "required": ["url"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_command",
                "description": "执行系统命令",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    },
                    "required": ["command"]
                }
            }
        }
    ]
    
    # 运行Agent
    for i in range(15):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        
        if msg.tool_calls:
            messages.append(msg)
            
            for tc in msg.tool_calls:
                name = tc.function.name
                args = __import__('json').loads(tc.function.arguments)
                
                print(f"\n[调用] {name}({args})")
                
                if name == "send_request":
                    try:
                        r = requests.request(
                            args.get("method", "GET"),
                            args["url"],
                            data=args.get("data"),
                            timeout=10
                        )
                        result = f"状态码:{r.status_code}\n{r.text[:1500]}"
                    except Exception as e:
                        result = f"请求失败: {e}"
                
                elif name == "execute_command":
                    import subprocess
                    r = subprocess.run(args["command"], shell=True, capture_output=True, text=True, timeout=60)
                    result = r.stdout[:1500]
                
                print(f"[结果] {result[:200]}...")
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            print(f"\n{'='*50}")
            print(f"最终答案:\n{msg.content}")
            return msg.content
    
    return "未找到flag"

if __name__ == "__main__":
    solve_sqli_challenge()
