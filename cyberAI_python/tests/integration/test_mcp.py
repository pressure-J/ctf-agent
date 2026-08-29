"""MCP 客户端集成测试: 跑 examples/mcp_demo.py(独立子进程) 验证连外部MCP+发现+调用。
注: 不在此进程内 asyncio.run(会与 pytest 的 anyio 插件 cancel-scope 冲突), 用子进程隔离。
"""
import os, sys, unittest, subprocess
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMCPClient(unittest.TestCase):
    def test_connect_list_call(self):
        r = subprocess.run([sys.executable, os.path.join(BASE, "examples/mcp_demo.py")],
                           capture_output=True, text=True, cwd=BASE, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("add", r.stdout)
        self.assertIn("DONE:", r.stdout)


if __name__ == "__main__":
    unittest.main()
