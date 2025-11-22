#!/usr/bin/env python3
"""快速检查当前进度"""
import json
from pathlib import Path

base_dir = Path("output/cross_evaluation_results")

print("=" * 60)
print("详细进度统计")
print("=" * 60)

total_valid = 0
total_zero = 0
total_files = 0

for i in range(1, 11):
    patient_dir = base_dir / f"患者{i}" / "evaluations"
    if not patient_dir.exists():
        continue

    valid = 0
    zero = 0
    files = 0

    for eval_file in patient_dir.glob("*.json"):
        files += 1
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score = data.get('average_score', -1)
            if score == 0.0:
                zero += 1
            elif score > 0:
                valid += 1
        except:
            pass

    total_files += files
    total_valid += valid
    total_zero += zero

    print(f"患者{i:2d}: {valid:2d} 有效 / {zero:2d} 零分 / {files:2d} 总数")

print("=" * 60)
print(f"总计:   {total_valid:3d} 有效 / {total_zero:2d} 零分 / {total_files:3d} 总数")
print(f"进度:   {total_valid}/640 ({total_valid/640*100:.1f}%)")
print(f"还需:   {640 - total_valid} 个有效评估")
print("=" * 60)
