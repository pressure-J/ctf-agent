FROM python:3.12-slim

WORKDIR /app

# 最小系统依赖(常用工具 dig/nmap; 重扫描工具如需要把注释打开再加)
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsutils curl nmap git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8080
# 生产: 直接 uvicorn(避开 server.py 的 reload=True)
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]
