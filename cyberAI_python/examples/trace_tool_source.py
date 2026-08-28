"""工具来源链路: 一个 YAML 文件 -> 注册表 -> LLM 可调用的工具 schema + 可执行函数。
运行: python examples/trace_tool_source.py
链路:
  tools/configs/nmap.yaml (纯数据, 没写代码)
     -> ToolRegistry.register_from_yaml() 读它, 动态生成:
           1) JSON schema  -> 给 LLM 当"调用契约"
           2) 执行函数     -> 真正 subprocess 跑 nmap
"""
import os, sys, subprocess as sp, json
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE); os.chdir(BASE)
from tools.registry import ToolRegistry

print("=" * 8, "第1步: YAML 里到底写了什么(纯数据) ", "=" * 8)
yml=open("tools/configs/nmap.yaml",encoding="utf-8").read()
print(yml)

print("=" * 8, "第2步: 注册表怎么把它变成工具 ", "=" * 8)
reg=ToolRegistry()
reg.register_from_yaml("tools/configs/nmap.yaml")
tool=reg.tools["nmap_scan"]
print("注册表里这个工具的字段:", list(tool.keys()))
print("  category:", tool["category"], "| enabled:", tool["enabled"], "| 有函数:", callable(tool["function"]))

print("=" * 8, "第3步: 给 LLM 的'调用契约'(JSON schema) ", "=" * 8)
for s in reg.get_schemas():
    print(json.dumps(s, ensure_ascii=False, indent=2))

print("=" * 8, "第4步: 真正执行 -> 命令怎么拼出来(不真跑, 拦截 subprocess) ", "=" * 8)
captured={}
def fake_run(cmd_parts, capture_output=True, text=True, timeout=60):
    captured["cmd"]=cmd_parts
    class R:
        returncode=0
        stdout="[演示] 命令已拼出: " + " ".join(cmd_parts)
        stderr=""
    return R()
sp.run=fake_run  # 只在脚本进程内生效

result=reg.execute("nmap_scan", {"target":"scanme.nmap.org", "ports":"22,80"})
print("  -> 被拼接并执行的命令:", captured["cmd"])
print("  -> 返回给 LLM 的结果  :", result)

print("=" * 8, "第5步: 这个工具现在能进 Agent 的 self.tools ", "=" * 8)
print("  reg.get_schemas() 长度 = 可用工具数, 它就是你 think() 里 self.tools 的来源。")
print("  结论: 加一个工具 = 写一个 nmap.yaml 这样的文件, 不碰任何 Python。")
