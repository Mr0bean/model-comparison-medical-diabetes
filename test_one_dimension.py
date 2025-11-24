#!/usr/bin/env python3
"""单维度测试脚本 - 快速验证评测流程"""
import sys
import os
from pathlib import Path
import json

# 加载.env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

sys.path.insert(0, str(Path(__file__).parent))

from cross_evaluation.report_loader import report_loader
from cross_evaluation.dimension_evaluator import dimension_evaluator
from cross_evaluation.config import config

print("=" * 70)
print("单维度评测测试 - gpt-5.1 by deepseek-chat")
print("=" * 70)

# 设置
evaluated_model = "gpt-5.1"
evaluator_model = "deepseek-chat"
patient = "患者1"
dimension = "准确性"

try:
    # 1. 加载报告
    print(f"\n1. 加载报告: {evaluated_model} - {patient}")
    conversation, report = report_loader.load_report_data(evaluated_model, patient)
    print(f"   对话长度: {len(conversation)} 字符")
    print(f"   报告长度: {len(report)} 字符")

    # 2. 执行评测
    print(f"\n2. 执行评测: {dimension}")
    print(f"   评测模型: {evaluator_model}")
    result = dimension_evaluator.evaluate(
        dimension_name=dimension,
        conversation=conversation,
        report=report,
        evaluator_model=evaluator_model,
        evaluated_model=evaluated_model,
        patient=patient
    )

    # 3. 显示结果
    print(f"\n3. 评测结果:")
    print(f"   source_llm (被评测模型): {result.get('source_llm')}")
    print(f"   target_llm (评测模型): {result.get('target_llm')}")
    print(f"   维度: {result.get('dimension')}")
    print(f"   得分: {result.get('score')}/{result.get('max_score')}")
    print(f"   问题: {result.get('issues')[:100] if result.get('issues') else '无'}...")
    print(f"   反馈: {result.get('critical_feedback')[:100]}...")

    # 4. 检查详细信息
    print(f"\n4. 详细信息:")
    print(f"   prompt_input长度: {len(result.get('prompt_input', ''))} 字符")
    print(f"   output长度: {len(result.get('output', ''))} 字符")

    # 5. 保存结果
    output_dir = Path("output/cross_evaluation_results") / patient
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{evaluated_model}_by_{evaluator_model}_{patient}_{dimension}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n5. 结果已保存:")
    print(f"   {output_file}")

    # 6. 显示文件部分内容
    print(f"\n6. JSON文件预览 (前500字符):")
    print("-" * 70)
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    print(content[:500] + "...")

    print("\n" + "=" * 70)
    print("✓ 测试成功完成!")
    print("=" * 70)

except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
