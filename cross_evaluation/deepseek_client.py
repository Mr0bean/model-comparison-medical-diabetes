"""
DeepSeek官方API客户端工厂

提供DeepSeek官方API的客户端创建和管理功能
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI


class DeepSeekClient:
    """DeepSeek官方API客户端封装"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        timeout: int = 60
    ):
        """
        初始化DeepSeek客户端

        Args:
            api_key: API密钥，如果不提供则从环境变量读取
            base_url: API基础URL
            timeout: 超时时间（秒）
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = base_url
        self.timeout = timeout

        if not self.api_key:
            raise ValueError(
                "DeepSeek API密钥未配置。请设置环境变量 DEEPSEEK_API_KEY "
                "或在初始化时提供 api_key 参数。"
            )

        # 创建OpenAI兼容客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )

    def chat(
        self,
        messages: list,
        model: str = "deepseek-chat",
        temperature: float = 1.0,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        发送聊天请求

        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            stream: 是否流式输出
            **kwargs: 其他参数

        Returns:
            API响应
        """
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )

    def chat_completion(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant",
        model: str = "deepseek-chat",
        **kwargs
    ) -> str:
        """
        简化的聊天完成接口

        Args:
            prompt: 用户提示
            system_message: 系统消息
            model: 模型名称
            **kwargs: 其他参数

        Returns:
            模型回复内容
        """
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]

        response = self.chat(messages=messages, model=model, **kwargs)
        return response.choices[0].message.content

    @staticmethod
    def is_configured() -> bool:
        """检查DeepSeek API是否已配置"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        return bool(api_key and api_key.startswith('sk-'))


class DeepSeekClientFactory:
    """DeepSeek客户端工厂类"""

    _instances: Dict[str, DeepSeekClient] = {}

    @classmethod
    def get_client(
        cls,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        timeout: int = 60,
        cache: bool = True
    ) -> DeepSeekClient:
        """
        获取DeepSeek客户端实例

        Args:
            api_key: API密钥
            base_url: API基础URL
            timeout: 超时时间
            cache: 是否缓存实例

        Returns:
            DeepSeekClient实例
        """
        if not cache:
            return DeepSeekClient(api_key, base_url, timeout)

        # 使用缓存
        cache_key = f"{api_key or 'default'}:{base_url}"
        if cache_key not in cls._instances:
            cls._instances[cache_key] = DeepSeekClient(
                api_key, base_url, timeout
            )

        return cls._instances[cache_key]

    @classmethod
    def clear_cache(cls):
        """清空客户端缓存"""
        cls._instances.clear()


def get_deepseek_client(**kwargs) -> DeepSeekClient:
    """
    获取DeepSeek客户端的便捷函数

    Args:
        **kwargs: 传递给DeepSeekClientFactory.get_client的参数

    Returns:
        DeepSeekClient实例

    Example:
        >>> client = get_deepseek_client()
        >>> response = client.chat_completion("Hello, DeepSeek!")
        >>> print(response)
    """
    return DeepSeekClientFactory.get_client(**kwargs)


# 用法示例
if __name__ == "__main__":
    # 检查配置
    if not DeepSeekClient.is_configured():
        print("错误: DEEPSEEK_API_KEY 未配置")
        print("请运行: export DEEPSEEK_API_KEY=your_api_key")
        exit(1)

    # 创建客户端
    client = get_deepseek_client()

    # 简单对话
    response = client.chat_completion(
        prompt="介绍一下DeepSeek",
        max_tokens=200
    )
    print("回复:", response)

    # 流式输出示例
    print("\n流式输出:")
    stream = client.chat(
        messages=[{"role": "user", "content": "数到5"}],
        stream=True,
        max_tokens=50
    )

    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()
