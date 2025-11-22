#!/usr/bin/env python3
"""测试详细日志输出"""

from cross_evaluation.engine import CrossEvaluationEngine

# 初始化引擎
engine = CrossEvaluationEngine(
    output_base_dir="output/cross_evaluation_results",
    markdown_reports_dir="output/markdown"
)

# 只测试1个评估
print("="*80)
print("测试详细日志输出")
print("="*80)

results = engine.run_report_cross_evaluation(
    患者列表=["患者1"],
    模型列表=["Baichuan-M2", "deepseek/deepseek-v3.1"]
)

print("\n" + "="*80)
print("测试完成！")
print(f"成功: {results['statistics']['successful']}")
print(f"失败: {results['statistics']['failed']}")
print("="*80)
