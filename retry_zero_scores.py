#!/usr/bin/env python3
"""
自动重试所有零分评估的脚本
步骤:
1. 识别零分评估
2. 删除零分评估文件
3. 运行交叉评估重新生成
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime


def identify_zero_scores():
    """识别零分评估"""
    print("=" * 70)
    print("步骤 1/3: 识别零分评估")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, "identify_failed_evals.py"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("❌ 识别失败:")
        print(result.stderr)
        return False

    # 检查是否生成了重试列表
    if not Path("retry_zero_scores.json").exists():
        print("❌ 未生成重试列表文件")
        return False

    with open("retry_zero_scores.json", 'r', encoding='utf-8') as f:
        zero_evals = json.load(f)

    return len(zero_evals)


def delete_zero_score_files():
    """删除零分评估文件"""
    print()
    print("=" * 70)
    print("步骤 2/3: 删除零分评估文件")
    print("=" * 70)

    with open("retry_zero_scores.json", 'r', encoding='utf-8') as f:
        zero_evals = json.load(f)

    deleted_count = 0
    for item in zero_evals:
        file_path = Path(item['file'])
        if file_path.exists():
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"  ✓ 已删除: {item['patient']} - {item['model']} → {item['evaluator']}")
            except Exception as e:
                print(f"  ✗ 删除失败: {file_path} - {e}")

    print(f"\n✅ 已删除 {deleted_count} 个零分评估文件")
    return deleted_count


def run_cross_evaluation():
    """运行交叉评估"""
    print()
    print("=" * 70)
    print("步骤 3/3: 运行交叉评估 (仅重试删除的文件)")
    print("=" * 70)
    print()

    # 生成日志文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"retry_zero_scores_{timestamp}.log"

    print(f"📝 日志文件: {log_file}")
    print()
    print("⏳ 开始评估... (这可能需要一些时间)")
    print()

    # 运行评估并实时显示输出
    with open(log_file, 'w', encoding='utf-8') as log_f:
        process = subprocess.Popen(
            [sys.executable, "run_cross_evaluation.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 实时显示输出并写入日志
        for line in process.stdout:
            print(line, end='')
            log_f.write(line)

        process.wait()

        if process.returncode == 0:
            print()
            print("✅ 交叉评估完成")
            return True
        else:
            print()
            print(f"❌ 交叉评估失败 (返回码: {process.returncode})")
            return False


def verify_results():
    """验证结果"""
    print()
    print("=" * 70)
    print("验证结果")
    print("=" * 70)

    base_dir = Path("output/cross_evaluation_results")
    total_evals = 0
    zero_scores = 0

    for patient_dir in sorted(base_dir.glob("患者*")):
        eval_dir = patient_dir / "evaluations"
        if not eval_dir.exists():
            continue

        for eval_file in eval_dir.glob("*.json"):
            try:
                with open(eval_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                total_evals += 1
                if data.get('average_score', -1) == 0.0:
                    zero_scores += 1
            except:
                pass

    print(f"总评估数: {total_evals}")
    print(f"零分评估: {zero_scores}")
    print(f"有效评估: {total_evals - zero_scores}")
    print()

    if zero_scores == 0:
        print("🎉🎉🎉 完美! 所有评估都有有效分数! 🎉🎉🎉")
        return True
    else:
        print(f"⚠️  仍有 {zero_scores} 个零分评估")
        return False


def main():
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 20 + "零分评估自动重试系统" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

    # 步骤1: 识别
    zero_count = identify_zero_scores()
    if not zero_count:
        print("❌ 识别失败，退出")
        return

    if zero_count == 0:
        print("✅ 没有零分评估，无需重试")
        return

    print()
    print(f"发现 {zero_count} 个零分评估需要重试")
    print()

    # 步骤2: 删除
    deleted = delete_zero_score_files()
    if deleted == 0:
        print("❌ 未删除任何文件，退出")
        return

    # 步骤3: 重新评估
    success = run_cross_evaluation()
    if not success:
        print()
        print("❌ 重试失败，请检查日志")
        return

    # 步骤4: 验证
    all_valid = verify_results()

    print()
    print("=" * 70)
    if all_valid:
        print("✨ 重试完成! 所有640个评估都有有效分数!")
    else:
        print("⚠️  重试完成，但仍有部分评估为零分")
        print("   可能需要再次运行此脚本")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
