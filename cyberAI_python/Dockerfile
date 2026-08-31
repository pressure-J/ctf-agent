FROM python:3.12-slim

WORKDIR /app

# apt 换清华源(CN 直连快, 不依赖宿主代理)
RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' \
        /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g; s|security.debian.org|mirrors.tuna.tsinghua.edu.cn|g' \
        /etc/apt/sources.list
RUN apt-get update && apt-get install -y --no-install-recommends \
    dnsutils curl nmap ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# pip 换清华源
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .
EXPOSE 8080
# 生产: 直接 uvicorn(避开 server.py 的 reload=True)
CMD ["uvicorn", "web.app:app", "--host", "0.0.0.0", "--port", "8080"]