"""
命令行入口 - 交互式使用 Agent
用法: python main.py "你的任务"
"""
import sys
from core.agent import Agent

def run(task: str):
    agent = Agent(name="CTF专家")
    result = agent.think(task)
    print("\n=== 结果 ===\n")
    print(result)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    run(sys.argv[1])
