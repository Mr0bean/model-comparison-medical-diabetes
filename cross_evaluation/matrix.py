"""
评分矩阵生成器
读取评估结果并生成评分矩阵
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict


class MatrixGenerator:
    """评分矩阵生成器"""

    def __init__(self, evaluation_base_dir: str = "output/cross_evaluation_results"):
        """
        初始化矩阵生成器

        Args:
            evaluation_base_dir: 评估结果基础目录
        """
        self.evaluation_base_dir = Path(evaluation_base_dir)

    def generate_matrix_for_conversation(
        self,
        patient: str,
        conv_id: str,
        models: List[str]
    ) -> Dict:
        """
        为特定对话生成评分矩阵

        Args:
            patient: 患者名称
            conv_id: 对话ID
            models: 模型列表

        Returns:
            矩阵数据字典
        """
        conv_dir = self.evaluation_base_dir / patient / f"conv_{conv_id}"
        eval_dir = conv_dir / "evaluations"

        if not eval_dir.exists():
            print(f"⚠️  评估目录不存在: {eval_dir}")
            return None

        # 初始化矩阵 (被评估者 × 评估者)
        matrix_size = len(models)
        score_matrix = np.zeros((matrix_size, matrix_size))
        dimension_matrices = {
            "accuracy": np.zeros((matrix_size, matrix_size)),
            "completeness": np.zeros((matrix_size, matrix_size)),
            "format": np.zeros((matrix_size, matrix_size)),
            "language": np.zeros((matrix_size, matrix_size)),
            "logic": np.zeros((matrix_size, matrix_size))
        }

        # 模型名称到索引的映射
        model_to_idx = {model: idx for idx, model in enumerate(models)}

        # 读取所有评估结果
        evaluation_files = {}
        for eval_file in eval_dir.glob("*.json"):
            # 文件名格式: {generated_by}_by_{evaluated_by}.json
            parts = eval_file.stem.replace("_by_", "|").split("|")
            if len(parts) != 2:
                continue

            generated_by = parts[0].replace("_", "/")  # 恢复斜杠
            evaluated_by = parts[1].replace("_", "/")

            # 读取评估数据
            with open(eval_file, 'r', encoding='utf-8') as f:
                eval_data = json.load(f)

            # 填充矩阵
            if generated_by in model_to_idx and evaluated_by in model_to_idx:
                row = model_to_idx[generated_by]  # 被评估者（行）
                col = model_to_idx[evaluated_by]  # 评估者（列）

                # 平均分
                score_matrix[row, col] = eval_data.get("average_score", 0)

                # 各维度分数
                dimensions = eval_data.get("evaluation", {}).get("dimensions", {})
                for dim_name, dim_data in dimensions.items():
                    if dim_name in dimension_matrices:
                        score = dim_data.get("score", 0) if isinstance(dim_data, dict) else 0
                        dimension_matrices[dim_name][row, col] = score

                # 保存评估文件路径以便后续查询（使用字符串键而非元组）
                eval_key = f"{generated_by}_evaluated_by_{evaluated_by}"
                evaluation_files[eval_key] = str(eval_file.relative_to(self.evaluation_base_dir))

        # 计算统计信息
        statistics = self._calculate_statistics(score_matrix, models)

        matrix_data = {
            "patient": patient,
            "conversation_id": conv_id,
            "models": models,
            "score_matrix": score_matrix.tolist(),
            "dimension_matrices": {
                dim: matrix.tolist()
                for dim, matrix in dimension_matrices.items()
            },
            "statistics": statistics,
            "evaluation_files": evaluation_files
        }

        return matrix_data

    def _calculate_statistics(self, score_matrix: np.ndarray, models: List[str]) -> Dict:
        """
        计算统计信息

        Args:
            score_matrix: 评分矩阵
            models: 模型列表

        Returns:
            统计信息字典
        """
        statistics = {}

        # 每个模型的平均得分（作为被评估者）
        row_means = np.mean(score_matrix, axis=1)  # 每行的平均值
        statistics["model_average_scores"] = {
            model: round(float(score), 2)
            for model, score in zip(models, row_means)
        }

        # 每个模型的评分严格度（作为评估者）
        col_means = np.mean(score_matrix, axis=0)  # 每列的平均值
        statistics["model_evaluator_strictness"] = {
            model: round(float(score), 2)
            for model, score in zip(models, col_means)
        }

        # 模型排名（基于平均得分）
        ranked_models = sorted(
            statistics["model_average_scores"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        statistics["model_rankings"] = [
            {"rank": i+1, "model": model, "score": score}
            for i, (model, score) in enumerate(ranked_models)
        ]

        # 评分一致性（标准差）
        statistics["score_consistency"] = {
            "overall_std": round(float(np.std(score_matrix)), 2),
            "overall_mean": round(float(np.mean(score_matrix)), 2)
        }

        return statistics

    def generate_all_matrices(self, patients: List[str], models: List[str]) -> Dict:
        """
        为所有患者和对话生成矩阵

        Args:
            patients: 患者列表
            models: 模型列表

        Returns:
            所有矩阵数据
        """
        all_matrices = {}

        for patient in patients:
            patient_dir = self.evaluation_base_dir / patient
            if not patient_dir.exists():
                continue

            all_matrices[patient] = {}

            # 遍历该患者的所有对话
            for conv_dir in patient_dir.glob("conv_*"):
                conv_id = conv_dir.name.replace("conv_", "")

                matrix_data = self.generate_matrix_for_conversation(
                    patient, conv_id, models
                )

                if matrix_data:
                    all_matrices[patient][conv_id] = matrix_data

                    # 保存矩阵到文件
                    self._save_matrix(patient, conv_id, matrix_data)

        return all_matrices

    def _save_matrix(self, patient: str, conv_id: str, matrix_data: Dict):
        """保存矩阵数据到文件"""
        matrix_dir = self.evaluation_base_dir / patient / f"conv_{conv_id}"
        matrix_dir.mkdir(parents=True, exist_ok=True)

        matrix_file = matrix_dir / "matrix.json"

        with open(matrix_file, 'w', encoding='utf-8') as f:
            json.dump(matrix_data, f, ensure_ascii=False, indent=2)

        print(f"✓ 矩阵已保存: {matrix_file}")

    def generate_summary_statistics(self, all_matrices: Dict) -> Dict:
        """
        生成汇总统计信息

        Args:
            all_matrices: 所有矩阵数据

        Returns:
            汇总统计
        """
        # 收集所有模型的评分
        model_scores = defaultdict(list)

        for patient, patient_data in all_matrices.items():
            for conv_id, matrix_data in patient_data.items():
                scores = matrix_data.get("statistics", {}).get("model_average_scores", {})
                for model, score in scores.items():
                    model_scores[model].append(score)

        # 计算每个模型的总体平均分
        overall_model_scores = {
            model: {
                "mean": round(np.mean(scores), 2),
                "std": round(np.std(scores), 2),
                "min": round(min(scores), 2),
                "max": round(max(scores), 2),
                "count": len(scores)
            }
            for model, scores in model_scores.items()
        }

        # 总体排名
        overall_rankings = sorted(
            overall_model_scores.items(),
            key=lambda x: x[1]["mean"],
            reverse=True
        )

        summary = {
            "overall_model_scores": overall_model_scores,
            "overall_rankings": [
                {"rank": i+1, "model": model, **stats}
                for i, (model, stats) in enumerate(overall_rankings)
            ]
        }

        # 保存汇总统计
        summary_dir = self.evaluation_base_dir / "summary"
        summary_dir.mkdir(parents=True, exist_ok=True)

        summary_file = summary_dir / "statistics.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 汇总统计已保存: {summary_file}")

        return summary

    def export_matrix_to_csv(
        self,
        patient: str,
        conv_id: str,
        models: List[str],
        output_file: Optional[Path] = None
    ):
        """
        导出矩阵为CSV格式

        Args:
            patient: 患者名称
            conv_id: 对话ID
            models: 模型列表
            output_file: 输出文件路径
        """
        matrix_data = self.generate_matrix_for_conversation(patient, conv_id, models)
        if not matrix_data:
            return

        import csv

        if output_file is None:
            output_file = self.evaluation_base_dir / patient / f"conv_{conv_id}" / "matrix.csv"

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # 写入表头
            header = ["被评估者 / 评估者"] + models
            writer.writerow(header)

            # 写入数据
            score_matrix = matrix_data["score_matrix"]
            for i, model in enumerate(models):
                row = [model] + [f"{score:.2f}" for score in score_matrix[i]]
                writer.writerow(row)

        print(f"✓ CSV已导出: {output_file}")
