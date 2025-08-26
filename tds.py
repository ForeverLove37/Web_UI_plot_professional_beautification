#!/usr/bin/env python3
import os
import requests
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
API_URLS = [
    "https://api.deepseek.com/chat/completions",
    "https://api.deepseek.com/v1/chat/completions",  # 可能的其他端点
    "https://api.deepseek.com/v1/completions"        # 可能的其他端点
]

def test_deepseek_api():
    print("=" * 60)
    print("DeepSeek API 连接测试")
    print("=" * 60)
    
    if not DEEPSEEK_API_KEY:
        print("❌ 未找到DEEPSEEK_API_KEY环境变量")
        return
    
    print(f"API密钥: {DEEPSEEK_API_KEY[:10]}...{DEEPSEEK_API_KEY[-4:]}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    # 简单的测试消息
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "Hello, are you working?"}],
        "max_tokens": 50
    }
    
    for i, api_url in enumerate(API_URLS):
        print(f"\n测试端点 {i+1}: {api_url}")
        
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=15)
            
            print(f"HTTP状态码: {response.status_code}")
            print(f"响应头: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ API调用成功！")
                result = response.json()
                print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
                return True
            elif response.status_code == 401:
                print("❌ 认证失败 - API密钥可能无效")
                print(f"响应: {response.text}")
            elif response.status_code == 404:
                print("❌ 端点不存在 (404)")
                print(f"响应: {response.text}")
            elif response.status_code == 429:
                print("⚠️  请求频率限制")
            else:
                print(f"❌ 未知错误: {response.status_code}")
                print(f"响应: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求异常: {e}")
        except Exception as e:
            print(f"❌ 其他异常: {e}")
    
    return False

def check_api_documentation():
    print("\n" + "=" * 60)
    print("API文档检查建议")
    print("=" * 60)
    
    print("1. 访问DeepSeek官方文档确认最新API端点")
    print("2. 检查API密钥是否有访问权限")
    print("3. 确认模型名称是否正确")
    print("4. 检查API密钥是否已激活")
    
    # 测试基础连接
    print("\n测试基础域名连接:")
    try:
        base_response = requests.get("https://api.deepseek.com", timeout=10)
        print(f"基础域名状态: {base_response.status_code}")
    except Exception as e:
        print(f"基础域名连接失败: {e}")

if __name__ == '__main__':
    success = test_deepseek_api()
    if not success:
        check_api_documentation()
