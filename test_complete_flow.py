#!/usr/bin/env python3
"""
完整流程测试 - 2个模型 × 1个患者 × 5个维度 + 聚合
"""
import sys
import os
from pathlib import Path
import json
import time

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

from cross_evaluation.engine import engine

print("=" * 70)
print("完整流程测试")
print("=" * 70)
print()
print("测试配置:")
print("  模型: gpt-5.1, deepseek_deepseek-v3.1")
print("  患者: 患者1")
print("  预计生成: 2 × 2 × 1 × 6 = 24个文件")
print("  - 单维度评测: 2×2×5 = 20个")
print("  - 聚合结果: 2×2×1 = 4个")
print()

start_time = time.time()

try:
    # 运行评测
    engine.run(
        models=["gpt-5.1", "deepseek_deepseek-v3.1"],
        patients=["患者1"],
        resume=False
    )

    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print(f"✓ 测试完成! 用时: {elapsed:.1f}秒")
    print("=" * 70)

    # 统计结果
    output_dir = Path("output/cross_evaluation_results/患者1")
    if output_dir.exists():
        all_files = list(output_dir.glob("*.json"))
        dimension_files = [f for f in all_files if not f.name.endswith("_aggregated.json")]
        aggregated_files = [f for f in all_files if f.name.endswith("_aggregated.json")]

        print(f"\n生成文件统计:")
        print(f"  总文件数: {len(all_files)}")
        print(f"  单维度评测: {len(dimension_files)}")
        print(f"  聚合结果: {len(aggregated_files)}")

        # 显示一个完整的评测示例
        if dimension_files:
            sample = dimension_files[0]
            print(f"\n示例文件: {sample.name}")
            print("-" * 70)
            with open(sample, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"source_llm: {data.get('source_llm')}")
            print(f"target_llm: {data.get('target_llm')}")
            print(f"dimension: {data.get('dimension')}")
            print(f"score: {data.get('score')}/{data.get('max_score')}")

            # 显示模块识别
            modules = data.get('report_modules', {})
            print(f"\n识别的报告模块 ({modules.get('module_count', 0)}个):")
            for mod in modules.get('identified_modules', []):
                print(f"  ✓ {mod}")

        # 显示一个聚合结果示例
        if aggregated_files:
            agg_sample = aggregated_files[0]
            print(f"\n聚合结果示例: {agg_sample.name}")
            print("-" * 70)
            with open(agg_sample, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"总分: {data.get('total_score')}/{data.get('max_total_score')}")
            print(f"\n各维度得分:")
            for dim_name, dim_data in data.get('dimensions', {}).items():
                print(f"  {dim_name}: {dim_data.get('score')}/{dim_data.get('max_score')}")

        print("\n" + "=" * 70)
        print("✓ 所有测试通过！系统运行正常")
        print("=" * 70)

except Exception as e:
    print(f"\n✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
