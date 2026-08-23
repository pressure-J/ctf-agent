# agent_with_registry.py
import os
import requests
from tools.registry import ToolRegistry


registry = ToolRegistry()


# 注册多个工具
def nmap_scan(target: str, ports: str = "1-1000") -> str:
    """执行Nmap端口扫描"""
    import subprocess
    cmd = ["nmap", "-sV", "-p", ports, target]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    return result.stdout if result.returncode == 0 else result.stderr


registry.register("nmap_scan", nmap_scan, {
    "name": "nmap_scan",
    "description": "网络端口扫描，检测开放端口和服务",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "目标IP或域名"},
            "ports": {"type": "string", "description": "端口范围，如 '80,443' 或 '1-1000'", "default": "1-1000"}
        },
        "required": ["target"]
    }
})


def read_file(path: str) -> str:
    """读取文件内容"""
    try:
        with open(path, 'r') as f:
            return f.read()[:5000]  # 限制5000字符
    except Exception as e:
        return f"读取文件失败: {str(e)}"


registry.register("read_file", read_file, {
    "name": "read_file",
    "description": "读取本地文件内容",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"}
        },
        "required": ["path"]
    }
})


# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("sk-a4de74114e254df38830abbd95309ceb")
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


def run_agent(task: str) -> str:
    messages = [{"role": "user", "content": task}]
    
    for _ in range(30):
        # 构造 DeepSeek API 请求
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "tools": registry.get_schemas(),
            "tool_choice": "auto",
            "max_tokens": 4096,
            "temperature": 0.1
        }


        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }


        # 发送请求
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        res_data = response.json()
        choice = res_data["choices"][0]
        stop_reason = choice["finish_reason"]
        assistant_msg = choice["message"]


        # 结束条件：模型不再调用工具
        if stop_reason == "stop" or not assistant_msg.get("tool_calls"):
            return assistant_msg["content"]
        
        # 保存助手消息
        messages.append(assistant_msg)
        
        # 执行所有工具调用
        tool_results = []
        for tool_call in assistant_msg["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = eval(tool_call["function"]["arguments"])  # 安全解析参数
            tool_id = tool_call["id"]
            
            # 执行工具
            result = registry.execute(tool_name, tool_args)
            
            # 构造工具结果
            tool_results.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": result
            })
        
        # 把结果返回给模型
        messages.extend(tool_results)
    
    return "达到最大迭代次数"




if __name__ == "__main__":
    # 先设置环境变量：export DEEPSEEK_API_KEY="你的密钥"
    result = run_agent("扫描 192.168.1.1 的80和443端口")
    print(result)

