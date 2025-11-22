"""
模型客户端工厂
根据模型名称创建正确配置的API客户端
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from chat_client import ChatClient
from .model_registry import ModelRegistry, ModelConfig

# 尝试导入DeepSeek客户端
try:
    from .deepseek_client import DeepSeekClient
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DEEPSEEK_AVAILABLE = False
    DeepSeekClient = None


class ModelClientFactory:
    """模型客户端工厂"""

    def __init__(self, config_dir: str = "."):
        """
        初始化工厂

        Args:
            config_dir: 配置文件目录
        """
        self.registry = ModelRegistry(config_dir)
        self._client_cache = {}  # 缓存已创建的客户端

    def _is_deepseek_official(self, model_name: str, config: ModelConfig) -> bool:
        """
        判断是否是DeepSeek官方API

        Args:
            model_name: 模型名称
            config: 模型配置

        Returns:
            是否是DeepSeek官方API
        """
        return (
            DEEPSEEK_AVAILABLE and
            "api.deepseek.com" in config.base_url and
            model_name.startswith("deepseek-")
        )

    def create_client(self, model_name: str, **kwargs):
        """
        为指定模型创建API客户端

        Args:
            model_name: 模型名称
            **kwargs: 额外的客户端参数

        Returns:
            配置好的客户端实例（ChatClient 或 DeepSeekClient）

        Raises:
            ValueError: 如果模型未注册
        """
        # 检查缓存
        if model_name in self._client_cache:
            return self._client_cache[model_name]

        # 获取模型配置
        config = self.registry.get_model_config(model_name)
        if not config:
            raise ValueError(
                f"模型 '{model_name}' 未注册。\n"
                f"已注册的模型: {list(self.registry.models.keys())}"
            )

        # 根据配置创建不同类型的客户端
        if self._is_deepseek_official(model_name, config):
            # 使用DeepSeek官方客户端
            client = DeepSeekClient(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=kwargs.get('timeout', 60)
            )
        else:
            # 使用通用ChatClient
            client = ChatClient(
                api_key=config.api_key,
                base_url=config.base_url,
                model=model_name,
                **kwargs
            )

        # 缓存客户端
        self._client_cache[model_name] = client

        return client

    def list_available_models(self) -> dict:
        """
        列出所有可用模型

        Returns:
            {模型名称: 提供商} 字典
        """
        return self.registry.list_models()

    def get_model_info(self, model_name: str) -> dict:
        """
        获取模型信息

        Args:
            model_name: 模型名称

        Returns:
            模型信息字典
        """
        config = self.registry.get_model_config(model_name)
        if not config:
            return {"error": f"模型 '{model_name}' 未注册"}

        return {
            "model_name": config.model_name,
            "provider": config.provider,
            "base_url": config.base_url,
            "has_api_key": config.api_key is not None,
            "max_tokens": config.max_tokens
        }

    def clear_cache(self):
        """清除客户端缓存"""
        self._client_cache.clear()


# 创建全局工厂实例
_factory = None


def get_factory(config_dir: str = ".") -> ModelClientFactory:
    """
    获取全局工厂实例

    Args:
        config_dir: 配置文件目录

    Returns:
        ModelClientFactory实例
    """
    global _factory
    if _factory is None:
        _factory = ModelClientFactory(config_dir)
    return _factory


def create_client_for_model(model_name: str, config_dir: str = ".", **kwargs) -> ChatClient:
    """
    便捷函数：为指定模型创建客户端

    Args:
        model_name: 模型名称
        config_dir: 配置文件目录
        **kwargs: 额外的客户端参数

    Returns:
        ChatClient实例
    """
    factory = get_factory(config_dir)
    return factory.create_client(model_name, **kwargs)
