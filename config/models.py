"""
模型注册表
管理不同模型的API配置和访问方式
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str          # 模型名称
    api_key: Optional[str]   # API密钥
    base_url: str            # API基础URL
    provider: str            # 提供商名称
    max_tokens: int = 2000   # 最大token数


class ModelRegistry:
    """模型注册表 - 管理所有模型的API配置"""

    def __init__(self, config_dir: str = "."):
        """
        初始化模型注册表

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = Path(config_dir)
        self.models: Dict[str, ModelConfig] = {}
        self._load_configurations()

    def _load_configurations(self):
        """从配置文件加载所有模型配置"""

        # 补充实际使用的Kimi模型名称（通过JieKou API代理访问）
        if "moonshotai/kimi-k2-0905" not in self.models:
            self.register_model(
                model_name="moonshotai/kimi-k2-0905",
                api_key=os.getenv("JIEKOU_API_KEY"),  # 使用JieKou API密钥
                base_url="https://api.jiekou.ai/openai",  # 通过JieKou API代理
                provider="Kimi (月之暗面) via JieKou",
                max_tokens=20000
            )

        # 2. 加载 Doubao 配置
        doubao_config = self._load_json_config("batch_config_doubao.json")
        if doubao_config:
            api_config = doubao_config.get("api_config", {})
            for model in doubao_config.get("models", []):
                self.register_model(
                    model_name=model,
                    api_key=api_config.get("api_key"),
                    base_url=api_config.get("base_url"),
                    provider="豆包 (火山引擎)",
                    max_tokens=doubao_config.get("max_tokens", 20000)
                )

        # 3. 加载 Qwen 配置
        qwen_config = self._load_json_config("batch_config_qwen.json")
        if qwen_config:
            api_config = qwen_config.get("api_config", {})
            for model in qwen_config.get("models", []):
                self.register_model(
                    model_name=model,
                    api_key=api_config.get("api_key"),
                    base_url=api_config.get("base_url"),
                    provider="通义千问 (阿里云)",
                    max_tokens=qwen_config.get("max_tokens", 20000)
                )

        # 4. 加载 Baichuan 配置
        baichuan_config = self._load_json_config("batch_config_baichuan.json")
        if baichuan_config:
            api_config = baichuan_config.get("api_config", {})
            for model in baichuan_config.get("models", []):
                self.register_model(
                    model_name=model,
                    api_key=api_config.get("api_key"),
                    base_url=api_config.get("base_url"),
                    provider="百川智能",
                    max_tokens=baichuan_config.get("max_tokens", 20000)
                )

        # 5. 从环境变量加载默认配置（用于JieKou API）
        from config import settings
        default_base_url = settings.jiekou_base_url
        default_api_key = settings.jiekou_api_key

        # 为其他模型注册默认配置
        default_models = [
            "gpt-5.1",
            "deepseek/deepseek-v3.1",
            "gemini-2.5-pro",
            "grok-4-0709"
        ]

        for model in default_models:
            if model not in self.models:
                self.register_model(
                    model_name=model,
                    api_key=default_api_key,
                    base_url=default_base_url,
                    provider="JieKou API",
                    max_tokens=20000
                )

        print(f"✓ 模型注册表已加载，共 {len(self.models)} 个模型")

    def _load_json_config(self, filename: str) -> Optional[Dict]:
        """加载JSON配置文件"""
        config_path = self.config_dir / filename
        if not config_path.exists():
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  加载配置失败: {filename} - {e}")
            return None

    def register_model(
        self,
        model_name: str,
        api_key: Optional[str],
        base_url: str,
        provider: str,
        max_tokens: int = 20000
    ):
        """
        注册模型配置

        Args:
            model_name: 模型名称
            api_key: API密钥
            base_url: API基础URL
            provider: 提供商名称
            max_tokens: 最大token数
        """
        self.models[model_name] = ModelConfig(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            provider=provider,
            max_tokens=max_tokens
        )

    def get_model_config(self, model_name: str) -> Optional[ModelConfig]:
        """
        获取模型配置

        Args:
            model_name: 模型名称

        Returns:
            模型配置，如果不存在返回None
        """
        return self.models.get(model_name)

    def list_models(self) -> Dict[str, str]:
        """
        列出所有已注册的模型

        Returns:
            {模型名称: 提供商} 字典
        """
        return {
            name: config.provider
            for name, config in self.models.items()
        }

    def export_to_json(self, output_file: str = "model_registry.json"):
        """
        导出模型注册表到JSON文件

        Args:
            output_file: 输出文件路径
        """
        export_data = {}
        for name, config in self.models.items():
            export_data[name] = {
                "provider": config.provider,
                "base_url": config.base_url,
                "has_api_key": config.api_key is not None,
                "max_tokens": config.max_tokens
            }

        output_path = self.config_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"✓ 模型注册表已导出: {output_path}")
