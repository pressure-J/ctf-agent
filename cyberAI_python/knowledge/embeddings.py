"""
嵌入封装 - 本地 hashed n-gram 向量(L2 归一)。
dims=1024 + 字符 unigram/bigram/trigram + 英文/数字整词加权, 提高关键词命中。
可替换为 llm.embed()/sentence-transformers(保持 embed(text)->list[float] 接口)来获得语义级质量。
"""
import zlib, re


class LocalEmbedder:
    def __init__(self, dim: int = 1024):
        self.dim = dim

    def _h(self, s): return zlib.crc32(s.encode()) % self.dim

    def embed(self, text: str):
        vec = [0.0] * self.dim
        t = text.lower()
        for i in range(len(t)):
            vec[self._h(t[i])] += 1
        for i in range(len(t) - 1):
            vec[self._h(t[i:i + 2])] += 2
        for i in range(len(t) - 2):
            vec[self._h(t[i:i + 3])] += 1
        for w in re.findall(r"[a-z0-9]+", t):   # 英文/数字整词(SQL/injection/id 等)
            vec[self._h(w)] += 5
        norm = sum(x * x for x in vec) ** 0.5
        return [x / norm for x in vec] if norm else vec

    def embed_batch(self, texts):
        return [self.embed(t) for t in texts]
