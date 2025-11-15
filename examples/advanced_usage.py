"""
高级使用示例
展示各种参数配置和高级功能
"""
import sys
sys.path.append('..')

from chat_client import ChatClient


def example_temperature():
    """演示temperature参数的效果"""
    print("=== Temperature 参数示例 ===")
    print("Temperature控制输出的随机性，值越高越随机，越低越确定\n")

    question = "用一句话描述春天"

    # 低temperature (更确定)
    print("1. Temperature = 0.3 (更确定、一致):")
    print("-" * 50)
    client = ChatClient()
    response = client.simple_chat(
        message=question,
        temperature=0.3,
        stream=False,
        max_tokens=100
    )
    print(f"回答: {response}\n")

    # 高temperature (更随机)
    print("2. Temperature = 1.5 (更随机、有创意):")
    print("-" * 50)
    response = client.simple_chat(
        message=question,
        temperature=1.5,
        stream=False,
        max_tokens=100
    )
    print(f"回答: {response}\n")


def example_max_tokens():
    """演示max_tokens参数"""
    print("=== Max Tokens 参数示例 ===")
    print("Max Tokens控制输出的最大长度\n")

    question = "介绍一下人工智能的发展历史"

    # 短回答
    print("1. Max Tokens = 100 (简短回答):")
    print("-" * 50)
    client = ChatClient()
    response = client.simple_chat(
        message=question,
        max_tokens=100,
        stream=False
    )
    print(f"{response}\n")

    # 长回答
    print("2. Max Tokens = 500 (详细回答):")
    print("-" * 50)
    response = client.simple_chat(
        message=question,
        max_tokens=500,
        stream=False
    )
    print(f"{response}\n")


def example_penalties():
    """演示penalty参数"""
    print("=== Penalty 参数示例 ===")
    print("Frequency/Presence Penalty 用于减少重复内容\n")

    question = "列举10个编程语言的名字"

    # 无penalty
    print("1. 无Penalty:")
    print("-" * 50)
    client = ChatClient()
    response = client.simple_chat(
        message=question,
        stream=False,
        max_tokens=200
    )
    print(f"{response}\n")

    # 有penalty
    print("2. 有Frequency Penalty (减少重复):")
    print("-" * 50)
    response = client.simple_chat(
        message=question,
        frequency_penalty=1.5,
        stream=False,
        max_tokens=200
    )
    print(f"{response}\n")


def example_stop_sequence():
    """演示stop参数"""
    print("=== Stop Sequence 参数示例 ===")
    print("Stop用于在遇到特定文本时停止生成\n")

    question = "请数数字：1, 2, 3, 4, 5, 6, 7, 8, 9, 10"

    print("使用stop=['5']，在遇到5时停止:")
    print("-" * 50)
    client = ChatClient()
    response = client.simple_chat(
        message=question,
        stop=["5"],
        stream=False,
        max_tokens=200
    )
    print(f"{response}\n")


def example_multi_turn_conversation():
    """演示多轮对话"""
    print("=== 多轮对话示例 ===")
    print("展示如何进行连续的对话\n")

    client = ChatClient(
        system_prompt="你是一个Python编程专家。"
    )

    conversations = [
        "什么是列表推导式？",
        "能给我一个例子吗？",
        "这种写法比普通for循环有什么优势？"
    ]

    for i, question in enumerate(conversations, 1):
        print(f"第{i}轮对话:")
        print("-" * 50)
        print(f"用户: {question}")
        print("助手: ", end="", flush=True)

        response_stream = client.chat(
            message=question,
            stream=True,
            max_tokens=300
        )

        for chunk in response_stream:
            print(chunk, end="", flush=True)
        print("\n")


def main():
    """运行所有示例"""
    examples = [
        ("Temperature 参数", example_temperature),
        ("Max Tokens 参数", example_max_tokens),
        ("Penalty 参数", example_penalties),
        ("Stop Sequence 参数", example_stop_sequence),
        ("多轮对话", example_multi_turn_conversation)
    ]

    print("选择要运行的示例：")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print(f"{len(examples) + 1}. 运行所有示例")

    try:
        choice = input("\n请输入选择 (1-{}): ".format(len(examples) + 1))
        choice = int(choice)

        if 1 <= choice <= len(examples):
            examples[choice - 1][1]()
        elif choice == len(examples) + 1:
            for name, func in examples:
                func()
                print("\n" + "=" * 70 + "\n")
        else:
            print("无效的选择")
    except (ValueError, KeyboardInterrupt):
        print("\n已取消")


if __name__ == "__main__":
    main()
