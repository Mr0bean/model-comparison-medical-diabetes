#!/usr/bin/env python3
"""
交叉评测入口脚本
用于启动交叉评测流程
"""
import argparse
import sys
import os
from pathlib import Path

# 加载.env文件
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from cross_evaluation.engine import engine
from cross_evaluation.config import config


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="交叉评测系统")

    parser.add_argument(
        "--models",
        nargs="+",
        help="指定要评测的模型列表（留空使用配置中的所有模型）"
    )

    parser.add_argument(
        "--patients",
        nargs="+",
        help="指定要评测的患者列表（留空使用配置中的所有患者）"
    )

    parser.add_argument(
        "--resume",
        action="store_true",
        help="从上次中断处继续"
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        help="使用并行模式（更快但需要更多资源）"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="并行模式下的最大并发数（默认使用配置中的值）"
    )

    parser.add_argument(
        "--list-models",
        action="store_true",
        help="列出配置中的所有模型"
    )

    parser.add_argument(
        "--list-patients",
        action="store_true",
        help="列出配置中的所有患者"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="跳过确认，直接开始评测"
    )

    args = parser.parse_args()

    # 列出模型
    if args.list_models:
        print("配置中的模型列表:")
        for i, model in enumerate(config.models, 1):
            print(f"  {i}. {model}")
        return

    # 列出患者
    if args.list_patients:
        print("配置中的患者列表:")
        for i, patient in enumerate(config.patients, 1):
            print(f"  {i}. {patient}")
        return

    # 打印配置信息
    print("=" * 60)
    print("交叉评测系统")
    print("=" * 60)

    models = args.models if args.models else config.models
    patients = args.patients if args.patients else config.patients

    print(f"\n配置信息:")
    print(f"  模型数量: {len(models)}")
    print(f"  患者数量: {len(patients)}")
    print(f"  评测维度: {len(config.dimensions)}")
    print(f"  并行模式: {'是' if args.parallel else '否'}")
    print(f"  断点续传: {'是' if args.resume else '否'}")

    if args.parallel and args.max_workers:
        print(f"  最大并发数: {args.max_workers}")

    print(f"\n输出目录: {config.output_dir}")
    print(f"Prompt目录: {config.prompt_base_dir}")
    print(f"报告目录: {config.raw_reports_dir}")

    # 确认
    if not args.yes:
        response = input("\n是否开始评测？(y/n): ")
        if response.lower() != 'y':
            print("已取消")
            return

    # 运行评测
    print("\n" + "=" * 60)

    try:
        if args.parallel:
            engine.run_parallel(
                models=models,
                patients=patients,
                resume=args.resume,
                max_workers=args.max_workers
            )
        else:
            engine.run(
                models=models,
                patients=patients,
                resume=args.resume
            )

        print("\n" + "=" * 60)
        print("评测完成!")
        print(f"结果保存在: {config.output_dir}")

    except KeyboardInterrupt:
        print("\n\n评测被中断")
        print("使用 --resume 参数可以从中断处继续")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n评测失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
