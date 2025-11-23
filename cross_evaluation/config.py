"""
交叉评测配置模块
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any


class CrossEvaluationConfig:
    """交叉评测配置类"""

    def __init__(self, config_path: str = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，默认为 config/cross_evaluation_config.json
        """
        if config_path is None:
            # 默认配置文件路径
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "cross_evaluation_config.json"

        self.config_path = Path(config_path)
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = json.load(f)

    @property
    def models(self) -> List[str]:
        """获取参与评测的模型列表"""
        return self._config.get("models", [])

    @property
    def patients(self) -> List[str]:
        """获取患者列表"""
        return self._config.get("patients", [])

    @property
    def dimensions(self) -> List[Dict[str, Any]]:
        """获取评测维度列表"""
        return self._config.get("dimensions", [])

    @property
    def prompt_base_dir(self) -> Path:
        """获取Prompt基础目录"""
        base_dir = Path(__file__).parent.parent
        return base_dir / self._config.get("prompt_base_dir", "Prompts/PromptForReportTest/Prompts")

    @property
    def raw_reports_dir(self) -> Path:
        """获取原始报告目录"""
        base_dir = Path(__file__).parent.parent
        return base_dir / self._config.get("raw_reports_dir", "output/raw")

    @property
    def output_dir(self) -> Path:
        """获取输出目录"""
        base_dir = Path(__file__).parent.parent
        return base_dir / self._config.get("output_dir", "output/cross_evaluation_results")

    @property
    def api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self._config.get("api_config", {
            "temperature": 0,
            "max_tokens": 4000,
            "retry_attempts": 3,
            "retry_delay": 2
        })

    @property
    def concurrency_config(self) -> Dict[str, Any]:
        """获取并发配置"""
        return self._config.get("concurrency", {"max_workers": 3})

    def get_dimension_file(self, dimension_name: str) -> Path:
        """
        获取指定维度的Prompt文件路径

        Args:
            dimension_name: 维度名称

        Returns:
            Prompt文件路径
        """
        for dim in self.dimensions:
            if dim["name"] == dimension_name:
                return self.prompt_base_dir / dim["file"]

        raise ValueError(f"未找到维度: {dimension_name}")

    def get_dimension_weight(self, dimension_name: str) -> int:
        """
        获取指定维度的权重

        Args:
            dimension_name: 维度名称

        Returns:
            维度权重（满分）
        """
        for dim in self.dimensions:
            if dim["name"] == dimension_name:
                return dim["weight"]

        raise ValueError(f"未找到维度: {dimension_name}")

    def get_total_score(self) -> int:
        """获取总分"""
        return sum(dim["weight"] for dim in self.dimensions)


# 创建全局配置实例
config = CrossEvaluationConfig()
