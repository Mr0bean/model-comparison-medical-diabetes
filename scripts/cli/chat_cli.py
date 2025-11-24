"""
命令行聊天工具
支持通过命令行参数或交互式输入 system_prompt 和 user_prompt
"""
from chat_client import ChatClient
import argparse
import sys


def chat(system_prompt: str, user_prompt: str, stream: bool = True, max_tokens: int = 2048):
    """
    执行聊天

    Args:
        system_prompt: 系统提示词
        user_prompt: 用户问题
        stream: 是否流式输出
        max_tokens: 最大token数
    """
    client = ChatClient(system_prompt=system_prompt)

    print(f"\n{'='*60}")
    print(f"System: {system_prompt}")
    print(f"{'='*60}")
    print(f"\nUser: {user_prompt}")
    print(f"\nAssistant: ", end="", flush=True)

    if stream:
        for chunk in client.chat(message=user_prompt, stream=True, max_tokens=max_tokens):
            print(chunk, end="", flush=True)
        print("\n")
    else:
        response = client.chat(message=user_prompt, stream=False, max_tokens=max_tokens)
        print(response)
        print()


def main():
    parser = argparse.ArgumentParser(
        description='简单的 AI 聊天工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 通过命令行参数
  python chat_cli.py -s "你是Python专家" -u "什么是装饰器?"

  # 交互式输入
  python chat_cli.py

  # 非流式输出
  python chat_cli.py -s "你是翻译助手" -u "翻译: Hello" --no-stream

  # 限制输出长度
  python chat_cli.py -s "你是AI助手" -u "介绍Python" -m 100
        """
    )

    parser.add_argument(
        '-s', '--system',
        type=str,
        help='系统提示词 (System Prompt)'
    )
    parser.add_argument(
        '-u', '--user',
        type=str,
        help='用户问题 (User Prompt)'
    )
    parser.add_argument(
        '--no-stream',
        action='store_true',
        help='禁用流式输出'
    )
    parser.add_argument(
        '-m', '--max-tokens',
        type=int,
        default=2048,
        help='最大 token 数 (默认: 2048)'
    )

    args = parser.parse_args()

    # 如果没有提供参数，使用交互式输入
    if not args.system and not args.user:
        print("\n" + "="*60)
        print("AI 聊天工具 - 交互模式")
        print("="*60)

        print("\n请输入 System Prompt (系统提示词):")
        print("(留空使用默认: '你是一个友好的AI助手。')")
        system_prompt = input("> ").strip()
        if not system_prompt:
            system_prompt = "你是一个友好的AI助手。"

        print("\n请输入 User Prompt (用户问题):")
        user_prompt = input("> ").strip()
        if not user_prompt:
            print("错误: 用户问题不能为空！")
            sys.exit(1)

        print("\n是否使用流式输出? (Y/n):")
        stream_input = input("> ").strip().lower()
        stream = stream_input != 'n'

    else:
        # 使用命令行参数
        system_prompt = args.system or "你是一个友好的AI助手。"
        user_prompt = args.user

        if not user_prompt:
            print("错误: 必须提供用户问题 (-u 或 --user)")
            parser.print_help()
            sys.exit(1)

        stream = not args.no_stream

    # 执行聊天
    chat(system_prompt, user_prompt, stream, args.max_tokens)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)
