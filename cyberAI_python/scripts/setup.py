"""一键安装脚本 - 创建venv+安装依赖+初始化"""
import subprocess
import sys

def main():
    print("[1/3] 创建虚拟环境...")
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    print("[2/3] 安装依赖...")
    subprocess.run([".venv/bin/pip", "install", "-r", "requirements.txt"], check=True)
    print("[3/3] 初始化数据库与工具...")
    # TODO: 导入 database/db.py 初始化 + 注册工具
    print("完成! 运行: source .venv/bin/activate && python server.py")

if __name__ == "__main__":
    main()
