"""Agent模型"""
from pydantic import BaseModel
from typing import Dict

class AgentCreate(BaseModel):
    name: str
    description: str = ""
    mode: str = "single"
    system_prompt: str = None
    model: str = "deepseek-chat"
    config: Dict = {}
