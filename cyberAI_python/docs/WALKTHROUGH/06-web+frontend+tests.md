# 06 · Web 交付壳 + 前端 + 测试

## 一、web/ — 把能力变成 HTTP API(FastAPI)
**马上要改名/理解三件套**:
- `web/app.py`: 最薄。创建 `FastAPI()` + 加 CORS + `include_router` 挂上各路由 + 挂静态前端 + 启动时 `database.init()`。也就 30 行 —— 因为它只做"装配", 逻辑全在别处。
- `web/deps.py`: **全局单例仓库**。`database / auth_manager / tool_registry` 三巨头 + Pydantic schema(LoginRequest/ChatRequest...) + 辅助 `get_or_create_agent`。**为什么必须有它**: 各 router 都要用 database/auth_manager; 若 router 自己 import app, app 又要 include router, 会循环 import 死锁。把"共享实例"集中到 deps, 谁要用就从这拿, 打破环。
- `web/routers/`(8个): 每个功能一个文件, 画等号:
  | 文件 | 提供 |
  |------|------|
  | auth.py | /api/auth/login·logout |
  | chat.py | /api/chat、**/api/chat/stream(SSE流式)**、/api/conversations |
  | tools.py | /api/tools 列表/详情/执行 |
  | agent.py | /api/agents |
  | workflow.py | /api/workflows(exec→DAG引擎) |
  | knowledge.py | /api/knowledge(向量检索) |
  | admin.py | /api/admin/stats·audit |
  | websocket.py | /ws |

**chat 为什么加 `run_in_threadpool`**: `agent.think` 是同步的(要跑很久)。若直接在 async 路由里同步执行, 会**卡死整个 FastAPI 事件循环**, 一个慢请求拖垮所有用户。丢进线程池 `await run_in_threadpool(...)` 就并发不阻塞。
**stream 为什么用 SSE**: `StreamingResponse` + 生成器, 后端每算出一个事件(`llm/tool_call/...`)就 `data: {...}` 推送一行, 前端打字机显示, 长任务不干等。

## 二、frontend/ — 轻量单页(不是SPA框架)
**为什么是"一个 index.html + 原生JS"而不是 React**: 对齐 Go 版(它也是一堆原生 JS); 后端 API 全, 前端只是"消费壳"; 纯静态零构建。
- `index.html`: 登录视图 + 主界面容器。
- `static/js/auth.js`: `fetch("/api/auth/login")` 拿 token 存 localStorage。
- `static/js/chat.js`: 普通对话 `fetch("/api/chat")`; **流式** 用 `fetch` 读 body 的 ReadableStream, 按 `data:` 行解析 `llm/tool_call/...` 事件实时渲染。
- `static/js/app.js`: token 存取 + 视图切换。
- `web/app.py` 用 `StaticFiles` 托管 `/static`, `GET /` 返回 index.html → 浏览器打开就能登录+对话。

## 三、tests/ — 怎么保证"改了不坏"
pytest 分单元+集成, 全在 `tests/`:
- `unit/`: test_agent_loop(循环) / test_tools_manager(工具桥接) / test_workflow(DAG拓扑+环) / test_knowledge(向量检索) / test_multiagent(主管派发) / test_agent_advanced(预算+checkpoint+恢复)。
- `integration/test_api.py`: 用 `TestClient` **真的打 HTTP** —— 登录→鉴权→列工具→chat/stream(用假Agent不花钱)。
- `integration/test_mcp.py`: 起本地 mock MCP server, 走 `examples/mcp_demo.py` 验证连外部MCP。
跑法: `cd cyberAI_python && .venv/bin/python -m pytest tests/`

## 四、把一切串起来的总图
```
浏览器 ──> /api/chat ──> deps.get_or_create_agent ──> core/agent.think(ReAct)
        auth_manager验token                    ├─> core/llm (LLM)
        database(单例)存消息                   ├─> tools(91YAML/mcp_client)
                                             ├─> workflow(DAG引擎)
                                             ├─> knowledge(向量RAG)
                                             └─> agents(多Agent supervisor)
```
**框架身份**: 自研轻量 "ReAct 工具Agent + Web壳" 运行时, 对标 LangChain AgentExecutor / eino 单Agent。
