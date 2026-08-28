"""注册任意 YAML 工具并演示命令拼装(拦截 subprocess, 不真执行)。
用法: python examples/register_any_tool.py tools/configs/你的工具.yaml
"""
import os, sys, subprocess as sp, json
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BASE); os.chdir(BASE)
from tools.registry import ToolRegistry

yml=sys.argv[1] if len(sys.argv)>1 else "tools/configs/dns.yaml"
reg=ToolRegistry(); reg.register_from_yaml(yml)
tool_name=list(reg.tools.keys())[0]
schema=reg.get_schemas()[0]
print("YAML 文件:", yml, " -> 注册为工具:", tool_name)
props=schema["function"]["parameters"]["properties"]

print("\n生成给 LLM 的 schema(调用契约):")
print(json.dumps(schema, ensure_ascii=False, indent=2))

demo={"target":"example.com","domain":"example.com","host":"example.com",
      "url":"https://example.com","record_type":"A","ports":"22,80",
      "output":"demo.txt","file":"demo.txt","user":"admin","wordlist":"list.txt"}
args={name: demo.get(name, f"demo_{name}") for name in props}
print("\n构造演示参数:", args)

class R:
    returncode=0; stdout=""
def fake_run(cmd, **kw):
    print("  -> [演示拦截,不真跑] 拼接命令:", cmd)
    R.stdout="[演示] 已拼命令: "+" ".join(cmd)
    return R
sp.run=fake_run   # 拦截, 不真执行外部命令

print("\n:: 执行工具 execute(%r, args) ::" % tool_name)
result=reg.execute(tool_name, args)
print("工具返回给 LLM 的结果:", result)
