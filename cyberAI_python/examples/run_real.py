"""真实端到端: 真 DeepSeek 决策 + 真执行 YAML 工具(dig)。"""
import os, sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from agents.base_agent import BaseAgent

a = BaseAgent(name="真侦察Agent",
              tools=["dns_lookup", "nmap_scan"],   # 白名单: 只挂这2个, 避免91份schema撑爆
              system_prompt="你是侦察Agent, 优先调用工具获取信息后再回答。")
print("[Agent 白名单工具]:", [t["function"]["name"] for t in a.core.tools])
print()
ans = a.think("用 dns_lookup 查询 example.com 的 DNS 记录, 并简要总结")
print("\n=== 最终回答 ===\n")
print(ans)
