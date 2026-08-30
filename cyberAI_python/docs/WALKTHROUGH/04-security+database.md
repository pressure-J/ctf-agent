# 04 · 底座:安全(登录/权限) + 数据(表/存储)

## 一、security/ — 一句话:谁会登录、他能干嘛
四件套(都在 security/):

**password.py**: 存密码。用 **bcrypt**(`$2b$`, 现代标准), 但对 Go 老格式 `sha256$` 也兼容校验 —— 配合"Go 的库我们能读"。
```python
def hash_password(pw) -> str     # bcrypt->"$2b$..."
def verify_password(pw, stored) -> bool  # bcrypt 验; 若以 sha256$ 开头则走老格式校验
```
**为什么**: 对齐 Go 的密码哈希; 只哈希(加盐), 绝不存明文。

**token.py**: 用户登录后给一个 **JWT**(`header.payload.signature`, JSON Web Token)。
里面装 `sub`(用户id) + `username/role` + 过期时间, 用 secret 签名。
之后客户端每次请求带 `Authorization: Bearer <token>`, 服务端验签名即可认人, 不用存会话(无状态)。

**auth.py**: `register`(注册)、`authenticate`(登录, 查库比对密码)、`create_access_token`(发JWT)、
`verify_token`(验JWT返回 {sub,username,role})、`bootstrap_admin`(首次启动建一个 admin 账号)、`revoke_token`.

**rbac.py**(关键差异化): **基于角色的细粒度权限** —— 不是"管理员/普通"两种, 而是
`module:action`(如 `tool:execute`、`user:delete`)。每个用户挂一个 role, role 映射一组权限点,
`can(user, "tool:execute")` 查表裁决。**为什么**: Go 版是 70 个 module:action 粒度,
我们做了其中 22 个(把安全工具执行/审计/用户管理等拆细), 比"一刀切管理员"精细得多。

**Web 层怎么用**: `web/routers/chat.py` 里 `Depends(security)` 掐住每个请求 →
`auth_manager.verify_token(token)` 认人 → 需要权限的再 `rbac.can(...)`。
(顺带: 前端登录返回的 token 存 localStorage, 之后都带它。)

## 二、database/ — 一句话:数据都落在一张 SQLite
**models.py**: 用 SQLAlchemy(ORM) 定义 **7 张表**:
`User` / `Conversation` / `Message` / `AuditLog` / `ToolExecution` / `Agent` / `Workflow`, 每张是一个 Python 类 + 字段, 建表自动生成。

**db.py**: `Database` 类封装所有数据操作 —— 造会话 `create_conversation`、
存消息 `save_message`、查用户 `get_user_with_password`(登录专用)、
统计 `count_conversations` 等。全部是对 models 的操作。

`Database(base_dir)` 默认把库建到 `data/cyberstrike.db`(gitignore 掉了, 数据不commit)。
**为什么用 SQLite(单文件)**: 轻量、零部署、够这个平台用; Go 版也用 SQLite(只是一个拆成3个库)。
**为什么有 `get_user_with_password`**: 把"读用户+校验密码"做成一个整体, 认证只在 auth.py 一处调它。

## 三、底座→上层怎么传数据
```
HTTP请求 → routers/chat.py → auth_manager.verify_token(认人)
                              └─> database.save_message(会话/消息入库)
                              └─> get_or_create_agent(...) → core.agent.Agent → think()
```
所有模块通过 `web/deps.py` 拿到**同一个** database/auth_manager/tool_registry 实例(全局单例),
保证"登录用的用户表"和"对话存的消息表"是同一个库。
