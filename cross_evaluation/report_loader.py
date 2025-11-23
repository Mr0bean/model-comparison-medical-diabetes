"""
报告加载器模块
用于从output/raw目录加载医疗报告
"""
import json
from pathlib import Path
from typing import Dict, Any, Tuple
from .config import config


class ReportLoader:
    """报告加载器"""

    def __init__(self):
        """初始化报告加载器"""
        self.raw_reports_dir = config.raw_reports_dir

    def get_report_path(self, model_name: str, patient: str) -> Path:
        """
        获取报告文件路径

        Args:
            model_name: 模型名称
            patient: 患者名称

        Returns:
            报告文件路径
        """
        # 文件命名格式: {模型名称}-{患者}.json
        filename = f"{model_name}-{patient}.json"
        return self.raw_reports_dir / filename

    def load_report(self, model_name: str, patient: str) -> Dict[str, Any]:
        """
        加载指定模型和患者的报告

        Args:
            model_name: 模型名称
            patient: 患者名称

        Returns:
            报告JSON数据
        """
        report_path = self.get_report_path(model_name, patient)

        if not report_path.exists():
            raise FileNotFoundError(f"报告文件不存在: {report_path}")

        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_result(self, model_name: str, patient: str) -> str:
        """
        提取并重组报告为标准格式

        Args:
            model_name: 模型名称
            patient: 患者名称

        Returns:
            标准格式的完整病历报告
        """
        report_data = self.load_report(model_name, patient)
        conversations = report_data.get("conversations", {})

        # 从conversations中提取各段Output
        chief_complaint = ""  # 主诉 - 对话1
        present_illness = ""  # 现病史 - 对话2
        past_history = ""     # 既往史 - 对话3
        family_history = ""   # 家族史 - 从对话4提取

        # 提取主诉（对话1）
        conv1 = conversations.get("1") or conversations.get("对话1")
        if conv1:
            chief_complaint = conv1.get("Output", "").strip()

        # 提取现病史（对话2）
        conv2 = conversations.get("2") or conversations.get("对话2")
        if conv2:
            present_illness = conv2.get("Output", "").strip()

        # 提取既往史（对话3）
        conv3 = conversations.get("3") or conversations.get("对话3")
        if conv3:
            past_history = conv3.get("Output", "").strip()

        # 从对话4提取家族史
        conv4 = conversations.get("4") or conversations.get("对话4")
        if conv4:
            output4 = conv4.get("Output", "")
            # 提取家族病史部分
            import re
            family_match = re.search(
                r'-\s*\*\*家族(?:病)?史[：:]\*\*\s*(.+?)(?=-\s*\*\*|$)',
                output4,
                re.DOTALL
            )
            if family_match:
                family_history = family_match.group(1).strip()

        # 组装标准格式报告
        report_parts = []

        if chief_complaint:
            report_parts.append(f"1. 主诉 (Chief Complaint)\n{chief_complaint}")

        if present_illness:
            report_parts.append(f"2. 现病史 (Present Illness History)\n{present_illness}")

        if past_history:
            report_parts.append(f"3. 既往史 (Past Medical History)\n{past_history}")

        if family_history:
            report_parts.append(f"4. 家族史 (Family History)\n{family_history}")

        result = "\n\n".join(report_parts)

        if not result:
            raise ValueError(f"报告无法提取标准格式内容: {model_name}-{patient}")

        return result

    def extract_conversation(self, model_name: str, patient: str) -> str:
        """
        提取原始对话内容

        从conversations字段中提取chat内容

        Args:
            model_name: 模型名称
            patient: 患者名称

        Returns:
            原始对话内容
        """
        report_data = self.load_report(model_name, patient)
        conversations = report_data.get("conversations", {})

        # 提取对话内容
        # 首先尝试从第一个对话段获取（通常所有对话段的chat内容相同）
        chat_contents = []

        # 尝试获取第一个对话段
        first_key = "1" if "1" in conversations else "对话1"
        if first_key in conversations:
            chat = conversations[first_key].get("chat", "")
            if chat:
                # 只使用第一个对话段，避免重复
                full_conversation = chat
            else:
                # 如果第一个为空，尝试其他对话段
                for i in range(1, 5):
                    conv_key = str(i) if str(i) in conversations else f"对话{i}"
                    if conv_key in conversations:
                        chat = conversations[conv_key].get("chat", "")
                        if chat and chat not in chat_contents:  # 去重
                            chat_contents.append(chat)
                full_conversation = "\n\n".join(chat_contents)
        else:
            # 如果没有标准格式，尝试合并所有不重复的内容
            for i in range(1, 5):
                conv_key = str(i) if str(i) in conversations else f"对话{i}"
                if conv_key in conversations:
                    chat = conversations[conv_key].get("chat", "")
                    if chat and chat not in chat_contents:  # 去重
                        chat_contents.append(chat)
            full_conversation = "\n\n".join(chat_contents)

        if not full_conversation:
            raise ValueError(f"报告缺少对话内容: {model_name}-{patient}")

        return full_conversation

    def load_report_data(self, model_name: str, patient: str) -> Tuple[str, str]:
        """
        加载报告数据，返回对话和报告内容

        Args:
            model_name: 模型名称
            patient: 患者名称

        Returns:
            (原始对话, 生成的报告) 元组
        """
        conversation = self.extract_conversation(model_name, patient)
        report = self.extract_result(model_name, patient)

        return conversation, report

    def check_report_exists(self, model_name: str, patient: str) -> bool:
        """
        检查报告文件是否存在

        Args:
            model_name: 模型名称
            patient: 患者名称

        Returns:
            是否存在
        """
        report_path = self.get_report_path(model_name, patient)
        return report_path.exists()


# 创建全局实例
report_loader = ReportLoader()
