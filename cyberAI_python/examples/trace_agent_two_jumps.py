"""两跳链路演示: LLM 连续决策调用 2 个工具, 历史从 2 条累积到 6 条。
运行: python examples/trace_agent_two_jumps.py
链路形态:
  [system,user]                          2条
   → http_get                             → [.., assistant(tc1), tool]     4条
   → base64_decode(解码http_get结果)       → [.., assistant(tc2), tool]     6条
   → 直接回答
"""
import os, sys, base64
os.environ["OPENAI_API_KEY"]="sk-test-mock"; os.environ["DEEPSEEK_API_KEY"]="sk-test-mock"
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE); os.chdir(BASE)
from core.agent import Agent

snap=[]  # 每次发给LLM的历史快照

def show(m):
    r=m["role"]
    if r=="assistant" and m.get("tool_calls"):
        f=m["tool_calls"][0]["function"]
        return f"assistant(tool_calls) -> {f['name']}"
    return f"{r:9s} {str(m.get('content') or '')[:40]}"

def fake_llm(messages, tools, tool_choice="auto", **kw):
    snap.append(list(messages))
    n=sum(1 for m in messages if m["role"]=="tool")
    print(f"\n===== 第{len(snap)}次调LLM | 历史 {len(messages)} 条: "
          f"{' → '.join(m['role'] for m in messages)}")
    for m in messages: print("   ", show(m))
    tc=lambda name,args: {"choices":[{"message":{"role":"assistant","content":None,
        "tool_calls":[{"id":f"c{len(snap)}","type":"function",
                       "function":{"name":name,"arguments":args}}]}}]}
    if n==0:
        print("   >>> LLM决策: 先抓取页面(http_get)")
        return tc("http_get", '{"url": "https://example.com"}')
    if n==1:
        print("   >>> LLM决策: 内容是base64, 解码它(base64_decode)")
        return tc("base64_decode", '{"data": "aGVsbG8gd29ybGQ="}')
    print("   >>> LLM决策: 已解码, 直接回答")
    return {"choices":[{"message":{"role":"assistant","content":"解码结果是: hello world"}}]}

def http_get(url):
    r="<title>aGVsbG8gd29ybGQ=</title>"   # 一个base64串
    print(f"  [执行工具] http_get -> {r}")
    return r
def base64_decode(data):
    r=base64.b64decode(data.encode()).decode()
    print(f"  [执行工具] base64_decode('{data}') -> {r}")
    return r

a=Agent(name="多跳Agent", system_prompt="你是侦察Agent, 用工具逐步获取并解码信息再回答。")
a.llm.chat_with_tools=fake_llm
a.register_tool("http_get","抓取URL",http_get,
    {"type":"object","properties":{"url":{"type":"string"}},"required":["url"]})
a.register_tool("base64_decode","base64解码",base64_decode,
    {"type":"object","properties":{"data":{"type":"string"}},"required":["data"]})

print("=== think('抓取页面并告诉我解码后内容') ===")
ans=a.think("抓取页面并告诉我解码后内容")

print("\n===== 链路演变(历史长度) =====")
for i,s in enumerate(snap):
    print(f"  第{i+1}次调LLM : {len(s)} 条  ({' → '.join(m['role'] for m in s)})")
print("工具调用顺序:", [t["name"] for t in a.state.tool_calls])
print("最终输出:", repr(ans))
