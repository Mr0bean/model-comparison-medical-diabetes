"""
测试通用模型服务
演示如何使用统一接口调用不同的模型
"""
import logging
from model_service import UniversalModelService, call_model

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_list_models():
    """测试1: 列出所有模型"""
    print("\n" + "=" * 60)
    print("测试1: 列出所有可用模型")
    print("=" * 60)

    service = UniversalModelService()

    # 列出所有提供商
    providers = service.registry.list_providers()
    print(f"\n支持的提供商: {', '.join(providers)}\n")

    # 按提供商分组显示模型
    for provider in providers:
        models = service.list_models(provider)
        print(f"[{provider}] - {len(models)} 个模型:")
        for model in models:
            info = service.get_model_info(model)
            print(f"  • {model}")
            print(f"    描述: {info['description']}")
            print(f"    API: {info['base_url']}")
            print(f"    Key: {info['api_key_env']}")
        print()


def test_simple_call():
    """测试2: 简单调用"""
    print("\n" + "=" * 60)
    print("测试2: 简单调用模型")
    print("=" * 60)

    service = UniversalModelService()

    # 测试问题
    question = "用一句话介绍什么是人工智能"

    # 尝试调用不同的模型
    test_models = [
        "gpt-5.1",
        # "deepseek-reasoner",  # 取消注释以测试
        # "Baichuan4",
    ]

    for model in test_models:
        print(f"\n测试模型: {model}")
        print("-" * 60)
        print(f"问题: {question}")

        try:
            response = service.call(
                model=model,
                prompt=question,
                temperature=0.7,
                max_tokens=200
            )
            print(f"回答: {response[:200]}...")  # 只显示前200字符
            print("✅ 调用成功")

        except Exception as e:
            print(f"❌ 调用失败: {str(e)}")


def test_stream_call():
    """测试3: 流式调用"""
    print("\n" + "=" * 60)
    print("测试3: 流式输出")
    print("=" * 60)

    service = UniversalModelService()

    model = "gpt-5.1"
    question = "用三句话解释什么是机器学习"

    print(f"\n模型: {model}")
    print(f"问题: {question}")
    print("\n流式回答:")
    print("-" * 60)

    try:
        for chunk in service.call(
            model=model,
            prompt=question,
            stream=True,
            temperature=0.7,
            max_tokens=300
        ):
            print(chunk, end="", flush=True)

        print("\n" + "-" * 60)
        print("✅ 流式调用成功")

    except Exception as e:
        print(f"\n❌ 调用失败: {str(e)}")


def test_batch_call():
    """测试4: 批量调用"""
    print("\n" + "=" * 60)
    print("测试4: 批量调用")
    print("=" * 60)

    service = UniversalModelService()

    model = "gpt-5.1"
    questions = [
        "什么是深度学习?",
        "什么是神经网络?",
        "什么是自然语言处理?"
    ]

    print(f"\n模型: {model}")
    print(f"批量处理 {len(questions)} 个问题\n")

    try:
        results = service.batch_call(
            model=model,
            prompts=questions,
            system_prompt="请用一句话简洁回答",
            temperature=0.7,
            max_tokens=100
        )

        for i, (question, answer) in enumerate(zip(questions, results), 1):
            print(f"{i}. 问题: {question}")
            print(f"   回答: {answer[:150]}...")
            print()

        print("✅ 批量调用成功")

    except Exception as e:
        print(f"❌ 调用失败: {str(e)}")


def test_with_system_prompt():
    """测试5: 使用系统提示词"""
    print("\n" + "=" * 60)
    print("测试5: 使用系统提示词")
    print("=" * 60)

    service = UniversalModelService()

    model = "gpt-5.1"
    system_prompt = "你是一个专业的医学AI助手,专注于糖尿病领域"
    user_prompt = "什么是2型糖尿病?"

    print(f"\n模型: {model}")
    print(f"系统角色: {system_prompt}")
    print(f"用户问题: {user_prompt}")
    print("\n回答:")
    print("-" * 60)

    try:
        response = service.call(
            model=model,
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )

        print(response)
        print("-" * 60)
        print("✅ 调用成功")

    except Exception as e:
        print(f"❌ 调用失败: {str(e)}")


def test_convenience_function():
    """测试6: 便捷函数"""
    print("\n" + "=" * 60)
    print("测试6: 使用便捷函数")
    print("=" * 60)

    question = "什么是深度学习?"

    print(f"\n问题: {question}")
    print("\n回答:")
    print("-" * 60)

    try:
        # 使用便捷函数快速调用
        response = call_model(
            model="gpt-5.1",
            prompt=question,
            temperature=0.7,
            max_tokens=200
        )

        print(response)
        print("-" * 60)
        print("✅ 便捷函数调用成功")

    except Exception as e:
        print(f"❌ 调用失败: {str(e)}")


def test_register_new_model():
    """测试7: 注册新模型"""
    print("\n" + "=" * 60)
    print("测试7: 动态注册新模型")
    print("=" * 60)

    service = UniversalModelService()

    # 注册一个新模型
    new_model = "custom-model-v1"

    print(f"\n注册新模型: {new_model}")

    service.registry.register_model(
        model_name=new_model,
        provider="custom",
        api_key_env="CUSTOM_API_KEY",
        base_url="https://api.custom.com/v1",
        description="自定义测试模型"
    )

    # 验证注册
    info = service.get_model_info(new_model)
    print(f"\n已注册模型信息:")
    print(f"  模型名: {new_model}")
    print(f"  提供商: {info['provider']}")
    print(f"  API URL: {info['base_url']}")
    print(f"  API Key: {info['api_key_env']}")
    print(f"  描述: {info['description']}")

    print("\n✅ 模型注册成功")


def main():
    """主函数 - 运行所有测试"""
    print("\n" + "=" * 60)
    print("通用模型服务 - 完整测试套件")
    print("=" * 60)

    tests = [
        ("列出所有模型", test_list_models),
        ("简单调用", test_simple_call),
        ("流式调用", test_stream_call),
        ("批量调用", test_batch_call),
        ("系统提示词", test_with_system_prompt),
        ("便捷函数", test_convenience_function),
        ("注册新模型", test_register_new_model),
    ]

    print("\n可用测试:")
    for i, (name, _) in enumerate(tests, 1):
        print(f"  {i}. {name}")

    print("\n" + "=" * 60)
    choice = input("\n请选择测试 (1-7, 或 'all' 运行所有, 'q' 退出): ").strip()

    if choice.lower() == 'q':
        print("\n退出测试")
        return

    if choice.lower() == 'all':
        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"\n❌ 测试 '{name}' 失败: {str(e)}")
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(tests):
                name, test_func = tests[index]
                test_func()
            else:
                print("❌ 无效的选择")
        except ValueError:
            print("❌ 请输入数字")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
