"""
配置管理模块
使用 pydantic-settings 进行配置管理和验证
"""
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """应用配置类"""

    # API 配置
    jiekou_api_key: str = Field(
        default="your_api_key_here",
        description="JieKou AI API Key"
    )
    jiekou_base_url: str = Field(
        default="https://api.jiekou.ai/openai",
        description="JieKou AI API Base URL"
    )

    # 默认模型设置
    default_model: str = Field(
        default="gpt-5.1",
        description="默认使用的模型"
    )
    default_temperature: Optional[float] = Field(
        default=None,  # gpt-5.1有beta限制，不能设置temperature
        ge=0.0,
        le=2.0,
        description="默认温度参数"
    )
    default_max_tokens: Optional[int] = Field(
        default=2048,
        gt=0,
        description="默认最大token数"
    )
    default_stream: bool = Field(
        default=True,
        description="默认是否使用流式输出"
    )

    # 日志配置
    log_level: str = Field(
        default="INFO",
        description="日志级别"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    def validate_api_key(self) -> bool:
        """验证API Key是否配置"""
        return bool(self.jiekou_api_key and self.jiekou_api_key != "your_api_key_here")


# 全局配置实例
settings = Settings()
