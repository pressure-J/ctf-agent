import os
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# ===================== 配置 =====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MODEL_NAME = "deepseek-chat"

# 初始化 DeepSeek 客户端
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com",
)

def simple_agent(task: str) -> str:  # 修复了参数缺失问题
    # 工具定义（OpenAI / DeepSeek 格式）
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "执行数学计算",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "数学表达式，例如'2+2'或'10*5'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    ]

    # 工具执行函数
    def execute_tool(name: str, params: dict) -> str:
        if name == "calculate":
            expression = params.get("expression")
            try:
                result = eval(expression)
                return f"计算结果为: {result}"
            except Exception as e:
                return f"计算表达式出错: {str(e)}"
        return f"未知工具: {name}"

    # 初始化消息
    messages = [{"role": "user", "content": task}]

    # 最大迭代 30 轮
    for iteration in range(30):
        print(f"\n---第{iteration+1}轮对话---")

        # 调用 DeepSeek API
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tools,
            temperature=0.1,
        )

        choice = response.choices[0]
        finish_reason = choice.finish_reason
        assistant_msg = choice.message

        # 如果正常结束
        if finish_reason == "stop":
            return assistant_msg.content or "无返回内容"

        # 如果需要调用工具
        if finish_reason == "tool_calls" and assistant_msg.tool_calls:
            # 把工具调用加入对话历史
            messages.append(assistant_msg.to_dict())

            # 执行所有工具调用
            for tool_call in assistant_msg.tool_calls:
                func_name = tool_call.function.name
                import json
                func_args = json.loads(tool_call.function.arguments)

                print(f"调用工具: {func_name}({func_args})")
                tool_result = execute_tool(func_name, func_args)
                print(f"工具结果: {tool_result}")

                # 把工具结果返回给模型
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

    return "达到最大迭代次数"

if __name__ == "__main__":
    # 测试数学计算
    result = simple_agent("计算 (15 + 27) * 3 - 100/5 的结果")
    print(f"\n最终答案: {result}")
