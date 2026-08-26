FROM python:3.12-slim

WORKDIR /app

# 系统依赖(扫描工具)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap sqlmap nikto gobuster ffuf hydra nuclei subfinder whatweb \
    iputils-ping dnsutils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python", "server.py"]
