from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),      # API密钥
    base_url=os.getenv("DEEPSEEK_BASE_URL")     # API地址
)

response=client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role":"user","content":"解释一下什么是agent"}
    ],
    max_tokens=512
)

print(response.choices[0].message.content)
