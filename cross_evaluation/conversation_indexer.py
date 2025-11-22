"""
对话内容索引器
负责读取原始对话数据并建立索引，用于评估时提供上下文
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class ConversationIndexer:
    """对话内容索引器"""

    def __init__(self, raw_data_dir: str = "output/raw"):
        """
        初始化索引器

        Args:
            raw_data_dir: 原始数据目录
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.index = {}  # (model, patient, conv_id) -> conversation_data
        self.loaded = False

    def load_all_conversations(self) -> Dict:
        """
        加载所有对话数据并建立索引

        Returns:
            索引字典
        """
        print("开始加载对话数据...")

        # 遍历所有raw JSON文件
        for json_file in self.raw_data_dir.glob("*.json"):
            try:
                self._load_single_file(json_file)
            except Exception as e:
                print(f"⚠️  加载文件失败: {json_file.name} - {e}")
                continue

        self.loaded = True
        print(f"✓ 对话数据加载完成，共索引 {len(self.index)} 条记录\n")

        return self.index

    def _load_single_file(self, json_file: Path):
        """
        加载单个JSON文件

        Args:
            json_file: JSON文件路径
        """
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        model = data.get("model", "")
        patient = data.get("people", "")
        conversations = data.get("conversations", {})

        # 为每个对话建立索引
        for conv_id, conv_data in conversations.items():
            key = (model, patient, conv_id)

            # 提取对话历史
            chat_text = conv_data.get("chat", "")
            conversation_history = self._parse_conversation_history(chat_text)

            # 提取输出内容
            output_text = conv_data.get("Output", "")

            # 存储索引
            self.index[key] = {
                "model": model,
                "patient": patient,
                "conversation_id": conv_id,
                "prompt": conv_data.get("prompt", ""),
                "chat_raw": chat_text,
                "conversation_history": conversation_history,
                "output": output_text,
                "conversation_title": self._infer_conversation_title(conv_id, conv_data)
            }

    def _parse_conversation_history(self, chat_text: str) -> List[Dict]:
        """
        解析对话历史文本

        Args:
            chat_text: 原始对话文本

        Returns:
            对话历史列表
        """
        history = []

        # 提取对话记录部分
        match = re.search(r'预问诊对话记录：\s*-+\s*(.*)', chat_text, re.DOTALL)
        if not match:
            return history

        conversation_text = match.group(1)

        # 解析每一轮对话
        # 格式: "数字. 角色: 内容"
        pattern = r'(\d+)\.\s*(患者|医助|医生):\s*([^\n]+)'
        matches = re.findall(pattern, conversation_text, re.MULTILINE)

        for round_num, role, content in matches:
            history.append({
                "round": int(round_num),
                "role": "patient" if role == "患者" else "doctor",
                "role_cn": role,
                "content": content.strip()
            })

        return history

    def _infer_conversation_title(self, conv_id: str, conv_data: Dict) -> str:
        """
        推断对话类型标题

        Args:
            conv_id: 对话ID
            conv_data: 对话数据

        Returns:
            对话类型标题
        """
        # 从prompt中推断
        prompt = conv_data.get("prompt", "")

        if "主诉" in prompt:
            return "主诉"
        elif "现病史" in prompt:
            return "现病史"
        elif "既往史" in prompt or "即往史" in prompt:
            return "既往史"
        elif "家族史" in prompt:
            return "家族史"
        elif "预病历" in prompt or "总结" in prompt:
            return "预病历总结"
        else:
            return f"对话{conv_id}"

    def get_conversation(
        self,
        model: str,
        patient: str,
        conv_id: str
    ) -> Dict[str, Any]:
        """
        获取特定对话数据

        Args:
            model: 模型名称
            patient: 患者名称
            conv_id: 对话ID

        Returns:
            对话数据字典，如果不存在返回None
        """
        if not self.loaded:
            self.load_all_conversations()

        key = (model, patient, conv_id)
        return self.index.get(key)

    def format_conversation_for_evaluation(
        self,
        model: str,
        patient: str,
        conv_id: str
    ) -> str:
        """
        格式化对话内容，用于评估prompt

        Args:
            model: 模型名称
            patient: 患者名称
            conv_id: 对话ID

        Returns:
            格式化的对话文本
        """
        conv_data = self.get_conversation(model, patient, conv_id)
        if not conv_data:
            return ""

        history = conv_data.get("conversation_history", [])
        if not history:
            return ""

        formatted_lines = []
        for item in history:
            round_num = item.get("round")
            role_cn = item.get("role_cn", "未知")
            content = item.get("content", "")

            icon = "👨‍⚕️" if item.get("role") == "doctor" else "👤"
            formatted_lines.append(f"Round {round_num} - {icon} {role_cn}:")
            formatted_lines.append(f"  {content}")
            formatted_lines.append("")

        return "\n".join(formatted_lines)

    def get_statistics(self) -> Dict:
        """
        获取索引统计信息

        Returns:
            统计信息字典
        """
        if not self.loaded:
            self.load_all_conversations()

        models = set()
        patients = set()
        conv_types = defaultdict(int)

        for (model, patient, conv_id), data in self.index.items():
            models.add(model)
            patients.add(patient)
            title = data.get("conversation_title", "未知")
            conv_types[title] += 1

        return {
            "total_conversations": len(self.index),
            "models_count": len(models),
            "patients_count": len(patients),
            "models": sorted(list(models)),
            "patients": sorted(list(patients)),
            "conversation_types": dict(conv_types)
        }
