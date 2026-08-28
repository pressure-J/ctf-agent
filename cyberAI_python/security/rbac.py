"""
RBAC 权限控制 - 角色 -> 权限点集合; 支持通配 (chat.* / *)。
"""
from typing import List, Dict

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": ["*"],
    "user": ["chat.*", "tools.*", "knowledge.read", "workflow.run"],
    "guest": ["chat.create"],
}


class RBAC:
    def check(self, role: str, permission: str) -> bool:
        for p in ROLE_PERMISSIONS.get(role, []):
            if p == "*" or self._match(p, permission):
                return True
        return False

    def _match(self, pattern: str, permission: str) -> bool:
        if pattern.endswith(".*"):
            return permission.startswith(pattern[:-1])
        return pattern == permission
