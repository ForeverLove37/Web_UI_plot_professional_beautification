#!/usr/bin/env python3
import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

def debug_server_environment():
    print("=" * 50)
    print("服务器环境调试信息")
    print("=" * 50)
    
    # 1. 检查当前目录和文件
    print("\n1. 当前工作目录和文件:")
    print(f"   工作目录: {os.getcwd()}")
    print(f"   当前文件: {__file__}")
    
    # 2. 检查.env文件
    print("\n2. .env文件检查:")
    env_path = Path('.env')
    if env_path.exists():
        print(f"   ✅ .env文件存在: {env_path.absolute()}")
        with open(env_path, 'r') as f:
            content = f.read()
            print(f"   .env内容: {content[:100]}...")  # 只显示前100字符
    else:
        print(f"   ❌ .env文件不存在")
        # 查找可能的.env文件
        for possible_path in ['.env', '../.env', '/etc/.env']:
            if Path(possible_path).exists():
                print(f"   发现可能的.env文件: {possible_path}")
    
    # 3. 加载环境变量
    print("\n3. 环境变量检查:")
    load_dotenv(override=True)
    api_key = os.getenv('DEEPSEEK_API_KEY')
    print(f"   DEEPSEEK_API_KEY: {'已设置' if api_key else '未设置'}")
    if api_key:
        print(f"   API密钥长度: {len(api_key)}")
        print(f"   API密钥格式: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else ''}")
    
    # 4. 网络连接测试
    print("\n4. 网络连接测试:")
    try:
        response = requests.get('https://api.deepseek.com/v1/chat/completion', timeout=10)
        print(f"   ✅ 可以访问DeepSeek API: HTTP {response.status_code}")
    except Exception as e:
        print(f"   ❌ 无法访问DeepSeek API: {e}")
    
    # 5. Python环境
    print("\n5. Python环境:")
    print(f"   Python版本: {sys.version}")
    print(f"   编码: {sys.stdout.encoding}")
    
    print("=" * 50)

if __name__ == '__main__':
    debug_server_environment()
