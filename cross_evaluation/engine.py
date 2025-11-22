"""
交叉评估引擎
负责执行模型间的交叉评估
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import sys
from tqdm import tqdm

# 添加父目录到路径以便导入chat_client
sys.path.insert(0, str(Path(__file__).parent.parent))

from chat_client import ChatClient, Message
from .config import EVALUATION_CONFIG, API_CONFIG, OUTPUT_CONFIG
from .prompt_template import EvaluationPromptTemplate
from .conversation_indexer import ConversationIndexer
from .model_client_factory import ModelClientFactory


class CrossEvaluationEngine:
    """交叉评估引擎"""

    def __init__(
        self,
        comparison_data_path: str = "output/comparison_data.json",
        output_base_dir: str = None,
        markdown_reports_dir: str = "output/markdown"
    ):
        """
        初始化评估引擎

        Args:
            comparison_data_path: 模型对比数据路径
            output_base_dir: 输出基础目录
            markdown_reports_dir: Markdown报告文件目录
        """
        self.comparison_data_path = Path(comparison_data_path)
        self.output_base_dir = Path(output_base_dir or OUTPUT_CONFIG["base_dir"])
        self.markdown_reports_dir = Path(markdown_reports_dir)

        # 加载对比数据
        self.comparison_data = self._load_comparison_data()

        # 初始化对话索引器
        self.conversation_indexer = ConversationIndexer()
        self.conversation_indexer.load_all_conversations()

        # 初始化prompt模板生成器
        self.prompt_template = EvaluationPromptTemplate()

        # 初始化模型客户端工厂
        self.client_factory = ModelClientFactory()

        # 创建输出目录
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def _load_comparison_data(self) -> Dict:
        """加载对比数据"""
        with open(self.comparison_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_markdown_report(self, model: str, patient: str) -> Optional[str]:
        """
        加载markdown报告文件

        Args:
            model: 模型名称（如 'gpt-5.1'）
            patient: 患者名称（如 '患者1'）

        Returns:
            报告内容，如果文件不存在或读取失败返回None
        """
        try:
            # 标准化模型名称（用于文件名）
            model_filename = model.replace('/', '_')

            # 构建文件路径：{model}-{patient}.md
            report_file = self.markdown_reports_dir / f"{model_filename}-{patient}.md"

            if not report_file.exists():
                return None

            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                print(f"  ⚠️  报告文件为空: {report_file}")
                return None

            return content

        except Exception as e:
            print(f"  ✗ 读取报告失败: {model}-{patient}.md - {e}")
            return None

    def run_report_cross_evaluation(
        self,
        患者列表: List[str] = None,
        模型列表: List[str] = None
    ) -> Dict:
        """
        运行完整报告的交叉评估（不按对话分段）

        Args:
            患者列表: 要评估的患者列表，None表示全部
            模型列表: 要使用的模型列表，None表示全部

        Returns:
            评估结果汇总
        """
        print("\n" + "="*60)
        print("完整报告交叉评估引擎启动")
        print("="*60 + "\n")

        # 显示模型注册信息
        print("已注册的模型及其API提供商:")
        registered_models = self.client_factory.list_available_models()
        for model, provider in registered_models.items():
            print(f"  - {model}: {provider}")
        print()

        # 确定评估范围
        patients = 患者列表 or self.comparison_data.get("patients", [])
        models = 模型列表 or self.comparison_data.get("models", [])

        print(f"评估范围:")
        print(f"  - 患者数量: {len(patients)}")
        print(f"  - 模型数量: {len(models)}")
        print(f"  - 评估矩阵大小: {len(models)} × {len(models)}")
        total_evals = len(patients) * len(models) * (len(models) - 1) if not EVALUATION_CONFIG["include_self_evaluation"] else len(patients) * len(models) * len(models)
        print(f"  - 预计评估次数: {total_evals}\n")

        results = {
            "start_time": datetime.now().isoformat(),
            "patients": patients,
            "models": models,
            "evaluations": {}
        }

        total_evaluations = 0
        successful_evaluations = 0
        failed_evaluations = 0

        # 计算总任务数
        total_tasks = 0
        for patient in patients:
            for generated_by_model in models:
                for evaluator_model in models:
                    if not EVALUATION_CONFIG["include_self_evaluation"] and generated_by_model == evaluator_model:
                        continue
                    total_tasks += 1

        # 创建总进度条
        with tqdm(total=total_tasks, desc="🔄 总体进度",
                  bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
                  ncols=100) as pbar:

            # 遍历每个患者
            for patient_idx, patient in enumerate(patients, 1):
                try:
                    pbar.set_description(f"📋 患者 {patient_idx}/{len(patients)}: {patient}")

                    # 遍历每个被评估的模型(报告生成者)
                    for gen_idx, generated_by_model in enumerate(models, 1):
                        try:
                            # 读取该模型生成的完整报告
                            report_content = self._load_markdown_report(generated_by_model, patient)

                            if not report_content:
                                tqdm.write(f"  ⚠️  未找到报告: {generated_by_model}-{patient}.md")
                                # 跳过这个模型的所有评估
                                skip_count = len(models)
                                if not EVALUATION_CONFIG["include_self_evaluation"]:
                                    skip_count -= 1
                                pbar.update(skip_count)
                                continue

                            # 让每个模型进行评估
                            for eval_idx, evaluator_model in enumerate(models, 1):
                                try:
                                    total_evaluations += 1

                                    # 检查是否跳过自我评估
                                    if not EVALUATION_CONFIG["include_self_evaluation"] and generated_by_model == evaluator_model:
                                        pbar.update(1)
                                        continue

                                    # 更新进度条描述
                                    pbar.set_postfix_str(
                                        f"生成者:{generated_by_model[:15]}... | 评估者:{evaluator_model[:15]}..."
                                    )

                                    # 检查缓存（检查evaluations文件，因为这是最终结果）
                                    eval_file = self._get_report_evaluation_file_path(
                                        patient, generated_by_model, evaluator_model
                                    )

                                    if EVALUATION_CONFIG["enable_caching"] and eval_file.exists():
                                        try:
                                            # 读取已有的评分
                                            with open(eval_file, 'r', encoding='utf-8') as f:
                                                cached_result = json.load(f)
                                                avg_score = cached_result.get("average_score", 0)
                                            tqdm.write(f"    ✓ 已缓存: {evaluator_model} (评分: {avg_score:.2f})")
                                            successful_evaluations += 1
                                            pbar.update(1)
                                            continue
                                        except Exception as cache_error:
                                            tqdm.write(f"    ⚠️  缓存读取失败: {cache_error}，重新评估")

                                    # 执行评估（两步走：先保存原始响应，再解析并保存评分）
                                    try:
                                        # 第一步：获取并保存原始响应
                                        raw_response = self._get_raw_report_evaluation(
                                            patient=patient,
                                            generated_by=generated_by_model,
                                            evaluated_by=evaluator_model,
                                            report_content=report_content
                                        )

                                        # 立即保存原始响应
                                        raw_file = self._save_report_raw_response(
                                            patient, generated_by_model,
                                            evaluator_model, raw_response
                                        )

                                        # 第二步：尝试解析并保存评分结果
                                        try:
                                            evaluation_result = self._parse_and_save_report_evaluation(
                                                patient, generated_by_model,
                                                evaluator_model, raw_response
                                            )

                                            avg_score = evaluation_result.get("average_score", 0)
                                            tqdm.write(f"    ✓ 完成: {evaluator_model} (评分: {avg_score:.2f})")

                                        except Exception as parse_error:
                                            tqdm.write(f"    ⚠️  解析失败: {evaluator_model} - {parse_error}")
                                            tqdm.write(f"       原始响应已保存: {raw_file}")

                                        successful_evaluations += 1

                                        # 避免API限流
                                        time.sleep(API_CONFIG.get("retry_delay", 1))

                                    except Exception as eval_error:
                                        tqdm.write(f"    ✗ 评估失败: {evaluator_model} - {eval_error}")
                                        failed_evaluations += 1

                                    finally:
                                        # 无论成功失败都更新进度
                                        pbar.update(1)

                                except Exception as eval_loop_error:
                                    tqdm.write(f"    ✗ 评估循环异常: {evaluator_model} - {eval_loop_error}")
                                    failed_evaluations += 1
                                    pbar.update(1)

                        except Exception as gen_loop_error:
                            tqdm.write(f"  ✗ 生成者循环异常: {generated_by_model} - {gen_loop_error}")
                            # 跳过剩余的评估者
                            remaining = len(models) - gen_idx + 1
                            if not EVALUATION_CONFIG["include_self_evaluation"]:
                                remaining -= 1
                            pbar.update(max(0, remaining))

                except Exception as patient_loop_error:
                    tqdm.write(f"✗ 患者循环异常: {patient} - {patient_loop_error}")
                    # 跳过该患者的剩余任务
                    remaining = (len(patients) - patient_idx) * len(models) * len(models)
                    if not EVALUATION_CONFIG["include_self_evaluation"]:
                        remaining -= (len(patients) - patient_idx) * len(models)
                    pbar.update(max(0, remaining))

        results["end_time"] = datetime.now().isoformat()
        results["statistics"] = {
            "total_evaluations": total_evaluations,
            "successful": successful_evaluations,
            "failed": failed_evaluations,
            "success_rate": f"{successful_evaluations/total_evaluations*100:.1f}%" if total_evaluations > 0 else "0%"
        }

        print("\n" + "="*60)
        print("交叉评估完成")
        print("="*60)
        print(f"总评估次数: {total_evaluations}")
        print(f"成功: {successful_evaluations}")
        print(f"失败: {failed_evaluations}")
        print(f"成功率: {results['statistics']['success_rate']}")
        print("="*60 + "\n")

        return results

    def run_cross_evaluation(
        self,
        患者列表: List[str] = None,
        对话类型列表: List[str] = None,
        模型列表: List[str] = None,
        include_conversation_context: bool = True
    ) -> Dict:
        """
        运行交叉评估

        Args:
            患者列表: 要评估的患者列表，None表示全部
            对话类型列表: 要评估的对话类型ID列表，None表示全部
            模型列表: 要使用的模型列表，None表示全部
            include_conversation_context: 是否在评估时包含原始对话上下文

        Returns:
            评估结果汇总
        """
        print("\n" + "="*60)
        print("交叉评估引擎启动")
        print("="*60 + "\n")

        # 显示模型注册信息
        print("已注册的模型及其API提供商:")
        registered_models = self.client_factory.list_available_models()
        for model, provider in registered_models.items():
            print(f"  - {model}: {provider}")
        print()

        # 确定评估范围
        patients = 患者列表 or self.comparison_data.get("patients", [])
        models = 模型列表 or self.comparison_data.get("models", [])

        print(f"评估范围:")
        print(f"  - 患者数量: {len(patients)}")
        print(f"  - 模型数量: {len(models)}")
        print(f"  - 评估矩阵大小: {len(models)} × {len(models)}")
        print(f"  - 预计评估次数: {len(patients) * len(models) * len(models)} (患者 × 生成者 × 评估者)\n")

        results = {
            "start_time": datetime.now().isoformat(),
            "patients": patients,
            "models": models,
            "evaluations": {}
        }

        total_evaluations = 0
        successful_evaluations = 0
        failed_evaluations = 0

        # 遍历每个患者
        for patient in patients:
            print(f"\n处理患者: {patient}")
            print("-" * 60)

            patient_data = self.comparison_data["data"].get(patient, {})

            # 确定要评估的对话类型
            conv_ids = 对话类型列表 or list(patient_data.keys())

            for conv_id in conv_ids:
                conv_data = patient_data.get(conv_id, {})
                if not conv_data:
                    continue

                # 获取对话标题
                conv_title = self._get_conversation_title(conv_data)
                print(f"\n  对话类型: {conv_title} (ID: {conv_id})")

                # 遍历每个被评估的模型(生成者)
                for generated_by_model in models:
                    if generated_by_model not in conv_data:
                        continue

                    output_to_evaluate = conv_data[generated_by_model].get("output", "")
                    if not output_to_evaluate:
                        continue

                    print(f"    评估 {generated_by_model} 的输出...")

                    # 让每个模型进行评估
                    for evaluator_model in models:
                        total_evaluations += 1

                        # 检查是否跳过自我评估
                        if not EVALUATION_CONFIG["include_self_evaluation"] and generated_by_model == evaluator_model:
                            print(f"      跳过自我评估: {evaluator_model}")
                            continue

                        # 检查缓存（检查raw文件）
                        raw_file = self._get_raw_file_path(
                            patient, conv_id, generated_by_model, evaluator_model
                        )

                        if EVALUATION_CONFIG["enable_caching"] and raw_file.exists():
                            print(f"      ✓ 已缓存: {evaluator_model}")
                            successful_evaluations += 1
                            continue

                        # 执行评估（两步走：先保存原始响应，后续再解析）
                        try:
                            # 第一步：获取并保存原始响应
                            raw_response = self._get_raw_evaluation(
                                patient=patient,
                                conversation_id=conv_id,
                                conversation_title=conv_title,
                                generated_by=generated_by_model,
                                evaluated_by=evaluator_model,
                                output_to_evaluate=output_to_evaluate,
                                include_context=include_conversation_context
                            )

                            # 立即保存原始响应
                            self._save_raw_response(
                                patient, conv_id, generated_by_model,
                                evaluator_model, raw_response
                            )

                            print(f"      ✓ 完成: {evaluator_model} (原始响应已保存)")
                            successful_evaluations += 1

                            # 避免API限流
                            time.sleep(API_CONFIG.get("retry_delay", 1))

                        except Exception as e:
                            print(f"      ✗ 失败: {evaluator_model} - {e}")
                            failed_evaluations += 1
                            continue

        results["end_time"] = datetime.now().isoformat()
        results["statistics"] = {
            "total_evaluations": total_evaluations,
            "successful": successful_evaluations,
            "failed": failed_evaluations,
            "success_rate": f"{successful_evaluations/total_evaluations*100:.1f}%" if total_evaluations > 0 else "0%"
        }

        print("\n" + "="*60)
        print("交叉评估完成")
        print("="*60)
        print(f"总评估次数: {total_evaluations}")
        print(f"成功: {successful_evaluations}")
        print(f"失败: {failed_evaluations}")
        print(f"成功率: {results['statistics']['success_rate']}")
        print("="*60 + "\n")

        return results

    def _evaluate_output(
        self,
        patient: str,
        conversation_id: str,
        conversation_title: str,
        generated_by: str,
        evaluated_by: str,
        output_to_evaluate: str,
        include_context: bool = True
    ) -> Dict:
        """
        执行单次评估

        Args:
            patient: 患者名称
            conversation_id: 对话ID
            conversation_title: 对话标题
            generated_by: 生成输出的模型
            evaluated_by: 进行评估的模型
            output_to_evaluate: 被评估的输出内容
            include_context: 是否包含对话上下文

        Returns:
            评估结果字典
        """
        # 获取对话上下文
        conversation_context = None
        if include_context:
            conversation_context = self.conversation_indexer.format_conversation_for_evaluation(
                generated_by, patient, conversation_id
            )

        # 生成评估prompt
        prompt = self.prompt_template.generate_evaluation_prompt(
            patient=patient,
            conversation_title=conversation_title,
            conversation_id=conversation_id,
            original_output=output_to_evaluate,
            conversation_context=conversation_context
        )

        # 使用工厂创建正确配置的客户端
        try:
            client = self.client_factory.create_client(evaluated_by)
        except ValueError as e:
            print(f"      ⚠️  无法创建客户端: {e}")
            raise

        response = client.chat(
            prompt,
            temperature=API_CONFIG.get("temperature", 0.0),
            max_tokens=8192,
            stream=False  # 使用非流式模式以获取完整响应
        )

        # 解析评估结果
        evaluation_data = self._parse_evaluation_response(response)

        # 计算平均分
        scores = [
            dim_data.get("score", 0)
            for dim_data in evaluation_data.get("dimensions", {}).values()
        ]
        average_score = sum(scores) / len(scores) if scores else 0

        # 构建完整评估结果
        result = {
            "patient": patient,
            "conversation_id": conversation_id,
            "conversation_title": conversation_title,
            "generated_by": generated_by,
            "evaluated_by": evaluated_by,
            "original_output": output_to_evaluate,
            "evaluation": evaluation_data,
            "average_score": round(average_score, 2),
            "metadata": {
                "evaluation_timestamp": datetime.now().isoformat(),
                "evaluator_model_version": evaluated_by,
                "included_conversation_context": include_context
            }
        }

        return result

    def _parse_evaluation_response(self, response: str) -> Dict:
        """
        解析评估响应

        Args:
            response: LLM返回的评估结果

        Returns:
            解析后的评估数据
        """
        try:
            # 尝试直接解析JSON
            # 移除可能的markdown代码块标记
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                # 移除代码块标记
                lines = cleaned_response.split('\n')
                cleaned_response = '\n'.join(lines[1:-1])

            evaluation_data = json.loads(cleaned_response)
            return evaluation_data

        except json.JSONDecodeError as e:
            print(f"      ⚠️  JSON解析失败: {e}")
            print(f"      原始响应: {response[:200]}...")

            # 返回默认结构
            return {
                "dimensions": {
                    "accuracy": {"score": 0, "reasoning": "解析失败"},
                    "completeness": {"score": 0, "reasoning": "解析失败"},
                    "format": {"score": 0, "reasoning": "解析失败"},
                    "language": {"score": 0, "reasoning": "解析失败"},
                    "logic": {"score": 0, "reasoning": "解析失败"}
                },
                "overall_comment": "评估响应解析失败",
                "strengths": [],
                "weaknesses": [],
                "suggestions": [],
                "parse_error": str(e),
                "raw_response": response
            }

    def _get_conversation_title(self, conv_data: Dict) -> str:
        """从对话数据中获取标题"""
        for model_data in conv_data.values():
            if isinstance(model_data, dict) and "title" in model_data:
                return model_data["title"]
        return "未知类型"

    def _get_evaluation_file_path(
        self,
        patient: str,
        conv_id: str,
        generated_by: str,
        evaluated_by: str
    ) -> Path:
        """获取评估结果文件路径"""
        # 创建患者目录
        patient_dir = self.output_base_dir / patient / f"conv_{conv_id}"
        patient_dir.mkdir(parents=True, exist_ok=True)

        # 评估详情目录
        eval_dir = patient_dir / OUTPUT_CONFIG["evaluations_dir"]
        eval_dir.mkdir(exist_ok=True)

        # 文件名: {生成者}_by_{评估者}.json
        filename = f"{generated_by.replace('/', '_')}_by_{evaluated_by.replace('/', '_')}.json"

        return eval_dir / filename

    def _get_raw_file_path(
        self,
        patient: str,
        conv_id: str,
        generated_by: str,
        evaluated_by: str
    ) -> Path:
        """获取原始响应文件路径"""
        # 创建raw子目录
        eval_dir = self.output_base_dir / patient / f"conv_{conv_id}" / "raw"
        eval_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{generated_by.replace('/', '_')}_by_{evaluated_by.replace('/', '_')}.json"
        return eval_dir / filename

    def _save_raw_response(
        self,
        patient: str,
        conv_id: str,
        generated_by: str,
        evaluated_by: str,
        raw_response: Dict
    ):
        """保存原始API响应"""
        file_path = self._get_raw_file_path(
            patient, conv_id, generated_by, evaluated_by
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(raw_response, f, ensure_ascii=False, indent=2)

    def _get_raw_evaluation(
        self,
        patient: str,
        conversation_id: str,
        conversation_title: str,
        generated_by: str,
        evaluated_by: str,
        output_to_evaluate: str,
        include_context: bool = True
    ) -> Dict:
        """
        获取原始评估响应（不解析）

        Returns:
            包含原始响应的字典
        """
        # 获取对话上下文
        conversation_context = None
        if include_context:
            conversation_context = self.conversation_indexer.format_conversation_for_evaluation(
                generated_by, patient, conversation_id
            )

        # 生成评估prompt
        prompt = self.prompt_template.generate_evaluation_prompt(
            patient=patient,
            conversation_title=conversation_title,
            conversation_id=conversation_id,
            original_output=output_to_evaluate,
            conversation_context=conversation_context
        )

        # 使用工厂创建正确配置的客户端
        try:
            client = self.client_factory.create_client(evaluated_by)
        except ValueError as e:
            print(f"      ⚠️  无法创建客户端: {e}")
            raise

        # 调用API获取响应
        response = client.chat(
            prompt,
            temperature=API_CONFIG.get("temperature", 0.0),
            max_tokens=8192,
            stream=False
        )

        # 构建原始响应数据（不解析评分）
        raw_data = {
            "patient": patient,
            "conversation_id": conversation_id,
            "conversation_title": conversation_title,
            "generated_by": generated_by,
            "evaluated_by": evaluated_by,
            "original_output": output_to_evaluate,
            "raw_response": response,  # 原始LLM响应
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "evaluator_model": evaluated_by,
                "included_context": include_context,
                "prompt_length": len(prompt)
            }
        }

        return raw_data

    def _get_report_raw_file_path(
        self,
        patient: str,
        generated_by: str,
        evaluated_by: str
    ) -> Path:
        """获取报告评估的原始响应文件路径（不分对话）"""
        # 创建raw子目录：患者/raw/
        eval_dir = self.output_base_dir / patient / "raw"
        eval_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{generated_by.replace('/', '_')}_by_{evaluated_by.replace('/', '_')}.json"
        return eval_dir / filename

    def _save_report_raw_response(
        self,
        patient: str,
        generated_by: str,
        evaluated_by: str,
        raw_response: Dict
    ) -> Path:
        """
        保存报告评估的原始API响应

        Returns:
            保存的文件路径
        """
        try:
            file_path = self._get_report_raw_file_path(
                patient, generated_by, evaluated_by
            )

            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(raw_response, f, ensure_ascii=False, indent=2)

            return file_path

        except Exception as e:
            print(f"  ✗ 保存原始响应失败: {e}")
            # 尝试保存到临时位置
            import tempfile
            temp_file = Path(tempfile.gettempdir()) / f"raw_response_{patient}_{generated_by}_{evaluated_by}.json"
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(raw_response, f, ensure_ascii=False, indent=2)
                print(f"  ⚠️  已保存到临时文件: {temp_file}")
                return temp_file
            except Exception as temp_error:
                print(f"  ✗ 保存到临时文件也失败: {temp_error}")
                raise

    def _get_raw_report_evaluation(
        self,
        patient: str,
        generated_by: str,
        evaluated_by: str,
        report_content: str
    ) -> Dict:
        """
        获取完整报告评估的原始响应（不解析）

        Args:
            patient: 患者名称
            generated_by: 生成报告的模型
            evaluated_by: 进行评估的模型
            report_content: 完整报告内容

        Returns:
            包含原始响应的字典
        """
        verbose = EVALUATION_CONFIG.get("verbose_logging", False)

        if verbose:
            tqdm.write(f"\n    📝 准备评估:")
            tqdm.write(f"       生成者: {generated_by}")
            tqdm.write(f"       评估者: {evaluated_by}")
            tqdm.write(f"       报告长度: {len(report_content)} 字符")

        # 生成评估prompt（针对完整报告）
        try:
            prompt = self.prompt_template.generate_report_evaluation_prompt(
                patient=patient,
                report_content=report_content
            )
        except Exception as e:
            tqdm.write(f"    ✗ 生成Prompt失败: {e}")
            raise

        if verbose:
            tqdm.write(f"       Prompt长度: {len(prompt)} 字符")
            tqdm.write(f"\n    📥 【入参 - Prompt预览】")
            tqdm.write(f"    {'-'*70}")
            # 显示prompt的前500和后200字符
            if len(prompt) > 700:
                tqdm.write(f"    {prompt[:500]}")
                tqdm.write(f"    ... (省略 {len(prompt)-700} 字符) ...")
                tqdm.write(f"    {prompt[-200:]}")
            else:
                tqdm.write(f"    {prompt}")
            tqdm.write(f"    {'-'*70}")

        # 使用工厂创建正确配置的客户端
        try:
            client = self.client_factory.create_client(evaluated_by)
        except ValueError as e:
            tqdm.write(f"    ⚠️  无法创建客户端: {e}")
            raise
        except Exception as e:
            tqdm.write(f"    ✗ 创建客户端失败: {e}")
            raise

        # 调用API获取响应
        if verbose:
            tqdm.write(f"\n       🔄 正在调用API...")

        start_time = time.time()

        try:
            response = client.chat(
                prompt,
                temperature=API_CONFIG.get("temperature", 0.0),
                max_tokens=8192,
                stream=False
            )
        except Exception as e:
            tqdm.write(f"    ✗ API调用失败: {e}")
            raise

        response_time = time.time() - start_time

        if verbose:
            tqdm.write(f"       ✓ API响应完成 (耗时: {response_time:.2f}秒)")
            tqdm.write(f"       响应长度: {len(response)} 字符")

            tqdm.write(f"\n    📤 【出参 - Response预览】")
            tqdm.write(f"    {'-'*70}")
            # 显示response的前800字符
            if len(response) > 800:
                tqdm.write(f"    {response[:800]}")
                tqdm.write(f"    ... (省略 {len(response)-800} 字符) ...")
            else:
                tqdm.write(f"    {response}")
            tqdm.write(f"    {'-'*70}\n")

        # 构建原始响应数据（包含输入和输出）
        raw_data = {
            "patient": patient,
            "generated_by": generated_by,
            "evaluated_by": evaluated_by,
            "input": {
                "report_content": report_content,  # 完整报告内容
                "prompt": prompt,  # 完整评估prompt
                "report_content_length": len(report_content),
                "prompt_length": len(prompt)
            },
            "output": {
                "raw_response": response,  # 原始LLM响应
                "response_length": len(response),
                "response_time_seconds": response_time
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "evaluator_model": evaluated_by,
                "evaluation_type": "complete_report",
                "api_config": {
                    "temperature": API_CONFIG.get("temperature", 0.0),
                    "max_tokens": 8192
                }
            }
        }

        return raw_data

    def _get_report_evaluation_file_path(
        self,
        patient: str,
        generated_by: str,
        evaluated_by: str
    ) -> Path:
        """获取报告评估结果文件路径（解析后的评分）"""
        # 创建evaluations子目录：患者/evaluations/
        eval_dir = self.output_base_dir / patient / "evaluations"
        eval_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{generated_by.replace('/', '_')}_by_{evaluated_by.replace('/', '_')}.json"
        return eval_dir / filename

    def _parse_and_save_report_evaluation(
        self,
        patient: str,
        generated_by: str,
        evaluated_by: str,
        raw_response: Dict
    ) -> Dict:
        """
        解析原始响应并保存评分结果

        Args:
            patient: 患者名称
            generated_by: 生成报告的模型
            evaluated_by: 评估模型
            raw_response: 原始响应数据

        Returns:
            解析后的评估结果
        """
        try:
            # 从raw_response中提取LLM响应文本
            llm_response = raw_response.get("output", {}).get("raw_response", "")

            if not llm_response:
                raise ValueError("原始响应为空")

            # 解析评估响应
            evaluation_data = self._parse_evaluation_response(llm_response)

            # 计算平均分
            scores = [
                dim_data.get("score", 0)
                for dim_data in evaluation_data.get("dimensions", {}).values()
                if isinstance(dim_data, dict) and "score" in dim_data
            ]
            average_score = sum(scores) / len(scores) if scores else 0

            # 构建完整评估结果
            result = {
                "patient": patient,
                "generated_by": generated_by,
                "evaluated_by": evaluated_by,
                "report_content": raw_response.get("input", {}).get("report_content", ""),
                "evaluation": evaluation_data,
                "average_score": round(average_score, 2),
                "metadata": {
                    "evaluation_timestamp": raw_response.get("metadata", {}).get("timestamp"),
                    "evaluator_model": evaluated_by,
                    "evaluation_type": "complete_report",
                    "response_time_seconds": raw_response.get("output", {}).get("response_time_seconds", 0)
                }
            }

            # 保存评估结果
            try:
                file_path = self._get_report_evaluation_file_path(
                    patient, generated_by, evaluated_by
                )

                # 确保目录存在
                file_path.parent.mkdir(parents=True, exist_ok=True)

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

            except Exception as save_error:
                print(f"  ⚠️  保存评估结果失败: {save_error}")
                # 即使保存失败，也返回结果
                pass

            return result

        except Exception as e:
            print(f"  ✗ 解析评估响应失败: {e}")
            # 返回一个默认的结果
            return {
                "patient": patient,
                "generated_by": generated_by,
                "evaluated_by": evaluated_by,
                "evaluation": {},
                "average_score": 0,
                "error": str(e),
                "metadata": {
                    "evaluation_timestamp": datetime.now().isoformat(),
                    "evaluator_model": evaluated_by,
                    "evaluation_type": "complete_report",
                    "parse_failed": True
                }
            }

    def _save_evaluation_result(
        self,
        patient: str,
        conv_id: str,
        generated_by: str,
        evaluated_by: str,
        evaluation_result: Dict
    ):
        """保存评估结果"""
        file_path = self._get_evaluation_file_path(
            patient, conv_id, generated_by, evaluated_by
        )

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(evaluation_result, f, ensure_ascii=False, indent=2)

    def parse_saved_raw_responses(
        self,
        患者列表: List[str] = None,
        对话类型列表: List[str] = None
    ) -> Dict:
        """
        第二步：解析已保存的原始响应

        Args:
            患者列表: 要解析的患者列表
            对话类型列表: 要解析的对话类型列表

        Returns:
            解析结果统计
        """
        print("\n" + "="*60)
        print("开始解析原始响应")
        print("="*60 + "\n")

        patients = 患者列表 or self.comparison_data.get("patients", [])

        total_parsed = 0
        successful_parsed = 0
        failed_parsed = 0

        for patient in patients:
            print(f"\n处理患者: {patient}")
            patient_dir = self.output_base_dir / patient

            if not patient_dir.exists():
                continue

            # 遍历所有对话目录
            for conv_dir in patient_dir.iterdir():
                if not conv_dir.is_dir() or not conv_dir.name.startswith("conv_"):
                    continue

                raw_dir = conv_dir / "raw"
                if not raw_dir.exists():
                    continue

                conv_id = conv_dir.name.replace("conv_", "").split("_")[0]

                # 如果指定了对话类型，检查是否匹配
                if 对话类型列表 and conv_id not in 对话类型列表:
                    continue

                print(f"  对话 {conv_id}:")

                # 解析所有原始响应文件
                for raw_file in raw_dir.glob("*.json"):
                    total_parsed += 1

                    try:
                        # 读取原始响应
                        with open(raw_file, 'r', encoding='utf-8') as f:
                            raw_data = json.load(f)

                        # 解析评估结果
                        evaluation_data = self._parse_evaluation_response(
                            raw_data["raw_response"]
                        )

                        # 计算平均分
                        scores = [
                            dim_data.get("score", 0)
                            for dim_data in evaluation_data.get("dimensions", {}).values()
                        ]
                        average_score = sum(scores) / len(scores) if scores else 0

                        # 构建完整评估结果
                        parsed_result = {
                            "patient": raw_data["patient"],
                            "conversation_id": raw_data["conversation_id"],
                            "conversation_title": raw_data["conversation_title"],
                            "generated_by": raw_data["generated_by"],
                            "evaluated_by": raw_data["evaluated_by"],
                            "original_output": raw_data["original_output"],
                            "evaluation": evaluation_data,
                            "average_score": round(average_score, 2),
                            "metadata": raw_data["metadata"]
                        }

                        # 保存解析后的结果
                        self._save_evaluation_result(
                            raw_data["patient"],
                            raw_data["conversation_id"],
                            raw_data["generated_by"],
                            raw_data["evaluated_by"],
                            parsed_result
                        )

                        print(f"    ✓ 解析: {raw_file.stem} (平均分: {average_score:.1f})")
                        successful_parsed += 1

                    except Exception as e:
                        print(f"    ✗ 解析失败: {raw_file.stem} - {e}")
                        failed_parsed += 1

        print("\n" + "="*60)
        print("解析完成")
        print("="*60)
        print(f"总数: {total_parsed}")
        print(f"成功: {successful_parsed}")
        print(f"失败: {failed_parsed}")
        print("="*60 + "\n")

        return {
            "total": total_parsed,
            "successful": successful_parsed,
            "failed": failed_parsed
        }
