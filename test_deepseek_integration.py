#!/usr/bin/env python3
"""
测试DeepSeek官方API集成到模型注册表

验证：
1. 模型注册表能否正确加载DeepSeek配置
2. 客户端工厂能否创建DeepSeek客户端
3. DeepSeek客户端能否正常工作
"""

import os
import sys
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


def test_registry():
    """测试模型注册表"""
    print("=" * 60)
    print("测试1: 模型注册表加载DeepSeek配置")
    print("=" * 60)

    try:
        from cross_evaluation.model_registry import ModelRegistry

        registry = ModelRegistry(".")

        # 检查DeepSeek模型是否注册
        models = registry.list_models()

        deepseek_models = [
            name for name in models.keys()
            if name.startswith("deepseek-")
        ]

        if deepseek_models:
            print(f"✅ 找到 {len(deepseek_models)} 个DeepSeek模型:")
            for model_name in deepseek_models:
                provider = models[model_name]
                config = registry.get_model_config(model_name)
                print(f"   - {model_name}")
                print(f"     提供商: {provider}")
                print(f"     Base URL: {config.base_url}")
                print(f"     Max Tokens: {config.max_tokens}")
        else:
            print("⚠️  未找到DeepSeek模型")
            print("   请确保:")
            print("   1. config/batch/batch_config_deepseek_official.json 存在")
            print("   2. DEEPSEEK_API_KEY 环境变量已设置")
            return False

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_client_factory():
    """测试客户端工厂"""
    print("\n" + "=" * 60)
    print("测试2: 客户端工厂创建DeepSeek客户端")
    print("=" * 60)

    try:
        from cross_evaluation.model_client_factory import ModelClientFactory

        factory = ModelClientFactory(".")

        # 获取可用模型
        models = factory.list_available_models()
        deepseek_models = [
            name for name in models.keys()
            if name.startswith("deepseek-")
        ]

        if not deepseek_models:
            print("⚠️  未找到DeepSeek模型，跳过客户端创建测试")
            return False

        # 尝试创建客户端
        model_name = deepseek_models[0]
        print(f"创建客户端: {model_name}")

        client = factory.create_client(model_name)
        print(f"✅ 客户端创建成功")
        print(f"   类型: {type(client).__name__}")

        # 检查是否是DeepSeekClient
        from cross_evaluation.deepseek_client import DeepSeekClient
        if isinstance(client, DeepSeekClient):
            print(f"   ✅ 正确使用了DeepSeekClient")
        else:
            print(f"   ⚠️  使用了 {type(client).__name__}，可能不是DeepSeek官方API")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_call():
    """测试API调用"""
    print("\n" + "=" * 60)
    print("测试3: 实际API调用")
    print("=" * 60)

    if not os.getenv('DEEPSEEK_API_KEY'):
        print("⚠️  DEEPSEEK_API_KEY 未设置，跳过API调用测试")
        return False

    try:
        from cross_evaluation.deepseek_client import get_deepseek_client

        client = get_deepseek_client()

        print("发送测试请求...")
        response = client.chat_completion(
            prompt="Say 'Hello, Integration Test!'",
            max_tokens=50
        )

        print(f"✅ API调用成功")
        print(f"   回复: {response[:100]}...")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_model_usage():
    """测试通过客户端工厂使用DeepSeek"""
    print("\n" + "=" * 60)
    print("测试4: 通过客户端工厂使用DeepSeek")
    print("=" * 60)

    if not os.getenv('DEEPSEEK_API_KEY'):
        print("⚠️  DEEPSEEK_API_KEY 未设置，跳过")
        return False

    try:
        from cross_evaluation.model_client_factory import ModelClientFactory

        factory = ModelClientFactory(".")

        # 找到DeepSeek模型
        models = factory.list_available_models()
        deepseek_models = [
            name for name in models.keys()
            if name.startswith("deepseek-")
        ]

        if not deepseek_models:
            print("⚠️  未找到DeepSeek模型")
            return False

        model_name = deepseek_models[0]
        print(f"使用模型: {model_name}")

        # 创建客户端
        client = factory.create_client(model_name)

        # 发送请求
        print("发送测试请求...")
        response = client.chat_completion(
            prompt="What is 2+2?",
            max_tokens=20
        )

        print(f"✅ 测试成功")
        print(f"   回复: {response}")

        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "🧪" * 30)
    print(" " * 15 + "DeepSeek集成测试")
    print("🧪" * 30 + "\n")

    # 检查必要的库
    try:
        import openai
        print(f"✅ OpenAI SDK: {openai.__version__}\n")
    except ImportError:
        print("❌ OpenAI SDK 未安装")
        print("请运行: pip install openai\n")
        return False

    # 运行测试
    results = {
        "模型注册表": test_registry(),
        "客户端工厂": test_client_factory(),
        "API调用": test_api_call(),
        "完整使用流程": test_model_usage()
    }

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败/跳过"
        print(f"{test_name}: {status}")

    total = len(results)
    passed = sum(results.values())
    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！DeepSeek集成成功！")
        print("\n📚 使用方法:")
        print("  from cross_evaluation.model_client_factory import ModelClientFactory")
        print("  factory = ModelClientFactory('.')")
        print("  client = factory.create_client('deepseek-chat')")
        print("  response = client.chat_completion('Hello')")
    else:
        print("\n⚠️  部分测试失败")
        print("\n请检查:")
        print("  1. DEEPSEEK_API_KEY 环境变量是否设置")
        print("  2. config/batch/batch_config_deepseek_official.json 是否存在")
        print("  3. OpenAI SDK 是否已安装 (pip install openai)")

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
