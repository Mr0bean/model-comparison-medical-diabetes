#!/usr/bin/env python3
"""找出缺失的评估"""
import json
from pathlib import Path

models = [
    "Baichuan-M2",
    "deepseek_deepseek-v3.1",
    "doubao-seed-1-6-251015",
    "gemini-2.5-pro",
    "gpt-5.1",
    "grok-4-0709",
    "moonshotai_kimi-k2-0905",
    "qwen3-max"
]

base_dir = Path("output/cross_evaluation_results")

print("查找缺失的评估:")
print("=" * 70)

total_missing = 0

for i in range(1, 11):
    patient = f"患者{i}"
    patient_dir = base_dir / patient / "evaluations"

    if not patient_dir.exists():
        print(f"\n{patient}: 目录不存在!")
        continue

    missing = []

    # 检查所有应该存在的评估（包括自我评估）
    for gen_model in models:
        for eval_model in models:
            # 构建文件名
            filename = f"{gen_model}_by_{eval_model}.json"
            filepath = patient_dir / filename

            if not filepath.exists():
                missing.append(f"{gen_model} → {eval_model}")

    if missing:
        print(f"\n{patient}: 缺失 {len(missing)} 个评估")
        for m in missing:
            print(f"  - {m}")
        total_missing += len(missing)

print("\n" + "=" * 70)
print(f"总计缺失: {total_missing} 个评估")
