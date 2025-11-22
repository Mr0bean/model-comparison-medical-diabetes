#!/usr/bin/env python3
"""
灵活的分批评估脚本
可以自定义批次大小、按模型分批、按患者分批
"""

import argparse
import subprocess
import time
from datetime import datetime
from typing import List


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """将列表分成指定大小的块"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def run_evaluation_chunk(patients: List[str], models: List[str] = None, dry_run: bool = False):
    """运行一个批次的评估"""
    cmd = ["python", "run_cross_evaluation.py", "--patients"] + patients

    if models:
        cmd.extend(["--models"] + models)

    print(f"\n{'='*80}")
    print(f"执行命令: {' '.join(cmd)}")
    print(f"患者: {', '.join(patients)}")
    if models:
        print(f"模型: {', '.join(models)}")
    print(f"预计评估: {len(patients)} × {len(models) if models else 8} × {len(models) if models else 8} = {len(patients) * (len(models) if models else 8) * (len(models) if models else 8)} 次")
    print(f"{'='*80}\n")

    if dry_run:
        print("⚠️  试运行模式，不实际执行\n")
        return {"status": "dry_run"}

    start_time = time.time()

    try:
        result = subprocess.run(cmd, check=True)
        duration = time.time() - start_time

        print(f"\n✅ 批次执行成功 (耗时: {duration/60:.1f} 分钟)")
        return {"status": "success", "duration": duration}

    except subprocess.CalledProcessError as e:
        print(f"\n❌ 批次执行失败: {e}")
        return {"status": "failed", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="灵活的分批评估脚本")

    parser.add_argument(
        "--batch-size",
        type=int,
        default=3,
        help="每批包含的患者数量（默认: 3）"
    )

    parser.add_argument(
        "--patients",
        nargs="+",
        default=[f"患者{i}" for i in range(1, 11)],
        help="要评估的患者列表（默认: 患者1-10）"
    )

    parser.add_argument(
        "--models",
        nargs="+",
        help="要使用的模型列表（默认: 全部）"
    )

    parser.add_argument(
        "--batch-index",
        type=int,
        help="只执行指定批次（从1开始），不指定则执行全部"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，仅显示命令不执行"
    )

    parser.add_argument(
        "--wait-time",
        type=int,
        default=5,
        help="批次间等待时间（秒，默认: 5）"
    )

    args = parser.parse_args()

    # 分批
    patient_chunks = chunk_list(args.patients, args.batch_size)

    print("\n" + "="*80)
    print("📊 灵活分批评估系统")
    print("="*80)
    print(f"\n总患者数: {len(args.patients)}")
    print(f"批次大小: {args.batch_size}")
    print(f"总批次数: {len(patient_chunks)}")
    print(f"\n批次划分:")

    for i, chunk in enumerate(patient_chunks, 1):
        print(f"  批次{i}: {', '.join(chunk)}")

    if args.models:
        print(f"\n指定模型: {', '.join(args.models)}")

    # 确定要执行的批次
    if args.batch_index:
        if args.batch_index < 1 or args.batch_index > len(patient_chunks):
            print(f"\n❌ 错误: 批次索引 {args.batch_index} 超出范围 (1-{len(patient_chunks)})")
            return

        chunks_to_run = [patient_chunks[args.batch_index - 1]]
        print(f"\n仅执行批次 {args.batch_index}")
    else:
        chunks_to_run = patient_chunks
        print(f"\n执行全部 {len(chunks_to_run)} 个批次")

    # 询问确认
    if not args.dry_run:
        print("\n" + "="*80)
        choice = input("是否开始执行？(y/n): ")
        if choice.lower() != 'y':
            print("已取消执行")
            return

    # 执行批次
    results = []
    overall_start_time = time.time()

    for i, chunk in enumerate(chunks_to_run, 1):
        print(f"\n{'='*80}")
        print(f"进度: {i}/{len(chunks_to_run)}")
        print(f"{'='*80}")

        result = run_evaluation_chunk(
            patients=chunk,
            models=args.models,
            dry_run=args.dry_run
        )
        results.append(result)

        # 批次间等待
        if i < len(chunks_to_run) and not args.dry_run:
            print(f"\n等待 {args.wait_time} 秒后执行下一批...")
            time.sleep(args.wait_time)

    # 总结
    overall_duration = time.time() - overall_start_time

    print("\n" + "="*80)
    print("📊 执行总结")
    print("="*80)

    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')

    print(f"\n执行批次数: {len(results)}/{len(chunks_to_run)}")
    print(f"成功: {successful}")
    print(f"失败: {failed}")
    print(f"总耗时: {overall_duration/60:.1f} 分钟")

    # 保存日志
    if not args.dry_run:
        log_file = f"flexible_batch_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"灵活分批评估执行日志\n")
            f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"批次大小: {args.batch_size}\n")
            f.write(f"总批次数: {len(results)}\n")
            f.write(f"总耗时: {overall_duration/60:.1f} 分钟\n\n")

            for i, (chunk, result) in enumerate(zip(chunks_to_run, results), 1):
                f.write(f"\n批次{i}:\n")
                f.write(f"  患者: {', '.join(chunk)}\n")
                f.write(f"  状态: {result['status']}\n")
                if 'duration' in result:
                    f.write(f"  耗时: {result['duration']/60:.1f} 分钟\n")

        print(f"\n📝 执行日志已保存: {log_file}")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
