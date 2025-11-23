"""
交叉评测主引擎
负责协调整个评测流程
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .config import config
from .report_loader import report_loader
from .dimension_evaluator import dimension_evaluator
from .aggregator import score_aggregator


class CrossEvaluationEngine:
    """交叉评测引擎"""

    def __init__(self):
        """初始化引擎"""
        self.config = config
        self.output_dir = config.output_dir
        self.progress_file = self.output_dir / ".progress.json"

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        models: Optional[List[str]] = None,
        patients: Optional[List[str]] = None,
        resume: bool = False
    ):
        """
        运行交叉评测

        Args:
            models: 要评测的模型列表（None表示使用配置中的所有模型）
            patients: 要评测的患者列表（None表示使用配置中的所有患者）
            resume: 是否从上次中断处继续
        """
        # 使用配置中的默认值
        if models is None:
            models = self.config.models
        if patients is None:
            patients = self.config.patients

        print(f"开始交叉评测")
        print(f"模型数量: {len(models)}")
        print(f"患者数量: {len(patients)}")
        print(f"评测维度: {len(self.config.dimensions)}")
        total_evaluations = len(models) * len(models) * len(patients) * (len(self.config.dimensions) + 1)
        print(f"预计生成文件: {total_evaluations}个")
        print("-" * 50)

        # 加载进度
        progress = self._load_progress() if resume else {}

        # 统计
        completed = 0
        failed = 0
        skipped = 0

        # 三层循环：患者 -> 被评测模型 -> 评测模型
        for patient in patients:
            print(f"\n处理患者: {patient}")

            # 创建患者目录
            patient_dir = self.output_dir / patient
            patient_dir.mkdir(parents=True, exist_ok=True)

            for evaluated_model in models:
                # 检查报告是否存在
                if not report_loader.check_report_exists(evaluated_model, patient):
                    print(f"  跳过: {evaluated_model} (报告不存在)")
                    skipped += 1
                    continue

                # 加载报告数据
                try:
                    conversation, report = report_loader.load_report_data(evaluated_model, patient)
                except Exception as e:
                    print(f"  加载报告失败: {evaluated_model} - {str(e)}")
                    failed += 1
                    continue

                for evaluator_model in models:
                    # 生成任务key
                    task_key = f"{patient}_{evaluated_model}_{evaluator_model}"

                    # 检查是否已完成（进度文件或输出文件存在）
                    if resume and progress.get(task_key, {}).get("completed", False):
                        print(f"  跳过已完成: {evaluated_model} by {evaluator_model}")
                        skipped += 1
                        continue

                    # 即使没有进度文件，也检查聚合文件是否存在
                    if resume:
                        aggregated_file = patient_dir / f"{evaluated_model}_by_{evaluator_model}_{patient}_aggregated.json"
                        if aggregated_file.exists():
                            print(f"  跳过已完成: {evaluated_model} by {evaluator_model} (文件已存在)")
                            skipped += 1
                            # 更新进度
                            progress[task_key] = {
                                "completed": True,
                                "timestamp": datetime.now().isoformat(),
                                "note": "从现有文件恢复"
                            }
                            self._save_progress(progress)
                            continue

                    print(f"  评测: {evaluated_model} by {evaluator_model}")

                    # 评测5个维度
                    try:
                        self._evaluate_dimensions(
                            conversation=conversation,
                            report=report,
                            evaluated_model=evaluated_model,
                            evaluator_model=evaluator_model,
                            patient=patient
                        )

                        # 聚合结果
                        self._aggregate_scores(
                            evaluated_model=evaluated_model,
                            evaluator_model=evaluator_model,
                            patient=patient
                        )

                        # 更新进度
                        progress[task_key] = {
                            "completed": True,
                            "timestamp": datetime.now().isoformat()
                        }
                        self._save_progress(progress)

                        completed += 1

                    except Exception as e:
                        print(f"    评测失败: {str(e)}")
                        failed += 1
                        progress[task_key] = {
                            "completed": False,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat()
                        }
                        self._save_progress(progress)

        # 最终统计
        print("\n" + "=" * 50)
        print(f"交叉评测完成!")
        print(f"完成: {completed}")
        print(f"跳过: {skipped}")
        print(f"失败: {failed}")
        print(f"结果保存至: {self.output_dir}")

    def _evaluate_dimensions(
        self,
        conversation: str,
        report: str,
        evaluated_model: str,
        evaluator_model: str,
        patient: str
    ):
        """
        评测所有维度

        Args:
            conversation: 原始对话
            report: 生成的报告
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
            patient: 患者名称
        """
        for dimension in self.config.dimensions:
            dimension_name = dimension["name"]

            # 检查文件是否已存在
            filename = f"{evaluated_model}_by_{evaluator_model}_{patient}_{dimension_name}.json"
            file_path = self.output_dir / patient / filename

            if file_path.exists():
                print(f"    跳过已存在的维度: {dimension_name}")
                continue

            print(f"    评测维度: {dimension_name}")

            # 评测
            result = dimension_evaluator.evaluate(
                dimension_name=dimension_name,
                conversation=conversation,
                report=report,
                evaluator_model=evaluator_model,
                evaluated_model=evaluated_model,
                patient=patient
            )

            # 保存结果
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

    def _aggregate_scores(
        self,
        evaluated_model: str,
        evaluator_model: str,
        patient: str
    ):
        """
        聚合评分结果

        Args:
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
            patient: 患者名称
        """
        print(f"    聚合评分")

        # 从文件加载并聚合
        aggregated_result = score_aggregator.aggregate_from_files(
            evaluated_model=evaluated_model,
            evaluator_model=evaluator_model,
            patient=patient
        )

        # 保存聚合结果
        score_aggregator.save_aggregated_result(
            aggregated_result=aggregated_result,
            evaluated_model=evaluated_model,
            evaluator_model=evaluator_model,
            patient=patient
        )

    def _load_progress(self) -> Dict[str, Any]:
        """加载进度文件"""
        if not self.progress_file.exists():
            return {}

        with open(self.progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_progress(self, progress: Dict[str, Any]):
        """保存进度文件"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

    def run_parallel(
        self,
        models: Optional[List[str]] = None,
        patients: Optional[List[str]] = None,
        resume: bool = False,
        max_workers: Optional[int] = None
    ):
        """
        并行运行交叉评测

        Args:
            models: 要评测的模型列表
            patients: 要评测的患者列表
            resume: 是否从上次中断处继续
            max_workers: 最大并发数
        """
        if max_workers is None:
            max_workers = self.config.concurrency_config.get("max_workers", 3)

        # 使用配置中的默认值
        if models is None:
            models = self.config.models
        if patients is None:
            patients = self.config.patients

        print(f"开始并行交叉评测 (并发数: {max_workers})")
        print(f"模型数量: {len(models)}")
        print(f"患者数量: {len(patients)}")
        print("-" * 50)

        # 生成所有任务
        tasks = []
        for patient in patients:
            for evaluated_model in models:
                if not report_loader.check_report_exists(evaluated_model, patient):
                    continue
                for evaluator_model in models:
                    tasks.append((patient, evaluated_model, evaluator_model))

        print(f"总任务数: {len(tasks)}")

        # 加载进度
        progress = self._load_progress() if resume else {}

        # 并行执行
        completed = 0
        failed = 0
        skipped = 0

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}

            for patient, evaluated_model, evaluator_model in tasks:
                task_key = f"{patient}_{evaluated_model}_{evaluator_model}"

                # 检查是否已完成
                if resume and progress.get(task_key, {}).get("completed", False):
                    skipped += 1
                    continue

                # 提交任务
                future = executor.submit(
                    self._evaluate_single_task,
                    patient, evaluated_model, evaluator_model
                )
                futures[future] = (patient, evaluated_model, evaluator_model, task_key)

            # 收集结果
            for future in as_completed(futures):
                patient, evaluated_model, evaluator_model, task_key = futures[future]

                try:
                    future.result()
                    completed += 1
                    progress[task_key] = {
                        "completed": True,
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"✓ [{completed + failed}/{len(tasks) - skipped}] {evaluated_model} by {evaluator_model} ({patient})")

                except Exception as e:
                    failed += 1
                    progress[task_key] = {
                        "completed": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    print(f"✗ 失败: {evaluated_model} by {evaluator_model} - {str(e)}")

                # 定期保存进度
                if (completed + failed) % 10 == 0:
                    self._save_progress(progress)

        # 最终保存进度
        self._save_progress(progress)

        # 统计
        print("\n" + "=" * 50)
        print(f"并行交叉评测完成!")
        print(f"完成: {completed}")
        print(f"跳过: {skipped}")
        print(f"失败: {failed}")

    def _evaluate_single_task(
        self,
        patient: str,
        evaluated_model: str,
        evaluator_model: str
    ):
        """
        评测单个任务

        Args:
            patient: 患者名称
            evaluated_model: 被评测模型
            evaluator_model: 评测模型
        """
        # 加载报告
        conversation, report = report_loader.load_report_data(evaluated_model, patient)

        # 评测维度
        self._evaluate_dimensions(
            conversation=conversation,
            report=report,
            evaluated_model=evaluated_model,
            evaluator_model=evaluator_model,
            patient=patient
        )

        # 聚合
        self._aggregate_scores(
            evaluated_model=evaluated_model,
            evaluator_model=evaluator_model,
            patient=patient
        )


# 创建全局实例
engine = CrossEvaluationEngine()
