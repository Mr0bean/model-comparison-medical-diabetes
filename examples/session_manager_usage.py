"""
会话管理示例
展示如何管理多个对话会话
"""
import sys
sys.path.append('..')

from chat_client import ConversationManager


def main():
    print("=== 会话管理示例 ===\n")

    # 创建会话管理器
    manager = ConversationManager()

    # 创建多个会话，每个会话有不同的角色
    print("1. 创建多个会话:")
    print("-" * 50)

    # Python专家会话
    python_expert = manager.create_session(
        session_id="python_expert",
        system_prompt="你是一个Python编程专家，精通Python的各个方面。"
    )
    print("✓ 创建了Python专家会话")

    # 文案写作会话
    writer = manager.create_session(
        session_id="writer",
        system_prompt="你是一个专业的文案写作者，擅长创作各种类型的文案。"
    )
    print("✓ 创建了文案写作会话")

    # 翻译会话
    translator = manager.create_session(
        session_id="translator",
        system_prompt="你是一个专业的翻译，精通中英文翻译。"
    )
    print("✓ 创建了翻译会话\n")

    # 列出所有会话
    print("2. 当前所有会话:")
    print("-" * 50)
    for session_id in manager.list_sessions():
        print(f"  - {session_id}")
    print()

    # 在不同会话中进行对话
    print("3. 在Python专家会话中对话:")
    print("-" * 50)
    print("用户: 什么是装饰器？")
    print("Python专家: ", end="", flush=True)

    response_stream = python_expert.chat(
        message="什么是装饰器？请简单解释",
        stream=True,
        max_tokens=300
    )
    for chunk in response_stream:
        print(chunk, end="", flush=True)
    print("\n")

    print("4. 在文案写作会话中对话:")
    print("-" * 50)
    print("用户: 帮我写一个产品广告语")
    print("文案写手: ", end="", flush=True)

    response_stream = writer.chat(
        message="帮我为一款智能手表写一个简短的广告语",
        stream=True,
        max_tokens=200
    )
    for chunk in response_stream:
        print(chunk, end="", flush=True)
    print("\n")

    print("5. 在翻译会话中对话:")
    print("-" * 50)
    print("用户: 翻译：The quick brown fox jumps over the lazy dog")
    print("翻译: ", end="", flush=True)

    response_stream = translator.chat(
        message="请将这句话翻译成中文：The quick brown fox jumps over the lazy dog",
        stream=True,
        max_tokens=200
    )
    for chunk in response_stream:
        print(chunk, end="", flush=True)
    print("\n")

    # 获取特定会话的历史
    print("6. Python专家会话的对话历史:")
    print("-" * 50)
    python_session = manager.get_session("python_expert")
    if python_session:
        history = python_session.get_history()
        for msg in history:
            role_name = {"system": "系统", "user": "用户", "assistant": "助手"}
            content_preview = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
            print(f"[{role_name[msg['role']]}]: {content_preview}")
    print()

    # 清空特定会话的历史
    print("7. 清空Python专家会话的对话历史（保留系统消息）:")
    print("-" * 50)
    if python_session:
        python_session.clear_history(keep_system=True)
        print(f"清空后的历史记录数: {len(python_session.get_history())}")
    print()

    # 删除会话
    print("8. 删除文案写作会话:")
    print("-" * 50)
    manager.delete_session("writer")
    print(f"剩余会话: {manager.list_sessions()}\n")


if __name__ == "__main__":
    main()
