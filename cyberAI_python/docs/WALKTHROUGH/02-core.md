# 02 · 核心发动机 core/（看懂 Agent 怎么工作）

这是任何 Agent 平台的心脏。core/ 里 5 个文件, 各管一件事:

## core/llm.py — 一句话:换模型只改这一处
**职责**: 把所有"跟大模型说话"封装成一个类 `LLMClient`。
```python
class LLMClient:
    def __init__(self, model="deepseek-chat", temperature=0.7):
        # 用 openai 兼容 SDK, base_url/key 从 .env 读(DEEPSEEK_API_BASE/KEY)
        self.client = openai.OpenAI(api_key=..., base_url=...)
    def chat(self, messages) -> str            # 最简: 问一句答一句
    def chat_with_tools(self, messages, tools) # 带工具声明, 返回可能含 tool_calls
    def stream_chat(self, messages)            # 逐 token 返回(打字机)
    def embed(self, text) -> list[float]       # 文本转向量(知识库用)
```
**为什么**: 之后凡是要调 LLM(Agent 循环/多Agent/规划)都只 `self.llm.xxx(...)`;
哪天换 OpenAI/通义/本地模型, 只改这一个文件, 别处零改动(分层的好处)。

## core/agent.py — 一句话:ReAct 循环(大脑)
两大角色:
- **AgentState**: 装"这次执行的现场" = `messages`(全部对话+工具结果)、`tool_calls`、`iteration`(跑到第几轮)、`status`。可 `to_dict/from_dict`(供 checkpoint 存/恢复)。
- **Agent**: 真正的循环。
  - `register_tool(name, schema, func)`: 把工具塞进 `self.tools`(给LLM看schema)+`self.tool_functions`(真正执行)。
  - `think(task)` —— 核心 ReAct 循环, 逻辑:
    ```
    初始化: messages 加 system(人设) + user(你的问题)
    循环 { 最多 max_iterations=30 轮:
      1) response = self._call_llm()   # 把 messages+全部工具schema 给LLM
      2) LLM 返回两类之一:
         a) 想调工具 -> msg.tool_calls:  逐个执行 self.tool_functions[名字](参数)
                                         结果以 role="tool" 回填 messages, 继续下一轮
         b) 不给工具 -> 这是最终答案, return
    }
    ```
    是不是朴素? LLM 就像个"会点名的调度": 它读完你给的能用工具清单, 说"我要用 dns_lookup", 我们真的去跑 dig, 把结果塞回给 LLM, 它再决定下一步。这就是 **ReAct(Reason+Act)**, 也是 Agent 的本质。
  - `stream_think(task)`: 同 think, 但把上面**每一轮的过程**用 `yield` 逐步吐出去, 事件有 `llm/tool_call/tool_result/done`, 前端 SSE 就能"看着它干活"。
  - `_handle_tool_calls(msg)`: 拆 LLM 要调的工具, 执行, 结果截断(<=2000字)后回填。
  - **高级**(对齐 Go): `set_context_budget`(历史超预算自动压缩防上下文爆)、`set_checkpoint`(每轮存状态)、`resume_from`(中断后从断点续跑)。
**为什么这样写**: 不引入框架, 循环就是裸 `for`, 因为你要"看得懂"; 也和 Go 版 agent.go 的循环语义一致(maxIterations/tool_calls/terminate)。

## core/tools.py — 一句话:给 Agent 上弹药
`ToolManager` 两个核心方法:
```python
def load_all(self, dir):          # 遍历 tools/configs/*.yaml, 全灌进 ToolRegistry
def attach_to_agent(self, agent): # 把 registry 里每条工具做两件事:
                                  #   agent.tools.appendChild(schema)   ← 给LLM看
                                  #   agent.tool_functions[name]=func   ← 供执行
```
**为什么**: 让"在 configs 放一个 YAML, 任意 BaseAgent 天生就会用" —— 你不用为每工具写胶水代码。

## core/context_budget.py — 一句话:别让上下文爆掉
- `is_context_overflow_error(err)`: 识别 API "上下文太长"报错(匹配13种error文案)。
- `estimate_tokens(text)`: 中文≈1字/token, 英文≈4字符/token 的粗略估算。
- `compress_history(messages, max_tokens)`: 超预算时保留 system+最近几条, 早期历史换成一则"(历史已压缩)"占位。
**为什么**: 长会话工具结果越堆越多, 不压缩迟早超模型窗口; Go 版有同样的 context_budget。

## core/checkpoint.py — 一句话:把"干到一半"存下来
`CheckpointStore`: 每条 checkpoint 存成一个文件 `data/checkpoints/<id>.ckpt`(对齐 Go fileCheckPointStore), 有 `save(id, dict)/load(id)/list()`。
配合 Agent.set_checkpoint 每轮存状态, 中断后 `resume_from(id)` 接着跑, 不重来。

---
**核心链路一句话**: `tools.py 给 agent 挂上武器 → think 循环里 LLM 决策调武器 → 结果回填再决策 → 直到给最终答案；过程可流式(stream_think)、可断点(agent.py+checkpoint)、可防爆(agent.py+context_budget)`。
