#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict

results_dir = Path("output/cross_evaluation_results")

print("=" * 80)
print("🔍 数据完整性与质量检查")
print("=" * 80)

# 1. 检查文件数量
print("\n【一】文件数量检查")
aggregated_files = list(results_dir.glob("**/*_aggregated.json"))
dimension_files = [f for f in results_dir.glob("**/*.json") if "_aggregated" not in f.name and f.name != ".progress.json"]

print(f"  聚合文件数: {len(aggregated_files)}/640")
print(f"  维度文件数: {len(dimension_files)}/{640*5}")
print(f"  总JSON文件: {len(aggregated_files) + len(dimension_files)}")

# 2. 检查每个患者的完成情况
print("\n【二】各患者文件分布")
for patient_dir in sorted(results_dir.glob("患者*")):
    agg_count = len(list(patient_dir.glob("*_aggregated.json")))
    dim_count = len([f for f in patient_dir.glob("*.json") if "_aggregated" not in f.name])
    expected_agg = 64  # 8 * 8
    expected_dim = 64 * 5  # 64 * 5 dimensions
    status = "✓" if agg_count == expected_agg and dim_count == expected_dim else "⚠️"
    print(f"  {patient_dir.name}: 聚合={agg_count}/{expected_agg}, 维度={dim_count}/{expected_dim} {status}")

# 3. 检查数据质量问题
print("\n【三】数据质量检查")
errors = []
warnings = []
empty_files = []
invalid_json = []
invalid_scores = []
missing_dimensions = []

for agg_file in aggregated_files:
    try:
        # 检查文件大小
        if agg_file.stat().st_size < 100:
            empty_files.append(str(agg_file))
            continue
        
        # 检查JSON格式
        with open(agg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查必要字段
        total_score = data.get("总分") or data.get("total_score")
        dimensions = data.get("维度评分") or data.get("dimensions")
        
        if total_score is None:
            errors.append(f"{agg_file.name}: 缺少总分")
        elif not isinstance(total_score, (int, float)):
            errors.append(f"{agg_file.name}: 总分类型错误 ({type(total_score)})")
        elif total_score < 0 or total_score > 100:
            invalid_scores.append(f"{agg_file.name}: 总分异常 ({total_score})")
        elif total_score == 0:
            warnings.append(f"{agg_file.name}: 总分为0")
        
        # 检查维度
        if not dimensions:
            missing_dimensions.append(f"{agg_file.name}: 缺少维度评分")
        elif len(dimensions) != 5:
            missing_dimensions.append(f"{agg_file.name}: 维度数错误 ({len(dimensions)}/5)")
        
    except json.JSONDecodeError as e:
        invalid_json.append(f"{agg_file.name}: JSON解析失败 - {e}")
    except Exception as e:
        errors.append(f"{agg_file.name}: {e}")

# 输出问题
if empty_files:
    print(f"\n  ❌ 空文件 ({len(empty_files)}个):")
    for f in empty_files[:5]:
        print(f"     - {f}")
    if len(empty_files) > 5:
        print(f"     ... 还有{len(empty_files)-5}个")

if invalid_json:
    print(f"\n  ❌ JSON格式错误 ({len(invalid_json)}个):")
    for err in invalid_json[:5]:
        print(f"     - {err}")
    if len(invalid_json) > 5:
        print(f"     ... 还有{len(invalid_json)-5}个")

if invalid_scores:
    print(f"\n  ❌ 评分异常 ({len(invalid_scores)}个):")
    for err in invalid_scores[:5]:
        print(f"     - {err}")
    if len(invalid_scores) > 5:
        print(f"     ... 还有{len(invalid_scores)-5}个")

if missing_dimensions:
    print(f"\n  ⚠️  维度问题 ({len(missing_dimensions)}个):")
    for err in missing_dimensions[:5]:
        print(f"     - {err}")
    if len(missing_dimensions) > 5:
        print(f"     ... 还有{len(missing_dimensions)-5}个")

if warnings:
    print(f"\n  ⚠️  警告 ({len(warnings)}个):")
    for w in warnings[:5]:
        print(f"     - {w}")
    if len(warnings) > 5:
        print(f"     ... 还有{len(warnings)-5}个")

if errors:
    print(f"\n  ❌ 其他错误 ({len(errors)}个):")
    for err in errors[:5]:
        print(f"     - {err}")
    if len(errors) > 5:
        print(f"     ... 还有{len(errors)-5}个")

# 4. 统计评分分布
print("\n【四】评分分布统计")
all_scores = []
for agg_file in aggregated_files:
    try:
        with open(agg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            score = data.get("总分") or data.get("total_score")
            if score and isinstance(score, (int, float)):
                all_scores.append(score)
    except:
        pass

if all_scores:
    score_ranges = {
        "0-20分": 0,
        "21-40分": 0,
        "41-60分": 0,
        "61-80分": 0,
        "81-100分": 0
    }
    for score in all_scores:
        if score <= 20:
            score_ranges["0-20分"] += 1
        elif score <= 40:
            score_ranges["21-40分"] += 1
        elif score <= 60:
            score_ranges["41-60分"] += 1
        elif score <= 80:
            score_ranges["61-80分"] += 1
        else:
            score_ranges["81-100分"] += 1
    
    for range_name, count in score_ranges.items():
        pct = count / len(all_scores) * 100
        bar = "█" * int(pct / 2)
        print(f"  {range_name:10s}: {count:3d} ({pct:5.1f}%) {bar}")

# 5. 总结
print("\n【五】总结")
total_issues = len(empty_files) + len(invalid_json) + len(invalid_scores) + len(errors)
if total_issues == 0 and len(missing_dimensions) == 0:
    print("  ✅ 所有数据检查通过，无错误！")
elif total_issues == 0:
    print(f"  ⚠️  有{len(missing_dimensions)}个维度警告，但无严重错误")
else:
    print(f"  ❌ 发现{total_issues}个错误，需要修复")

print("=" * 80)
