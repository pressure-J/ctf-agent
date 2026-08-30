# 03 · 工具库(91个YAML) + 多Agent("一队特工")

## 一、工具:纯数据声明, 不写代码
Go 版工具就是 90 个 YAML(指向外部命令), 我们照搬成 `tools/configs/*.yaml` **91 个**, 零 Python 实现。

**一个工具长这样**(tools/configs/dns.yaml):
```yaml
name: dns_lookup
description: 查询域名的DNS记录
category: recon
command: dig                    # 实际执行的命令
parameters:
  - name: target                # LLM 需要传入的参数
    type: string
    description: 要查询的域名
    required: true
  - name: record_type
    type: string
    default: A
timeout: 30
```

**tools/registry.py** 把它变成 Agent 能用的工具:
- `register_from_yaml`: 读 YAML → 生成一个函数(闭包, 把参数按 `positional/flag/template` 拼出 shell 命令给 subprocess 执行) + 一个 JSON schema(给LLM看参数)。
  - **为什么支持三种拼法**: 有的命令要 `dig example.com`(位置), 有的要 `nmap -T4 1.1.1.1`(flag), 有的是模板 —— 不同工具参数习惯不同。这是放进来时对齐 Go 的关键点。
- `execute(name, args)`: 找函数, 传参执行, 回结果。

**tools/mcp_client.py**(你要的"连外部MCP"): `MCPClient` 用官方 SDK 连外部 MCP 服务器(stdio/SSE), 能 `list_tools`(拉它的工具)+`call_tool`+`make_sync_tool`(把外部工具转成 schema+函数并入我们注册表)。这样 Agent 不止用本地91个, 还能借 Burp/别的 MCP 的武器。

## 二、多 Agent:一名主管 + 一队专业特工
**agents/base_agent.py**: 通用 Agent 工厂。构造时 `ToolManager().load_all + attach_to_agent`, 于是任何 BaseAgent 天生带 91 工具; `tools=` 可白名单。它就是"自带装备的特工"。

**agents/roles_loader.py**: 读取 `agents/roles/*.yaml`(13个角色:CTF/Web扫描/提权…, 从Go搬来), 用每个角色的 `user_prompt`(人设)建一个 BaseAgent → `build_role_agent(name)`。

**agents/supervisor_agent.py**(分工的关键, 对齐 Go supervisor):
```python
class SupervisorAgent(BaseAgent):
    def __init__(self, name, sub_agents):   # sub_agents: {"角色名": BaseAgent}
        ...
        for 每个子Agent:                     # 把"每个子Agent"注册成主管的一个"工具"
            self.core.tools.append({name: 角色名, description: 擅长什么,
                                    parameters:{task: "要交给它的任务"}})
            self.core.tool_functions[角色名] = 丢弃->调 sub.think(task)
```
主管的 ReAct 循环(等同 core.agent.think)里, LLM 看到"工具清单=各专业子Agent",
于是会说"叫 CTF 角色去干这个" → 我们真的调那个子Agent的 think → 结果回填 → 主管汇总。
**这就是 Go 的 supervisor 模式**, 拆成"调度工具"来调用子特工。

**agents/plan_execute_agent.py**: 继承 supervisor 机制, 只换提示词引导"先规划再逐步执行"(对齐 Go plan_execute)。

**agents/orchestrator.py**: 全局管家。按 `config.mode` 建 Agent:
- `single` → 单Agent; `supervisor`/`plan_execute` → 从 roles 用 `_build_role_pool()` 建 **13个角色子Agent池**, 塞给主管;
- 带缓存: 同名 Agent 只建一次, `list_active/destroy` 管理生命周期。

**Why 这样**: 主管做决策、子特工做专业活, 职责清晰; 加新角色只加个 yaml, 主管自动"学会指挥它"。
