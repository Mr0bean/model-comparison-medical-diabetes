"""
单维度评测器模块
用于对单个维度进行评测
"""
import json
import re
from datetime import datetime
from typing import Dict, Any
from .config import config
from .model_client import model_client
from .prompt_loader import prompt_loader
from .module_parser import module_parser


class DimensionEvaluator:
    """单维度评测器"""

    def __init__(self):
        """初始化评测器"""
        pass

    def evaluate(
        self,
        dimension_name: str,
        conversation: str,
        report: str,
        evaluator_model: str,
        evaluated_model: str,
        patient: str
    ) -> Dict[str, Any]:
        """
        对单个维度进行评测

        Args:
            dimension_name: 维度名称（如 "准确性"）
            conversation: 原始对话内容
            report: 生成的医疗报告
            evaluator_model: 评测模型名称
            evaluated_model: 被评测模型名称
            patient: 患者名称

        Returns:
            评测结果字典
        """
        # 1. 解析报告模块
        modules = module_parser.parse_report(report)
        module_summary = module_parser.get_module_summary(report)

        # 2. 格式化prompt
        prompt = prompt_loader.format_prompt(
            dimension_name=dimension_name,
            conversation=conversation,
            report=report
        )

        # 3. 调用评测模型
        response = model_client.call_model(
            model_name=evaluator_model,
            prompt=prompt
        )

        # 4. 解析响应
        parsed_result = self._parse_response(
            response=response,
            dimension_name=dimension_name,
            evaluator_model=evaluator_model,
            evaluated_model=evaluated_model,
            patient=patient
        )

        # 5. 添加详细的输入输出信息
        parsed_result["source_llm"] = evaluated_model  # 被评测模型
        parsed_result["target_llm"] = evaluator_model  # 评测模型
        parsed_result["prompt_input"] = prompt  # 输入的完整prompt
        parsed_result["output"] = response  # 模型的原始输出

        # 6. 添加模块分析信息
        parsed_result["report_modules"] = {
            "identified_modules": list(modules.keys()),
            "module_count": len(modules),
            "modules_detail": {
                name: {
                    "length": info["length"],
                    "has_content": info["has_content"],
                    "preview": info["preview"]
                }
                for name, info in module_summary.items()
            }
        }

        return parsed_result

    def _parse_response(
        self,
        response: str,
        dimension_name: str,
        evaluator_model: str,
        evaluated_model: str,
        patient: str
    ) -> Dict[str, Any]:
        """
        解析模型响应，提取JSON评分结果

        Args:
            response: 模型响应内容
            dimension_name: 维度名称
            evaluator_model: 评测模型
            evaluated_model: 被评测模型
            patient: 患者名称

        Returns:
            解析后的评测结果
        """
        # 尝试直接解析JSON
        try:
            result = json.loads(response)
            return self._format_result(result, dimension_name, evaluator_model, evaluated_model, patient)
        except json.JSONDecodeError:
            pass

        # 尝试从markdown代码块中提取JSON
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)

        if matches:
            try:
                result = json.loads(matches[0])
                return self._format_result(result, dimension_name, evaluator_model, evaluated_model, patient)
            except json.JSONDecodeError:
                pass

        # 如果都失败，返回原始响应
        print(f"警告: 无法解析JSON响应，维度={dimension_name}, 评测模型={evaluator_model}")
        return {
            "evaluated_model": evaluated_model,
            "evaluator_model": evaluator_model,
            "patient": patient,
            "dimension": dimension_name,
            "max_score": config.get_dimension_weight(dimension_name),
            "score": 0,
            "issues": "解析失败",
            "critical_feedback": "响应格式错误",
            "timestamp": datetime.now().isoformat()
        }

    def _format_result(
        self,
        parsed_json: Dict[str, Any],
        dimension_name: str,
        evaluator_model: str,
        evaluated_model: str,
        patient: str
    ) -> Dict[str, Any]:
        """
        格式化评测结果

        Args:
            parsed_json: 解析的JSON对象
            dimension_name: 维度名称
            evaluator_model: 评测模型
            evaluated_model: 被评测模型
            patient: 患者名称

        Returns:
            格式化的评测结果
        """
        # 根据不同维度提取对应的字段
        # 准确性: accuracy
        # 逻辑性: logic
        # 完整性: completeness
        # 格式规范性: formatting
        # 语言表达: language

        dimension_key_mapping = {
            "准确性": "accuracy",
            "逻辑性": "logic",
            "完整性": "completeness",
            "格式规范性": "formatting",
            "语言表达": "language"
        }

        dimension_key = dimension_key_mapping.get(dimension_name)

        if dimension_key and dimension_key in parsed_json:
            dimension_data = parsed_json[dimension_key]
            score = dimension_data.get("score", 0)
            issues = dimension_data.get("issues", "")
        else:
            # 如果找不到对应的key，尝试直接从顶层提取
            score = parsed_json.get("score", 0)
            issues = parsed_json.get("issues", "")

        # 提取critical_feedback
        critical_feedback = parsed_json.get("critical_feedback", "")

        # 构建标准化的结果
        result = {
            "evaluated_model": evaluated_model,
            "evaluator_model": evaluator_model,
            "patient": patient,
            "dimension": dimension_name,
            "max_score": config.get_dimension_weight(dimension_name),
            "score": self._parse_score(score),
            "issues": issues,
            "critical_feedback": critical_feedback,
            "timestamp": datetime.now().isoformat()
        }

        return result

    def _parse_score(self, score_value: Any) -> int:
        """
        解析分数值

        Args:
            score_value: 分数值（可能是字符串或数字）

        Returns:
            整数分数
        """
        if isinstance(score_value, (int, float)):
            return int(score_value)

        if isinstance(score_value, str):
            # 尝试提取数字
            numbers = re.findall(r'\d+', score_value)
            if numbers:
                return int(numbers[0])

        return 0


# 创建全局实例
dimension_evaluator = DimensionEvaluator()
