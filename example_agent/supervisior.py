# supervisor_agent.py
# 监督模式：一个Agent负责路由，多个专家Agent执行

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class BaseExpertAgent:
    """专家Agent基类，统一接口"""
    def __init__(self, system_prompt):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.system_prompt = system_prompt  # 专家专业领域提示词

    def think(self, task: str) -> str:
        """执行任务思考并返回结果"""
        print(f"【专家】正在处理任务：{task}")
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": task}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()


class WebSecAgent(BaseExpertAgent):
    """Web安全专家：负责SQL注入、XSS、文件上传等Web漏洞"""
    def __init__(self):
        super().__init__(
            system_prompt="你是专业的Web安全专家，擅长SQL注入、XSS、CSRF、文件上传、命令执行等Web漏洞检测与利用，给出专业、简洁的安全分析方案。"
        )


class CryptoAgent(BaseExpertAgent):
    """密码学专家：负责加解密、编码、哈希、RSA/AES等问题"""
    def __init__(self):
        super().__init__(
            system_prompt="你是密码学专家，擅长各种编码解码、古典密码、对称加密、非对称加密、哈希破解，能快速分析并解密各类密码题目。"
        )


class MiscAgent(BaseExpertAgent):
    """杂项专家：负责隐写、流量分析、压缩包修复、取证等Misc问题"""
    def __init__(self):
        super().__init__(
            system_prompt="你是CTF杂项专家，擅长图片隐写、流量分析、压缩包修复、文件取证、音频视频隐写分析。"
        )


class Supervisor:
    """监督者 - 负责任务路由"""
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL")
        )
        self.experts = {}  # 专家Agent字典

    def register_expert(self, name: str, agent):
        """注册专家Agent"""
        self.experts[name] = agent
        print(f"注册专家: {name}")

    def route(self, task: str) -> str:
        """
        路由任务到合适的专家
        参数: task: 任务描述
        返回: 专家名称
        """
        # 构建专家列表
        expert_list = "\n".join([
            f"- {name}: {agent.system_prompt[:100]}"
            for name, agent in self.experts.items()
        ])

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                # 这里修复了：给 content 加上引号
                {"role": "system", "content": f"""你是任务路由器。
根据任务类型，选择最合适的专家。

可用专家:
{expert_list}

只返回专家名称，不要其他内容。"""},
                {"role": "user", "content": task}
            ],
            max_tokens=50
        )

        expert_name = response.choices[0].message.content.strip()

        # 容错：不存在则返回第一个专家
        if expert_name not in self.experts:
            expert_name = list(self.experts.keys())[0]

        return expert_name

    def run(self, task: str) -> str:
        """执行任务流程"""
        print(f"\n{'='*60}")
        print(f"Supervisor 接收任务")
        print(f"{'='*60}")
        print(f"任务: {task}")

        # 路由到专家
        expert_name = self.route(task)
        expert = self.experts[expert_name]

        print(f"\n路由到: {expert_name}")

        # 执行任务
        result = expert.think(task)

        print(f"\n{'='*60}")
        print(f"任务完成")
        print(f"{'='*60}")
        print(f"最终结果：\n{result}")

        return result


# 使用示例
if __name__ == "__main__":
    # 创建监督者
    supervisor = Supervisor()

    # 注册三个专家
    supervisor.register_expert("web安全", WebSecAgent())
    supervisor.register_expert("crypto", CryptoAgent())
    supervisor.register_expert("misc", MiscAgent())

    # 测试任务
    result = supervisor.run("http://target.com/login.php 有SQL注入漏洞")
