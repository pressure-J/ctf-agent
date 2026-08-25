import concurrent.futures
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

# 新增：基础 Agent 类（你代码里缺失了这个类）
class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )

    def think(self, task: str) -> str:
        """Agent 核心思考逻辑"""
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.role},
                    {"role": "user", "content": task}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"API 调用失败: {str(e)}"

class ParallelExecutor:
    """并行执行器"""
    
    def __init__(self, agents: list):
        """
        参数:
            agents: Agent列表，会同时执行
        """
        self.agents = agents
    
    def run(self, task: str) -> dict:
        """
        并行执行所有Agent
        
        参数:
            task: 任务描述
        
        返回:
            所有Agent的结果
        """
        # 修复：闭合 f-string 引号（原代码这里少了一个 "）
        print(f"\n{'='*60}")
        print(f"并行执行 {len(self.agents)} 个Agent")
        print(f"{'='*60}")
        
        results = {}
        
        # 使用线程池并行执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.agents)) as executor:
            # 提交所有任务
            future_to_agent = {
                executor.submit(agent.think, task): agent.name
                for agent in self.agents
            }
            
            # 等待所有完成
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    result = future.result(timeout=120)
                    results[agent_name] = result
                    print(f"\n✓ {agent_name} 完成")
                except Exception as e:
                    results[agent_name] = f"执行失败: {str(e)}"
                    print(f"\n✗ {agent_name} 失败: {e}")
        
        return results
    
    def merge_results(self, results: dict) -> str:
        """
        合并所有结果
        
        参数:
            results: 各Agent的结果
        
        返回:
            合并后的结果
        """
        merged = "## 综合扫描结果\n\n"
        
        for agent_name, result in results.items():
            merged += f"### {agent_name}\n{result}\n\n"
        
        return merged


# 使用示例
if __name__ == "__main__":
    
    # 创建多个并行Agent
    agents = [
        BaseAgent("端口扫描", "你是端口扫描专家，分析开放端口和服务"),
        BaseAgent("目录扫描", "你是目录扫描专家，发现隐藏路径"),
        BaseAgent("子域名", "你是子域名枚举专家，发现子域名"),
    ]
    
    # 并行执行
    executor = ParallelExecutor(agents)
    results = executor.run("扫描 http://example.com")
    
    # 合并结果
    merged = executor.merge_results(results)
    print("\n" + merged)
