"""
评分聚合器模块
用于聚合5个维度的评分结果
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .config import config


class ScoreAggregator:
    """评分聚合器"""

    def __init__(self):
        """初始化聚合器"""
        self.output_dir = config.output_dir

    def aggregate(
        self,
        dimension_results: List[Dict[str, Any]],
        evaluated_model: str,
        evaluator_model: str,
        patient: str
    ) -> Dict[str, Any]:
        """
        聚合5个维度的评分结果

        Args:
            dimension_results: 5个维度的评测结果列表
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
            patient: 患者名称

        Returns:
            聚合后的评测结果
        """
        # 计算总分
        total_score = sum(result.get("score", 0) for result in dimension_results)
        max_total_score = config.get_total_score()

        # 构建维度字典
        dimensions = {}
        for result in dimension_results:
            dimension_name = result.get("dimension", "")
            dimensions[dimension_name] = {
                "score": result.get("score", 0),
                "max_score": result.get("max_score", 0),
                "issues": result.get("issues", "")
            }

        # 收集所有critical_feedback
        feedbacks = [
            result.get("critical_feedback", "")
            for result in dimension_results
            if result.get("critical_feedback")
        ]

        # 构建聚合结果
        aggregated_result = {
            "evaluated_model": evaluated_model,
            "evaluator_model": evaluator_model,
            "patient": patient,
            "total_score": total_score,
            "max_total_score": max_total_score,
            "dimensions": dimensions,
            "critical_feedbacks": feedbacks,
            "timestamp": datetime.now().isoformat()
        }

        return aggregated_result

    def load_dimension_result(
        self,
        evaluated_model: str,
        evaluator_model: str,
        patient: str,
        dimension_name: str
    ) -> Dict[str, Any]:
        """
        加载单个维度的评测结果

        Args:
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
            patient: 患者名称
            dimension_name: 维度名称

        Returns:
            维度评测结果
        """
        # 构建文件路径
        filename = f"{evaluated_model}_by_{evaluator_model}_{patient}_{dimension_name}.json"
        file_path = self.output_dir / patient / filename

        if not file_path.exists():
            raise FileNotFoundError(f"维度评测结果文件不存在: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def aggregate_from_files(
        self,
        evaluated_model: str,
        evaluator_model: str,
        patient: str
    ) -> Dict[str, Any]:
        """
        从文件中加载5个维度的结果并聚合

        Args:
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
            patient: 患者名称

        Returns:
            聚合后的评测结果
        """
        # 加载所有维度的结果
        dimension_results = []
        for dimension in config.dimensions:
            dimension_name = dimension["name"]
            try:
                result = self.load_dimension_result(
                    evaluated_model=evaluated_model,
                    evaluator_model=evaluator_model,
                    patient=patient,
                    dimension_name=dimension_name
                )
                dimension_results.append(result)
            except FileNotFoundError as e:
                print(f"警告: {e}")
                # 如果某个维度的结果不存在，使用默认值
                dimension_results.append({
                    "dimension": dimension_name,
                    "score": 0,
                    "max_score": dimension["weight"],
                    "issues": "评测文件不存在",
                    "critical_feedback": ""
                })

        # 聚合结果
        return self.aggregate(
            dimension_results=dimension_results,
            evaluated_model=evaluated_model,
            evaluator_model=evaluator_model,
            patient=patient
        )

    def save_aggregated_result(
        self,
        aggregated_result: Dict[str, Any],
        evaluated_model: str,
        evaluator_model: str,
        patient: str
    ) -> Path:
        """
        保存聚合结果

        Args:
            aggregated_result: 聚合后的评测结果
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
            patient: 患者名称

        Returns:
            保存的文件路径
        """
        # 创建输出目录
        patient_dir = self.output_dir / patient
        patient_dir.mkdir(parents=True, exist_ok=True)

        # 构建文件路径
        filename = f"{evaluated_model}_by_{evaluator_model}_{patient}_aggregated.json"
        file_path = patient_dir / filename

        # 保存结果
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(aggregated_result, f, ensure_ascii=False, indent=2)

        return file_path


# 创建全局实例
score_aggregator = ScoreAggregator()
