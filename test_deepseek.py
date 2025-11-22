#!/usr/bin/env python3
"""
DeepSeek API 测试脚本

测试DeepSeek官方API配置是否正常工作
"""

import os
import sys


def test_configuration():
    """测试配置"""
    print("=" * 60)
    print("测试1: 检查配置")
    print("=" * 60)

    try:
        from config import deepseek_settings, is_deepseek_configured

        print(f"✅ 配置模块导入成功")
        print(f"   Base URL: {deepseek_settings.base_url}")
        print(f"   Default Model: {deepseek_settings.default_model}")

        if is_deepseek_configured():
            print(f"✅ API密钥已配置")
            # 只显示前10个字符，保护隐私
            masked_key = deepseek_settings.api_key[:10] + "..." if deepseek_settings.api_key else "未设置"
            print(f"   API Key: {masked_key}")
        else:
            print(f"❌ API密钥未配置")
            print(f"   请运行: python scripts/setup_deepseek.py")
            return False

        return True

    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_chat():
    """测试基础对话"""
    print("\n" + "=" * 60)
    print("测试2: 基础对话")
    print("=" * 60)

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com",
            timeout=30.0
        )

        print("发送测试消息...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Say 'Hello, DeepSeek!'"},
            ],
            max_tokens=50
        )

        reply = response.choices[0].message.content
        print(f"✅ 收到回复: {reply}")

        return True

    except Exception as e:
        print(f"❌ 对话测试失败: {e}")
        return False


def test_streaming():
    """测试流式输出"""
    print("\n" + "=" * 60)
    print("测试3: 流式输出")
    print("=" * 60)

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com",
            timeout=30.0
        )

        print("流式输出测试: ", end="", flush=True)
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Count from 1 to 5"}
            ],
            stream=True,
            max_tokens=50
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)

        print("\n✅ 流式输出测试成功")
        return True

    except Exception as e:
        print(f"\n❌ 流式输出测试失败: {e}")
        return False


def test_with_config():
    """使用配置类测试"""
    print("\n" + "=" * 60)
    print("测试4: 使用配置类")
    print("=" * 60)

    try:
        from config import deepseek_settings
        from openai import OpenAI

        client = OpenAI(
            api_key=deepseek_settings.api_key,
            base_url=deepseek_settings.base_url,
            timeout=30.0
        )

        model_config = deepseek_settings.get_model_config()
        print(f"使用配置: {model_config}")

        response = client.chat.completions.create(
            messages=[
                {"role": "user", "content": "Hi"}
            ],
            **model_config
        )

        print(f"✅ 配置类测试成功")
        print(f"   回复: {response.choices[0].message.content[:50]}...")

        return True

    except Exception as e:
        print(f"❌ 配置类测试失败: {e}")
        return False


def test_model_info():
    """测试模型信息"""
    print("\n" + "=" * 60)
    print("测试5: 模型信息")
    print("=" * 60)

    try:
        from config import DEEPSEEK_MODELS

        print(f"可用模型数量: {len(DEEPSEEK_MODELS)}")
        for model_name, info in DEEPSEEK_MODELS.items():
            print(f"\n模型: {model_name}")
            print(f"  名称: {info['name']}")
            print(f"  描述: {info['description']}")
            print(f"  上下文窗口: {info['context_window']}")
            print(f"  最大输出: {info['max_tokens']}")

        print(f"\n✅ 模型信息获取成功")
        return True

    except Exception as e:
        print(f"❌ 模型信息测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "🔍" * 30)
    print(" " * 20 + "DeepSeek API 测试")
    print("🔍" * 30 + "\n")

    # 检查openai库
    try:
        import openai
        print(f"✅ OpenAI SDK 版本: {openai.__version__}\n")
    except ImportError:
        print("❌ OpenAI SDK 未安装")
        print("请运行: pip install openai\n")
        return False

    # 运行测试
    results = {
        "配置检查": test_configuration(),
        "基础对话": test_basic_chat(),
        "流式输出": test_streaming(),
        "配置类使用": test_with_config(),
        "模型信息": test_model_info()
    }

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！DeepSeek API 配置完成！")
        print("\n📚 下一步:")
        print("  - 查看完整示例: python examples/deepseek_official_example.py")
        print("  - 阅读使用指南: config/DEEPSEEK_GUIDE.md")
    else:
        print("\n⚠️  部分测试失败，请检查配置")
        print("\n排查建议:")
        print("  1. 检查API密钥是否正确")
        print("  2. 确认网络连接正常")
        print("  3. 验证账户余额充足")
        print("  4. 运行配置向导: python scripts/setup_deepseek.py")

    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
