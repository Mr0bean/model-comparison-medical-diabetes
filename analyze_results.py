#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

results_dir = Path("output/cross_evaluation_results")
stats = defaultdict(lambda: {"total": 0, "completed": 0, "scores": []})

for patient_dir in sorted(results_dir.glob("患者*")):
    patient = patient_dir.name
    for agg_file in patient_dir.glob("*_aggregated.json"):
        parts = agg_file.stem.split("_by_")
        evaluated = parts[0]
        evaluator = parts[1].replace(f"_{patient}_aggregated", "")
        
        with open(agg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            total_score = data.get("总分", 0)
            stats[evaluated]["scores"].append(total_score)
            stats[evaluated]["completed"] += 1

print("=" * 80)
print("各模型被评测统计")
print("=" * 80)
for model in sorted(stats.keys()):
    scores = stats[model]["scores"]
    if scores:
        avg_score = sum(scores) / len(scores)
        print(f"{model:30s} | 完成: {len(scores):3d}/80 | 平均分: {avg_score:.2f}")
    else:
        print(f"{model:30s} | 完成: 0/80")

print("\n" + "=" * 80)
print("失败任务列表")
print("=" * 80)

# 应该是 8 models * 10 patients = 80 次被评测
all_models = ["Baichuan-M2", "deepseek_deepseek-v3.1", "doubao-seed-1-6-251015", 
              "gemini-3-pro-preview", "gpt-5.1", "grok-4-0709", 
              "moonshotai_kimi-k2-0905", "qwen3-max"]

for model in all_models:
    expected = 80  # 8 evaluators * 10 patients
    actual = stats[model]["completed"]
    if actual < expected:
        missing = expected - actual
        print(f"❌ {model}: 缺失 {missing} 个评测")

print(f"\n总完成率: {sum(len(s['scores']) for s in stats.values())}/640 ({sum(len(s['scores']) for s in stats.values())/640*100:.1f}%)")
