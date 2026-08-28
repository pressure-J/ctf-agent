"""
工具注册表 - 完整版
管理100+工具的注册、发现和执行
"""

import yaml
import json
from typing import Dict, Any, Callable, List, Optional
from pathlib import Path
import importlib
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    工具注册表 - 完整版
    
    与Go版CyberStrikeAI的MCP服务器功能对齐
    """
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.tool_configs: Dict[str, Dict] = {}
        self.categories: Dict[str, List[str]] = {}
        
        logger.info("工具注册表初始化完成")
    
    def register(
        self,
        name: str,
        func: Callable,
        schema: Dict[str, Any],
        category: str = "general",
        enabled: bool = True
    ):
        """
        注册工具 - 完整版
        
        支持分类、启用/禁用、配置
        """
        
        self.tools[name] = {
            "function": func,
            "schema": schema,
            "category": category,
            "enabled": enabled,
            "config": {}
        }
        
        # 添加到分类
        if category not in self.categories:
            self.categories[category] = []
        self.categories[category].append(name)
        
        logger.debug(f"注册工具: {name} (category={category})")
    
    def register_from_yaml(self, yaml_path: str):
        """从YAML配置文件注册工具"""
        
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        tool_name = config.get("name", Path(yaml_path).stem)
        
        # 保存配置
        self.tool_configs[tool_name] = config
        
        # 动态导入工具函数
        if "module" in config and "function" in config:
            module = importlib.import_module(config["module"])
            func = getattr(module, config["function"])
        else:
            # 使用默认的命令执行器
            func = self._create_command_executor(config)
        
        # 注册工具
        self.register(
            name=tool_name,
            func=func,
            schema=self._build_schema(config),
            category=config.get("category", "general"),
            enabled=config.get("enabled", True)
        )
        return tool_name
    
    def _create_command_executor(self, config: Dict) -> Callable:
        """创建命令执行器(支持完整协议: positional/flag/template + position/default)。
        与 Go 版 YAML 协议对齐:
          - positional+position: 按 position 排序的位置参数
          - format=flag:         append flag + 值 (bool 型只加 flag: -O)
          - format=template:     template.replace("{value}", 值) 如 "-T{value}" -> "-T4"
        """
        import subprocess
        params = config.get("parameters", []) or []

        def executor(**kwargs):
            cmd = [config.get("command", "")]
            cmd += list(config.get("args", []) or [])

            # ① positional: 按 position 排序(缺省排最后)
            pos = [p for p in params
                   if p.get("format") == "positional" or p.get("position") is not None]
            pos.sort(key=lambda p: p.get("position", 99))
            for p in pos:
                v = kwargs.get(p["name"], p.get("default"))
                if v is None or v == "":
                    continue
                cmd.append(str(v))

            # ② flag / template / 其他
            for p in params:
                if p in pos:
                    continue
                v = kwargs.get(p["name"], p.get("default"))
                if v is None or v == "":
                    continue
                f = p.get("format")
                if f == "flag":
                    if p.get("type") == "bool":
                        if str(v).lower() in ("true", "1", "yes"):
                            cmd.append(p.get("flag", ""))
                    else:
                        cmd.append(p.get("flag", ""))
                        cmd.append(str(v))
                elif f == "template":
                    cmd.append(p.get("template", "{value}").replace("{value}", str(v)))
                else:
                    cmd.append(str(v))

            try:
                result = subprocess.run(cmd, capture_output=True, text=True,
                                        timeout=config.get("timeout", 60))
                return result.stdout if result.returncode == 0 else result.stderr
            except Exception as e:
                return f"命令执行失败: {e}"

        return executor
    
    def _build_schema(self, config: Dict) -> Dict:
        """从配置构建schema"""
        
        parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        for param in config.get("parameters", []):
            parameters["properties"][param["name"]] = {
                "type": param.get("type", "string"),
                "description": param.get("description", "")
            }
            
            if param.get("required"):
                parameters["required"].append(param["name"])
        
        return {
            "type": "function",
            "function": {
                "name": config.get("name", ""),
                "description": config.get("description", ""),
                "parameters": parameters
            }
        }
    
    def execute(self, name: str, args: Dict[str, Any]) -> str:
        """执行工具"""
        
        if name not in self.tools:
            return f"错误: 工具 '{name}' 不存在"
        
        tool = self.tools[name]
        
        if not tool["enabled"]:
            return f"错误: 工具 '{name}' 已禁用"
        
        try:
            result = tool["function"](**args)
            return str(result)
        except Exception as e:
            return f"错误: {str(e)}"
    
    def get_schemas(self, enabled_only: bool = True) -> List[Dict]:
        """获取所有工具的schema"""
        
        schemas = []
        for name, tool in self.tools.items():
            if enabled_only and not tool["enabled"]:
                continue
            schemas.append(tool["schema"])
        
        return schemas
    
    def list_tools(self, category: str = None, enabled_only: bool = True) -> List[str]:
        """列出工具"""
        
        if category:
            tools = self.categories.get(category, [])
        else:
            tools = list(self.tools.keys())
        
        if enabled_only:
            tools = [t for t in tools if self.tools[t]["enabled"]]
        
        return tools
    
    def disable_tool(self, name: str):
        """禁用工具"""
        if name in self.tools:
            self.tools[name]["enabled"] = False
    
    def enable_tool(self, name: str):
        """启用工具"""
        if name in self.tools:
            self.tools[name]["enabled"] = True
    
    def get_tool_info(self, name: str) -> Optional[Dict]:
        """获取工具信息"""
        return self.tools.get(name)
    
    def reload_tools(self, yaml_dir: str):
        """重新加载所有工具"""
        
        self.tools.clear()
        self.tool_configs.clear()
        self.categories.clear()
        
        yaml_files = Path(yaml_dir).glob("*.yaml")
        
        for yaml_file in yaml_files:
            try:
                self.register_from_yaml(str(yaml_file))
            except Exception as e:
                logger.error(f"加载工具配置失败 {yaml_file}: {e}")
