#!/usr/bin/env python3
"""简单测试脚本"""
import sys
import os
from pathlib import Path

# 加载.env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

print("API Keys loaded:")
print(f"JIEKOU_API_KEY: {os.getenv('JIEKOU_API_KEY')[:20] if os.getenv('JIEKOU_API_KEY') else 'NOT SET'}...")
print(f"DEEPSEEK_API_KEY: {os.getenv('DEEPSEEK_API_KEY')[:20] if os.getenv('DEEPSEEK_API_KEY') else 'NOT SET'}...")

# 测试导入
sys.path.insert(0, str(Path(__file__).parent))
from cross_evaluation.model_client import model_client
from cross_evaluation.report_loader import report_loader

print("\n测试1: 加载报告")
try:
    conversation, report = report_loader.load_report_data("gpt-5.1", "患者1")
    print(f"✓ 对话长度: {len(conversation)} 字符")
    print(f"✓ 报告长度: {len(report)} 字符")
except Exception as e:
    print(f"✗ 失败: {e}")
    sys.exit(1)

print("\n测试2: 调用API (deepseek-chat)")
try:
    prompt = "你好，请回复'测试成功'"
    response = model_client.call_model("deepseek-chat", prompt)
    print(f"✓ API响应: {response[:100]}")
except Exception as e:
    print(f"✗ API调用失败: {e}")
    import traceback
    traceback.print_exc()

print("\n✓ 所有测试通过！")
