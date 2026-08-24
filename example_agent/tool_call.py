from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()	

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL")
)

def calculate(expression:str)->str:
    try:
        result=eval(expression)
        return f"计算结果是：{expression}={result}"
    except Exception as e:
        return f"计算错误：{e}"


tools=[
    {
        "type":"function",
        "function":{
            "name":"calculate",
            "description":"用于计算数学表达式",
            "parameters":{
                "type":"object",
                "properties":{
                    "expression":{
                        "type":"string",
                        "description":"要计算的数学表达式"
                    }
                },
                "required":["expression"]
            }
        }
    }
]


def chat_with_tools(task:str)->str:
    messages=[{"role":"user","content":task}]
    print(f"\n{'='*50}")
    print(f"用户: {task}")
    print(f"{'='*50}")
    for iteration in range(10):
        print(f"\n--- 第{iteration + 1}轮 ---")
        
        # 调用AI
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,           # 告诉AI有哪些工具
            tool_choice="auto"    # 让AI自己决定是否调用工具
        )
        
        # 获取AI的回复
        assistant_message = response.choices[0].message
        
        # 检查AI是否要调用工具
        if assistant_message.tool_calls:
            # AI要调用工具！
            print(f"AI决定调用工具...")
            
            # 把AI的回复加入对话历史
            messages.append(assistant_message)
            
            # 处理每个工具调用
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name        # 工具名称
                arguments = json.loads(tool_call.function.arguments)  # 参数
                
                print(f"  调用: {function_name}({arguments})")
                
                # 执行工具
                if function_name == "calculate":
                    result = calculate(arguments["expression"])
                else:
                    result = f"未知工具: {function_name}"
                
                print(f"  结果: {result}")
                
                # 把工具结果返回给AI
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        else:
            # AI没有调用工具，直接回复
            print(f"\nAI回复:")
            print(assistant_message.content)
            return assistant_message.content
    
    return "达到最大循环次数"

# ========== 第3步：运行 ==========

if __name__ == "__main__":
    # 测试1：简单计算
    chat_with_tools("帮我算一下 (15 + 27) * 3 - 100/5 等于多少")
    
    print("\n" + "="*50)
    
    # 测试2：需要多步计算
    chat_with_tools("先算 123 * 456，然后把结果除以7")
