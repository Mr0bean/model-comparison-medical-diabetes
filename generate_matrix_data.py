#!/usr/bin/env python3
"""生成交叉评估矩阵数据（100分制）"""

import json
from pathlib import Path
from collections import defaultdict

MODELS = [
    "Baichuan-M2",
    "deepseek_deepseek-v3.1",
    "doubao-seed-1-6-251015",
    "gemini-2.5-pro",
    "gpt-5.1",
    "grok-4-0709",
    "moonshotai_kimi-k2-0905",
    "qwen3-max"
]

PATIENTS = [f"患者{i}" for i in range(1, 11)]

# 100分制评分配置
DIMENSION_WEIGHTS = {
    "accuracy": 6,      # 准确性: 满分30分
    "completeness": 5,  # 完整性: 满分25分
    "format": 4,        # 格式规范: 满分20分
    "language": 3,      # 语言表达: 满分15分
    "logic": 2          # 逻辑性: 满分10分
}
# 总分 = 100分

base_dir = Path("output/cross_evaluation_results")

print("=" * 70)
print("生成交叉评估矩阵数据（100分制）")
print("=" * 70)
print()
print("评分方案:")
print("  准确性：满分30分")
print("  完整性：满分25分")
print("  格式规范：满分20分")
print("  语言表达：满分15分")
print("  逻辑性：满分10分")
print("  总分 = 100分")
print()


def calculate_weighted_score(data):
    """根据维度分数计算100分制总分"""
    if not data.get('evaluation') or not data['evaluation'].get('dimensions'):
        # 如果没有维度数据，尝试使用旧的 average_score 并转换
        old_score = data.get('average_score', 0)
        if old_score > 0:
            # 旧分数是1-5分，转换为100分制（乘以20）
            return old_score * 20
        return 0

    dimensions = data['evaluation']['dimensions']
    total_score = 0

    for dim, weight in DIMENSION_WEIGHTS.items():
        if dim in dimensions:
            dim_score = dimensions[dim].get('score', 0)
            if isinstance(dim_score, str):
                try:
                    dim_score = float(dim_score)
                except:
                    dim_score = 0
            total_score += dim_score * weight

    return total_score


# 初始化矩阵数据结构
matrix_data = {
    "models": MODELS,
    "patients": PATIENTS,
    "matrices": {},  # 每个患者一个矩阵
    "score_system": "100_point",  # 标记使用100分制
    "dimension_max_scores": {
        "accuracy": 30,
        "completeness": 25,
        "format": 20,
        "language": 15,
        "logic": 10
    }
}

# 全局矩阵 (所有患者的平均)
global_matrix = defaultdict(lambda: defaultdict(list))

# 为每个患者生成矩阵
for patient in PATIENTS:
    patient_dir = base_dir / patient / "evaluations"

    if not patient_dir.exists():
        print(f"⚠️  {patient}: 目录不存在")
        continue

    # 患者矩阵
    patient_matrix = defaultdict(lambda: defaultdict(lambda: None))

    for eval_file in patient_dir.glob("*.json"):
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 计算100分制分数
            weighted_score = calculate_weighted_score(data)

            # 解析文件名: model_by_evaluator.json
            filename = eval_file.stem
            parts = filename.split('_by_')

            if len(parts) == 2:
                generated_by = parts[0]
                evaluated_by = parts[1]

                if weighted_score > 0:
                    patient_matrix[generated_by][evaluated_by] = weighted_score
                    global_matrix[generated_by][evaluated_by].append(weighted_score)

        except Exception as e:
            print(f"读取失败: {eval_file} - {e}")

    # 转换为普通字典
    matrix_data["matrices"][patient] = {
        gen: dict(evals) for gen, evals in patient_matrix.items()
    }

    print(f"✓ {patient}: 已生成矩阵")

# 计算全局平均矩阵
global_avg_matrix = {}
for generated_by in MODELS:
    global_avg_matrix[generated_by] = {}
    for evaluated_by in MODELS:
        scores = global_matrix[generated_by][evaluated_by]
        if scores:
            global_avg_matrix[generated_by][evaluated_by] = {
                "average": sum(scores) / len(scores),
                "count": len(scores),
                "min": min(scores),
                "max": max(scores)
            }
        else:
            global_avg_matrix[generated_by][evaluated_by] = None

matrix_data["global_matrix"] = global_avg_matrix

# 计算统计数据
total_cells = len(MODELS) * len(MODELS)
filled_cells = sum(1 for gen in MODELS for ev in MODELS if global_avg_matrix[gen][ev] is not None)

# 计算全局分数范围
all_scores = []
for gen in MODELS:
    for ev in MODELS:
        if global_avg_matrix[gen][ev]:
            all_scores.extend(global_matrix[gen][ev])

matrix_data["statistics"] = {
    "total_cells": total_cells,
    "filled_cells": filled_cells,
    "coverage": f"{filled_cells/total_cells*100:.1f}%",
    "score_range": {
        "min": min(all_scores) if all_scores else 0,
        "max": max(all_scores) if all_scores else 100,
        "average": sum(all_scores) / len(all_scores) if all_scores else 0
    }
}

# 保存数据
output_file = "cross_evaluation_matrix.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(matrix_data, f, indent=2, ensure_ascii=False)

print()
print("=" * 70)
print("矩阵数据生成完成")
print("=" * 70)
print(f"模型数量: {len(MODELS)}")
print(f"患者数量: {len(PATIENTS)}")
print(f"矩阵大小: {len(MODELS)} × {len(MODELS)} = {total_cells} 个单元格")
print(f"已填充: {filled_cells} 个单元格 ({filled_cells/total_cells*100:.1f}%)")
if all_scores:
    print(f"分数范围: {min(all_scores):.2f} - {max(all_scores):.2f}")
    print(f"平均分: {sum(all_scores)/len(all_scores):.2f}")
print()
print(f"✅ 数据已保存到: {output_file}")
