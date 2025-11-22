"""
DeepSeek官方API使用示例

安装依赖:
    pip install openai

环境变量配置:
    export DEEPSEEK_API_KEY=your_api_key_here
"""

import os
from openai import OpenAI


def basic_chat_example():
    """基础对话示例"""
    print("=" * 50)
    print("基础对话示例")
    print("=" * 50)

    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
        ],
        stream=False
    )

    print("回复:", response.choices[0].message.content)
    print()


def streaming_chat_example():
    """流式对话示例"""
    print("=" * 50)
    print("流式对话示例")
    print("=" * 50)

    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

    print("回复: ", end="", flush=True)
    stream = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "写一首关于AI的短诗"},
        ],
        stream=True
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print("\n")


def medical_assistant_example():
    """医疗助手示例"""
    print("=" * 50)
    print("医疗助手示例")
    print("=" * 50)

    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一名经验丰富的医疗助手，擅长根据患者症状生成规范的病历记录。"
            },
            {
                "role": "user",
                "content": """
患者信息：
- 姓名：张三
- 年龄：45岁
- 性别：男
- 主诉：胸闷气短一周

请生成主诉和现病史部分的病历记录。
                """
            },
        ],
        temperature=0.7,
        max_tokens=2048
    )

    print("病历记录:")
    print(response.choices[0].message.content)
    print()


def multi_turn_conversation_example():
    """多轮对话示例"""
    print("=" * 50)
    print("多轮对话示例")
    print("=" * 50)

    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

    messages = [
        {"role": "system", "content": "You are a helpful assistant"}
    ]

    # 第一轮对话
    messages.append({"role": "user", "content": "什么是深度学习？"})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    assistant_reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_reply})
    print(f"用户: 什么是深度学习？")
    print(f"助手: {assistant_reply}\n")

    # 第二轮对话
    messages.append({"role": "user", "content": "它有哪些应用？"})
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages
    )
    assistant_reply = response.choices[0].message.content
    print(f"用户: 它有哪些应用？")
    print(f"助手: {assistant_reply}\n")


def with_config_example():
    """使用配置类的示例"""
    print("=" * 50)
    print("使用配置类示例")
    print("=" * 50)

    # 导入配置
    from config.deepseek import deepseek_settings

    # 验证API密钥
    if not deepseek_settings.validate_api_key():
        print("错误: DEEPSEEK_API_KEY 未配置或无效")
        return

    client = OpenAI(
        api_key=deepseek_settings.api_key,
        base_url=deepseek_settings.base_url
    )

    # 使用配置中的参数
    model_config = deepseek_settings.get_model_config()

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "介绍一下DeepSeek"},
        ],
        **model_config
    )

    print("回复:", response.choices[0].message.content)
    print()


def error_handling_example():
    """错误处理示例"""
    print("=" * 50)
    print("错误处理示例")
    print("=" * 50)

    from openai import APIError, APIConnectionError, RateLimitError

    client = OpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=100
        )
        print("成功:", response.choices[0].message.content)

    except RateLimitError as e:
        print(f"速率限制错误: {e}")
    except APIConnectionError as e:
        print(f"连接错误: {e}")
    except APIError as e:
        print(f"API错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
    print()


def main():
    """主函数"""
    # 检查API密钥
    if not os.environ.get('DEEPSEEK_API_KEY'):
        print("错误: 请设置环境变量 DEEPSEEK_API_KEY")
        print("示例: export DEEPSEEK_API_KEY=your_api_key_here")
        return

    print("DeepSeek官方API示例\n")

    # 运行各个示例
    try:
        basic_chat_example()
        streaming_chat_example()
        medical_assistant_example()
        multi_turn_conversation_example()
        with_config_example()
        error_handling_example()

        print("=" * 50)
        print("所有示例运行完成!")
        print("=" * 50)

    except Exception as e:
        print(f"运行错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
