"""
报告加载器
从 output/raw/ 目录加载已生成的模型报告
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ReportLoader:
    """加载并管理已生成的模型报告"""

    def __init__(self, reports_dir: str = "output/raw"):
        """
        初始化报告加载器

        Args:
            reports_dir: 报告目录路径
        """
        self.reports_dir = Path(reports_dir)
        self.reports_cache = {}  # 缓存加载的报告

        if not self.reports_dir.exists():
            raise ValueError(f"报告目录不存在: {reports_dir}")

        logger.info(f"报告加载器初始化完成，目录: {reports_dir}")

    def load_report(self, model: str, patient: str) -> Optional[Dict]:
        """
        加载指定模型和患者的报告

        Args:
            model: 模型名称
            patient: 患者编号

        Returns:
            报告数据字典，如果文件不存在返回None
        """
        # 缓存键
        cache_key = f"{model}_{patient}"
        if cache_key in self.reports_cache:
            return self.reports_cache[cache_key]

        # 构建文件名（模型名中的斜杠替换为下划线）
        safe_model = model.replace('/', '_')
        filename = f"{safe_model}-{patient}.json"
        filepath = self.reports_dir / filename

        if not filepath.exists():
            logger.warning(f"报告文件不存在: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                report_data = json.load(f)

            # 缓存
            self.reports_cache[cache_key] = report_data
            logger.info(f"成功加载报告: {filename}")

            return report_data

        except Exception as e:
            logger.error(f"加载报告失败 {filepath}: {e}")
            return None

    def get_full_report_text(self, model: str, patient: str) -> Optional[str]:
        """
        获取完整报告文本（合并所有对话的Output）

        Args:
            model: 模型名称
            patient: 患者编号

        Returns:
            完整报告文本，如果报告不存在返回None
        """
        report_data = self.load_report(model, patient)
        if not report_data:
            return None

        conversations = report_data.get('conversations', {})
        if not conversations:
            logger.warning(f"报告中没有对话数据: {model}-{patient}")
            return None

        # 按对话编号排序并合并Output
        sorted_convs = sorted(conversations.items(), key=lambda x: int(x[0]))

        report_parts = []
        for conv_id, conv_data in sorted_convs:
            output = conv_data.get('Output', '')
            if output:
                # 尝试获取对话标题（从prompt中提取）
                prompt = conv_data.get('prompt', '')
                title = self._extract_title_from_prompt(prompt, conv_id)

                if title:
                    report_parts.append(f"{title}：{output}")
                else:
                    report_parts.append(output)

        full_report = '\n\n'.join(report_parts)
        return full_report

    def _extract_title_from_prompt(self, prompt: str, conv_id: str) -> str:
        """
        从prompt中提取对话标题

        Args:
            prompt: prompt内容
            conv_id: 对话ID

        Returns:
            标题字符串
        """
        import re

        # 优先从"任务"描述中提取更准确的标题
        # 匹配模式: "你的任务是...生成病历XXX" 或 "你的任务是...生成XXX"
        # 注意: 处理"既往史"和"即往史"两种拼写
        task_patterns = [
            r'你的任务是.*?生成病历(主诉|现病史|既往史|即往史|家族史|体格检查)',
            r'你的任务是.*?生成.*?(主诉|现病史|既往史|即往史|家族史|体格检查)',
            r'你的任务是总结.*?(医疗总结|预问诊)',
        ]

        for pattern in task_patterns:
            match = re.search(pattern, prompt)
            if match:
                extracted = match.group(1)
                # 医疗总结/预问诊统一标记为"医疗总结"
                if extracted in ['医疗总结', '预问诊']:
                    return '医疗总结'
                # 纠正"即往史"拼写错误
                if extracted == '即往史':
                    return '既往史'
                return extracted

        # 如果任务描述中没有找到，尝试更精确的关键词匹配
        # 只匹配明确出现的标题（避免在示例文本中误匹配）
        title_keywords = [
            ('生成病历主诉', '主诉'),
            ('生成病历现病史', '现病史'),
            ('生成病历既往史', '既往史'),
            ('生成病历家族史', '家族史'),
            ('生成病历体格检查', '体格检查'),
            ('医疗总结', '医疗总结'),
        ]

        for keyword, title in title_keywords:
            if keyword in prompt:
                return title

        # 如果无法识别，使用对话ID
        return f"对话{conv_id}"

    def get_report_metadata(self, model: str, patient: str) -> Optional[Dict]:
        """
        获取报告的元数据

        Args:
            model: 模型名称
            patient: 患者编号

        Returns:
            包含元数据的字典
        """
        report_data = self.load_report(model, patient)
        if not report_data:
            return None

        conversations = report_data.get('conversations', {})

        return {
            'model': model,
            'patient': patient,
            'conversation_count': len(conversations),
            'conversation_ids': sorted(conversations.keys(), key=lambda x: int(x)),
            'source_file': f"{model.replace('/', '_')}-{patient}.json"
        }

    def get_available_reports(self) -> Dict[str, List[str]]:
        """
        获取所有可用报告的模型和患者列表

        Returns:
            字典 {患者编号: [模型列表]}
        """
        reports = {}

        for filepath in self.reports_dir.glob("*.json"):
            # 解析文件名: {model}-{patient}.json
            filename = filepath.stem
            parts = filename.rsplit('-', 1)

            if len(parts) != 2:
                continue

            model = parts[0].replace('_', '/')  # 恢复斜杠
            patient = parts[1]

            if patient not in reports:
                reports[patient] = []

            reports[patient].append(model)

        # 排序
        for patient in reports:
            reports[patient].sort()

        logger.info(f"发现 {len(reports)} 个患者的报告")
        return reports

    def get_conversation_details(self, model: str, patient: str) -> Optional[Dict]:
        """
        获取报告中所有对话的详细信息

        Args:
            model: 模型名称
            patient: 患者编号

        Returns:
            对话详情字典
        """
        report_data = self.load_report(model, patient)
        if not report_data:
            return None

        conversations = report_data.get('conversations', {})
        sorted_convs = sorted(conversations.items(), key=lambda x: int(x[0]))

        details = {}
        for conv_id, conv_data in sorted_convs:
            prompt = conv_data.get('prompt', '')
            title = self._extract_title_from_prompt(prompt, conv_id)

            details[conv_id] = {
                'title': title,
                'output': conv_data.get('Output', ''),
                'input': conv_data.get('Input', ''),
                'prompt': prompt,
                'chat': conv_data.get('chat', '')
            }

        return details


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    loader = ReportLoader()

    # 获取可用报告
    available = loader.get_available_reports()
    print(f"\n可用报告: {len(available)} 个患者")
    for patient, models in list(available.items())[:3]:
        print(f"  {patient}: {len(models)} 个模型")

    # 测试加载报告
    if available:
        patient = list(available.keys())[0]
        model = available[patient][0]

        print(f"\n测试加载: {model} - {patient}")

        # 获取完整报告
        full_report = loader.get_full_report_text(model, patient)
        if full_report:
            print(f"\n完整报告 (前200字):\n{full_report[:200]}...")

        # 获取元数据
        metadata = loader.get_report_metadata(model, patient)
        print(f"\n元数据: {metadata}")
