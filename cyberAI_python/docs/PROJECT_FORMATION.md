# CyberStrikeAI Python — 项目形成史与设计说明

> 你问"如今这个项目是怎么形成的、每个文件代码怎么样、为什么这样写、是什么架构类型"。本文完整回答。

## 0. 这是什么架构
**工具调用型(ReAct)单 Agent 运行时 + 注册表驱动工具 + SQLite 底座 + FastAPI 交付壳**。
对位开源：≈ LangChain AgentExecutor / 轻量版 eino 单 Agent。核心是"LLM 看历史+工具 → 决策调工具 → 执行回填 → 再决策"的 ReAct 循环，外层 Web 用依赖注入(deps)把能力交付成 HTTP。

## 1. 形成阶段（按 git 顺序）

### 阶段0 框架：从方案文档搭骨架
读 `PYTHON_FULL_REWRITE.md`(Go→Python 重构图) → 建 156 文件目录树 + 全部 `__init__.py`；5 个有完整代码的**种子文件**落地：`core/agent.py`、`tools/registry.py`、`web/app.py`、`database/models.py`、`database/db.py`；其余建成分层正确、带签名的骨架(`raise NotImplementedError`)。附 `GUIDE.md`/`HOW_IT_WORKS.md`。
**为什么**：先有结构后有实现；种子文件当作"地基照抄"，骨架当"待填格子"，避免从零手写 156 文件。

### 阶段1 核心发动机（真正跑起来）
- **`core/llm.py`**：`LLMClient` 封装 OpenAI 兼容 API(`chat/chat_with_tools/stream_chat/embed`)。因为 base_url+key+model 可切 DeepSeek/本地。**换模型只改这一个文件**。
- **`core/agent.py`**：把 `self.client=OpenAI` 下沉为 `self.llm=LLMClient`(分层)；修 `self.memory` 未初始化 bug。`think()` 是 ReAct 循环：`_call_llm`→`_handle_tool_calls`→回填→再循环，`max_iterations=30`(对齐 Go)。`AgentState` 存 messages/tool_calls/iteration。
- **`tools/registry.py`**：`register_from_yaml` 从 YAML 生成工具(闭包+json_schema)，返回**注册名**(修拼音节 bug)。`register` 存 `{function,schema,category,enabled,config}`。
- **`core/tools.py`**：`ToolManager` 门面——`load_all`(批量灌 registry)、`attach_to_agent`(**把 registry 工具桥接给 Agent**：填 `agent.tools`(LLM 用)+`agent.tool_functions`(执行用))。
- **`agents/base_agent.py`**：构造时自动 `load_all+attach_to_agent`，并支持 `tools=` 白名单(只给 Agent 部分工具，不撑爆 context)。
**为什么这段是核心**：它打通了"YAML 工具 → Agent 真能调用"这条链(即你最早问的"Go 只放 yaml 我们行不行")。

### 阶段2 工具库对齐 Go
- 升级 `registry._create_command_executor` 支持 Go 完整协议(**positional/flag/template**)——之前只会裸 append，Go 的 yaml 拼错命令。
- 搬入 `~/CyberStrikeAI/tools/` 87 个 yaml → `tools/configs/` 共 **91 工具**，零 Python 代码。
- `pyproject.toml` 声明 pytest canonical；tools/unit + integration 测试固化。

### 阶段3 安全 + 数据底座
- `database/db.py`+`models.py` 连库跑通(SQLAlchemy SQLite `data/cyberstrike.db`)，默认库统一到 data/；加 `get_user_with_password`(认证专用)。
- `security/password.py`(**bcrypt**+兼容 Go sha256$ 老格式)、`token.py`(JWT)、`auth.py`(注册/登录/bootstrap admin)、`rbac.py`(**22 个 module:action 细粒度权限**)。
**为什么**：对齐 Go 的 `internal/security`(bcrypt+细粒度 RBAC)——你要求"安全功能也一样"。

### 阶段4 资产导入
复制 Go 的 `roles/`(13 角色 yaml)、`knowledge_base/`(19 知识 md)、`skills/`(24 方法论) 进本项目；写 `agents/roles_loader.py` 把角色 yaml 变成 BaseAgent(user_prompt→system_prompt)。

### 阶段5 Web 交付
- `web/deps.py`：**全局单例 + schemas + 辅助函数**集中(避免 routers↔app 循环 import)——`database/auth_manager/tool_registry` + `get_or_create_agent`。
- `web/routers/` 8 个：auth/chat/tools/agent/workflow/knowledge/admin/websocket。
- `web/app.py` 精简为 app+CORS+include_router+startup。
- `chat` 用 `run_in_threadpool` 异步化(不阻塞事件循环)；`/api/chat/stream` 用 SSE 事件流。
- `core/agent.py` 加 `stream_think`(**带工具循环的事件流式**：llm/tool_call/tool_result/done) + `save/restore_checkpoint`(AgentState 快照，中断恢复)。
**为什么**：对齐 Go 的多用户并发/工具过程可视化/checkpoint。

## 2. 文件链接总图
```
tests/integration ──► web.deps + web.app + core.agent
web/app.py ──include_router──► web/routers/*.py ──► web/deps.py ──► database/security/tools.registry + core.agent
core/agent.py ──► core/llm.py (LLMClient)
agents/base_agent ──► core.agent + core.tools(ToolManager)
web/routers/chat.py ──► deps.get_or_create_agent ──► core.agent.Agent.think/stream_think
```
**为什么这样链**：解耦(Web 不直接 new Agent，走 deps 注入)；分层(Agent 只依赖 llm.py)；避免循环 import(deps 当中间仓库)。

## 3. 已实现 vs 骨架（诚实标注）
**已实现并验证**：core(agent/llm/tools)、tools/registry+configs(91 yaml)、agents(base_agent/roles_loader)、security、database(接线)、web(deps/routers/app)、tests、pyproject、examples、docs。
**仍是骨架/待办**(种子占位)：`workflow/`(engine/node/graph)、`agents/supervisor_agent`/`orchestrator`/`specialists/*`、`integrations/*`、`scripts/*`、`web/middleware`、`frontend/`、`tools/builtin/*`、`knowledge` 是导入的 md(未做向量化)。
```