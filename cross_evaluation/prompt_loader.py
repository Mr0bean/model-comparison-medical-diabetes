"""
Prompt加载器模块
用于加载和格式化评测prompt
"""
from pathlib import Path
from typing import Dict, Any
from .config import config


class PromptLoader:
    """Prompt加载器"""

    def __init__(self):
        """初始化Prompt加载器"""
        self.prompt_base_dir = config.prompt_base_dir
        self._prompt_cache = {}

    def load_dimension_prompt(self, dimension_name: str) -> str:
        """
        加载指定维度的Prompt模板

        Args:
            dimension_name: 维度名称（如 "准确性"）

        Returns:
            Prompt模板内容
        """
        # 检查缓存
        if dimension_name in self._prompt_cache:
            return self._prompt_cache[dimension_name]

        # 获取Prompt文件路径
        prompt_file = config.get_dimension_file(dimension_name)

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt文件不存在: {prompt_file}")

        # 读取Prompt内容
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()

        # 缓存
        self._prompt_cache[dimension_name] = prompt_content

        return prompt_content

    def format_prompt(
        self,
        dimension_name: str,
        conversation: str,
        report: str
    ) -> str:
        """
        格式化Prompt，填充原始对话和生成的报告

        Args:
            dimension_name: 维度名称
            conversation: 原始对话内容
            report: 生成的医疗报告

        Returns:
            格式化后的Prompt
        """
        # 加载模板
        template = self.load_dimension_prompt(dimension_name)

        # 构建完整的prompt
        # Prompt文件本身包含了角色设定和任务目标，我们需要在后面附加实际数据
        formatted_prompt = f"""{template}

---

【原始对话】

{conversation}

---

【生成的医疗报告】

{report}

---

请按照上述要求对该报告进行评测，并以JSON格式输出结果。
"""

        return formatted_prompt

    def get_all_dimensions(self) -> list:
        """
        获取所有评测维度

        Returns:
            维度列表
        """
        return [dim["name"] for dim in config.dimensions]


# 创建全局实例
prompt_loader = PromptLoader()
