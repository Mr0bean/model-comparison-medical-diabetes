"""
简单的对话测试脚本
演示如何进行多轮对话
"""
from chat_client import ChatClient


def main():
    print("=" * 60)
    print("对话测试")
    print("=" * 60)

    # 创建客户端
    client = ChatClient(
        system_prompt="你是一个友好的AI助手，擅长回答各种问题。"
    )

    print(f"\n✓ 客户端初始化成功，使用模型: {client.model}\n")

    # 测试对话列表
    conversations = [
        "你好，请介绍一下你自己",
        "你能帮我做什么？",
        "给我讲一个有趣的科技故事",
        "用一句话总结我们刚才的对话"
    ]

    # 进行多轮对话
    for i, question in enumerate(conversations, 1):
        print(f"\n{'='*60}")
        print(f"对话 {i}:")
        print(f"{'='*60}")
        print(f"\n用户: {question}")
        print(f"\n助手: ", end="", flush=True)

        # 流式输出
        for chunk in client.chat(message=question, stream=True, max_tokens=300):
            print(chunk, end="", flush=True)

        print("\n")

    # 显示对话统计
    print(f"\n{'='*60}")
    print("对话统计")
    print(f"{'='*60}")
    history = client.get_history()
    print(f"总消息数: {len(history)}")
    print(f"  - 系统消息: {sum(1 for m in history if m['role'] == 'system')}")
    print(f"  - 用户消息: {sum(1 for m in history if m['role'] == 'user')}")
    print(f"  - 助手消息: {sum(1 for m in history if m['role'] == 'assistant')}")

    print(f"\n{'='*60}")
    print("✓ 对话测试完成！")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
