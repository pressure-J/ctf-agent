# CyberStrikeAI Python — 看得懂版全讲解

这是把 Go 版 `CyberStrikeAI`(CTF 安全 AI 平台)重写成 Python 的项目。
本文档专门"讲人话":每个文件代码什么意思、为什么这么分层、和 Go 差多少、网上大厂框架怎么做。

## 一、当前进度(14 项 todo, 完成 9 项)

| 模块 | 状态 | 一句话 |
|------|------|--------|
| 数据层 database | ✅ | SQLAlchemy+SQLite, 用户/会话/消息/审计表 |
| 安全层 security | ✅ | bcrypt 密码 + JWT + 细粒度 RBAC + bootstrap admin |
| 资产导入 IMP | ✅ | 从 Go 搬来 13角色/91工具YAML/24技能/19知识md |
| Web 后端 B1+B2 | ✅ | FastAPI + 拆分routers + 全局deps + 异步化 + SSE流式 |
| 多Agent C | ✅ | supervisor(子Agent当工具) + orchestrator + context_budget/checkpoint/中断恢复 |
| 工作流 DAG D | ✅ | Kahn拓扑排序 + 共享state + agent/tool节点执行 |
| 知识库RAG E | ✅ | 向量检索(余弦+TopK) + 索引552chunk |
| 前端 F1 | 🟡部分 | 亮单页最小闭环(登录+对话SSE流式); 其余页面待补 |
| 部署 H2 / 集成 H1 / 测试H3 | ⬜ | 待做 |
| 工具精化 G1 | ⬜跳过 | 与"Go 全YAML"相悖,不做 builtin 实现 |

**能跑**:登录+鉴权+91工具+/api/chat(异步)+/api/chat/stream(带工具流式)+知识库检索+工作流DAG+多Agent编排+pytest(20+用例)全绿。

## 二、和 Go 版对比(功能/性能)

| 维度 | Go 版 | 我们 Python | 相似度 |
|------|-------|------------|--------|
| 工具 | 90 个 YAML + MCP server | 91 个 YAML + registry + **本地MCP client** | ✅ 等价(数量几乎一致) |
| 安全 | bcrypt + 70细粒度RBAC + session | bcrypt + 22细粒度RBAC + JWT | ✅ 核心对齐 |
| Agent循环 | openAI+mcp+maxIter30+流式+checkpoint | llm+tool+maxIter30+事件流式+checkpoint+异步化 | ✅ 对齐 |
| 多Agent | eino ADK(supervisor/plan_execute+预算+断点) | supervisor/plan_execute+context_budget+checkpoint+resume | ✅ 对齐核心+高级 |
| 工作流 | eino图+表达式/jsonpath/dry_run/hitl | DAG拓扑(无表达式/jsonpath等高级) | 🟡 核心对齐,高级缺 |
| 知识库 | eino真语义embedding+rerank+multiQuery | 本地hashed向量+余弦(无语言模型) | 🟡 机制对齐,语义质量待提 |
| Web | app+handler+原生JS单页 | FastAPI+routers+原生JS单页 | ✅ 模式一致 |
| 测试 | 各包 _test.go | pytest(20+) | ✅ |

**最大差距**:知识库语义质量(本地嵌入 vs 真embedding)、工作流高级特性、前端页面齐全度。

## 三、框架是什么类型

**"工具调用型(ReAct) Agent 运行时 + 注册表驱动工具 + SQLite 底座 + FastAPI 交付壳"。**
核心是 `LLM看历史/工具 → 决策调工具 → 执行回填 → 再决策` 的 ReAct 循环(see 01)。

## 四、文档索引(怎么读)

```
WALKTHROUGH/
  README.md             ← 本文件(进度/Go对比/框架类型)
  01-架构与业界对比.md     ← 为什么这样分层 + 网上的框架怎么做
  02-core.md            ← core/ 发动机(llm/agent/tools/context_budget/checkpoint)
  03-tools+agents.md    ← tools(91YAML) + agents(多Agent)
  04-security+database.md ← 底座(密码/JWT/RBAC + 数据表)
  05-workflow+knowledge.md ← DAG引擎 + 向量RAG
  06-web+frontend+tests.md ← FastAPI壳 + 轻单页 + pytest
```

> 学读顺序:README → 01 → 02(core) → 03(工具/多Agent) → 06(Web能跑) → 04/05(底座/数据)。
