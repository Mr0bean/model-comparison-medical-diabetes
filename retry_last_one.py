#!/usr/bin/env python3
"""重试最后1个缺失的评估"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from cross_evaluation.engine import CrossEvaluationEngine

def main():
    print("=" * 70)
    print("重试最后1个缺失的评估")
    print("=" * 70)
    print()

    # 最后1个: 患者9: deepseek/deepseek-v3.1 → grok-4-0709

    patient = "患者9"
    model = "deepseek/deepseek-v3.1"
    evaluator = "grok-4-0709"

    engine = CrossEvaluationEngine(
        output_base_dir="output/cross_evaluation_results",
        markdown_reports_dir="output/markdown"
    )

    print(f"评估: {patient} - {model} → {evaluator}")
    print("-" * 70)

    try:
        # 加载报告
        report_content = engine._load_markdown_report(model, patient)
        if not report_content:
            print(f"✗ 报告文件不存在")
            return

        print(f"✓ 报告已加载 ({len(report_content)} 字符)")

        # 获取原始响应 (增加超时时间和重试次数)
        print(f"⏳ 正在请求 {evaluator} 进行评估...")
        print(f"   提示: grok-4-0709 可能响应较慢，请耐心等待...")

        raw_response = engine._get_raw_report_evaluation(
            patient=patient,
            generated_by=model,
            evaluated_by=evaluator,
            report_content=report_content
        )

        # 保存原始响应
        raw_file = engine._save_report_raw_response(
            patient, model, evaluator, raw_response
        )
        print(f"✓ 原始响应已保存: {raw_file}")

        # 解析并保存评分
        evaluation_result = engine._parse_and_save_report_evaluation(
            patient, model, evaluator, raw_response
        )

        avg_score = evaluation_result.get("average_score", 0)
        print(f"✓ 评估完成! 平均分: {avg_score:.2f}")
        print()
        print("🎉🎉🎉 所有640个评估已完成! 🎉🎉🎉")

    except Exception as e:
        print(f"✗ 评估失败: {e}")
        print()
        print("建议: 可以稍后再试，或者检查grok-4-0709 API状态")
        import traceback
        traceback.print_exc()

    print()
    print("=" * 70)

if __name__ == "__main__":
    main()
