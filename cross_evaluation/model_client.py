"""
模型客户端模块
用于调用各个模型的API进行评测
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI
from .config import config


class ModelClient:
    """模型API客户端"""

    def __init__(self):
        """初始化模型客户端"""
        # 加载模型注册表
        self.model_registry = self._load_model_registry()
        self.api_config = config.api_config

    def _load_model_registry(self) -> Dict[str, Any]:
        """加载模型注册表"""
        base_dir = Path(__file__).parent.parent
        registry_path = base_dir / "config" / "models" / "model_registry.json"

        if not registry_path.exists():
            raise FileNotFoundError(f"模型注册表不存在: {registry_path}")

        with open(registry_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_model_config(self, model_name: str) -> Dict[str, Any]:
        """
        获取模型配置

        Args:
            model_name: 模型名称

        Returns:
            模型配置信息
        """
        # 尝试直接匹配
        if model_name in self.model_registry:
            return self.model_registry[model_name]

        # 尝试将下划线转换为斜杠匹配（如 deepseek_deepseek-v3.1 -> deepseek/deepseek-v3.1）
        normalized_name = model_name.replace("_", "/", 1)
        if normalized_name in self.model_registry:
            return self.model_registry[normalized_name]

        # 尝试特殊映射
        # Baichuan-M2 可能对应 Baichuan2-Turbo 或其他版本
        model_mapping = {
            "Baichuan-M2": "Baichuan2-Turbo",
            "doubao-seed-1-6-251015": "gpt-5.1",  # 如果没有配置，使用替代模型
            "qwen3-max": "gpt-5.1"  # 如果没有配置，使用替代模型
        }

        if model_name in model_mapping:
            mapped_name = model_mapping[model_name]
            if mapped_name in self.model_registry:
                return self.model_registry[mapped_name]

        raise ValueError(f"未找到模型配置: {model_name}")

    def _create_client(self, model_name: str) -> OpenAI:
        """
        创建OpenAI客户端

        Args:
            model_name: 模型名称

        Returns:
            OpenAI客户端实例
        """
        model_config = self._get_model_config(model_name)

        # 获取API密钥
        api_key_env = model_config.get("api_key_env")
        api_key = os.getenv(api_key_env)

        if not api_key:
            raise ValueError(f"未设置环境变量: {api_key_env}")

        # 创建客户端
        client = OpenAI(
            api_key=api_key,
            base_url=model_config.get("base_url")
        )

        return client

    def call_model(
        self,
        model_name: str,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        调用模型API

        Args:
            model_name: 模型名称
            prompt: 输入prompt
            temperature: 温度参数（默认使用配置中的值）
            max_tokens: 最大token数（默认使用配置中的值）

        Returns:
            模型响应内容
        """
        # 使用配置中的默认值
        if temperature is None:
            temperature = self.api_config.get("temperature", 0)
        if max_tokens is None:
            max_tokens = self.api_config.get("max_tokens", 4000)

        # 重试逻辑
        retry_attempts = self.api_config.get("retry_attempts", 3)
        retry_delay = self.api_config.get("retry_delay", 2)

        for attempt in range(retry_attempts):
            try:
                # 创建客户端
                client = self._create_client(model_name)

                # 获取实际的模型ID（用于API调用）
                model_config = self._get_model_config(model_name)

                # 对于jiekou provider，需要使用原始模型名
                # 对于其他provider，也使用模型名
                actual_model_name = model_name.replace("_", "/", 1) if "_" in model_name else model_name

                # 如果在model_registry中，直接使用key
                if model_name in self.model_registry:
                    actual_model_name = model_name
                elif model_name.replace("_", "/", 1) in self.model_registry:
                    actual_model_name = model_name.replace("_", "/", 1)

                # 调用API
                response = client.chat.completions.create(
                    model=actual_model_name,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # 提取响应内容
                content = response.choices[0].message.content

                return content

            except Exception as e:
                print(f"调用模型失败 (尝试 {attempt + 1}/{retry_attempts}): {model_name}")
                print(f"错误: {str(e)}")

                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"调用模型失败，已重试{retry_attempts}次: {model_name}") from e


# 创建全局实例
model_client = ModelClient()
