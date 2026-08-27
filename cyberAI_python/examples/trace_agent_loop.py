"""
链路追踪演示 —— 亲眼看到 Agent think() 内部, 数据链路怎么一步步形成。
不联网: 用一个"懂工具"的假 LLM 驱动真实 think() 循环, 把每一环打印出来。
运行: python examples/trace_agent_loop.py
链路(一次带工具的 think)的完整形态:
  system        Agent身份
  user          任务
  ── 第1次调LLM(带上工具schema) ──
  assistant    LLM决策: 调用工具 http_get(...)   (tool_calls)
  tool         工具执行结果(回填给LLM)
  ── 第2次调LLM(历史已包含工具结果) ──
  assistant    最终答案
"""
import os, sys
os.environ["OPENAI_API_KEY"]="sk-test-mock"; os.environ["DEEPSEEK_API_KEY"]="sk-test-mock"
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE); os.chdir(BASE)
from core.agent import Agent

snapshots=[]   # 记下每次发给LLM的历史快照, 用于对比"链路演变"

def show(m):
    r=m["role"]
    c=str(m.get("content") or "")
    if r=="system":   return f"  system    {c[:38]}..."
    if r=="user":     return f"  user      {c[:38]}"
    if r=="assistant":
        if m.get("tool_calls"):
            t=m["tool_calls"][0]["function"]
            return f"  assistant (tool_calls) -> 调 {t['name']}({t['arguments'][:24]})"
        return f"  assistant {c[:38]}"
    if r=="tool":     return f"  tool      {c[:38]}"
    return f"  {r:8s} {c[:38]}"

def fake_llm(messages, tools, tool_choice="auto", temperature=None, max_tokens=None):
    snapshots.append(list(messages))
    print(f"\n===== 第{len(snapshots)}次调 LLM | 此时历史共 {len(messages)} 条消息 | 可用工具 {len(tools or [])}个 =====")
    for m in messages: print(show(m))
    n_tool=sum(1 for m in messages if m["role"]=="tool")
    if n_tool==0:
        print("  >>> LLM 决策: 信息不够, 调用工具 http_get 抓取页面内容")
        return {"choices":[{"message":{"role":"assistant","content":None,
            "tool_calls":[{"id":"c1","type":"function",
                "function":{"name":"http_get","arguments":'{"url": "https://example.com"}'}}]}}]}
    print("  >>> LLM 决策: 已拿到工具结果, 直接回答工具")
    return {"choices":[{"message":{"role":"assistant","content":"标题是: Example"}}]}

def http_get(url):
    print(f"  [执行工具] http_get(url={url})")
    r="<title>Example Domain</title>"
    print(f"  [工具返回] {r}")
    return r

# ---- 组装 Agent 并注入假 LLM + 真工具 ----
a=Agent(name="侦察Agent", system_prompt="你是网络侦察Agent, 优先调用工具获取信息再回答。")
a.llm.chat_with_tools=fake_llm
a.register_tool(name="http_get", description="用HTTP GET抓取URL内容",
                func=http_get,
                parameters={"type":"object",
                            "properties":{"url":{"type":"string"}},
                            "required":["url"]})

print("=== 开始 think('抓取 https://example.com 并告诉我标题') ===")
答案=a.think("抓取 https://example.com 并告诉我标题")

print("\n======= 链路形成过程（消息如何一步步累积） =======")
print("  第1次调LLM前 历史条数: %d  (%s)"   % (len(snapshots[0]), " → ".join(m["role"] for m in snapshots[0])))
print("  第2次调LLM前 历史条数: %d  (%s)"   % (len(snapshots[1]), " → ".join(m["role"] for m in snapshots[1])))
print("  工具调用次数: %d  (%s)" % (len(a.state.tool_calls), a.state.tool_calls[0]["name"]))
print("\n  >>> 最终输出: %r" % 答案)
