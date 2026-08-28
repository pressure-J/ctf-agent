# 变更记录 (CyberStrikeAI Python)

> 阶段 1：LLM 分层、工具桥接、自动加载、真实跑通
> 主线动机：把「YAML 工具 → Agent 用上它」这条链路补齐并固化。

## 一、编辑过的代码文件

### 1. core/agent.py — Agent 核心，改造 3 处
- **LLM 客户端下沉**：`self.client = OpenAI(...)` → `self.llm = LLMClient(...)`
  - 同时 `_call_llm()` / `chat()` 改走 `self.llm.chat_with_tools()` / `.chat()`。
  - 原因：LLM 通信收敛到 `core/llm.py`，Agent 只管循环逻辑，换模型只改一处。
- **修复 self.memory 未初始化 bug**：`think()` 里读写 `self.memory` 但未初始化 → 加 `self.memory: List[str] = []`。
  - 原因：一调 `think()` 就 AttributeError（mock 验证抓出）。
- **导入**：`from openai import OpenAI` → `from core.llm import LLMClient`。

### 2. core/llm.py — 从骨架重写成完整实现
- 新增 `LLMClient`：`chat()` / `chat_with_tools()` / `stream_chat()` / `embed()`。
- 原因：LLM 唯一出口，封装 OpenAI 兼容调用与参数。

### 3. core/tools.py — ToolManager 从骨架补全
- 补 `load_all(config_dir)`：glob `*.yaml` → registry，返回注册名列表。
- 补 `attach_to_agent(agent)`：遍历 registry.tools，拆 schema 喂给 `agent.register_tool`。
- 补 `list_tools()`；补 `aexecute()`（`run_in_executor` 后台线程，不阻塞事件循环）。
- 原因：桥接缺口—让工具库能被单个 Agent 用上。

### 4. tools/registry.py — 一行修改
- `register_from_yaml()` 末尾 `return tool_name`（返回注册名）。
- 原因：文件名(`dns`)≠注册名(`dns_lookup`)，不返回真名则 `load_all` 拿错 key。

### 5. agents/base_agent.py — 重写为自动加载版
- `__init__(..., auto_load=True)` 时调用 `_load_tools()`。
- `_load_tools()`：`ToolManager().load_all("tools/configs")` + `attach_to_agent(self.core)`。
- 原因：插件化—任何 Agent 构造即带全部 YAML 工具。

## 二、新增文件

| 文件 | 类型 | 原因 |
|------|------|------|
| tools/configs/dns.yaml | 数据 | 演示「写 YAML=加工具」 |
| tests/unit/test_agent_loop.py | 测试 | 固化 Agent 循环 + LLM 透传 |
| tests/unit/test_tools_manager.py | 测试 | 固化 ToolManager 桥接链路 |
| tests/unit/test_base_agent.py | 测试 | 固化 BaseAgent 自动加载 |
| examples/trace_agent_loop.py | 演示 | 单跳链路形成 |
| examples/trace_agent_two_jumps.py | 演示 | 链路 2→4→6 累积 |
| examples/trace_tool_source.py | 演示 | YAML→schema→命令拼接 |
| examples/trace_agent_with_yaml_tools.py | 演示 | YAML 工具被 Agent 循环调用 |
| examples/register_any_tool.py | 演示 | 注册任意 YAML 工具 |
| examples/run_real.py | 演示 | 真实端到端(真 DeepSeek+真 dig) |

## 三、验证状态
- 单元测试：`python -m unittest discover -s tests/unit -p "test_*.py"` → 6 用例 OK。
- 真实链路：`example.com` DNS 查询端到端跑通（DeepSeek 决策 + 真 dig）。
- 说明：单元测试网络部分为 mock；真实网络调用已验证一次。

## 四、当前未提交(git status)
- M：`agents/base_agent.py`、`core/tools.py`、`tools/registry.py`
- ??：`examples/{register_any_tool,trace_agent_with_yaml_tools,trace_tool_source,run_real}.py`、`tests/unit/{test_tools_manager,test_base_agent}.py`、`tools/configs/{dns,amass}.yaml`（amass.yaml 为仓库原有，非本阶段创建）