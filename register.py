# tools/registry.py
from typing import Callable, Dict, Any
import json

class ToolRegistry:
    """工具注册表 - 管理所有可用工具"""
    
    def __init__(self):
        self.tools: Dict[str, dict] = {}
    
    def register(self, name: str, func: Callable, schema: dict):
        """
        注册工具
        
        Args:
            name: 工具名称
            func: 执行函数
            schema: 工具描述（OpenAI格式）
        """
        self.tools[name] = {
            "function": func,
            "schema": schema
        }
        print(f"✓ 注册工具: {name}")
    
    def execute(self, name: str, params: dict) -> str:
        """执行工具"""
        if name not in self.tools:
            return f"错误: 工具 '{name}' 不存在"
        
        try:
            result = self.tools[name]["function"](**params)
            return str(result)
        except Exception as e:
            return f"错误: {str(e)}"
    
    def get_schemas(self) -> list:
        """获取所有工具的schema（发给LLM）"""
        return [t["schema"] for t in self.tools.values()]
    
    def list_tools(self) -> list:
        """列出所有工具"""
        return list(self.tools.keys())


# 使用示例
registry = ToolRegistry()

# 注册calculate工具
def calculate(expression: str) -> str:
    """执行数学计算"""
    result = eval(expression)  # 注意：生产环境用ast.literal_eval
    return f"结果: {result}"

registry.register(
    name="calculate",
    func=calculate,
    schema={
        "name": "calculate",
        "description": "执行数学计算，支持加减乘除和括号",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "数学表达式，如 '(10 + 5) * 2'"
                }
            },
            "required": ["expression"]
        }
    }
)
