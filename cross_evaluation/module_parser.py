"""
报告模块解析器
用于识别和提取医疗报告中的各个模块
"""
import re
from typing import Dict, List, Tuple


class ReportModuleParser:
    """医疗报告模块解析器"""

    # 定义标准模块及其可能的标识
    MODULE_PATTERNS = {
        "主诉": [
            r"主诉[：:]\s*(.+?)(?=现病史|既往史|家族史|个人史|##|\n\n|$)",
            r"^(.+?)\n现病史",  # 第一行作为主诉
        ],
        "现病史": [
            r"现病史[：:]\s*(.+?)(?=既往史|家族史|个人史|##|\n\n患者预问诊|$)",
            r"(?:现病史|病史摘要)[：:](.+?)(?=既往史|家族史|$)",
        ],
        "既往史": [
            r"既往史[：:]\s*(.+?)(?=家族史|个人史|##|\n\n|$)",
            r"既往[有]?(.+?)(?=家族史|个人史|$)",
        ],
        "家族史": [
            r"家族史[：:]\s*(.+?)(?=个人史|##|\n\n|$)",
            r"(?:家族史|家族病史)[：:](.+?)(?=个人史|##|$)",
        ],
        "个人史": [
            r"个人史[：:]\s*(.+?)(?=##|\n\n|$)",
        ]
    }

    def __init__(self):
        """初始化解析器"""
        pass

    def parse_report(self, report: str) -> Dict[str, str]:
        """
        解析报告，提取各个模块

        Args:
            report: 完整的医疗报告文本

        Returns:
            模块字典 {模块名: 内容}
        """
        modules = {}

        # 检查报告是否包含结构化标记（##或**）
        has_structured_format = "##" in report or "- **" in report

        if has_structured_format:
            # 解析结构化部分
            modules = self._parse_structured_report(report)
        else:
            # 尝试使用正则模式提取
            for module_name, patterns in self.MODULE_PATTERNS.items():
                content = self._extract_module(report, patterns)
                if content:
                    modules[module_name] = content.strip()

        # 如果没有找到任何模块，尝试简单分段
        if not modules:
            modules = self._parse_by_sections(report)

        return modules

    def _extract_module(self, report: str, patterns: List[str]) -> str:
        """
        使用正则模式提取模块内容

        Args:
            report: 报告文本
            patterns: 正则模式列表

        Returns:
            提取的内容
        """
        for pattern in patterns:
            match = re.search(pattern, report, re.DOTALL | re.MULTILINE)
            if match:
                # 如果有捕获组，返回第一个捕获组
                if match.groups():
                    return match.group(1)
                else:
                    return match.group(0)

        return ""

    def _parse_structured_report(self, report: str) -> Dict[str, str]:
        """
        解析结构化报告（包含**或##标记的）

        Args:
            report: 报告文本

        Returns:
            模块字典
        """
        modules = {}

        # 提取主诉
        chief_match = re.search(r'-\s*\*\*主诉[：:]\*\*\s*(.+?)(?=\n|$)', report)
        if chief_match:
            modules["主诉"] = chief_match.group(1).strip()

        # 提取现病史
        present_match = re.search(
            r'-\s*\*\*现病史[：:]\*\*\s*(.+?)(?=-\s*\*\*既往|$)',
            report,
            re.DOTALL
        )
        if present_match:
            modules["现病史"] = present_match.group(1).strip()

        # 提取既往史/既往病史
        past_match = re.search(
            r'-\s*\*\*既往(?:病)?史[：:]\*\*\s*(.+?)(?=-\s*\*\*|$)',
            report,
            re.DOTALL
        )
        if past_match:
            modules["既往史"] = past_match.group(1).strip()

        # 提取家族史/家族病史
        family_match = re.search(
            r'-\s*\*\*家族(?:病)?史[：:]\*\*\s*(.+?)(?=-\s*\*\*|$)',
            report,
            re.DOTALL
        )
        if family_match:
            modules["家族史"] = family_match.group(1).strip()

        # 提取个人史
        personal_match = re.search(
            r'-\s*\*\*(?:个人史|烟酒史)[：:]\*\*\s*(.+?)(?=-\s*\*\*|$)',
            report,
            re.DOTALL
        )
        if personal_match:
            modules["个人史"] = personal_match.group(1).strip()

        # 如果报告以传统格式开头（\n分隔），也提取那部分
        if report.startswith("发现") or "\\n" in report[:100]:
            self._parse_traditional_part(report, modules)

        return modules

    def _parse_traditional_part(self, report: str, modules: Dict[str, str]):
        """
        解析报告中的传统叙述部分

        Args:
            report: 报告文本
            modules: 已解析的模块字典（会被修改）
        """
        # 按\\n分段
        parts = report.split('\\n')

        if len(parts) >= 1 and not modules.get("主诉"):
            # 第一段通常是主诉
            first_line = parts[0].strip()
            if first_line and "##" not in first_line:
                modules["主诉_叙述部分"] = first_line

        if len(parts) >= 2:
            # 第二段是现病史
            second_part = parts[1].strip()
            if second_part and "##" not in second_part and "既往" not in second_part:
                modules["现病史_叙述部分"] = second_part

        if len(parts) >= 3:
            # 第三段可能是既往史
            third_part = parts[2].strip()
            if third_part and "##" not in third_part:
                if "既往" in third_part:
                    modules["既往史_叙述部分"] = third_part

    def _parse_by_sections(self, report: str) -> Dict[str, str]:
        """
        通过段落分隔来解析报告

        Args:
            report: 报告文本

        Returns:
            模块字典
        """
        # 按双换行符分段
        sections = report.split('\n\n')
        modules = {}

        if len(sections) >= 2:
            # 第一段通常是主诉
            modules["主诉"] = sections[0]

            # 中间段落可能是现病史
            if len(sections) >= 3:
                modules["现病史"] = sections[1]

            # 后续段落
            for i, section in enumerate(sections[2:], start=2):
                if "既往" in section:
                    modules["既往史"] = section
                elif "家族" in section:
                    modules["家族史"] = section
                elif "个人" in section or "吸烟" in section or "饮酒" in section:
                    modules["个人史"] = section

        return modules

    def identify_modules_in_report(self, report: str) -> List[Tuple[str, int, int]]:
        """
        识别报告中各模块的位置

        Args:
            report: 报告文本

        Returns:
            [(模块名, 起始位置, 结束位置), ...]
        """
        module_positions = []

        # 查找各模块的关键词位置
        keywords = {
            "主诉": ["主诉"],
            "现病史": ["现病史", "病史摘要"],
            "既往史": ["既往史", "既往病史"],
            "家族史": ["家族史", "家族病史"],
            "个人史": ["个人史"]
        }

        for module_name, kws in keywords.items():
            for keyword in kws:
                pos = report.find(keyword)
                if pos >= 0:
                    # 找到下一个模块的位置作为结束位置
                    end_pos = len(report)
                    for other_module, other_kws in keywords.items():
                        if other_module != module_name:
                            for other_kw in other_kws:
                                other_pos = report.find(other_kw, pos + len(keyword))
                                if other_pos > pos and other_pos < end_pos:
                                    end_pos = other_pos

                    module_positions.append((module_name, pos, end_pos))
                    break

        # 按位置排序
        module_positions.sort(key=lambda x: x[1])

        return module_positions

    def get_module_summary(self, report: str) -> Dict[str, Dict[str, any]]:
        """
        获取模块摘要信息

        Args:
            report: 报告文本

        Returns:
            模块摘要字典
        """
        modules = self.parse_report(report)
        positions = self.identify_modules_in_report(report)

        summary = {}
        for module_name, content in modules.items():
            summary[module_name] = {
                "content": content,
                "length": len(content),
                "has_content": bool(content.strip()),
                "preview": content[:100] + "..." if len(content) > 100 else content
            }

        # 添加位置信息
        for module_name, start, end in positions:
            if module_name in summary:
                summary[module_name]["start_pos"] = start
                summary[module_name]["end_pos"] = end

        return summary


# 创建全局实例
module_parser = ReportModuleParser()
