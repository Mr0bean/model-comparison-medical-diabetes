#!/usr/bin/env python3
"""
第二步：解析已保存的原始响应
将raw响应解析为评分数据
"""

import argparse
from pathlib import Path
from cross_evaluation.engine import CrossEvaluationEngine


def main():
    parser = argparse.ArgumentParser(description="解析已保存的原始响应")

    parser.add_argument(
        "--patients",
        nargs="+",
        help="指定要解析的患者列表，不指定则解析全部"
    )

    parser.add_argument(
        "--conversations",
        nargs="+",
        help="指定要解析的对话类型ID列表，不指定则解析全部"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/cross_evaluation_results",
        help="原始响应所在目录（默认: output/cross_evaluation_results）"
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("📊 解析原始响应（第二步）")
    print("="*80 + "\n")

    # 初始化引擎
    engine = CrossEvaluationEngine(output_base_dir=args.output_dir)

    # 执行解析
    results = engine.parse_saved_raw_responses(
        患者列表=args.patients,
        对话类型列表=args.conversations
    )

    print("\n" + "="*80)
    print("✨ 解析完成！")
    print("="*80)
    print(f"\n📁 解析结果保存位置: {args.output_dir}/")
    print(f"\n📊 统计:")
    print(f"   总数: {results['total']}")
    print(f"   成功: {results['successful']}")
    print(f"   失败: {results['failed']}")
    print(f"   成功率: {results['successful']/results['total']*100:.1f}%" if results['total'] > 0 else "   成功率: 0%")
    print("\n💡 下一步:")
    print("   运行 python run_cross_evaluation.py --skip-evaluation 生成评分矩阵")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
