# 05 · 两个"能力引擎":DAG工作流 + 向量RAG

## 一、workflow/ — 把"套路"做成一张图
**一句话**: 你想把某次渗透的步骤固定成"先扫描→没结果就试web→最后写报告", 用一张 DAG 图描述, 引擎按依赖顺序自动跑。

**workflow/node.py**: `WorkflowNode(id, type, config)`。type 有 `agent/tool/condition/merge...`; 一个节点就是图里一个方块。
**workflow/graph.py**: `WorkflowGraph` 装节点+有向边。
- `add_edge(from,to)`: A→B 表示"B 等 A 跑完"。
- `topological_order()`: **Kahn 拓扑排序** —— 反复找"入度=0"的节点先做, 删掉后继续。得到"谁先谁后都合法"的顺序; 有环则返回 None(检测死锁)。
- `validate()`: 就是"能否排出一个拓扑序"(有环=假)。
**workflow/state.py**: `WorkflowState` = 一块共享黑板。每个节点结果写进去, 下游节点可读, 支持 `${node.字段}` 引用。
**workflow/executor.py**: `WorkflowExecutor.execute` —— 按拓扑序遍历节点:
- `agent` 节点 → 调对应 Agent 的 `think(task, context=黑板)`;
- `tool` 节点 → 调 tool_registry.execute;
- 每节点结果 `state.set_node_result` 记黑板。
**workflow/engine.py**: 对外门户 `WorkflowEngine.execute(definition, input_data)` = 构建图→校验→交给 executor 跑。

**一个例子(分叉+汇合)**:
```yaml
nodes: [a 扫描, b web, c 密码, d 报告]
edges: a->b, a->c, b->d, c->d    # a先; b、c拿a结果并行; 等b、c都完才d
```
引擎拓扑序 = [a, b, c, d], 保证 d 一定在所有依赖后, 这就是"DAG"。

**与 Go 差距**: Go 版 workflow 更重, 还有表达式求值/jsonpath/dry_run(预演)/checkpoint/HITL(人工门控)。我们做了核心拓扑, 这些高级特性待补。

## 二、knowledge/ — 让 Agent 学会"查资料再答"
**一句话**: 把一堆 markdown 知识文档变成"能按意思搜索"的向量库, 查询时返回最相关片段喂给 Agent。

**为什么向量搜索**: 关键词搜"SQL注入"可能漏写"SQLi/报错注入"的文档; 向量把文本变成一串数字, "意思相近"的数字也相近, 用**余弦相似度**找 TopK。

**四个文件分工**:
- `embeddings.py`: `LocalEmbedder.embed(text) -> list[float]`。默认把文本的字符 bigram/单词哈希进 1024 维向量并做 L2 归一(离线、稳定、不依赖外部key)。
- `vector_store.py`: `VectorStore.add(...)` 存向量; `search(qvec, top_k, threshold)` 遍历算余弦(归一后=点积), 过滤阈值, 按相似度取 TopK。
- `base.py`: `KnowledgeBase` 把上面组合起来 —— `index_dir("knowledge/docs")` 把每篇 md 切块(每块400字)embed 后入库, `retrieve_context(query)` 检索出带 score 的片段。
- `retriever.py`: 便捷入口, **懒加载单例** —— 第一次调用才去索引 docs+skills(共552个chunk), 之后复用。

**Web 里谁再用**: `deps.search_knowledge_base` 从"关键词匹配"改成了 `retriever.retrieve`(向量TopK); `/api/knowledge/search` 就走它。

**诚实短板(和 Go 比)**: Go 用 eino **真语义 embedding**(有语言模型)+rerank+multiQuery, 所以"弱口令"这种要理解意思的查询命中好; 我们默认用**本地哈希向量**(无语言模型), 关键词型的查得好, 语义型的一般。要提升: 把 `LocalEmbedder` 换成 `llm.embed()`(OpenAI兼容)或 `sentence-transformers` 一行就换 —— 接口已留。
