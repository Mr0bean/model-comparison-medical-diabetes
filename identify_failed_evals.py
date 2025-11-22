#!/usr/bin/env python3
"""识别所有需要重试的零分评估"""

import json
import os
from pathlib import Path
from collections import defaultdict

def identify_zero_score_evaluations():
    """识别所有average_score=0.0的评估"""
    base_dir = Path("output/cross_evaluation_results")

    zero_score_evals = []
    stats_by_evaluator = defaultdict(int)
    stats_by_patient = defaultdict(int)

    # 遍历所有患者
    for patient_dir in sorted(base_dir.glob("患者*")):
        if not patient_dir.is_dir():
            continue

        patient = patient_dir.name
        eval_dir = patient_dir / "evaluations"

        if not eval_dir.exists():
            continue

        # 遍历所有评估文件
        for eval_file in eval_dir.glob("*.json"):
            try:
                with open(eval_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                score = data.get('average_score', -1)

                # 识别零分评估
                if score == 0.0:
                    # 解析文件名: model_by_evaluator.json
                    filename = eval_file.stem
                    parts = filename.split('_by_')

                    if len(parts) == 2:
                        model = parts[0]
                        evaluator = parts[1]

                        zero_score_evals.append({
                            'patient': patient,
                            'model': model,
                            'evaluator': evaluator,
                            'file': str(eval_file)
                        })

                        stats_by_evaluator[evaluator] += 1
                        stats_by_patient[patient] += 1

            except Exception as e:
                print(f"Error reading {eval_file}: {e}")

    return zero_score_evals, stats_by_evaluator, stats_by_patient


def main():
    print("=" * 60)
    print("识别零分评估")
    print("=" * 60)
    print()

    zero_evals, by_evaluator, by_patient = identify_zero_score_evaluations()

    print(f"📊 总计: {len(zero_evals)} 个零分评估")
    print()

    # 按评估者统计
    print("按评估者分布:")
    for evaluator, count in sorted(by_evaluator.items(), key=lambda x: -x[1]):
        print(f"  {evaluator}: {count}")
    print()

    # 按患者统计
    print("按患者分布:")
    for patient, count in sorted(by_patient.items()):
        print(f"  {patient}: {count}")
    print()

    # 保存重试列表
    retry_list_file = "retry_zero_scores.json"
    with open(retry_list_file, 'w', encoding='utf-8') as f:
        json.dump(zero_evals, f, indent=2, ensure_ascii=False)

    print(f"✅ 重试列表已保存到: {retry_list_file}")
    print()

    # 显示前10个示例
    print("前10个示例:")
    for i, item in enumerate(zero_evals[:10], 1):
        print(f"  {i}. {item['patient']} - {item['model']} → {item['evaluator']}")

    if len(zero_evals) > 10:
        print(f"  ... 还有 {len(zero_evals) - 10} 个")

    return zero_evals


if __name__ == "__main__":
    main()
