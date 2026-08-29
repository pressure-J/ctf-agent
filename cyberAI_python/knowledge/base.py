"""
知识库 - 组合 embedder + vector_store: 索引 md / 检索 / 取上下文。
对齐 Go internal/knowledge 的 retriever(TopK+threshold) 核心。
"""
from pathlib import Path
from knowledge.embeddings import LocalEmbedder
from knowledge.vector_store import VectorStore


class KnowledgeBase:
    def __init__(self, embedder=None, store=None, chunk: int = 400):
        self.embedder = embedder or LocalEmbedder()
        self.store = store or VectorStore(self.embedder.dim)
        self.chunk = chunk

    def index_file(self, path) -> int:
        text = Path(path).read_text(encoding="utf-8")
        n = 0
        for i in range(0, len(text), self.chunk):
            c = text[i:i + self.chunk].strip()
            if not c:
                continue
            self.store.add(f"{Path(path).name}:{i}", c, Path(path).name,
                           self.embedder.embed(c))
            n += 1
        return n

    def index_dir(self, dir_path) -> int:
        total = 0
        for md in sorted(Path(dir_path).glob("*.md")):
            try:
                total += self.index_file(md)
            except Exception:
                pass
        return total

    def search(self, query, top_k: int = 5, threshold: float = 0.0):
        return self.store.search(self.embedder.embed(query), top_k, threshold)

    def retrieve_context(self, query, top_k: int = 3, threshold: float = 0.0):
        return [{"text": h[1]["text"], "source": h[1]["source"],
                 "score": round(h[0], 4)}
                for h in self.search(query, top_k, threshold)]
