#!/usr/bin/env python3
"""
完整报告交叉评估 - 主程序
评估 output/raw/ 中已生成的模型报告
"""

import argparse
import logging
from pathlib import Path

from cross_evaluation.report_loader import ReportLoader
from cross_evaluation.report_evaluation_engine import ReportEvaluationEngine
from cross_evaluation.model_registry import ModelRegistry


def setup_logging(log_level: str = "INFO"):
    """配置日志"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="完整报告交叉评估系统")

    parser.add_argument(
        '--models',
        nargs='+',
        help='要评估的模型列表（默认使用所有可用模型）'
    )

    parser.add_argument(
        '--patients',
        nargs='+',
        help='要评估的患者列表（默认评估所有患者）'
    )

    parser.add_argument(
        '--reports-dir',
        default='output/raw',
        help='报告目录路径（默认: output/raw）'
    )

    parser.add_argument(
        '--output-dir',
        default='output/report_cross_evaluation',
        help='输出目录路径（默认: output/report_cross_evaluation）'
    )

    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='测试模式：只评估第一个患者'
    )

    parser.add_argument(
        '--include-self-evaluation',
        action='store_true',
        help='包含模型自我评估'
    )

    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='日志级别'
    )

    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='跳过确认提示，自动继续'
    )

    args = parser.parse_args()

    # 配置日志
    setup_logging(args.log_level)

    print("\n" + "="*80)
    print("🤖 完整报告交叉评估系统")
    print("="*80 + "\n")

    # 初始化
    report_loader = ReportLoader(args.reports_dir)
    engine = ReportEvaluationEngine(
        reports_dir=args.reports_dir,
        output_dir=args.output_dir
    )

    # 获取可用报告
    available_reports = report_loader.get_available_reports()

    if not available_reports:
        print("❌ 没有找到可用的报告")
        print(f"   请检查目录: {args.reports_dir}")
        return

    print(f"📊 发现报告:")
    print(f"   患者数量: {len(available_reports)}")

    # 确定要评估的患者
    if args.patients:
        patients = [p for p in args.patients if p in available_reports]
        if not patients:
            print(f"❌ 指定的患者没有报告: {args.patients}")
            return
    else:
        patients = sorted(available_reports.keys())

    if args.test_mode:
        patients = patients[:1]
        print(f"\n⚠️  测试模式：只评估第一个患者 ({patients[0]})")

    print(f"\n🎯 评估范围:")
    print(f"   患者: {', '.join(patients)}")

    # 确定要使用的模型
    if args.models:
        models = args.models
    else:
        # 使用所有已注册的模型
        registry = ModelRegistry()
        models = list(registry.list_models().keys())

    print(f"   模型: {', '.join(models)}")
    print(f"   矩阵大小: {len(models)} × {len(models)}")
    print(f"   自我评估: {'是' if args.include_self_evaluation else '否'}")

    # 计算评估次数
    evals_per_patient = len(models) * len(models)
    if not args.include_self_evaluation:
        evals_per_patient -= len(models)

    total_evals = len(patients) * evals_per_patient
    print(f"   预计评估次数: {total_evals} ({len(patients)}患者 × {evals_per_patient}评估)")

    # 确认
    print(f"\n输出目录: {args.output_dir}")
    if not args.yes:
        choice = input("\n是否继续？(Y/n): ")
        if choice.lower() == 'n':
            print("已取消")
            return
    else:
        print("\n自动确认，开始评估...")

    # 开始评估
    print("\n" + "="*80)
    print("开始交叉评估")
    print("="*80 + "\n")

    results = []
    for i, patient in enumerate(patients, 1):
        print(f"\n[{i}/{len(patients)}] 评估患者: {patient}")

        result = engine.evaluate_patient_reports(
            patient=patient,
            models=models,
            include_self_evaluation=args.include_self_evaluation
        )

        results.append(result)

    # 生成汇总统计
    print("\n" + "="*80)
    print("📊 汇总统计")
    print("="*80 + "\n")

    # 按模型汇总平均分
    model_scores = {}
    for result in results:
        for model in result['models']:
            if model not in model_scores:
                model_scores[model] = []

            # 获取该模型在这个患者中的平均分
            patient_score = result['matrix']['statistics']['model_average_scores'].get(model, 0)
            model_scores[model].append(patient_score)

    # 计算总体平均分
    print("🏆 模型总体排名（跨患者平均）:")
    print("-" * 60)

    import numpy as np

    overall_rankings = []
    for model, scores in model_scores.items():
        mean_score = np.mean(scores)
        std_score = np.std(scores)
        overall_rankings.append({
            'model': model,
            'mean': round(mean_score, 2),
            'std': round(std_score, 2),
            'count': len(scores)
        })

    overall_rankings.sort(key=lambda x: x['mean'], reverse=True)

    for i, ranking in enumerate(overall_rankings, 1):
        print(f"   {i}. {ranking['model']:<30} - 平均分: {ranking['mean']:.2f} (±{ranking['std']:.2f}, n={ranking['count']})")

    # 保存汇总统计
    summary_dir = Path(args.output_dir) / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)

    summary_file = summary_dir / "overall_statistics.json"
    import json
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'patients': patients,
            'models': models,
            'overall_rankings': overall_rankings,
            'patient_results': [
                {
                    'patient': r['patient'],
                    'statistics': r['statistics'],
                    'rankings': r['matrix']['statistics']['model_rankings']
                }
                for r in results
            ]
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 汇总统计已保存: {summary_file}")

    print("\n" + "="*80)
    print("✨ 交叉评估完成！")
    print("="*80)

    print(f"\n📁 结果保存位置: {args.output_dir}/")
    print(f"\n📊 查看结果:")
    print(f"   - 患者详细结果: {{output_dir}}/{{患者}}/complete_result.json")
    print(f"   - 单个评估: {{output_dir}}/{{患者}}/evaluations/{{模型}}_evaluated_by_{{模型}}.json")
    print(f"   - 汇总统计: {{output_dir}}/summary/overall_statistics.json")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
