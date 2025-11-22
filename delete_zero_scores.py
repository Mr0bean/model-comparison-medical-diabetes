#!/usr/bin/env python3
"""删除所有零分评估文件以便重试"""

import json
import os
from pathlib import Path

def delete_zero_score_files():
    """删除所有average_score=0.0的评估文件"""

    # 加载重试列表
    retry_list_file = "retry_zero_scores.json"
    if not Path(retry_list_file).exists():
        print(f"❌ 错误: 未找到 {retry_list_file}")
        print("   请先运行 identify_failed_evals.py")
        return

    with open(retry_list_file, 'r', encoding='utf-8') as f:
        zero_evals = json.load(f)

    print("=" * 60)
    print(f"准备删除 {len(zero_evals)} 个零分评估文件")
    print("=" * 60)
    print()

    deleted_count = 0
    not_found_count = 0

    for item in zero_evals:
        file_path = Path(item['file'])

        if file_path.exists():
            try:
                os.remove(file_path)
                deleted_count += 1
                print(f"✓ 已删除: {item['patient']} - {item['model']} → {item['evaluator']}")
            except Exception as e:
                print(f"✗ 删除失败: {file_path} - {e}")
        else:
            not_found_count += 1
            print(f"⚠️  文件不存在: {file_path}")

    print()
    print("=" * 60)
    print("删除完成")
    print("=" * 60)
    print(f"已删除: {deleted_count}")
    print(f"未找到: {not_found_count}")
    print()
    print("💡 下一步: 运行交叉评估脚本重新生成这些评估")
    print()

if __name__ == "__main__":
    # 安全确认
    print()
    print("⚠️  警告: 此操作将删除80个零分评估文件!")
    print("   (原始raw响应文件将保留)")
    print()

    response = input("确认删除? (yes/no): ").strip().lower()

    if response == "yes":
        delete_zero_score_files()
    else:
        print("操作已取消")
