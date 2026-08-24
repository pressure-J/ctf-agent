import requests
import subprocess
import hashlib
import base64
import re
from urllib.parse import unquote

def sqlmap_scan(url: str, param: str = "id", level: int = 1) -> str:
    """
    SQL注入扫描
    
    参数:
        url: 目标URL（如 http://target.com/page.php?id=1）
        param: 测试的参数名
        level: 扫描级别（1-5，越高越详细）
    
    返回:
        扫描结果
    """
    try:
        cmd = f'sqlmap -u "{url}" -p {param} --level={level} --batch --output-dir=/tmp/sqlmap_out'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return result.stdout[-3000:] if result.stdout else "无输出"
    except Exception as e:
        return f"sqlmap执行失败: {str(e)}"

def dirb_scan(url: str) -> str:
    """
    目录扫描
    
    参数:
        url: 目标URL
    
    返回:
        发现的目录和文件
    """
    try:
        cmd = f'dirb {url} /usr/share/wordlists/dirb/common.txt -r'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return result.stdout[-2000:] if result.stdout else "无输出"
    except Exception as e:
        return f"dirb执行失败: {str(e)}"

def xss_test(url: str, param: str) -> str:
    """
    XSS测试
    
    参数:
        url: 目标URL
        param: 测试的参数名
    
    返回:
        测试结果
    """
    payloads = [
        '<script>alert(1)</script>',
        '<img src=x onerror=alert(1)>',
        '"><script>alert(1)</script>',
        "'><script>alert(1)</script>"
    ]
    
    results = []
    for payload in payloads:
        try:
            test_url = f"{url}?{param}={payload}"
            response = requests.get(test_url, timeout=10)
            if payload in response.text:
                results.append(f"[+] XSS可能: {payload}")
        except:
            pass
    
    return "\n".join(results) if results else "未发现XSS"


# ========== Crypto工具 ==========

def base64_decode(text: str) -> str:
    """Base64解码"""
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return "解码失败"

def base64_encode(text: str) -> str:
    """Base64编码"""
    return base64.b64encode(text.encode()).decode()

def hash_crack(hash_value: str) -> str:
    """
    常见hash识别和破解
    
    参数:
        hash_value: hash值
    
    返回:
        识别结果
    """
    # 常见hash的正则
    patterns = {
        'MD5': r'^[a-f0-9]{32}$',
        'SHA1': r'^[a-f0-9]{40}$',
        'SHA256': r'^[a-f0-9]{64}$',
    }
    
    for hash_type, pattern in patterns.items():
        if re.match(pattern, hash_value, re.I):
            return f"识别为: {hash_type}\n建议使用在线破解: https://crackstation.net/"
    
    return "未识别的hash类型"

def caesar_cipher(text: str, shift: int) -> str:
    """
    凯撒密码解密
    
    参数:
        text: 密文
        shift: 偏移量
    
    返回:
        解密结果
    """
    result = ""
    for char in text:
        if char.isalpha():
            ascii_offset = 65 if char.isupper() else 97
            result += chr((ord(char) - ascii_offset - shift) % 26 + ascii_offset)
        else:
            result += char
    return result

def rot13(text: str) -> str:
    """ROT13解密"""
    return caesar_cipher(text, 13)


# ========== Misc工具 ==========

def extract_strings(file_path: str) -> str:
    """
    从文件中提取可读字符串
    
    参数:
        file_path: 文件路径
    
    返回:
        提取的字符串
    """
    try:
        result = subprocess.run(
            f'strings {file_path}',
            shell=True, capture_output=True, text=True
        )
        # 过滤出可能是flag的行
        lines = result.stdout.split('\n')
        interesting = [l for l in lines if 'flag' in l.lower() or 'ctf' in l.lower() or len(l) > 20]
        return "\n".join(interesting[:50]) if interesting else result.stdout[:2000]
    except Exception as e:
        return f"strings命令失败: {str(e)}"

def hex_decode(hex_str: str) -> str:
    """十六进制解码"""
    try:
        hex_str = hex_str.replace(' ', '').replace('0x', '')
        return bytes.fromhex(hex_str).decode('utf-8', errors='ignore')
    except:
        return "解码失败"

def xor_decode(text: str, key: str) -> str:
    """XOR解密"""
    try:
        result = []
        for i in range(len(text)):
            result.append(chr(ord(text[i]) ^ ord(key[i % len(key)])))  # 修复：缺半个括号
        return ''.join(result)
    except:
        return "解密失败"


# ========== 工具注册 ==========

CTF_TOOLS = {
    "sqlmap_scan": {
        "func": sqlmap_scan,
        "desc": "SQL注入扫描工具",
        "params": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "目标URL"},
                "param": {"type": "string", "description": "测试参数", "default": "id"},
                "level": {"type": "integer", "description": "扫描级别1-5", "default": 1}
            },
            "required": ["url"]
        }
    },
    "base64_decode": {
        "func": base64_decode,
        "desc": "Base64解码",
        "params": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要解码的Base64文本"}
            },
            "required": ["text"]
        }
    },
    "hash_crack": {
        "func": hash_crack,
        "desc": "识别hash类型",
        "params": {
            "type": "object",
            "properties": {
                "hash_value": {"type": "string", "description": "hash值"}
            },
            "required": ["hash_value"]
        }
    },
    "caesar_cipher": {
        "func": caesar_cipher,
        "desc": "凯撒密码解密",
        "params": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "密文"},
                "shift": {"type": "integer", "description": "偏移量"}
            },
            "required": ["text", "shift"]
        }
    },
    "rot13": {
        "func": rot13,
        "desc": "ROT13解密",
        "params": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要解密的文本"}
            },
            "required": ["text"]
        }
    },
    "hex_decode": {
        "func": hex_decode,
        "desc": "十六进制解码",
        "params": {
            "type": "object",
            "properties": {
                "hex_str": {"type": "string", "description": "十六进制字符串"}
            },
            "required": ["hex_str"]
        }
    },
    "send_request": {
        "func": lambda url, method="GET", data=None: requests.request(method, url, data=data, timeout=10).text[:2000],
        "desc": "发送HTTP请求",
        "params": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL"},
                "method": {"type": "string", "enum": ["GET", "POST"], "default": "GET"},
                "data": {"type": "string", "description": "POST数据"}
            },
            "required": ["url"]
        }
    }
}
