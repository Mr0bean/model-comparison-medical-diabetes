"""
完整报告交叉评估引擎
评估从 output/raw/ 加载的已生成报告
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

from .report_loader import ReportLoader
from .model_client_factory import ModelClientFactory
from .config import EVALUATION_CONFIG, EVALUATION_DIMENSIONS, API_CONFIG

logger = logging.getLogger(__name__)


class ReportEvaluationEngine:
    """完整报告交叉评估引擎"""

    def __init__(
        self,
        reports_dir: str = "output/raw",
        output_dir: str = "output/report_cross_evaluation",
        client_factory: Optional[ModelClientFactory] = None
    ):
        """
        初始化评估引擎

        Args:
            reports_dir: 报告目录
            output_dir: 输出目录
            client_factory: 模型客户端工厂
        """
        self.report_loader = ReportLoader(reports_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.client_factory = client_factory or ModelClientFactory()

        logger.info(f"报告评估引擎初始化完成")
        logger.info(f"  报告目录: {reports_dir}")
        logger.info(f"  输出目录: {output_dir}")

    @staticmethod
    def _sanitize_model_name(model_name: str) -> str:
        """
        清理模型名称用于文件系统路径
        将 / 替换为 _ 以避免创建意外的目录结构

        例如: moonshotai/kimi-k2-0905 -> moonshotai_kimi-k2-0905
        """
        return model_name.replace('/', '_')

    def evaluate_patient_reports(
        self,
        patient: str,
        models: List[str],
        include_self_evaluation: bool = False
    ) -> Dict:
        """
        评估一个患者的所有模型报告

        Args:
            patient: 患者编号
            models: 要评估的模型列表
            include_self_evaluation: 是否包含自我评估

        Returns:
            完整的评估结果字典
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"开始评估患者: {patient}")
        logger.info(f"{'='*60}")
        logger.info(f"模型数量: {len(models)}")
        logger.info(f"评估矩阵: {len(models)} × {len(models)} = {len(models)**2} 次评估")

        # 1. 加载所有模型的报告
        reports = {}
        for model in models:
            full_report = self.report_loader.get_full_report_text(model, patient)
            if not full_report:
                logger.warning(f"  跳过模型 {model}: 报告不存在")
                continue

            metadata = self.report_loader.get_report_metadata(model, patient)
            conv_details = self.report_loader.get_conversation_details(model, patient)

            reports[model] = {
                'full_report': full_report,
                'metadata': metadata,
                'conversation_details': conv_details
            }

        available_models = list(reports.keys())
        logger.info(f"\n成功加载 {len(available_models)} 个模型的报告")

        # 2. 执行交叉评估
        evaluations = {}
        total_count = 0
        success_count = 0
        failed_count = 0

        for generated_by in available_models:
            logger.info(f"\n评估 {generated_by} 的报告...")

            for evaluated_by in available_models:
                # 检查是否跳过自我评估
                if not include_self_evaluation and generated_by == evaluated_by:
                    logger.info(f"  跳过自我评估: {evaluated_by}")
                    continue

                total_count += 1
                # 清理模型名称中的 / 以避免文件路径问题
                safe_generated_by = self._sanitize_model_name(generated_by)
                safe_evaluated_by = self._sanitize_model_name(evaluated_by)
                eval_key = f"{safe_generated_by}_evaluated_by_{safe_evaluated_by}"

                # 检查缓存
                cached_eval = self._load_cached_evaluation(patient, eval_key)
                if cached_eval:
                    logger.info(f"  ✓ 使用缓存: {evaluated_by}")
                    evaluations[eval_key] = cached_eval
                    success_count += 1
                    continue

                # 执行评估（带重试机制，最多3次）
                max_retries = 3
                retry_count = 0
                evaluation_success = False

                while retry_count < max_retries and not evaluation_success:
                    try:
                        if retry_count > 0:
                            logger.info(f"  ⟳ 重试 {retry_count}/{max_retries}: {evaluated_by}")

                        evaluation_result = self._evaluate_single_report(
                            patient=patient,
                            generated_by=generated_by,
                            evaluated_by=evaluated_by,
                            report_content=reports[generated_by]['full_report'],
                            report_metadata=reports[generated_by]['metadata']
                        )

                        evaluations[eval_key] = evaluation_result
                        success_count += 1

                        # 保存评估结果
                        self._save_evaluation(patient, eval_key, evaluation_result)
                        logger.info(f"  ✓ 完成: {evaluated_by} (平均分: {evaluation_result['average_score']})")
                        evaluation_success = True

                    except Exception as e:
                        retry_count += 1
                        if retry_count < max_retries:
                            logger.warning(f"  ⚠ 失败 (尝试 {retry_count}/{max_retries}): {evaluated_by} - {str(e)}")
                            import time
                            time.sleep(2)  # 等待2秒后重试
                        else:
                            logger.error(f"  ✗ 最终失败 (已重试{max_retries}次): {evaluated_by} - {str(e)}")
                            failed_count += 1

        # 3. 生成评分矩阵
        matrix_data = self._generate_matrix(available_models, evaluations)

        # 4. 构建完整结果
        result = {
            'patient': patient,
            'evaluation_time': datetime.now().isoformat(),
            'models': available_models,
            'reports': {
                model: {
                    'full_report': reports[model]['full_report'],
                    'metadata': reports[model]['metadata'],
                    'conversation_details': reports[model]['conversation_details']
                }
                for model in available_models
            },
            'evaluations': evaluations,
            'matrix': matrix_data,
            'statistics': {
                'total_evaluations': total_count,
                'successful': success_count,
                'failed': failed_count,
                'success_rate': f"{success_count/total_count*100:.1f}%" if total_count > 0 else "0%"
            }
        }

        # 5. 保存完整结果
        self._save_patient_result(patient, result)

        logger.info(f"\n{'='*60}")
        logger.info(f"患者 {patient} 评估完成")
        logger.info(f"成功: {success_count}/{total_count}")
        logger.info(f"{'='*60}\n")

        return result

    def _evaluate_single_report(
        self,
        patient: str,
        generated_by: str,
        evaluated_by: str,
        report_content: str,
        report_metadata: Dict
    ) -> Dict:
        """
        评估单个报告

        Args:
            patient: 患者编号
            generated_by: 生成报告的模型
            evaluated_by: 进行评估的模型
            report_content: 报告内容
            report_metadata: 报告元数据

        Returns:
            评估结果字典
        """
        # 构建评估prompt
        prompt = self._generate_evaluation_prompt(
            patient=patient,
            report_content=report_content,
            generated_by_model=generated_by
        )

        # 调用评估模型
        client = self.client_factory.create_client(evaluated_by)

        # 清空对话历史，避免缓存污染
        client.clear_history(keep_system=False)

        # 增加max_tokens以支持详细的100分制评分
        response = client.chat(
            prompt,
            temperature=API_CONFIG.get("temperature", 0.0),
            max_tokens=20000,  # 设置为20000支持超长详细评分
            stream=False
        )

        # 检查空响应
        if not response or not response.strip():
            logger.warning(f"模型 {evaluated_by} 返回空响应")
            raise ValueError(f"模型 {evaluated_by} 返回空响应，可能是API限制或prompt太长")

        # 解析评估响应
        evaluation_data = self._parse_evaluation_response(response)

        # 获取总分（100分制）
        total_score = evaluation_data.get("total_score", 0)

        # 构建完整评估结果
        result = {
            'patient': patient,
            'generated_by': generated_by,
            'evaluated_by': evaluated_by,
            'report_content': report_content,
            'report_metadata': report_metadata,
            'evaluation': evaluation_data,
            'total_score': total_score,  # 100分制总分
            'average_score': total_score,  # 保持兼容性，用于矩阵计算
            'metadata': {
                'evaluation_timestamp': datetime.now().isoformat(),
                'evaluator_model': evaluated_by
            }
        }

        return result

    def _generate_evaluation_prompt(
        self,
        patient: str,
        report_content: str,
        generated_by_model: str
    ) -> str:
        """生成评估prompt - 使用专业的100分制评分标准"""
        prompt = f"""你是一位专业的医疗AI模型输出质量评测专家，具有丰富的临床经验和AI评测经验。你的任务是对医疗AI模型生成的病历信息提取结果进行客观、严格的评分。

## 评分标准（总分100分）

### 1. 信息准确性（30分）
**评分方法**：从30分开始，发现错误即扣分

**扣分规则**：
- 数值完全错误：-5分（如血糖数值错误）
- 药名错误：-5分
- 无中生有（编造信息）：-5分
- 时间点严重错误（>3年）：-4分
- 药物剂量/频次错误：-3分
- 时间点小错（1-2年）：-2分
- 数值不精确（范围vs精确值）：-1分

**检查项**：
- 患者基本信息（性别、年龄、身高、体重）
- 病程时间
- 所有药物名称、剂量、频次
- 所有检查数值及单位
- 时间节点准确性
- 是否有无中生有的信息

### 2. 信息完整性（25分）
**评分方法**：覆盖率 = (提取的信息点数 / 应有的信息点数) × 25

**必需信息点**：
⭐⭐⭐ 高优先级（缺1个 -4分）：
- 主诉/就诊原因
- 病程时间
- 当前用药方案（药名+剂量+频次）
- 近期检查结果
- 重要症状

⭐⭐ 中优先级（缺1个 -2分）：
- 既往治疗史
- 并发症/合并症
- 家族史
- 近期病情变化

⭐ 低优先级（缺1个 -1分）：
- 生活方式
- 依从性信息

### 3. 临床实用性（20分）
**评分方法**：检查是否突出以下关键点，每突出1项+2-3分

**临床关键点**（必须突出）：
- 血糖控制情况（当前值+控制目标） +3分
- 体重异常变化（快速下降需警示） +3分
- 当前完整用药方案（集中列出） +3分
- 并发症线索（如泡沫尿→肾病） +3分
- 强家族史（影响预后） +2分
- 有"重点关注"或风险提示区域 +3分
- 信息组织有助于快速决策 +3分

### 4. 结构清晰度（15分）
**评分方法**：整体评估信息组织的清晰度

**优秀结构特征**（每项+2-3分）：
- 有清晰的章节划分 +3分
- 使用标题层级 +2分
- 相关信息归类合理 +3分
- 时间线清晰 +3分
- 使用列表/表格组织信息 +2分
- 能快速定位关键信息 +2分

### 5. 语言专业性（10分）
**评分方法**：从10分开始，发现问题即扣分

**扣分规则**：
- 冗余表达：-0.5分/处
- 口语化：-1分/处
- 不专业表达：-1分/处
- 语病/表达不清：-1分/处

---

## 待评估的病历报告

**患者编号**：{patient}
**生成模型**：{generated_by_model}

**报告内容**：
{report_content}

---

## 输出格式

请严格按照以下JSON格式输出评分结果：

```json
{{
  "scores": {{
    "accuracy": {{
      "score": 28,
      "max": 30,
      "deductions": [
        {{"item": "扣分项描述", "points": -1, "detail": "具体细节"}}
      ],
      "evaluation": "准确性总体评价"
    }},
    "completeness": {{
      "score": 22,
      "max": 25,
      "coverage_rate": "88%",
      "found_items": 15,
      "total_items": 17,
      "missing_items": [
        {{"item": "遗漏项", "priority": "低/中/高", "points": -1}}
      ],
      "evaluation": "完整性总体评价"
    }},
    "clinical_utility": {{
      "score": 17,
      "max": 20,
      "highlighted_points": [
        {{"item": "血糖控制情况", "highlighted": true, "points": 3}},
        {{"item": "体重异常变化", "highlighted": false, "points": 0}}
      ],
      "evaluation": "临床实用性总体评价"
    }},
    "structure": {{
      "score": 13,
      "max": 15,
      "features": [
        {{"item": "章节划分", "present": true, "points": 3}},
        {{"item": "标题层级", "present": false, "points": 0}}
      ],
      "evaluation": "结构清晰度总体评价"
    }},
    "language": {{
      "score": 8,
      "max": 10,
      "issues": [
        {{"type": "冗余/口语化/不专业/语病", "count": 2, "points": -1, "examples": ["示例1", "示例2"]}}
      ],
      "evaluation": "语言专业性总体评价"
    }}
  }},
  "total_score": 88,
  "grade": "A 良好",
  "clinical_usability": "稍作修改即可使用/可直接使用/需要修改/不可用",
  "overall_evaluation": "整体评价...",
  "strengths": [
    "优点1",
    "优点2",
    "优点3"
  ],
  "weaknesses": [
    "不足1",
    "不足2"
  ],
  "recommendations": [
    "改进建议1",
    "改进建议2"
  ]
}}
```

请严格按照上述JSON格式输出，不要包含markdown代码块标记或其他内容。
"""
        return prompt

    def _parse_evaluation_response(self, response: str) -> Dict:
        """解析评估响应 - 支持100分制新格式"""
        try:
            # 移除可能的markdown代码块标记
            cleaned_response = response.strip()
            if cleaned_response.startswith("```"):
                lines = cleaned_response.split('\n')
                # 移除第一行和最后一行
                cleaned_response = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned_response

            # 尝试查找JSON部分
            if '```json' in cleaned_response:
                start = cleaned_response.find('```json') + 7
                end = cleaned_response.find('```', start)
                cleaned_response = cleaned_response[start:end].strip()

            evaluation_data = json.loads(cleaned_response)

            # 验证新格式的必需字段
            if "scores" in evaluation_data and "total_score" in evaluation_data:
                return evaluation_data
            else:
                logger.warning("评估响应缺少必需字段，返回默认结构")
                raise ValueError("Missing required fields")

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON解析失败: {e}")
            logger.debug(f"原始响应: {response[:500]}...")

            # 返回默认的100分制结构
            return {
                "scores": {
                    "accuracy": {
                        "score": 0,
                        "max": 30,
                        "deductions": [],
                        "evaluation": "解析失败"
                    },
                    "completeness": {
                        "score": 0,
                        "max": 25,
                        "coverage_rate": "0%",
                        "found_items": 0,
                        "total_items": 0,
                        "missing_items": [],
                        "evaluation": "解析失败"
                    },
                    "clinical_utility": {
                        "score": 0,
                        "max": 20,
                        "highlighted_points": [],
                        "evaluation": "解析失败"
                    },
                    "structure": {
                        "score": 0,
                        "max": 15,
                        "features": [],
                        "evaluation": "解析失败"
                    },
                    "language": {
                        "score": 0,
                        "max": 10,
                        "issues": [],
                        "evaluation": "解析失败"
                    }
                },
                "total_score": 0,
                "grade": "F 解析失败",
                "clinical_usability": "不可用",
                "overall_evaluation": "评估响应解析失败",
                "strengths": [],
                "weaknesses": ["JSON解析失败"],
                "recommendations": [],
                "parse_error": str(e),
                "raw_response": response[:500]
            }

    def _generate_matrix(self, models: List[str], evaluations: Dict) -> Dict:
        """生成评分矩阵 - 支持100分制新评分系统"""
        import numpy as np

        n = len(models)
        score_matrix = np.zeros((n, n))
        model_to_idx = {model: i for i, model in enumerate(models)}

        # 新的100分制维度矩阵
        dimension_matrices = {
            "accuracy": np.zeros((n, n)),           # 准确性 (30分)
            "completeness": np.zeros((n, n)),       # 完整性 (25分)
            "clinical_utility": np.zeros((n, n)),   # 临床实用性 (20分)
            "structure": np.zeros((n, n)),          # 结构清晰度 (15分)
            "language": np.zeros((n, n))            # 语言专业性 (10分)
        }

        # 填充矩阵
        for eval_key, eval_data in evaluations.items():
            generated_by = eval_data['generated_by']
            evaluated_by = eval_data['evaluated_by']

            if generated_by not in model_to_idx or evaluated_by not in model_to_idx:
                continue

            row = model_to_idx[generated_by]
            col = model_to_idx[evaluated_by]

            # 总分 (100分制)
            score_matrix[row, col] = eval_data.get('total_score', 0)

            # 各维度分数 (新格式: scores.accuracy.score)
            scores_data = eval_data.get('evaluation', {}).get('scores', {})
            for dim_name in dimension_matrices.keys():
                dim_data = scores_data.get(dim_name, {})
                if isinstance(dim_data, dict):
                    score = dim_data.get('score', 0)
                    dimension_matrices[dim_name][row, col] = score

        # 计算统计信息
        statistics = {
            'model_average_scores': {
                model: round(float(np.mean(score_matrix[i, :])), 2)
                for i, model in enumerate(models)
            },
            'model_rankings': [],
            'score_consistency': {
                'overall_std': round(float(np.std(score_matrix)), 2),
                'overall_mean': round(float(np.mean(score_matrix)), 2)
            }
        }

        # 模型排名
        ranked = sorted(
            statistics['model_average_scores'].items(),
            key=lambda x: x[1],
            reverse=True
        )
        statistics['model_rankings'] = [
            {'rank': i+1, 'model': model, 'score': score}
            for i, (model, score) in enumerate(ranked)
        ]

        return {
            'score_matrix': score_matrix.tolist(),
            'dimension_matrices': {
                dim: matrix.tolist()
                for dim, matrix in dimension_matrices.items()
            },
            'statistics': statistics
        }

    def _save_evaluation(self, patient: str, eval_key: str, evaluation: Dict):
        """保存单个评估结果"""
        eval_dir = self.output_dir / patient / "evaluations"
        eval_dir.mkdir(parents=True, exist_ok=True)

        eval_file = eval_dir / f"{eval_key}.json"
        with open(eval_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, ensure_ascii=False, indent=2)

    def _load_cached_evaluation(self, patient: str, eval_key: str) -> Optional[Dict]:
        """加载缓存的评估结果"""
        eval_file = self.output_dir / patient / "evaluations" / f"{eval_key}.json"

        if not eval_file.exists():
            return None

        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载缓存失败: {e}")
            return None

    def _save_patient_result(self, patient: str, result: Dict):
        """保存患者的完整评估结果"""
        result_file = self.output_dir / patient / "complete_result.json"
        result_file.parent.mkdir(parents=True, exist_ok=True)

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        logger.info(f"完整结果已保存: {result_file}")
