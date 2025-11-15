"""
快速开始示例
最简单的使用方式，用于快速测试和验证配置
"""
from chat_client import ChatClient


def main():
    print("JieKou AI Chat Client - 快速开始\n")
    print("=" * 60)

    try:
        # 创建客户端
        print("\n1. 初始化客户端...")
        client = ChatClient(
            system_prompt="你是一个友好的AI助手。"
        )
        print(f"✓ 客户端初始化成功")
        print(f"   模型: {client.model}")

        # 测试非流式对话
        print("\n2. 测试非流式对话...")
        print("-" * 60)
        question = "用一句话介绍你自己"
        print(f"问题: {question}")

        response = client.chat(
            message=question,
            stream=False,
            max_tokens=100
        )

        print(f"回答: {response}")
        print("✓ 非流式对话测试成功")

        # 测试流式对话
        print("\n3. 测试流式对话...")
        print("-" * 60)
        question = "说一个编程笑话"
        print(f"问题: {question}")
        print("回答: ", end="", flush=True)

        response_stream = client.chat(
            message=question,
            stream=True,
            max_tokens=200
        )

        for chunk in response_stream:
            print(chunk, end="", flush=True)

        print("\n✓ 流式对话测试成功")

        # 显示对话历史
        print("\n4. 对话历史统计...")
        print("-" * 60)
        history = client.get_history()
        print(f"总消息数: {len(history)}")
        print(f"  - 系统消息: {sum(1 for m in history if m['role'] == 'system')}")
        print(f"  - 用户消息: {sum(1 for m in history if m['role'] == 'user')}")
        print(f"  - 助手消息: {sum(1 for m in history if m['role'] == 'assistant')}")

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！客户端工作正常。")
        print("\n下一步:")
        print("  - 查看 README.md 了解更多功能")
        print("  - 运行 examples/interactive_chat.py 体验交互式聊天")
        print("  - 运行 examples/advanced_usage.py 查看高级功能")

    except ValueError as e:
        print(f"\n✗ 配置错误: {e}")
        print("\n请确保:")
        print("  1. 已创建 .env 文件（可从 .env.example 复制）")
        print("  2. 在 .env 中设置了正确的 JIEKOU_API_KEY")
        print("  3. API Key 有效且有足够的额度")

    except Exception as e:
        print(f"\n✗ 运行错误: {e}")
        print("\n请检查:")
        print("  1. 网络连接是否正常")
        print("  2. API 服务是否可访问")
        print("  3. 依赖包是否正确安装 (pip install -r requirements.txt)")


if __name__ == "__main__":
    main()
