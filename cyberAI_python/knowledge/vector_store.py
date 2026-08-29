"""
向量存储 - 存向量+元数据, 余弦相似检索(TopK + 阈值)。
normalized 后余弦 = 点积, O(N) 遍历即可(小规模够用)。
"""
class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.items = []   # [{id,text,source,vec}]

    def add(self, id_: str, text: str, source: str, vec):
        self.items.append({"id": id_, "text": text, "source": source, "vec": vec})

    def search(self, qvec, top_k: int = 5, threshold: float = 0.0):
        scored = []
        for it in self.items:
            s = sum(x * y for x, y in zip(qvec, it["vec"]))   # 点积=余弦(已归一)
            if s >= threshold:
                scored.append((s, it))
        scored.sort(key=lambda x: -x[0])
        return scored[:top_k]

    def __len__(self):
        return len(self.items)
