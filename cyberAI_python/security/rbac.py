"""
RBAC 权限控制
"""
from typing import List, Dict
import logging
logger = logging.getLogger(__name__)

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": ["*"],
    "user": ["chat.*", "tools.*", "knowledge.read", "workflow.run"],
    "guest": ["chat.create"],
}

class RBAC:
    def check(self, role: str, permission: str) -> bool:
        raise NotImplementedError

    def require(self, permission: str):
        raise NotImplementedError
