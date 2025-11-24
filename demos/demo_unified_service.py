"""
统一模型服务演示
展示如何用统一接口调用不同的AI模型
"""
from src.core import UniversalModelService, call_model
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def demo_1_simple_call():
    """演示1: 最简单的用法 - 一行代码调用任意模型"""
    print("\n" + "=" * 60)
    print("演示1: 快捷函数 - 一行代码调用模型")
    print("=" * 60)

    # 只需一行代码!
    response = call_model("gpt-5.1", "用一句话介绍什么是人工智能")
    print(f"\n回答: {response}\n")


def demo_2_multiple_models():
    """演示2: 同一个问题,使用不同模型回答"""
    print("\n" + "=" * 60)
    print("演示2: 多模型对比 - 同一个接口调用不同模型")
    print("=" * 60)

    service = UniversalModelService()
    question = "用一句话解释量子计算"

    # 可以轻松切换不同的模型
    models_to_test = [
        "gpt-5.1",              # JieKou AI
        "gemini-2.5-pro",       # Google Gemini
        # "Baichuan4",          # 百川智能
        # "deepseek-reasoner",  # DeepSeek
    ]

    for model in models_to_test:
        print(f"\n[{model}]")
        print("-" * 60)
        try:
            response = service.call(
                model=model,
                prompt=question,
                temperature=0.7,
                max_tokens=200
            )
            print(response)
        except Exception as e:
            print(f"❌ 调用失败: {str(e)}")


def demo_3_stream_output():
    """演示3: 流式输出"""
    print("\n" + "=" * 60)
    print("演示3: 流式输出 - 实时显示AI回答")
    print("=" * 60)

    service = UniversalModelService()

    print("\n问题: 什么是机器学习?请详细解释。")
    print("\n实时回答:")
    print("-" * 60)

    try:
        for chunk in service.call(
            model="gpt-5.1",
            prompt="什么是机器学习?请用2-3句话解释。",
            stream=True,
            temperature=0.7,
            max_tokens=300
        ):
            print(chunk, end="", flush=True)
        print("\n" + "-" * 60)
    except Exception as e:
        print(f"\n❌ 调用失败: {str(e)}")


def demo_4_cross_provider():
    """演示4: 跨提供商调用 - 这就是统一服务的威力!"""
    print("\n" + "=" * 60)
    print("演示4: 跨提供商调用 - 统一接口的威力")
    print("=" * 60)

    service = UniversalModelService()

    # 同一个service实例,可以调用来自不同提供商的模型
    # 不需要创建不同的客户端!

    calls = [
        ("gpt-5.1", "jiekou", "什么是深度学习?"),
        ("Baichuan4", "baichuan", "什么是神经网络?"),
        ("deepseek-reasoner", "deepseek", "什么是自然语言处理?"),
    ]

    print("\n同一个服务实例,调用3个不同提供商的模型:")
    print()

    for model, provider, question in calls:
        print(f"[{provider}] {model}")
        print(f"问题: {question}")
        try:
            # 完全相同的调用方式!
            response = service.call(
                model=model,
                prompt=question,
                system_prompt="请用一句话简洁回答",
                temperature=0.7,
                max_tokens=150
            )
            print(f"回答: {response}")
        except Exception as e:
            print(f"回答: ❌ {str(e)}")
        print()


def demo_5_batch_processing():
    """演示5: 批量处理"""
    print("\n" + "=" * 60)
    print("演示5: 批量处理 - 一次处理多个问题")
    print("=" * 60)

    service = UniversalModelService()

    questions = [
        "什么是Python?",
        "什么是JavaScript?",
        "什么是Rust?"
    ]

    print(f"\n批量处理 {len(questions)} 个问题:")
    print()

    try:
        results = service.batch_call(
            model="gpt-5.1",
            prompts=questions,
            system_prompt="请用一句话简洁回答",
            temperature=0.7,
            max_tokens=100
        )

        for i, (question, answer) in enumerate(zip(questions, results), 1):
            print(f"{i}. {question}")
            print(f"   → {answer}")
            print()

    except Exception as e:
        print(f"❌ 批量处理失败: {str(e)}")


def demo_6_model_discovery():
    """演示6: 模型发现 - 查看所有可用模型"""
    print("\n" + "=" * 60)
    print("演示6: 模型发现 - 动态查询可用模型")
    print("=" * 60)

    service = UniversalModelService()

    # 列出所有提供商
    providers = service.registry.list_providers()
    print(f"\n支持的提供商: {', '.join(providers)}")
    print()

    # 按提供商查看模型
    for provider in providers:
        models = service.list_models(provider)
        print(f"[{provider}] - {len(models)} 个模型:")
        for model in models[:3]:  # 只显示前3个
            info = service.get_model_info(model)
            print(f"  • {model}")
            print(f"    {info['description']}")
        if len(models) > 3:
            print(f"  ... 还有 {len(models) - 3} 个模型")
        print()


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("统一模型服务 - 完整演示")
    print("=" * 60)
    print("\n核心理念: 一个接口,调用所有AI模型")
    print("         只需传入模型名称,自动路由到正确的API提供商")

    demos = [
        ("快捷函数调用", demo_1_simple_call),
        ("多模型对比", demo_2_multiple_models),
        ("流式输出", demo_3_stream_output),
        ("跨提供商调用", demo_4_cross_provider),
        ("批量处理", demo_5_batch_processing),
        ("模型发现", demo_6_model_discovery),
    ]

    print("\n可用演示:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")

    print("\n" + "=" * 60)
    choice = input("\n请选择演示 (1-6, 或 'all' 运行所有, 'q' 退出): ").strip()

    if choice.lower() == 'q':
        print("\n退出演示")
        return

    print()

    if choice.lower() == 'all':
        for name, demo_func in demos:
            try:
                demo_func()
                input("\n按Enter继续...")
            except KeyboardInterrupt:
                print("\n\n演示已取消")
                break
            except Exception as e:
                print(f"\n❌ 演示 '{name}' 出错: {str(e)}")
                input("\n按Enter继续...")
    else:
        try:
            index = int(choice) - 1
            if 0 <= index < len(demos):
                name, demo_func = demos[index]
                demo_func()
            else:
                print("❌ 无效的选择")
        except ValueError:
            print("❌ 请输入数字")

    print("\n" + "=" * 60)
    print("演示完成!")
    print("\n下一步:")
    print("  • 查看 UNIFIED_MODEL_SERVICE_README.md 了解详细文档")
    print("  • 运行 test_model_service.py 进行完整测试")
    print("  • 使用 unified_batch_processor.py 进行批量处理")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
