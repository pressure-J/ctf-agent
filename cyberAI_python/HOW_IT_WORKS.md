# HOW IT WORKS — 文件关系与运行原理详解

> 本文件回答三个问题：
> 1. 代码是怎么运行的（运行时视角）
> 2. 每个文件之间是什么关系（依赖图）
> 3. 文件之间到底靠什么"联系起来"（4 种连接机制）
>
> 所有说法都来自对当前目录真实代码的扫描，不是纸面设计。

---

## 一、先说结论：整个项目是一个"单向金字塔"

```
               ┌───────────────┐
               │  入口层         │  main.py / server.py / webapp.py
               └──────┬────────┘
                      │ import（往下依赖）
               ┌──────▼────────┐
               │  Web层 web/    │  app.py(汇聚点) →routers/ →schemas/ →middleware/
               └──────┬────────┘
                      │
               ┌──────▼────────┐
               │  Agent层 agents/ │  orchestrator → base_agent → 专业代理
               └──────┬────────┘
                      │
               ┌──────▼────────┐    ┌────────────────┐
               │  核心层 core/   │◄───│ 工具层 tools/    │
               │  agent llm    │    │ registry executor│
               │  memory       │    │ builtin/ 内置工具 │
               └──────┬────────┘    └───────┬────────┘
                      │                      │
               ┌──────▼────────┐   ┌────────▼────────┐
               │  数据层 database/ │   │ 知识层 knowledge/ │
               └───────────────┘   └─────────────────┘
```

**最重要的规则：依赖是单向的（上层 import 下层），绝不允许反向。**
- `web` → 依赖 `core / tools / security / database`
- `agents` → 依赖 `core`
- `core` → 依赖 `tools / workflow`
- 谁也不该去 `import web`（否则就成环了，Python 会报循环导入）

---

## 二、真实扫描出来的 import 依赖图（项目内部）

这是我从你每个 `.py` 文件的 `import` 语句里逐条抠出来的真实结果：

```
main.py                            -> core.agent
web/app.py                         -> core.agent, core.tools, database.db, security.auth
core/tools.py                      -> tools.executor, tools.registry
core/workflow.py                   -> workflow.engine, workflow.graph
workflow/engine.py                 -> workflow.executor, workflow.graph
workflow/executor.py               -> workflow.graph, workflow.state
workflow/graph.py                  -> workflow.node
security/auth.py                   -> security.token
agents/base_agent.py               -> core.agent
agents/single_agent.py             -> agents.base_agent
agents/supervisor_agent.py         -> agents.base_agent
agents/plan_execute_agent.py       -> agents.base_agent
agents/orchestrator.py             -> agents.base_agent
agents/specialists/*.py (7个)      -> agents.base_agent
```

看一眼就明白依赖是分层递进的：
- `main.py` 只认识 `core.agent`（CLI 的最简入口）
- `web/app.py` 是**汇聚点**，一口气认识 4 个下层模块
- `agents/*` 全挂在 `base_agent` 上，`base_agent` 挂在 `core.agent` 上
- tools 内部自洽：`core/tools.py` 拉 `tools/registry` 和 `tools/executor`

---

## 三、核心概念：文件之间靠 4 种"联系"连起来

这是理解整个系统的关键。文件之间不是孤立存在的，它们靠下面这 4 种机制互相联系：

### 联系方式 A：import（编译期/加载期）—— 访问别人的类或函数

最常见的联系。`from core.agent import Agent` 表示"我要用 Agent 这个类"。
它决定了**编译依赖方向**，也是上面依赖图的来源。

例：
```python
# web/app.py
from core.agent import Agent, AgentMode      # 用 core 里的 Agent
from security.auth import AuthManager         # 用 security 里的认证
from database.db import Database              # 用 database 里的库
```

### 联系方式 B：对象传递 / 依赖注入（运行期）—— 把东西塞给别人

`import` 只是"认识类型"，真正干活要靠**实例**。常见做法：上层创建对象，塞给下层用。

例（app.py 里）：
```python
tool_registry = ToolRegistry()   # 创建一个工具注册表对象
auth_manager  = AuthManager()    # 创建认证管理对象
database      = Database()       # 创建数据库对象
```
这三个全局实例就是"共享的服务"，路由处理函数直接引用它们（见下文 C）。

### 联系方式 C：共享全局单例（运行期）—— 谁都能摸到同一个对象

FastAPI 里常用"模块级全局变量"做服务容器。app.py 里创建的 `tool_registry / auth_manager / database` 就是全局对象，路由函数不 import 它们，而是直接引用 `web.app` 这个模块的全局变量，实现"所有路由共享一套服务"。

这就是为什么 Web 层能把"登录、对话、工具"三个功能串起来：它们操作的是**同一个 database**、**同一个 auth_manager**。

### 联系方式 D：配置文件驱动（数据联系）—— 代码不写死，靠 YAML 喂

这是最妙的一种"联系"，工具和 Agent 的扩展**不改代码**，改 YAML 即可：

- `tools/registry.py` 的 `register_from_yaml()` 读 `tools/configs/*.yaml`，按文件里的 `command/args/parameters` **自动生成**工具函数并注册。
- 也就是说：`tools/registry.py`（代码）↔ `tools/configs/nmap.yaml`（数据）通过"约定路径 + yaml.safe_load"联系起来。
- 同样 `agents/configs/*.yaml`、`workflow/templates/*.yaml`、`knowledge/configs/*.yaml` 都是这个模式。

**一句话总结 4 种联系：**
> A（import）决定"我能用谁"；B（注入）决定"把谁传给谁"；C（全局单例）决定"谁和谁共享同一个"；D（YAML）决定"我怎么不写代码就新增东西"。

---

## 四、按"一次运行"追踪代码怎么流动

我们分两个入口看运行过程。

### 场景 1：CLI — `python main.py 帮我扫一下 127.0.0.1`

```
main.py
  └─ Agent(name="CTF专家").think(task)          ← 只剩 core.agent
        core/agent.py 里的 think():
            for 迭代 in range(max_iterations):
                response = self._call_llm()       # 调 LLM(见下)
                if 消息里有 tool_calls:
                    执行工具函数, 回填结果, 继续  # ← 工具从哪来? 见下
                else:
                    return 最终答案
```

`_call_llm()` 用的其实是 `core/llm.py` 该有的东西（`OpenAI` 客户端）——目前 agent.py 里直接 `import os` + `OpenAI`。**这就是一个"该连却没连"的点**：按设计，LLM 操作应下沉到 `core/llm.py`，agent.py 通过它去调用，而不是自己 new 客户端（见第八节的缺口②）。

那"工具"从哪来？CLI 里 Agent 目前**没接工具**（`self.tools=[]`）。要让它能用工具，需要 `core/tools.py` 的 ToolManager 把 `tools/registry.py` 的工具注册进 Agent —— 这是里程碑 1 你要补的接线。

### 场景 2：Web — 浏览器 POST /api/chat

```
浏览器/React (frontend)
   │  POST http://host:8080/api/chat  {message:"扫一下 127.0.0.1", "Authorization":"Bearer <token>"}
   ▼
uvicorn 把 Web 请求交给 FastAPI (web/app.py)
   │  app 是 FastAPI 实例, 一堆 @app.post/@app.websocket 装饰的函数就是"路由"
   ▼
web/app.py 的 chat() 路由
   │  1) auth_manager.verify_token(token)      ← security/auth.py (B/C联系)
   │  2) database.create_conversation(...)     ← database/db.py (B/C联系)
   │  3) agent = get_or_create_agent(...)      ← 创建 Agent (core/agent.py)
   │  4) response = agent.think(message, ...)  ← 进入 Agent 循环 (A联系)
   │  5) database.save_message(...)            ← 存历史
   ▼
返回 JSON 给浏览器
```

**观察要点：** `web/app.py` 没 import `agents/`，它直接 new `core.agent.Agent`。设计上的路由是 `agents/orchestrator.py` 负责"按配置建 Agent"，但当前 app.py 是绕过 orchestrator 直接调 `core.agent`（这也是个参照点，见缺口④）。

---

## 五、Agent 循环到底是哪几行（读懂它就懂整个项目）

`core/agent.py` 是唯一真正"活"的核心，`think()` 里的循环是：

```python
for iteration in range(self.max_iterations):     # 最多 30 轮
    response = self._call_llm()                   # 1. 把全部消息+工具schema发给LLM
    msg = response["choices"][0]["message"]
    if msg.get("tool_calls"):                     # 2. LLM 想调用工具?
        self._handle_tool_calls(msg)              # 3. 查 self.tool_functions[名字] 并执行
        #    结果以 role="tool" 回填进 self.state.messages, 下一轮继续
    else:
        return msg["content"]                     # 4. 没有工具需求 = 有终答, 退出
```

`_call_llm()` 关键：
```python
self.client.chat.completions.create(
    messages=self.state.messages,
    tools=self.tools,            # ← 这就是"文件间的联系"：self.tools 是从 ToolRegistry 拿来的 schema
    tool_choice="auto")
```

**核心思想**：`self.tools` 是一个"能力清单"，它告诉 LLM 你能干什么；LLM 不直接执行，它只是"提出请求"，执行权在你手里（`_handle_tool_calls`）。这就是 AI Agent 的本质：**LLM 负责决策，你的代码负责执行，两边靠 tool_calls 协议对话**。

---

## 六、事务型模块之间的"调用链"画全一张图

把上一节的 4 种联系和 import 图合并，得到完整运行时关系（已被实现/待实现的')：

```
web/app.py  ──(import A)──►  core/agent.py ──(A)──►  core/llm.py(待接线)
    │   │                        │
    │   │ (B/C: 全局实例)         │ (D: tools/configs/*.yaml)
    │   ├──► security/auth.py ──(A)──► security/token.py
    │   ├──► database/db.py ──(A)─► database/models.py (ORM表)
    │   └──► core/tools.py  ──(A)─► tools/registry.py ──(A)─► tools/executor.py
    │                                 │                     tools/mcp_client.py
    │                                 └──(D)读YAML──► tools/configs/*.yaml
    │                                                    tools/builtin/*.py(subprocess调工具)
    │
    └──(将来)► agents/orchestrator.py ──► base_agent ──► 专业Agent(7个)
```

---

## 七、你问的"每个文件之间的关系"——分层逐个讲

### 入口层（3 个文件，只负责"启动"）
| 文件 | 关系 | 干嘛 |
|------|------|------|
| `main.py` | `→ core.agent` | 命令行：new 一个 Agent 直接 think |
| `server.py` | `→ uvicorn "web.app:app"` | 启动 FastAPI 后端 |
| `webapp.py` | 同上 + 静态前端 | 启动并托管前端产物 |

### Web 层（对外唯一的"门"）
| 文件 | 关系 | 干嘛 |
|------|------|------|
| `web/app.py` | `→ core.agent / core.tools / security.auth / database.db` | **汇聚点**：创建全局服务、定义路由 |
| `web/routers/*.py` | 将来被 app.include_router 挂载 | 各业务路由（auth/chat/tools/...） |
| `web/schemas/*.py` | 被 routers 引用 | Pydantic 请求/响应模型（数据校验+文档） |
| `web/middleware/*.py` | app.add_middleware 挂载 | 认证/限流/日志中间件 |

### Agent 层（组织 Agent 用）
| 文件 | 关系 | 干嘛 |
|------|------|------|
| `agents/base_agent.py` | `→ core.agent` | 所有 Agent 的父类，持有 `self.core=Agent(...)` |
| `agents/orchestrator.py` | `→ base_agent` | 工厂：按 config 的 mode 造出对应 Agent |
| `agents/{single,supervisor,plan_execute}.py` | `→ base_agent` | 三种协作模式 |
| `agents/specialists/*.py` | `→ base_agent` | 7 个专业 Agent（recon/web/crypto/...） |

### 核心层（Agent 的"大脑零件"）
| 文件 | 关系 | 干嘛 |
|------|------|------|
| `core/agent.py` | `→ openai/dotenv` | 核心循环。**他是唯一实例化过的"老板"** |
| `core/llm.py` | 独立 | 应封装 OpenAI 调用（目前 agent.py 没接，是缺口②） |
| `core/tools.py` | `→ tools.executor, tools.registry` | ToolManager 门面，把工具包给 Agent 用 |
| `core/memory.py` | 独立 | 长期记忆 |
| `core/workflow.py` | `→ workflow.engine/graph` | 工作流门面 |

### 工具层（能力库，数量最多的层）
| 文件 | 关系 | 干嘛 |
|------|------|------|
| `tools/registry.py` | 独立 | 注册表：name→{func,schema,enabled}；提供 get_schemas/execute |
| `tools/executor.py` | `→ registry` | 执行器：给执行加超时/错误包装 |
| `tools/mcp_server.py` | `→ registry` | 把自己暴露成 MCP（后置） |
| `tools/mcp_client.py` | 独立 | 连外部 MCP（后置） |
| `tools/builtin/*.py` | 独立 | **真正干活的函数**（http/nmap/sqlmap...每个用 subprocess/库） |
| `tools/configs/*.yaml` | 被 registry 读取 | 声明式工具定义（D 联系） |

### 其他层
| 层 | 文件 | 关系 | 干嘛 |
|----|------|------|------|
| 数据层 | `database/db.py` →`database/models.py` | 连接+操作 / ORM 表 |
| 数据层 | `database/repositories/*` | 将来按实体拆查询（可选重构） |
| 安全层 | `security/auth.py` →`security/token.py` | 认证 / JWT |
| 知识层 | `knowledge/*.py` | RAG：base/vector_store/embeddings/retriever |
| 工作流 | `workflow/engine→executor→graph→node` | DAG 执行 |

---

## 八、当前代码里真实的"连接缺口"（读完你就明白该怎么接）

我扫代码时发现 4 处 `import`/调用存在，但对应实现不匹配——**这正是你接下来要补齐的"接线"**：

1. **缺口①：`web/app.py` 第 17 行 `from core.tools import ToolRegistry`**
   但 `core/tools.py` 里目前只有 `ToolManager`，没有 `ToolRegistry`（后者在 `tools/registry.py`）。
   → 修法（二选一）：
   - 改 import：`from tools.registry import ToolRegistry`，或
   - 在 `core/tools.py` 里补一行 `from tools.registry import ToolRegistry`（re-export，保持门面统一）。

2. **缺口②：`core/agent.py` 自己 new `OpenAI` 客户端，没走 `core/llm.py`**
   设计意图是 LLM 操作下沉到 llm.py。目前可用（能跑），但分层不干净。
   → 里程碑 1 实现 `core/llm.py` 后，agent.py 改用 `LLMClient`。

3. **缺口③：`web/routers/` 还没被 `app.py` 挂载（缺 `app.include_router(...)`）**
   现在 app.py 的路由都写在文件里，插件的 routers/ 是空的。
   → 实现时逐个 `from web.routers import chat, tools...` + `app.include_router(router)`。

4. **缺口④：app.py 直接 new `Agent`，绕过了 `agents/orchestrator.py`**
   设计上应由 orchestrator 按 YAML 配置建 Agent。当前是"默认 Agent"直连。
   → 里程碑 3/4 用 orchestrator 替换。

> 这些缺口不是 bug，是"方案给全了、连接点到实现时才接上"的正常状态。找到这些缺口 = 你已经看懂文件怎么连了。

---

## 九、为什么这样分层？（这决定你能不能改对地方）

- **入口层薄**：只做启动，方便换 UI（CLI/Web/机器人共用同一套上层）。
- **Web 层只做"翻译"**：把 HTTP 请求翻译成对 Agent 的调用，不懂"扫描"。
- **Agent 层只做"决策"**：决定用什么工具，不自己写扫描逻辑。
- **工具层只做"执行"**：nmap 就是 nmap，不关心谁在用它。
- **数据层只做"存取"**：不关心业务。

**好处**：加一个工具 = 加一个 `tools/builtin/xxx.py` + 一个 `tools/configs/xxx.yaml`，**不动 Agent、不动 Web**。这就是模块化的意义。

---

## 十、现在该怎么读代码（实操顺序）

想真正看懂，按这个顺序读文件（每个 5~10 分钟）：

1. `core/agent.py` —— 只有它真正在"思考"（本轮最重要）
2. `tools/registry.py` —— 看懂"注册表 + YAML 生成工具"
3. `web/app.py` —— 看懂"汇聚点怎么把下层串起来"
4. `database/db.py` + `models.py` —— 看懂数据存取
5. `agents/base_agent.py` —— 看懂多 Agent 怎么挂
6. 其余按需（workflow/knowledge/mcp 是附加能力）

每读一个文件，问自己一句：**"谁 import 了我？我又 import 了谁？哪个 YAML 在喂我？"** —— 这三个问题答出来，文件关系就通了。

---

> 配套：开发进度与逐文件写法见 `GUIDE.md`；本文件只讲"关系和运行"。