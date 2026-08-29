"""知识库向量RAG单元测试: 索引 + 语义检索命中相关文档。"""
import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestKnowledge(unittest.TestCase):
    def test_vec_retrieve_hits_related(self):
        from knowledge.retriever import get_kb, retrieve
        kb = get_kb()
        self.assertGreater(len(kb.store), 50)      # 已索引 552 chunks
        r = retrieve("SQL 注入 利用", top_k=3)
        self.assertGreater(len(r), 0)
        self.assertTrue(any("Injection" in x["source"] or "SQL" in x["source"] for x in r),
                        [x["source"] for x in r])
        r2 = retrieve("业务逻辑 漏洞", top_k=2)
        self.assertTrue(any("业务逻辑" in x["source"] for x in r2),
                        [x["source"] for x in r2])


if __name__ == "__main__":
    unittest.main()
