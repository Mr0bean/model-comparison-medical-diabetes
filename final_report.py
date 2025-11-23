#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

results_dir = Path("output/cross_evaluation_results")

# 统计各模型作为被评测者的分数
evaluated_stats = defaultdict(lambda: {"scores": [], "by_evaluator": defaultdict(list)})

# 统计各模型作为评测者的评分情况
evaluator_stats = defaultdict(lambda: {"given_scores": [], "count": 0})

for patient_dir in sorted(results_dir.glob("患者*")):
    for agg_file in patient_dir.glob("*_aggregated.json"):
        parts = agg_file.stem.split("_by_")
        evaluated = parts[0]
        evaluator = parts[1].replace(f"_{patient_dir.name}_aggregated", "")
        
        with open(agg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            total_score = data.get("总分") or data.get("total_score", 0)
            if total_score:
                evaluated_stats[evaluated]["scores"].append(total_score)
                evaluated_stats[evaluated]["by_evaluator"][evaluator].append(total_score)
                evaluator_stats[evaluator]["given_scores"].append(total_score)
                evaluator_stats[evaluator]["count"] += 1

print("=" * 90)
print("📊 交叉评测完整报告")
print("=" * 90)

print("\n【一】各模型被评测表现（作为被测模型）")
print("-" * 90)
print(f"{'模型名称':30s} | {'完成率':8s} | {'平均分':6s} | {'最低分':6s} | {'最高分':6s} | {'标准差':6s}")
print("-" * 90)

import statistics
for model in sorted(evaluated_stats.keys()):
    scores = evaluated_stats[model]["scores"]
    if scores:
        avg = sum(scores) / len(scores)
        std = statistics.stdev(scores) if len(scores) > 1 else 0
        print(f"{model:30s} | {len(scores):3d}/80  | {avg:6.2f} | {min(scores):6d} | {max(scores):6d} | {std:6.2f}")

print("\n【二】各模型评测行为（作为评测者）")
print("-" * 90)
print(f"{'评测者模型':30s} | {'评测数':8s} | {'平均给分':8s} | {'评分范围':15s} | {'标准差':6s}")
print("-" * 90)

for evaluator in sorted(evaluator_stats.keys()):
    given = evaluator_stats[evaluator]["given_scores"]
    count = evaluator_stats[evaluator]["count"]
    if given:
        avg = sum(given) / len(given)
        std = statistics.stdev(given) if len(given) > 1 else 0
        score_range = f"{min(given)}-{max(given)}"
        print(f"{evaluator:30s} | {count:3d}/80  | {avg:8.2f} | {score_range:15s} | {std:6.2f}")

print("\n【三】模型互评矩阵（平均分）")
print("-" * 90)

all_models = sorted(evaluated_stats.keys())
# Print header
print(f"{'被评测↓ / 评测者→':25s}", end="")
for evaluator in all_models[:4]:
    print(f" | {evaluator[:8]:8s}", end="")
print()
print("-" * 90)

for evaluated in all_models:
    print(f"{evaluated[:25]:25s}", end="")
    for evaluator in all_models[:4]:
        scores = evaluated_stats[evaluated]["by_evaluator"].get(evaluator, [])
        if scores:
            avg = sum(scores) / len(scores)
            print(f" | {avg:8.1f}", end="")
        else:
            print(f" | {'---':8s}", end="")
    print()

print("\n【四】总体统计")
print("-" * 90)
total_completed = sum(len(s['scores']) for s in evaluated_stats.values())
total_expected = 640
print(f"✓ 完成评测: {total_completed}/{total_expected} ({total_completed/total_expected*100:.1f}%)")
print(f"✗ 失败任务: {total_expected - total_completed}")
print(f"📁 生成文件: {len(list(results_dir.glob('**/*.json')))} 个JSON文件")

all_scores = []
for model_stats in evaluated_stats.values():
    all_scores.extend(model_stats["scores"])
if all_scores:
    print(f"📈 所有评分统计: 平均 {sum(all_scores)/len(all_scores):.2f}, 中位数 {statistics.median(all_scores):.2f}")
