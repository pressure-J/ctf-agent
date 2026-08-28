"""真实侦察: 真 DeepSeek 决策 + 真 nmap 扫目标常用端口 + 服务分析。"""
import os, sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)
from agents.base_agent import BaseAgent

TARGET = "114.55.93.214"   # 你自己的公网靶场(vulhub)
PORTS  = "80,443,8080,22,3389,3306"

a = BaseAgent(name="侦察Agent",
              tools=["nmap_scan"],            # 白名单: 只挂 nmap
              system_prompt="你是渗透测试侦察Agent, 用 nmap 扫描目标, 列出开放端口与运行的服务, 再给出风险评估。")
print("[白名单工具]:", [t["function"]["name"] for t in a.core.tools])

q = f"用 nmap_scan 扫描 {TARGET} 的常用端口 {PORTS}, 列出开放端口及其运行的服务, 并简要总结暴露面与风险。"
print(">>> 任务:", q)
ans = a.think(q)
print("\n=== DeepSeek 最终分析 ===\n")
print(ans)
