"""
交互式聊天示例
提供一个简单的命令行交互界面
"""
import sys
sys.path.append('..')

from chat_client import ChatClient
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel


console = Console()


def print_help():
    """打印帮助信息"""
    help_text = """
可用命令:
  /help          - 显示此帮助信息
  /clear         - 清空对话历史（保留系统提示）
  /history       - 显示对话历史
  /system <msg>  - 添加系统消息
  /model <name>  - 切换模型
  /temp <value>  - 设置temperature (0-2)
  /tokens <num>  - 设置max_tokens
  /quit 或 /exit - 退出程序

直接输入消息开始对话
    """
    console.print(Panel(help_text, title="帮助", border_style="blue"))


def print_history(client: ChatClient):
    """打印对话历史"""
    history = client.get_history()
    if not history:
        console.print("[yellow]暂无对话历史[/yellow]")
        return

    console.print("\n[bold]对话历史:[/bold]")
    for i, msg in enumerate(history, 1):
        role = msg['role']
        content = msg['content']

        if role == "system":
            console.print(f"\n[dim]{i}. [cyan]系统[/cyan]:[/dim]")
            console.print(f"[dim]{content}[/dim]")
        elif role == "user":
            console.print(f"\n[dim]{i}.[/dim] [green]用户[/green]:")
            console.print(content)
        else:  # assistant
            console.print(f"\n[dim]{i}.[/dim] [blue]助手[/blue]:")
            console.print(Markdown(content))
    print()


def main():
    """主函数"""
    console.print(Panel.fit(
        "[bold cyan]欢迎使用 JieKou AI 交互式聊天[/bold cyan]\n"
        "输入 /help 查看可用命令",
        border_style="cyan"
    ))

    # 初始化客户端
    client = ChatClient(
        system_prompt="你是一个友好、专业的AI助手。"
    )

    # 当前设置
    current_temp = 0.7
    current_tokens = 2048

    console.print(f"\n[dim]当前模型: {client.model}[/dim]")
    console.print(f"[dim]Temperature: {current_temp}, Max Tokens: {current_tokens}[/dim]\n")

    while True:
        try:
            # 获取用户输入
            user_input = console.input("[green]你[/green]: ").strip()

            if not user_input:
                continue

            # 处理命令
            if user_input.startswith('/'):
                parts = user_input.split(maxsplit=1)
                command = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if command in ['/quit', '/exit']:
                    console.print("[yellow]再见！[/yellow]")
                    break

                elif command == '/help':
                    print_help()

                elif command == '/clear':
                    client.clear_history(keep_system=True)
                    console.print("[yellow]对话历史已清空（保留系统消息）[/yellow]")

                elif command == '/history':
                    print_history(client)

                elif command == '/system':
                    if not arg:
                        console.print("[red]请提供系统消息内容[/red]")
                    else:
                        client.add_system_message(arg)
                        console.print(f"[yellow]已添加系统消息: {arg}[/yellow]")

                elif command == '/model':
                    if not arg:
                        console.print(f"[yellow]当前模型: {client.model}[/yellow]")
                    else:
                        client.model = arg
                        console.print(f"[yellow]已切换到模型: {arg}[/yellow]")

                elif command == '/temp':
                    if not arg:
                        console.print(f"[yellow]当前temperature: {current_temp}[/yellow]")
                    else:
                        try:
                            current_temp = float(arg)
                            if 0 <= current_temp <= 2:
                                console.print(f"[yellow]Temperature已设置为: {current_temp}[/yellow]")
                            else:
                                console.print("[red]Temperature必须在0-2之间[/red]")
                        except ValueError:
                            console.print("[red]请提供有效的数字[/red]")

                elif command == '/tokens':
                    if not arg:
                        console.print(f"[yellow]当前max_tokens: {current_tokens}[/yellow]")
                    else:
                        try:
                            current_tokens = int(arg)
                            if current_tokens > 0:
                                console.print(f"[yellow]Max tokens已设置为: {current_tokens}[/yellow]")
                            else:
                                console.print("[red]Max tokens必须大于0[/red]")
                        except ValueError:
                            console.print("[red]请提供有效的整数[/red]")

                else:
                    console.print(f"[red]未知命令: {command}[/red]")
                    console.print("[yellow]输入 /help 查看可用命令[/yellow]")

                continue

            # 发送消息
            console.print("[blue]助手[/blue]: ", end="")

            response_stream = client.chat(
                message=user_input,
                stream=True,
                temperature=current_temp,
                max_tokens=current_tokens
            )

            response_text = []
            for chunk in response_stream:
                console.print(chunk, end="", markup=False)
                response_text.append(chunk)

            console.print("\n")

        except KeyboardInterrupt:
            console.print("\n[yellow]使用 /quit 退出程序[/yellow]")
            continue
        except Exception as e:
            console.print(f"[red]错误: {str(e)}[/red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]程序已退出[/yellow]")
