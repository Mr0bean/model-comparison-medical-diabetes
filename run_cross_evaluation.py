#!/usr/bin/env python3
"""
交叉评估系统主执行脚本
运行模型间的交叉评估并生成评分矩阵
"""

import argparse
import json
from pathlib import Path
from cross_evaluation.engine import CrossEvaluationEngine
from cross_evaluation.matrix import MatrixGenerator
from cross_evaluation.conversation_indexer import ConversationIndexer


def main():
    parser = argparse.ArgumentParser(description="运行模型交叉评估系统")

    parser.add_argument(
        "--patients",
        nargs="+",
        help="指定要评估的患者列表（如：患者1 患者2），不指定则评估全部"
    )

    parser.add_argument(
        "--models",
        nargs="+",
        help="指定要使用的模型列表，不指定则使用全部模型"
    )

    # 注释：不再需要conversations参数，因为现在评估的是完整报告
    # parser.add_argument(
    #     "--conversations",
    #     nargs="+",
    #     help="指定要评估的对话类型ID列表（如：1 2 3），不指定则评估全部"
    # )

    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="跳过评估，仅生成矩阵（用于已有评估结果的情况）"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/cross_evaluation_results",
        help="输出目录（默认: output/cross_evaluation_results）"
    )

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="测试模式：仅评估1个患者的1个对话"
    )

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤖 模型交叉评估系统")
    print("="*80 + "\n")

    # 加载对比数据以获取可用的患者和模型
    comparison_data_path = Path("output/comparison_data.json")
    if not comparison_data_path.exists():
        print("❌ 错误: 未找到 output/comparison_data.json")
        print("   请先运行 prepare_comparison_data.py 生成对比数据")
        return

    with open(comparison_data_path, 'r', encoding='utf-8') as f:
        comparison_data = json.load(f)

    available_patients = comparison_data.get("patients", [])
    available_models = comparison_data.get("models", [])

    print("📊 可用数据:")
    print(f"   患者数量: {len(available_patients)}")
    print(f"   模型数量: {len(available_models)}")
    print(f"   模型列表: {', '.join(available_models)}\n")

    # 确定评估范围
    patients = args.patients or available_patients
    models = args.models or available_models

    # 测试模式：只评估第一个患者
    if args.test_mode:
        print("⚠️  测试模式：仅评估第一个患者的完整报告\n")
        patients = patients[:1]

    print("🎯 评估范围:")
    print(f"   患者: {', '.join(patients)}")
    print(f"   模型: {', '.join(models)}")
    print(f"   评估类型: 完整报告（所有对话合并）")
    print()

    # 步骤1: 运行交叉评估（完整报告）
    if not args.skip_evaluation:
        print("="*80)
        print("步骤 1/3: 运行完整报告交叉评估")
        print("="*80 + "\n")

        engine = CrossEvaluationEngine(
            output_base_dir=args.output_dir,
            markdown_reports_dir="output/markdown"
        )

        results = engine.run_report_cross_evaluation(
            患者列表=patients,
            模型列表=models
        )

        print("\n✅ 交叉评估完成")
        print(f"   成功: {results['statistics']['successful']}")
        print(f"   失败: {results['statistics']['failed']}")
    else:
        print("⏭️  跳过评估步骤（使用已有结果）\n")

    # 步骤2: 生成评分矩阵
    print("\n" + "="*80)
    print("步骤 2/3: 生成评分矩阵")
    print("="*80 + "\n")

    matrix_gen = MatrixGenerator(evaluation_base_dir=args.output_dir)
    all_matrices = matrix_gen.generate_all_matrices(patients, models)

    print(f"\n✅ 已生成 {sum(len(p) for p in all_matrices.values())} 个矩阵")

    # 步骤3: 生成汇总统计
    print("\n" + "="*80)
    print("步骤 3/3: 生成汇总统计")
    print("="*80 + "\n")

    summary = matrix_gen.generate_summary_statistics(all_matrices)

    # 显示总体排名
    print("\n🏆 模型总体排名:")
    print("-" * 60)
    for rank_data in summary["overall_rankings"][:10]:  # 显示前10名
        rank = rank_data["rank"]
        model = rank_data["model"]
        mean = rank_data["mean"]
        std = rank_data["std"]
        count = rank_data["count"]

        print(f"  {rank:2d}. {model:30s} - 平均分: {mean:.2f} (±{std:.2f}, n={count})")

    print("\n" + "="*80)
    print("✨ 完整报告交叉评估系统运行完成！")
    print("="*80)
    print(f"\n📁 结果保存位置: {args.output_dir}/")
    print("\n📊 查看结果:")
    print("   - 原始评估响应: {output_dir}/{患者}/raw/")
    print("   - 解析后评估: {output_dir}/{患者}/evaluations/")
    print("   - 评分矩阵: {output_dir}/{患者}/matrix.json")
    print("   - 汇总统计: {output_dir}/summary/statistics.json")
    print("\n💡 下一步:")
    print("   - 运行 python parse_raw_responses.py 解析原始响应")
    print("   - 打开 cross_evaluation_viewer.html 可视化查看结果")
    print("   - 使用 --test-mode 快速测试系统")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
