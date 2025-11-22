#!/usr/bin/env python3
"""全面的完整性检查"""

import json
from pathlib import Path
from collections import defaultdict
import statistics

# 定义模型列表
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

base_dir = Path("output/cross_evaluation_results")

print("=" * 80)
print("全面完整性检查")
print("=" * 80)
print()

# 检查1: 文件数量
print("【检查1】文件数量验证")
print("-" * 80)

total_expected = len(PATIENTS) * len(MODELS) * len(MODELS)
print(f"预期总数: {total_expected} (10患者 × 8模型 × 8评估者)")

total_found = 0
total_valid = 0
total_zero = 0

patient_stats = {}

for patient in PATIENTS:
    eval_dir = base_dir / patient / "evaluations"

    if not eval_dir.exists():
        print(f"❌ {patient}: 目录不存在!")
        patient_stats[patient] = {"found": 0, "valid": 0, "zero": 0}
        continue

    found = len(list(eval_dir.glob("*.json")))
    valid = 0
    zero = 0

    for eval_file in eval_dir.glob("*.json"):
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            score = data.get('average_score', -1)
            if score > 0:
                valid += 1
            elif score == 0:
                zero += 1
        except:
            pass

    total_found += found
    total_valid += valid
    total_zero += zero

    patient_stats[patient] = {"found": found, "valid": valid, "zero": zero}

    status = "✓" if found == 64 and valid == 64 else "✗"
    print(f"{status} {patient}: {found}/64 文件, {valid} 有效, {zero} 零分")

print()
print(f"总计: {total_found}/{total_expected} 文件")
print(f"      {total_valid} 有效评估")
print(f"      {total_zero} 零分评估")
print()

# 检查2: 缺失的评估组合
print("【检查2】缺失评估检查")
print("-" * 80)

all_missing = []

for patient in PATIENTS:
    eval_dir = base_dir / patient / "evaluations"

    if not eval_dir.exists():
        continue

    patient_missing = []

    for gen_model in MODELS:
        for eval_model in MODELS:
            filename = f"{gen_model}_by_{eval_model}.json"
            filepath = eval_dir / filename

            if not filepath.exists():
                patient_missing.append(f"{gen_model} → {eval_model}")
                all_missing.append({
                    "patient": patient,
                    "generated_by": gen_model,
                    "evaluated_by": eval_model
                })

    if patient_missing:
        print(f"{patient}: 缺失 {len(patient_missing)} 个")
        for m in patient_missing[:5]:  # 只显示前5个
            print(f"  - {m}")
        if len(patient_missing) > 5:
            print(f"  ... 还有 {len(patient_missing) - 5} 个")

if not all_missing:
    print("✓ 没有缺失的评估组合!")
else:
    print(f"❌ 总计缺失: {len(all_missing)} 个评估")

print()

# 检查3: 零分评估详情
print("【检查3】零分评估详情")
print("-" * 80)

zero_score_details = []

for patient in PATIENTS:
    eval_dir = base_dir / patient / "evaluations"

    if not eval_dir.exists():
        continue

    for eval_file in eval_dir.glob("*.json"):
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            score = data.get('average_score', -1)

            if score == 0:
                filename = eval_file.stem
                parts = filename.split('_by_')
                if len(parts) == 2:
                    zero_score_details.append({
                        "patient": patient,
                        "model": parts[0],
                        "evaluator": parts[1],
                        "file": str(eval_file)
                    })
        except:
            pass

if zero_score_details:
    print(f"❌ 发现 {len(zero_score_details)} 个零分评估:")
    for item in zero_score_details[:10]:
        print(f"  - {item['patient']}: {item['model']} → {item['evaluator']}")
    if len(zero_score_details) > 10:
        print(f"  ... 还有 {len(zero_score_details) - 10} 个")
else:
    print("✓ 没有零分评估!")

print()

# 检查4: 分数统计分析
print("【检查4】分数统计分析")
print("-" * 80)

all_scores = []
model_scores = defaultdict(list)
evaluator_scores = defaultdict(list)

for patient in PATIENTS:
    eval_dir = base_dir / patient / "evaluations"

    if not eval_dir.exists():
        continue

    for eval_file in eval_dir.glob("*.json"):
        try:
            with open(eval_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            score = data.get('average_score', 0)

            if score > 0:
                all_scores.append(score)

                filename = eval_file.stem
                parts = filename.split('_by_')
                if len(parts) == 2:
                    model_scores[parts[0]].append(score)
                    evaluator_scores[parts[1]].append(score)
        except:
            pass

if all_scores:
    print(f"有效评估数: {len(all_scores)}")
    print(f"平均分: {statistics.mean(all_scores):.2f}")
    print(f"标准差: {statistics.stdev(all_scores):.2f}")
    print(f"中位数: {statistics.median(all_scores):.2f}")
    print(f"最高分: {max(all_scores):.2f}")
    print(f"最低分: {min(all_scores):.2f}")
    print()

    # 分数分布
    ranges = {
        "1.0-2.0": 0,
        "2.0-3.0": 0,
        "3.0-4.0": 0,
        "4.0-5.0": 0
    }

    for score in all_scores:
        if 1.0 <= score < 2.0:
            ranges["1.0-2.0"] += 1
        elif 2.0 <= score < 3.0:
            ranges["2.0-3.0"] += 1
        elif 3.0 <= score < 4.0:
            ranges["3.0-4.0"] += 1
        elif 4.0 <= score <= 5.0:
            ranges["4.0-5.0"] += 1

    print("分数分布:")
    for range_name, count in ranges.items():
        pct = count / len(all_scores) * 100
        bar = "█" * int(pct / 2)
        print(f"  {range_name}: {count:3d} ({pct:5.1f}%) {bar}")

print()

# 检查5: 每个模型的评估覆盖度
print("【检查5】模型评估覆盖度")
print("-" * 80)

for model in MODELS:
    # 作为被评估者
    as_subject_count = len(model_scores.get(model, []))
    expected_as_subject = len(PATIENTS) * len(MODELS)  # 10患者 × 8评估者

    # 作为评估者
    as_evaluator_count = len(evaluator_scores.get(model, []))
    expected_as_evaluator = len(PATIENTS) * len(MODELS)  # 10患者 × 8被评估者

    subject_status = "✓" if as_subject_count == expected_as_subject else "✗"
    evaluator_status = "✓" if as_evaluator_count == expected_as_evaluator else "✗"

    print(f"{model}:")
    print(f"  {subject_status} 作为被评估者: {as_subject_count}/{expected_as_subject}")
    print(f"  {evaluator_status} 作为评估者: {as_evaluator_count}/{expected_as_evaluator}")

print()

# 最终结论
print("=" * 80)
print("【最终结论】")
print("=" * 80)

issues = []

if total_found != total_expected:
    issues.append(f"文件数量不完整: {total_found}/{total_expected}")

if total_zero > 0:
    issues.append(f"存在零分评估: {total_zero}个")

if all_missing:
    issues.append(f"缺失评估组合: {len(all_missing)}个")

if issues:
    print("❌ 发现问题:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("✅ 完整性检查通过!")
    print(f"   - 所有 {total_expected} 个评估文件存在")
    print(f"   - 所有评估都有有效分数")
    print(f"   - 没有缺失的评估组合")
    print()
    print("🎉🎉🎉 数据完整! 可以进行下一步分析! 🎉🎉🎉")

print("=" * 80)
