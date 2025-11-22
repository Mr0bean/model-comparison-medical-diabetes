#!/usr/bin/env python3
"""
分批次运行交叉评估
按指定的患者分组批量执行
"""

import subprocess
import time
from datetime import datetime

# 定义患者分组
PATIENT_BATCHES = [
    {
        "name": "第一批",
        "patients": ["患者2", "患者3", "患者4"]
    },
    {
        "name": "第二批",
        "patients": ["患者5", "患者6", "患者7"]
    },
    {
        "name": "第三批",
        "patients": ["患者8", "患者9", "患者10"]
    }
]


def run_evaluation_for_batch(batch_name, patients, dry_run=False):
    """
    运行一批患者的评估

    Args:
        batch_name: 批次名称
        patients: 患者列表
        dry_run: 是否仅显示命令不执行
    """
    print("\n" + "="*80)
    print(f"🚀 开始执行: {batch_name}")
    print("="*80)
    print(f"患者列表: {', '.join(patients)}")
    print(f"患者数量: {len(patients)}")
    print(f"评估类型: 完整报告（不分对话）")
    print(f"预计API调用: {len(patients)} × 8 × 8 = {len(patients) * 64} 次")
    print("="*80 + "\n")

    # 构建命令
    cmd = [
        "python", "run_cross_evaluation.py",
        "--patients"
    ] + patients

    print(f"执行命令: {' '.join(cmd)}\n")

    if dry_run:
        print("⚠️  试运行模式，不实际执行\n")
        return {"status": "dry_run", "batch": batch_name}

    # 记录开始时间
    start_time = time.time()
    start_datetime = datetime.now()

    try:
        # 执行命令
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,  # 实时显示输出
            text=True
        )

        # 记录结束时间
        end_time = time.time()
        duration = end_time - start_time

        print("\n" + "="*80)
        print(f"✅ {batch_name} 执行成功")
        print("="*80)
        print(f"开始时间: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"耗时: {duration/60:.1f} 分钟")
        print("="*80 + "\n")

        return {
            "status": "success",
            "batch": batch_name,
            "patients": patients,
            "duration": duration,
            "start_time": start_datetime,
            "end_time": datetime.now()
        }

    except subprocess.CalledProcessError as e:
        print("\n" + "="*80)
        print(f"❌ {batch_name} 执行失败")
        print("="*80)
        print(f"错误: {e}")
        print("="*80 + "\n")

        return {
            "status": "failed",
            "batch": batch_name,
            "patients": patients,
            "error": str(e)
        }
    except KeyboardInterrupt:
        print("\n" + "="*80)
        print(f"⚠️  {batch_name} 被用户中断")
        print("="*80 + "\n")

        return {
            "status": "interrupted",
            "batch": batch_name,
            "patients": patients
        }


def main():
    print("\n" + "="*80)
    print("📊 分批次交叉评估系统")
    print("="*80 + "\n")

    print("批次设置:")
    for i, batch in enumerate(PATIENT_BATCHES, 1):
        print(f"  {i}. {batch['name']}: {', '.join(batch['patients'])}")

    print(f"\n总患者数: {sum(len(b['patients']) for b in PATIENT_BATCHES)}")
    print(f"总批次数: {len(PATIENT_BATCHES)}")
    print(f"预计总API调用: {sum(len(b['patients']) for b in PATIENT_BATCHES) * 64} 次")

    # 询问是否继续
    print("\n" + "="*80)
    choice = input("是否开始执行？(y/n): ")
    if choice.lower() != 'y':
        print("已取消执行")
        return

    # 询问执行模式
    print("\n执行模式:")
    print("  1. 全部执行（所有3批）")
    print("  2. 仅第一批（患者2,3,4）")
    print("  3. 仅第二批（患者5,6,7）")
    print("  4. 仅第三批（患者8,9,10）")
    print("  5. 试运行（仅显示命令）")

    mode = input("\n选择模式 (1-5): ").strip()

    # 确定要执行的批次
    batches_to_run = []
    dry_run = False

    if mode == '1':
        batches_to_run = PATIENT_BATCHES
    elif mode == '2':
        batches_to_run = [PATIENT_BATCHES[0]]
    elif mode == '3':
        batches_to_run = [PATIENT_BATCHES[1]]
    elif mode == '4':
        batches_to_run = [PATIENT_BATCHES[2]]
    elif mode == '5':
        batches_to_run = PATIENT_BATCHES
        dry_run = True
    else:
        print("无效选择，已取消")
        return

    # 记录执行结果
    results = []
    overall_start_time = time.time()

    # 执行每一批
    for i, batch in enumerate(batches_to_run, 1):
        print(f"\n{'='*80}")
        print(f"进度: {i}/{len(batches_to_run)}")
        print(f"{'='*80}")

        result = run_evaluation_for_batch(
            batch['name'],
            batch['patients'],
            dry_run=dry_run
        )
        results.append(result)

        # 如果失败，询问是否继续
        if result['status'] == 'failed':
            choice = input("\n批次执行失败，是否继续下一批？(y/n): ")
            if choice.lower() != 'y':
                print("已停止执行")
                break

        # 如果被中断，停止
        if result['status'] == 'interrupted':
            print("执行已中断")
            break

        # 批次间等待
        if i < len(batches_to_run) and not dry_run:
            wait_time = 5
            print(f"\n等待 {wait_time} 秒后执行下一批...")
            time.sleep(wait_time)

    # 总结
    overall_duration = time.time() - overall_start_time

    print("\n" + "="*80)
    print("📊 执行总结")
    print("="*80 + "\n")

    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'failed')
    interrupted = sum(1 for r in results if r['status'] == 'interrupted')

    print(f"执行批次数: {len(results)}/{len(batches_to_run)}")
    print(f"成功: {successful}")
    print(f"失败: {failed}")
    print(f"中断: {interrupted}")
    print(f"总耗时: {overall_duration/60:.1f} 分钟")

    if not dry_run:
        print(f"\n详细结果:")
        for result in results:
            status_icon = {
                'success': '✅',
                'failed': '❌',
                'interrupted': '⚠️',
                'dry_run': '🔍'
            }.get(result['status'], '?')

            print(f"\n  {status_icon} {result['batch']}")
            print(f"     患者: {', '.join(result.get('patients', []))}")
            if result['status'] == 'success':
                print(f"     耗时: {result.get('duration', 0)/60:.1f} 分钟")
            elif result['status'] == 'failed':
                print(f"     错误: {result.get('error', '未知')}")

    print("\n" + "="*80)
    print("💡 下一步:")
    print("  1. 运行 python parse_raw_responses.py 解析原始响应")
    print("  2. 运行 python run_cross_evaluation.py --skip-evaluation 生成矩阵")
    print("="*80 + "\n")

    # 保存执行日志
    log_file = f"batch_evaluation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"分批次评估执行日志\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"总耗时: {overall_duration/60:.1f} 分钟\n\n")

        for result in results:
            f.write(f"\n{result['batch']}:\n")
            f.write(f"  状态: {result['status']}\n")
            f.write(f"  患者: {', '.join(result.get('patients', []))}\n")
            if 'duration' in result:
                f.write(f"  耗时: {result['duration']/60:.1f} 分钟\n")
            if 'error' in result:
                f.write(f"  错误: {result['error']}\n")

    print(f"📝 执行日志已保存: {log_file}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n\n程序错误: {e}")
        import traceback
        traceback.print_exc()
