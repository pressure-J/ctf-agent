"""
加载 Go 版导入的角色 yaml -> BaseAgent。
角色 = {name, description, user_prompt, icon, enabled}; user_prompt 充当 system_prompt。
纯数据消费: yaml.safe_load, 与 Go 解耦。
"""
import yaml
from typing import List, Dict, Optional
from pathlib import Path
from agents.base_agent import BaseAgent
import logging
logger = logging.getLogger(__name__)

ROLES_DIR = Path(__file__).parent / "roles"


def load_roles() -> List[Dict]:
    """读 agents/roles/*.yaml, 返回角色配置列表(纯数据, Python 直接消费)"""
    roles = []
    for fp in sorted(ROLES_DIR.glob("*.yaml")):
        with open(fp, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        roles.append({
            "name": cfg.get("name", fp.stem),
            "description": cfg.get("description", ""),
            "user_prompt": cfg.get("user_prompt", ""),
            "icon": cfg.get("icon", ""),
            "enabled": cfg.get("enabled", True),
        })
    return roles


def get_role(name: str) -> Optional[Dict]:
    """按名字取角色"""
    for r in load_roles():
        if r["name"] == name:
            return r
    return None


def build_role_agent(name: str, tools: Optional[List[str]] = None,
                     model: str = "deepseek-chat") -> BaseAgent:
    """用角色配置建一个 BaseAgent(user_prompt 当 system_prompt), 可配工具白名单"""
    role = get_role(name)
    if not role:
        raise ValueError(f"角色不存在: {name}")
    return BaseAgent(name=name, system_prompt=role["user_prompt"],
                     tools=tools, model=model)
