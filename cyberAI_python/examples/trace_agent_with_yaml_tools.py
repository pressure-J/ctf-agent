"""完整集成闭环演示(不联网):
tools/configs/*.yaml -> ToolRegistry -> 桥接进 Agent.tools -> think() 里被LLM决策调用
运行: python examples/trace_agent_with_yaml_tools.py
"""
import os, sys, subprocess as sp
os.environ["OPENAI_API_KEY"]="sk-test-mock"
os.environ["DEEPSEEK_API_KEY"]="sk-test-mock"
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE); os.chdir(BASE)
from tools.registry import ToolRegistry
from core.agent import Agent

# 1) 从 2 个 YAML 加载工具库
reg=ToolRegistry()
for yml in ["tools/configs/nmap.yaml","tools/configs/dns.yaml"]:
    reg.register_from_yaml(yml)
print("从 YAML 加载出的工具:", list(reg.tools.keys()))

# 2) 桥接进 Agent(把 registry 的 func+schema 喂给 self.tools/self.tool_functions)
a=Agent(name="工具Agent", system_prompt="你是侦察Agent, 优先用工具获取信息再回答。")
for name,tool in reg.tools.items():
    fdef=tool["schema"]["function"]
    a.register_tool(name, fdef["description"], tool["function"], fdef["parameters"])
print("Agent 现有工具(schema):", [t["function"]["name"] for t in a.tools])

# 3) mock LLM: 决策调用 dns_lookup(它来自 dns.yaml)
calls=[]
def fake_llm(messages, tools, **kw):
    calls.append(list(messages))
    n=sum(1 for m in messages if m["role"]=="tool")
    roles=" → ".join(m["role"] for m in messages)
    print(f"  第{len(calls)}次调LLM | 历史{len(messages)}条: {roles}")
    if n==0:
        print("   >>> LLM决策: 调用 dns_lookup (这工具是刚从 dns.yaml 加载进来的)")
        return {"choices":[{"message":{"role":"assistant","content":None,
            "tool_calls":[{"id":"c1","type":"function",
              "function":{"name":"dns_lookup","arguments":"{\"target\": \"example.com\"}"}}]}}]}
    return {"choices":[{"message":{"role":"assistant","content":"example.com 的DNS记录已查到"}}]}
a.llm.chat_with_tools=fake_llm

# 4) 拦截 subprocess: 只打印拼出的命令, 不真跑 dig
def fake_run(cmd,**kw):
    class R: returncode=0; stdout="example.com. 3600 IN A 1.2.3.4"
    print("   [执行] 拼接命令:", cmd)
    return R
sp.run=fake_run

print("\n:: think('查一下 example.com 的 DNS') ::")
ans=a.think("查一下 example.com 的 DNS")
print("最终输出:", repr(ans))
print("Agent 实际调用过的工具:", [t["name"] for t in a.state.tool_calls])
