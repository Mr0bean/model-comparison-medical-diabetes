"""
通用模型服务 - Universal Model Service
统一的模型调用接口,支持所有API提供商

特性:
- 自动路由到正确的API提供商
- 统一的输入输出接口
- 支持所有模型(JieKou AI、百川、豆包、Kimi、Qwen等)
- 智能配置管理
"""
import os
import json
from typing import Dict, Any, Optional, List, Iterator, Union
from pathlib import Path
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """模型注册表 - 管理所有模型的配置和路由"""

    def __init__(self, registry_file: str = "model_registry.json"):
        """
        初始化模型注册表

        Args:
            registry_file: 模型注册表配置文件路径
        """
        self.registry_file = registry_file
        self.models = self._load_registry()

    def _load_registry(self) -> Dict[str, Dict[str, Any]]:
        """加载模型注册表"""
        if not Path(self.registry_file).exists():
            # 创建默认注册表
            default_registry = self._create_default_registry()
            self._save_registry(default_registry)
            return default_registry

        with open(self.registry_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _create_default_registry(self) -> Dict[str, Dict[str, Any]]:
        """创建默认模型注册表"""
        return {
            # JieKou AI 模型
            "gpt-5.1": {
                "provider": "jiekou",
                "api_key_env": "JIEKOU_API_KEY",
                "base_url": "https://api.jiekou.ai/openai",
                "description": "JieKou AI GPT-5.1"
            },
            "gemini-2.5-pro": {
                "provider": "jiekou",
                "api_key_env": "JIEKOU_API_KEY",
                "base_url": "https://api.jiekou.ai/openai",
                "description": "Google Gemini 2.5 Pro"
            },
            "deepseek/deepseek-v3.1": {
                "provider": "jiekou",
                "api_key_env": "JIEKOU_API_KEY",
                "base_url": "https://api.jiekou.ai/openai",
                "description": "DeepSeek V3.1 via JieKou"
            },
            "moonshotai/kimi-k2-0905": {
                "provider": "jiekou",
                "api_key_env": "JIEKOU_API_KEY",
                "base_url": "https://api.jiekou.ai/openai",
                "description": "Kimi K2 via JieKou"
            },
            "grok-4-0709": {
                "provider": "jiekou",
                "api_key_env": "JIEKOU_API_KEY",
                "base_url": "https://api.jiekou.ai/openai",
                "description": "Grok 4 via JieKou"
            },

            # 百川智能直连
            "Baichuan2-Turbo": {
                "provider": "baichuan",
                "api_key_env": "BAICHUAN_API_KEY",
                "base_url": "https://api.baichuan-ai.com/v1",
                "description": "百川2 Turbo"
            },
            "Baichuan2-Turbo-192k": {
                "provider": "baichuan",
                "api_key_env": "BAICHUAN_API_KEY",
                "base_url": "https://api.baichuan-ai.com/v1",
                "description": "百川2 Turbo 192K"
            },
            "Baichuan3-Turbo": {
                "provider": "baichuan",
                "api_key_env": "BAICHUAN_API_KEY",
                "base_url": "https://api.baichuan-ai.com/v1",
                "description": "百川3 Turbo"
            },
            "Baichuan3-Turbo-128k": {
                "provider": "baichuan",
                "api_key_env": "BAICHUAN_API_KEY",
                "base_url": "https://api.baichuan-ai.com/v1",
                "description": "百川3 Turbo 128K"
            },
            "Baichuan4": {
                "provider": "baichuan",
                "api_key_env": "BAICHUAN_API_KEY",
                "base_url": "https://api.baichuan-ai.com/v1",
                "description": "百川4"
            },

            # DeepSeek 官方直连
            "deepseek-reasoner": {
                "provider": "deepseek",
                "api_key_env": "DEEPSEEK_API_KEY",
                "base_url": "https://api.deepseek.com",
                "description": "DeepSeek Reasoner (官方)"
            },
            "deepseek-chat": {
                "provider": "deepseek",
                "api_key_env": "DEEPSEEK_API_KEY",
                "base_url": "https://api.deepseek.com",
                "description": "DeepSeek Chat (官方)"
            }
        }

    def _save_registry(self, registry: Dict[str, Dict[str, Any]]):
        """保存模型注册表"""
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)

    def get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型配置

        Args:
            model_name: 模型名称

        Returns:
            模型配置字典

        Raises:
            ValueError: 如果模型未注册
        """
        if model_name not in self.models:
            available_models = list(self.models.keys())
            raise ValueError(
                f"模型 '{model_name}' 未注册。\n"
                f"可用模型: {', '.join(available_models[:5])}... (共{len(available_models)}个)\n"
                f"请检查 {self.registry_file} 或使用 register_model() 注册新模型"
            )

        return self.models[model_name]

    def register_model(
        self,
        model_name: str,
        provider: str,
        api_key_env: str,
        base_url: str,
        description: str = ""
    ):
        """
        注册新模型

        Args:
            model_name: 模型名称
            provider: 提供商名称
            api_key_env: API Key 环境变量名
            base_url: API 基础URL
            description: 模型描述
        """
        self.models[model_name] = {
            "provider": provider,
            "api_key_env": api_key_env,
            "base_url": base_url,
            "description": description
        }
        self._save_registry(self.models)
        logger.info(f"已注册模型: {model_name} ({provider})")

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        """
        列出所有模型

        Args:
            provider: 可选,仅列出指定提供商的模型

        Returns:
            模型名称列表
        """
        if provider:
            return [
                name for name, config in self.models.items()
                if config["provider"] == provider
            ]
        return list(self.models.keys())

    def list_providers(self) -> List[str]:
        """列出所有提供商"""
        providers = set(config["provider"] for config in self.models.values())
        return sorted(list(providers))


class UniversalModelService:
    """
    通用模型服务 - 统一的模型调用接口

    使用方法:
        service = UniversalModelService()

        # 方法1: 一次性调用
        response = service.call(
            model="gpt-5.1",
            prompt="你好",
            system_prompt="你是一个AI助手"
        )

        # 方法2: 流式调用
        for chunk in service.call(
            model="deepseek-reasoner",
            prompt="解释量子计算",
            stream=True
        ):
            print(chunk, end="")

        # 方法3: 批量调用
        results = service.batch_call(
            model="Baichuan4",
            prompts=["问题1", "问题2", "问题3"]
        )
    """

    def __init__(self, registry_file: str = "model_registry.json"):
        """
        初始化通用模型服务

        Args:
            registry_file: 模型注册表文件路径
        """
        self.registry = ModelRegistry(registry_file)
        self.clients = {}  # 缓存客户端实例
        logger.info(f"通用模型服务已初始化")
        logger.info(f"已加载 {len(self.registry.list_models())} 个模型")
        logger.info(f"支持提供商: {', '.join(self.registry.list_providers())}")

    def _get_client(self, model_name: str) -> OpenAI:
        """
        获取或创建模型对应的客户端

        Args:
            model_name: 模型名称

        Returns:
            OpenAI 客户端实例
        """
        # 检查缓存
        if model_name in self.clients:
            return self.clients[model_name]

        # 获取模型配置
        config = self.registry.get_model_config(model_name)

        # 获取API Key
        api_key = os.getenv(config["api_key_env"])
        if not api_key:
            raise ValueError(
                f"API Key 未配置。请设置环境变量: {config['api_key_env']}"
            )

        # 创建客户端
        client = OpenAI(
            api_key=api_key,
            base_url=config["base_url"],
            timeout=60.0
        )

        # 缓存客户端
        self.clients[model_name] = client
        logger.info(f"已创建客户端: {model_name} ({config['provider']})")

        return client

    def call(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        stream: bool = False,
        temperature: float = 0.3,
        max_tokens: int = 2000,
        **kwargs
    ) -> Union[str, Iterator[str]]:
        """
        调用模型 - 统一接口

        Args:
            model: 模型名称
            prompt: 用户提示词
            system_prompt: 系统提示词(可选)
            stream: 是否流式输出
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数(top_p, frequency_penalty等)

        Returns:
            如果stream=False,返回完整响应字符串
            如果stream=True,返回迭代器
        """
        client = self._get_client(model)

        # 构建消息
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # 准备参数
        params = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        logger.info(f"调用模型: {model}, stream={stream}")

        try:
            response = client.chat.completions.create(**params)

            if stream:
                return self._handle_stream(response)
            else:
                return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"模型调用失败 ({model}): {str(e)}")
            raise

    def _handle_stream(self, response) -> Iterator[str]:
        """处理流式响应"""
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content

    def batch_call(
        self,
        model: str,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        批量调用模型

        Args:
            model: 模型名称
            prompts: 提示词列表
            system_prompt: 系统提示词
            **kwargs: 其他参数

        Returns:
            响应列表
        """
        results = []
        for i, prompt in enumerate(prompts):
            logger.info(f"批量处理: {i+1}/{len(prompts)}")
            response = self.call(
                model=model,
                prompt=prompt,
                system_prompt=system_prompt,
                stream=False,
                **kwargs
            )
            results.append(response)

        return results

    def list_models(self, provider: Optional[str] = None) -> List[str]:
        """
        列出可用模型

        Args:
            provider: 可选,仅列出指定提供商的模型

        Returns:
            模型列表
        """
        return self.registry.list_models(provider)

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        获取模型信息

        Args:
            model: 模型名称

        Returns:
            模型配置信息
        """
        return self.registry.get_model_config(model)


# 便捷函数
def create_service(registry_file: str = "model_registry.json") -> UniversalModelService:
    """
    创建通用模型服务实例

    Args:
        registry_file: 模型注册表文件

    Returns:
        UniversalModelService 实例
    """
    return UniversalModelService(registry_file)


def call_model(
    model: str,
    prompt: str,
    **kwargs
) -> str:
    """
    快速调用模型的便捷函数

    Args:
        model: 模型名称
        prompt: 提示词
        **kwargs: 其他参数

    Returns:
        模型响应
    """
    service = create_service()
    return service.call(model=model, prompt=prompt, stream=False, **kwargs)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # 示例用法
    print("=" * 60)
    print("通用模型服务 - 使用示例")
    print("=" * 60)

    # 创建服务
    service = create_service()

    # 列出所有可用模型
    print("\n可用模型:")
    for provider in service.registry.list_providers():
        models = service.list_models(provider)
        print(f"  [{provider}] {len(models)} 个模型")
        for model in models[:2]:  # 只显示前2个
            info = service.get_model_info(model)
            print(f"    - {model}: {info['description']}")

    print(f"\n共 {len(service.list_models())} 个模型")

    # 示例调用(需要配置API Key)
    print("\n" + "=" * 60)
    print("调用示例:")
    print("=" * 60)
    print("""
# 示例1: 简单调用
response = service.call(
    model="gpt-5.1",
    prompt="用一句话介绍自己"
)

# 示例2: 流式调用
for chunk in service.call(
    model="deepseek-reasoner",
    prompt="解释量子计算",
    stream=True
):
    print(chunk, end="")

# 示例3: 批量调用
results = service.batch_call(
    model="Baichuan4",
    prompts=["问题1", "问题2", "问题3"],
    system_prompt="你是一个AI助手"
)

# 示例4: 快捷函数
response = call_model("gemini-2.5-pro", "什么是AI?")
    """)
