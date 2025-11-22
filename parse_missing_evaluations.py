#!/usr/bin/env python3
"""解析已有raw文件但未解析的评估结果"""

import json
from pathlib import Path
from cross_evaluation.engine import CrossEvaluationEngine

def find_missing_parsed_files():
    """找到所有需要解析的raw文件"""
    base_dir = Path("output/cross_evaluation_results")
    missing = []

    for patient_dir in sorted(base_dir.glob("患者*")):
        patient = patient_dir.name
        raw_dir = patient_dir / "raw"
        eval_dir = patient_dir / "evaluations"

        if not raw_dir.exists():
            continue

        # 检查每个raw文件
        for raw_file in raw_dir.glob("*.json"):
            eval_file = eval_dir / raw_file.name

            if not eval_file.exists():
                missing.append({
                    "patient": patient,
                    "raw_file": raw_file,
                    "eval_file": eval_file
                })

    return missing

def parse_raw_file(raw_file_path, eval_file_path, engine):
    """解析单个raw文件"""
    try:
        # 读取raw文件
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        patient = raw_data.get("patient")
        generated_by = raw_data.get("generated_by")
        evaluated_by = raw_data.get("evaluated_by")

        # 调用解析函数
        result = engine._parse_and_save_report_evaluation(
            patient=patient,
            generated_by=generated_by,
            evaluated_by=evaluated_by,
            raw_response=raw_data
        )

        return True, result.get("average_score", 0)

    except Exception as e:
        return False, str(e)

def main():
    print("=" * 80)
    print("🔧 解析未处理的Raw文件")
    print("=" * 80)
    print()

    # 查找缺失的文件
    missing = find_missing_parsed_files()

    print(f"📊 找到 {len(missing)} 个需要解析的raw文件\n")

    if not missing:
        print("✅ 所有raw文件都已解析完成！")
        return

    # 初始化引擎
    engine = CrossEvaluationEngine(
        output_base_dir="output/cross_evaluation_results",
        markdown_reports_dir="output/markdown"
    )

    # 解析每个文件
    success_count = 0
    failed_count = 0

    for i, item in enumerate(missing, 1):
        patient = item["patient"]
        raw_file = item["raw_file"]
        eval_file = item["eval_file"]

        print(f"[{i}/{len(missing)}] {patient} - {raw_file.name}")

        success, result = parse_raw_file(raw_file, eval_file, engine)

        if success:
            print(f"    ✓ 成功解析，平均分: {result:.2f}")
            success_count += 1
        else:
            print(f"    ✗ 解析失败: {result}")
            failed_count += 1

        print()

    print("=" * 80)
    print(f"✨ 解析完成！")
    print(f"   成功: {success_count}")
    print(f"   失败: {failed_count}")
    print("=" * 80)

if __name__ == "__main__":
    main()
