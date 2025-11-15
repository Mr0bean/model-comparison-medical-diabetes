"""
基础使用示例
展示最简单的对话使用方式
"""
import sys
sys.path.append('..')

from chat_client import ChatClient


def main():
    print("=== 基础使用示例 ===\n")

    # 创建客户端
    client = ChatClient(
        system_prompt="你是一个专业的AI助手，善于解答各种问题。"
    )

    # 示例1：非流式对话
    print("1. 非流式对话：")
    print("-" * 50)
    response = client.chat(
        message="请简单介绍一下Python的主要特点",
        stream=False,
        max_tokens=500
    )
    print(f"用户: 请简单介绍一下Python的主要特点")
    print(f"助手: {response}\n")

    # 示例2：流式对话
    print("2. 流式对话：")
    print("-" * 50)
    print("用户: 什么是机器学习？")
    print("助手: ", end="", flush=True)

    response_stream = client.chat(
        message="什么是机器学习？请用一段话简单解释",
        stream=True,
        max_tokens=500
    )

    for chunk in response_stream:
        print(chunk, end="", flush=True)
    print("\n")

    # 示例3：查看对话历史
    print("3. 对话历史：")
    print("-" * 50)
    history = client.get_history()
    for i, msg in enumerate(history):
        role_name = {"system": "系统", "user": "用户", "assistant": "助手"}
        print(f"{i+1}. [{role_name[msg['role']]}]: {msg['content'][:50]}...")
    print()


if __name__ == "__main__":
    main()
