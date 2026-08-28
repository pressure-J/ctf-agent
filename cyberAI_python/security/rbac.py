"""
RBAC - 对齐 Go 版: 细粒度 module:action 权限点 + 角色->权限集合。
PermissionCatalog 是平台权限点清单(继承 Go 的命名风格); ROLE_PERMISSIONS 定义三种平台角色。
"""
from typing import List, Dict

PermissionCatalog: List[str] = [
    "auth:self", "dashboard:read",
    "chat:read", "chat:write", "chat:delete",
    "tools:read", "tools:execute",
    "agent:execute", "workflow:execute",
    "knowledge:read", "knowledge:write", "knowledge:delete",
    "asset:read", "project:read", "audit:read", "config:read",
    "monitor:read", "tasks:read", "rbac:read",
    "files:read", "files:write", "notification:read",
]

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "admin": ["*"],
    "user": ["auth:self", "dashboard:read",
             "chat:read", "chat:write",
             "tools:read", "tools:execute",
             "agent:execute", "workflow:execute",
             "knowledge:read", "files:read", "files:write"],
    "guest": ["auth:self", "chat:read", "knowledge:read"],
}


class RBAC:
    def __init__(self, catalog: List[str] = None):
        self.catalog = catalog or PermissionCatalog

    def check(self, role: str, permission: str) -> bool:
        for p in ROLE_PERMISSIONS.get(role, []):
            if p == "*" or p == permission:
                return True
        return False

    def check_many(self, role: str, permissions: List[str]) -> Dict[str, bool]:
        return {p: self.check(role, p) for p in permissions}
