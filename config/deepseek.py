"""
DeepSeek官方API配置

官方文档: https://platform.deepseek.com/api-docs/
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DeepSeekSettings(BaseSettings):
    """DeepSeek API配置类"""

    # API配置
    api_key: str = Field(
        default="",
        description="DeepSeek API Key (从环境变量 DEEPSEEK_API_KEY 读取)"
    )
    base_url: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API Base URL"
    )

    # 模型配置
    default_model: str = Field(
        default="deepseek-reasoner",
        description="默认使用的DeepSeek模型"
    )

    # 可用模型列表
    available_models: list = Field(
        default=[
            "deepseek-chat",       # DeepSeek聊天模型
            "deepseek-coder",      # DeepSeek代码模型
            "deepseek-reasoner",   # DeepSeek推理模型（默认）
        ],
        description="可用的DeepSeek模型列表"
    )

    # 模型参数
    temperature: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="温度参数，控制随机性"
    )
    max_tokens: Optional[int] = Field(
        default=8192,
        gt=0,
        description="最大输出token数"
    )
    top_p: Optional[float] = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="核采样参数"
    )
    stream: bool = Field(
        default=False,
        description="是否使用流式输出"
    )

    # 超时配置
    timeout: int = Field(
        default=60,
        description="API调用超时时间(秒)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="DEEPSEEK_",  # 环境变量前缀
        case_sensitive=False,
        extra="ignore"
    )

    def validate_api_key(self) -> bool:
        """验证API Key是否配置"""
        return bool(self.api_key and self.api_key.startswith("sk-"))

    def get_model_config(self, model_name: str = None) -> dict:
        """获取模型配置"""
        model = model_name or self.default_model
        return {
            "model": model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stream": self.stream
        }


# 全局配置实例
deepseek_settings = DeepSeekSettings()


# 模型信息字典
DEEPSEEK_MODELS = {
    "deepseek-chat": {
        "name": "DeepSeek Chat",
        "description": "DeepSeek通用对话模型",
        "max_tokens": 4096,
        "context_window": 32768,
        "supports_streaming": True,
        "pricing": {
            "input": 0.0001,   # 每1k tokens
            "output": 0.0002
        }
    },
    "deepseek-coder": {
        "name": "DeepSeek Coder",
        "description": "DeepSeek代码专用模型",
        "max_tokens": 4096,
        "context_window": 16384,
        "supports_streaming": True,
        "pricing": {
            "input": 0.0001,
            "output": 0.0002
        }
    },
    "deepseek-reasoner": {
        "name": "DeepSeek Reasoner",
        "description": "DeepSeek推理增强模型",
        "max_tokens": 8192,
        "context_window": 65536,
        "supports_streaming": True,
        "pricing": {
            "input": 0.0002,
            "output": 0.0004
        }
    }
}
