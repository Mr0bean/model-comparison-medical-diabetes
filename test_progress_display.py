#!/usr/bin/env python3
"""
测试进度显示功能
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from cross_evaluation.engine import CrossEvaluationEngine

def main():
    print("\n" + "="*80)
    print("🧪 测试进度显示功能")
    print("="*80 + "\n")

    # 创建引擎实例
    engine = CrossEvaluationEngine(
        comparison_data_path="output/comparison_data.json",
        output_base_dir="output/cross_evaluation_results_test",
        markdown_reports_dir="output/markdown"
    )

    # 运行测试评估（只评估一个患者）
    try:
        results = engine.run_report_cross_evaluation(
            患者列表=["患者1"],
            模型列表=["Baichuan-M2", "doubao-seed-1-6-251015"]
        )

        print("\n" + "="*80)
        print("✅ 测试完成")
        print("="*80)
        print(f"成功: {results['statistics']['successful']}")
        print(f"失败: {results['statistics']['failed']}")
        print(f"成功率: {results['statistics']['success_rate']}")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
