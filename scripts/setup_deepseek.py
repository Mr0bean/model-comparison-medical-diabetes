#!/usr/bin/env python3
"""
DeepSeek API 快速配置脚本

帮助用户快速配置DeepSeek官方API密钥
"""

import os
import sys
from pathlib import Path


def main():
    print("=" * 60)
    print(" " * 15 + "DeepSeek API 配置向导")
    print("=" * 60)
    print()

    # 检查.env文件
    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        print("📝 .env 文件不存在，正在从模板创建...")
        env_file.write_text(env_example.read_text())
        print("✅ 已创建 .env 文件\n")

    # 获取API密钥
    print("请输入您的 DeepSeek API 密钥:")
    print("(可以在 https://platform.deepseek.com/ 获取)")
    print()
    api_key = input("API Key: ").strip()

    if not api_key:
        print("❌ API密钥不能为空")
        return

    if not api_key.startswith("sk-"):
        print("⚠️  警告: API密钥通常以 'sk-' 开头")
        confirm = input("确认继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("已取消")
            return

    # 更新.env文件
    print("\n📝 正在更新配置...")

    env_content = env_file.read_text()
    lines = env_content.split('\n')

    # 更新或添加配置
    deepseek_key_found = False
    new_lines = []

    for line in lines:
        if line.startswith('DEEPSEEK_API_KEY='):
            new_lines.append(f'DEEPSEEK_API_KEY={api_key}')
            deepseek_key_found = True
        else:
            new_lines.append(line)

    # 如果没有找到配置，添加到文件末尾
    if not deepseek_key_found:
        new_lines.extend([
            '',
            '# DeepSeek Official API',
            f'DEEPSEEK_API_KEY={api_key}',
            'DEEPSEEK_BASE_URL=https://api.deepseek.com',
            'DEEPSEEK_DEFAULT_MODEL=deepseek-chat'
        ])

    env_file.write_text('\n'.join(new_lines))

    print("✅ 配置已保存到 .env 文件\n")

    # 测试连接
    print("🔍 正在测试连接...")
    test_result = test_connection(api_key)

    if test_result:
        print("\n" + "=" * 60)
        print("✅ 配置成功！DeepSeek API 可以正常使用")
        print("=" * 60)
        print("\n📚 下一步:")
        print("  1. 查看使用示例: python examples/deepseek_official_example.py")
        print("  2. 阅读完整文档: config/DEEPSEEK_GUIDE.md")
        print("  3. 开始使用: from config import deepseek_settings")
    else:
        print("\n" + "=" * 60)
        print("⚠️  配置已保存，但连接测试失败")
        print("=" * 60)
        print("\n请检查:")
        print("  1. API密钥是否正确")
        print("  2. 网络连接是否正常")
        print("  3. 账户余额是否充足")


def test_connection(api_key):
    """测试API连接"""
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            timeout=10.0
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Hi"}
            ],
            max_tokens=10
        )

        print(f"✅ 测试成功! 响应: {response.choices[0].message.content[:30]}...")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消配置")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
