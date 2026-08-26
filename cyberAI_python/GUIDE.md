# CyberStrikeAI Python 完整开发指南（GUIDE）

> 本指南详细说明如何把 `PYTHON_FULL_REWRITE.md` 的重构方案落地成可运行的代码。
> 项目根目录：`/home/kali/agent-simple/cyberAI_python`
> 目标：用 Python 完整重写 CyberStrikeAI（Go 版），功能 100% 对齐。

---

## 一、项目概述

我们要做的是一个 **AI 驱动的 CTF / 渗透测试平台**：用户通过 Web 界面或命令行给 Agent 下达任务，Agent 会自主调用各种安全工具（nmap、sqlmap、nuclei、编码/加密工具等），分析结果，多轮循环直到给出答案。

与 Go 版的关系：
- Go 版是 `Gin + Eino 多代理 + sqlite3 + zap`（见 `~/CyberStrikeAI`）
- Python 版用 `FastAPI + OpenAI 兼容库 + SQLAlchemy + SQLite`
- 架构意图、功能点、端口(8080)、API 风格全部对齐

**关键点**：这不是 C/C++ 那种性能敏感系统，Python 开发速度比 Go 快很多，所以该方案估 2~3 个月。我们按里程碑推进，每阶段都有可验证的产出。

---

## 二、架构与数据流原理

整个系统分 5 层，一次用户对话完整流过它们：

```
用户(浏览React前端)
   │  POST /api/chat  {message}
   ▼
Web后端 (web/ FastAPI)
   │  ① 校验JWT (security/auth+rbac)
   │  ② 写入会话 (database/repositories)
   │  ③ 调 Agent
   ▼
Agent层 (agents/ Orchestrator创建实例)
   │  ④ think(task) —— 核心循环
   ▼
核心层 (core/)                     工具层 (tools/)
   │  Agent循环                     │  注册表(ToolRegistry)
   │  ┌──────────────────────┐     │  + 独立工具模块(builtin/)
   │  │ 5)调LLM(带tools)      │     │  + YAML配置(configs/*.yaml)
   │  │ 6)LLM返回tool_call    │◄────┤  6)返回schema给LLM
   │  │ 7)执行对应工具函数    │─────►│  7)subprocess调nmap/sqlmap等
   │  │ 8)结果回填消息,继续   │     │
   │  │ 9)无tool_call时输出终答│    │
   │  └──────────────────────┘     │
   ▼                                   ▼
数据层 (database/ SQLAlchemy + SQLite)   ← 会话/消息/用户/审计/工具执行记录
```

**核心循环（Agent brain）原理** —— 这是整系统最关键的机制：

1. 把 `系统提示词 + 历史消息 + 用户任务` 发给 LLM，同时附上"我能用哪些工具"的 schema 列表。
2. LLM 判断：如果要查资料/执行命令，它**不会直接回答**，而是返回一个特殊的 `tool_calls` 结构，指明"调用工具 X，参数是 Y"。
3. 你的代码拿到 `tool_calls`，去工具注册表找到对应函数并执行（比如跑 nmap）。
4. 把工具输出以 `role="tool"` 的消息回填给 LLM。
5. LLM 看到工具结果，要么再调下一个工具，要么给出 `content` 最终回答。
6. 循环一直到 LLM 不再要工具、或达到最大迭代次数。

> 这就是 OpenAI 官方 "function calling" 协议，`core/agent.py` 已经完整实现了这个循环（种子代码已在 md 里给出，已落地）。

---

## 三、环境搭建（先做这个）

```bash
cd /home/kali/agent-simple/cyberAI_python

# 1. 创建虚拟环境（Kali 是 PEP668 系统，必须用 venv，不能直接 pip install）
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置密钥
cp .env.example .env
#    编辑 .env，填入 DEEPSEEK_API_KEY（你有 mimo@token-plan-cn 或 DeepSeek key 都可以）

# 4. 需要的安全工具（Kali 大多自带；缺哪个装哪个）
sudo apt install nmap sqlmap nikto gobuster ffuf hydra nuclei subfinder whatweb
```

---

## 四、每个文件怎么写 —— 逐模块详解

> 表格里标注了 **[已落地]**（md 里有完整代码，直接是种子实现）和 **[骨架]**（已建好函数签名+注释，你补 `raise NotImplementedError` 下面的逻辑）。
> 顶层 `__init__.py` 已全部生成，通常不需要动。

### 4.1 核心层 core/

| 文件 | 状态 | 职责与写法要点 |
|------|------|--------------|
| `core/agent.py` | **[已落地]** | Agent 主类。`think()` 是循环；`register_tool()` 把函数+JSON schema 注册给 LLM。这是整系统大脑，直接读通它就能理解一切。 |
| `core/llm.py` | [骨架] | 封装 `OpenAI` 客户端。重点实现 `chat_with_tools()`（传入 tools 列表，返回含 tool_calls 的响应）。用 `response.choices[0].message.tool_calls` 判断。 |
| `core/tools.py` | [骨架] | 门面类 ToolManager，把 registry+executor 包起来给 Agent 用。逻辑薄，主要是转发。 |
| `core/memory.py` | [骨架] | 长期记忆。存 SQLite 表，`recall()` 按关键词/向量召回，注入到 Agent 的 system 消息里。 |
| `core/workflow.py` | [骨架] | 门面类，forward 给 workflow 包。可选，工作流模块完成后填。 |

### 4.2 工具系统 tools/（最大模块，代码量占大头）

**设计原理**：工具分两层 —— **注册表**（管理元信息/schema）+ **内置工具模块**（每个工具一个 Python 函数，实际干活）。

| 文件 | 状态 | 职责与写法要点 |
|------|------|--------------|
| `tools/registry.py` | **[已落地]** | 核心注册表。`register()` 存 name→{func, schema, category, enabled}；`execute()` 抛错包装成文本；`get_schemas()` 给 LLM 用。 |
| `tools/executor.py` | [骨架] | 执行器。包一层超时/错误处理/耗时统计。异步 `aexecute()` 用 `loop.run_in_executor` 把同步工具扔线程池。 |
| `tools/mcp_server.py` | [骨架] | 把自己暴露成 MCP 服务。用官方 `mcp` 库（`pip install mcp`）把 registry 注册成 tools。**次要，可后置**。 |
| `tools/mcp_client.py` | [骨架] | 连外部 MCP（可对接你的 HexStrike/Burp MCP）。**后置**。 |
| `tools/builtin/http_tools.py` | [骨架] | `requests` 实现 GET/POST/HEAD/上传/下载。每个函数返回"状态码+头+正文"的字符串。 |
| `tools/builtin/nmap_tool.py` 等 | [骨架] | 模式统一：`subprocess.run([cmd, ...], capture_output=True, text=True, timeout=..)`，解析输出成简洁文本。**10 个工具文件名对应 10 个扫描器**。 |
| `tools/builtin/crypto_tools.py` | [骨架] | `pycryptodome` 实现 RSA/AES/哈希/异或。加密解密要成对，写单元测试验证往返一致。 |
| `tools/builtin/encoding_tools.py` | [骨架] | base64/hex/url 编解码，纯标准库，最易完成。 |
| `tools/builtin/forensics_tools.py` | [骨架] | 调 `file/strings/exiftool/binwalk`，解析结果。 |
| `tools/builtin/misc_tools.py` | [骨架] | DNS/whois/端口检查/JSON格式化。 |
| `tools/configs/*.yaml` | [已有2个示例] | **每个工具的另一种注册方式**：写 `command/args/parameters`，`registry.register_from_yaml()` 会自动生成工具函数和 schema。这是把工具声明式接入的关键，100+ 个 yaml 逐步补。 |

**内置工具怎么写（标准模板）**：
```python
def nmap_scan(target: str, ports: str = "", scan_type: str = "-sV") -> str:
    cmd = ["nmap", scan_type]
    if ports: cmd += ["-p", ports]
    cmd.append(target)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.stdout if r.returncode == 0 else r.stderr   # 返回文本，LLM 能读
```

### 4.3 多 Agent 系统 agents/

**原理**：多 Agent 不是"多个独立循环"，而是 **单循环 + 子Agent作为工具**。Supervisor 把自己的子 Agent 的 `think()` 注册成工具，LLM 觉得某个子 Agent 合适就"调用"它。

| 文件 | 状态 | 写法要点 |
|------|------|---------|
| `agents/base_agent.py` | [骨架] | 基类，持有 `self.core = Agent(...)`。组合优于继承。 |
| `agents/single_agent.py` | [骨架] | 最简单，BaseAgent 加默认工具即可。 |
| `agents/supervisor_agent.py` | [骨架] | 实现 `_dispatch()`：把 `sub_agents[name].think(task)` 包装成工具函数注册。 |
| `agents/plan_execute_agent.py` | [骨架] | `_plan` 让 LLM 输出 JSON 步骤数组 → `_execute_step` 逐个执行 → `_revise` 失败重规划。 |
| `agents/orchestrator.py` | [骨架] | 全局单例，`get_or_create(agent_id, config)` 按 `config.mode` 选类型。 |
| `agents/specialists/*.py` | [骨架] | 7 个专业 Agent，每个 = 定制 system_prompt + 注册对应工具集。**这是最高优先级的生产内容**，直接影响 CTF 能力。 |
| `agents/configs/*.yaml` | [已有2个] | 声明式 Agent 定义（tools + system_prompt）。 |

### 4.4 工作流 workflow/

**原理**：工作流 = 有向无环图(DAG)。节点是"调 Agent"或"调工具"，边决定先后；拓扑排序出执行序；条件节点做分支。适合把"侦察→扫描→利用"等套路固化成可复用流程。

| 文件 | 写法要点 |
|------|---------|
| `workflow/node.py` | **已完成**，节点类 + 类型枚举。 |
| `workflow/graph.py` | [骨架] 实现 Kahn 拓扑排序；`from_definition` 解析 YAML/JSON。 |
| `workflow/state.py` | [骨架] 共享状态，支持 `${node_id.output}` 变量引用。 |
| `workflow/executor.py` | [骨架] 按拓扑序逐节点执行；条件节点分支；可选并行。 |
| `workflow/engine.py` | [骨架] 统一入口：构建→校验→执行。 |
| `workflow/templates/*.yaml` | [已有3个] 预定义套路流程。 |

### 4.5 知识库 knowledge/（RAG）

**原理**：RAG = 检索增强生成。把知识文档切块→向量化→存向量库；查询时把提问向量化→相似度检索→把片段拼进 LLM 上下文。让 Agent 有"记忆的 CTF 知识"。
建议开发期先用 **关键词搜索（简单）**，跑通后再上向量库（chromadb）。

| 文件 | 写法要点 |
|------|---------|
| `base.py` | 基础增删改查，先用 JSON/SQLite 存。 |
| `vector_store.py` | 选 chromadb（内嵌最省事），`add/query`。 |
| `embeddings.py` | 优先用 LLM embed 接口；没有 key 就先用 hash 占位。 |
| `retriever.py` | `build_context()` 检索并拼装成给 LLM 的文本。 |
| `docs/*.json` + `configs/*.yaml` | [已有] 知识数据和配置。 |

### 4.6 数据层 database/

| 文件 | 状态 | 写法要点 |
|------|------|---------|
| `models.py` | **[已落地]** | SQLAlchemy ORM：User/Conversation/Message/Agent/ToolExecution/Workflow/AuditLog 7 张表。 |
| `db.py` | **[已落地]** | `Database` 类：`get_session()` 上下文管理器 + 全部增删改查。seed 已给全。 |
| `repositories/*.py` | [骨架] | **建议重构方向**：把 db.py 里的查询按实体拆到各 repo，让 db.py 只留连接与会话，路径更干净。二阶段再做。 |
| `migrations/` | [空] | 数据表演进。规模化后用 Alembic。 |

### 4.7 安全层 security/

| 文件 | 写法要点 |
|------|---------|
| `password.py` | `passlib` 的 pbkdf2_sha256（不需要 bcrypt C 依赖）。 |
| `token.py` | JWT：`create_token`(HS256) / `verify_token`。用 `payjose` 或 `python-jose`。密钥从 `.env` 读。 |
| `auth.py` | 登录验证 + 签发/校验 token；登录失败限速。 |
| `rbac.py` | 角色→权限点映射 + `require(permission)` FastAPI 依赖。 |
| `middleware.py` | 安全头/错误脱敏。可选。 |

### 4.8 Web 后端 web/

| 文件 | 状态 | 写法要点 |
|------|------|---------|
| `app.py` | **[已落地]** | FastAPI 主应用：CORS、挂载路由、startup 事件加载工具/DB。路由和 Pydantic 模型都已写好（引用了你围住的 AuthManager/Database 等，实现这些依赖即可跑）。 |
| `routers/*.py` | [骨架] | 8 个路由文件。**填空时把"丢 NotImplementedError"换成调 AuthManager/Orchestrator/Database**。核心：chat 路由调 `agent.think()`。 |
| `middleware/*.py` | [骨架] | 认证/限流/日志中间件。 |
| `schemas/*.py` | [骨架] | Pydantic 请求/响应模型。已有 login/chat/agent。 |

### 4.9 Web 前端 frontend/react-app/

Vite + React + TS。已建骨架：`package.json`、`index.html`、`main.tsx`、`App.tsx`、`services/api.ts`、页面/组件空壳。
开发：`cd frontend/react-app && npm install && npm run dev`（Vite 默认 5173，需配代理到 8080）。
**中后期**再深入，先把后端+Agent 跑通。

### 4.10 集成/脚本/测试/部署

| 目录 | 说明 |
|------|------|
| `integrations/` | 微信/钉钉/飞书/Telegram 机器人。机器人收消息→转给 Agent→回推。后置。 |
| `scripts/` | setup（建venv装依赖）/ migrate / seed（建admin+示例知识）/ backup。 |
| `tests/` | unit / integration / e2e 三套。强推先给 crypto/encoding 写往返测试，再给 API 写流程测试。 |
| 根目录 | `main.py`(CLI入口) / `server.py`(API入口) / `webapp.py`；`config.yaml` / `.env.example` / `requirements.txt` / `Dockerfile` / `docker-compose.yml` / `nginx.conf` / `Makefile` 已就绪。 |

---

## 五、开发顺序（里程碑，每阶段有验收标准）

### 里程碑 1：跑通核心 Agent（第 1~2 天）
1. `pip install -r requirements.txt`
2. 配 `.env`（填 DeepSeek/mimo key）
3. `python main.py "HELLO，测试一下"` —— 应能无工具直接回答
4. 实现 `core/llm.py` 的 `chat_with_tools()`
5. 验证 `core/agent.py` 循环：注册一个 http_get 工具，问 Agent "访问 http://example.com 并告诉我标题"，应看到它自主调工具。
   **验收**：命令行能用 Agent 调至少一个工具。

### 里程碑 2：工具丰富化（第 1~2 周）
1. 完成 `tools/builtin/` 的编码/加密/HTTP 工具（纯标准库，最快见效）
2. 完成 nmap/sqlmap/nuclei/subfinder 等扫描工具（subprocess 模板）
3. 为每个工具写 `tools/configs/*.yaml`，用 `register_from_yaml` 批量注册
4. 写单元测试（crypto 往返、encoding 已知向量）
   **验收**：`scripts/` 里能跑一个"列工具"清单，Agent 能自主调用 5+ 种工具。

### 里程碑 3：Web 后端 + 数据（第 3~4 周）
1. 实现 `database/db.py` 需要的依赖已完成（seed 已全）—— 直接可用
2. 实现 `security/`（password/token/auth/rbac）
3. 逐个填 `web/routers/*.py`
4. `python server.py` 启动，访问 `http://localhost:8080/docs` 看 Swagger
5. 用 curl 测：注册 → 登录拿 token → 带 token 调 `/api/chat`
   **验收**：HTTP API 全流程可用（登录→对话→工具执行→会话历史）。

### 里程碑 4：多 Agent + 工作流 + 知识库（第 5~6 周）
1. 完成 `agents/`（supervisor 分派 / plan-execute）
2. 完成 `workflow/`（DAG + 模板）
3. 完成 `knowledge/`（先关键词，后向量）
   **验收**：能配置一个 supervisor 让"侦察+Web+crypto"子Agent协作解一道 CTF。

### 里程碑 5：前端 + 集成 + 部署（第 7~8 周）
1. React 页面（登录/对话/工具/Agent/工作流/知识库）
2. `integrations/` 机器人（可选）
3. Docker 部署
   **验收**：完整 Web UI 单机跑通。

---

## 六、运行与验证命令

```bash
# 启动 API
python server.py          # 或 uvicorn web.app:app --reload

# Swagger 交互文档
# 访问 http://localhost:8080/docs

# 命令行测 Agent
python main.py "扫描 http://127.0.0.1:8080 的目录结构"

# 快速验证工具注册
python -c "from core.tools import ToolManager; m=ToolManager(); m.load_all('tools/configs'); print(m.get_schemas())"

# 跑测试
pytest tests/ -v
```

---

## 七、常见坑（避雷）

1. **Kali 是 PEP668**：必须 venv，`pip install` 直接装会报 externally-managed-environment。
2. **subprocess 工具超时**：nmap/sqlmap 可能跑很久，务必 `timeout=`，否则卡死 Agent 循环。
3. **工具输出别太大**：工具结果会塞进 LLM 上下文，超 2000 字符要截断（`core/agent.py` 已有 `[:2000]`）。
4. **LLM 传错参数类型**：工具函数要容忍 `str`/`int` 混用，executor 里做宽松校验。
5. **JWT 密钥别硬编码**：`security/token.py` 里 `secret="CHANGE_ME"` 是占位，必须从 `.env` 读随机长串，否则被别人伪造 token。
6. **数据库路径**：`config.yaml` 里 `sqlite:///data/cyberstrike.db`，确保 `data/` 目录存在（程序里 `os.makedirs`）。
7. **前端跨域**：React dev(5173) 调后端(8080) 要配 Vite proxy 或 CORS（app.py 已开 CORS）。
8. **`raise NotImplementedError` 是占位**：所有骨架文件里这类就是"等你填"的标记。

---

## 八、现在下一步（照着做）

1. `cd /home/kali/agent-simple/cyberAI_python && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. `cp .env.example .env` 填入你的 key
3. 通读 `core/agent.py`（已完整落地，整个系统的核心）
4. 实现 `core/llm.py` 的 `chat_with_tools()`
5. 跑 `python main.py "水测试"` 验证 Agent 循环
6. 回来告诉我结果，我们再进入里程碑 2（工具丰富化）

从第 4 步开始，有任何文件不会写，直接找我，我按上面的模板帮你把实现填出来。