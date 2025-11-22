#!/usr/bin/env python3
"""
测试多API支持
验证不同模型使用不同API接口的功能
"""

import json
from cross_evaluation.model_registry import ModelRegistry
from cross_evaluation.model_client_factory import ModelClientFactory


def test_model_registry():
    """测试模型注册表"""
    print("\n" + "="*80)
    print("测试模型注册表")
    print("="*80 + "\n")

    registry = ModelRegistry()

    print("已注册的模型:")
    models = registry.list_models()

    # 按提供商分组显示
    providers = {}
    for model, provider in models.items():
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)

    for provider, model_list in sorted(providers.items()):
        print(f"\n{provider}:")
        for model in sorted(model_list):
            config = registry.get_model_config(model)
            print(f"  - {model}")
            print(f"    Base URL: {config.base_url}")
            print(f"    Has API Key: {config.api_key is not None}")
            print(f"    Max Tokens: {config.max_tokens}")

    # 导出注册表
    registry.export_to_json("model_registry_export.json")
    print(f"\n✓ 模型注册表已导出到 model_registry_export.json")

    return registry


def test_client_factory():
    """测试客户端工厂"""
    print("\n" + "="*80)
    print("测试客户端工厂")
    print("="*80 + "\n")

    factory = ModelClientFactory()

    # 测试创建不同提供商的客户端
    test_models = [
        "gpt-5.1",           # JieKou API
        "deepseek/deepseek-v3.1",  # JieKou API
        "qwen3-max",         # 通义千问
        "doubao-seed-1-6-251015",  # 豆包
        "Baichuan-M2",       # 百川
        "moonshotai/kimi-k2-0905"  # Kimi
    ]

    print("测试创建客户端:")
    for model in test_models:
        try:
            info = factory.get_model_info(model)
            if "error" not in info:
                print(f"\n{model}:")
                print(f"  提供商: {info['provider']}")
                print(f"  API基础URL: {info['base_url']}")
                print(f"  有API密钥: {'是' if info['has_api_key'] else '否'}")

                # 尝试创建客户端
                try:
                    client = factory.create_client(model)
                    print(f"  ✓ 客户端创建成功")
                except Exception as e:
                    print(f"  ✗ 客户端创建失败: {e}")
            else:
                print(f"\n{model}: {info['error']}")
        except Exception as e:
            print(f"\n{model}: 错误 - {e}")

    return factory


def test_simple_evaluation():
    """测试简单的评估调用（可选）"""
    print("\n" + "="*80)
    print("测试评估调用（可选）")
    print("="*80 + "\n")

    choice = input("是否测试实际API调用？这将消耗API配额。(y/N): ")
    if choice.lower() != 'y':
        print("跳过API调用测试")
        return

    factory = ModelClientFactory()

    # 测试prompt
    test_prompt = """请评估以下内容的质量（1-5分）：

    内容：发现血糖升高2月，口渴、头晕2月，体重减轻2月

    请给出一个简单的评分和理由。
    """

    # 选择一个模型进行测试
    test_model = "gpt-5.1"  # 或其他模型

    print(f"\n使用 {test_model} 进行测试评估...")

    try:
        client = factory.create_client(test_model)
        response = client.chat(test_prompt, temperature=0.0, max_tokens=200)
        print(f"\n响应:\n{response}")
        print("\n✓ API调用成功")
    except Exception as e:
        print(f"\n✗ API调用失败: {e}")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🔧 多API支持测试程序")
    print("="*80)

    # 1. 测试模型注册表
    registry = test_model_registry()

    # 2. 测试客户端工厂
    factory = test_client_factory()

    # 3. 可选：测试实际API调用
    test_simple_evaluation()

    print("\n" + "="*80)
    print("✅ 测试完成")
    print("="*80)

    print("\n📋 测试总结:")
    print(f"  - 注册的模型总数: {len(registry.models)}")
    print(f"  - 不同API提供商数: {len(set(config.provider for config in registry.models.values()))}")
    print("\n💡 建议:")
    print("  1. 检查 model_registry_export.json 确认所有模型配置正确")
    print("  2. 确保所有需要的API密钥都已在对应的batch_config_*.json中配置")
    print("  3. 运行 run_cross_evaluation.py --test-mode 进行完整测试")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()