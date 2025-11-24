#!/usr/bin/env python3
"""
重新组织评测数据：删除对话4（医疗总结），将对话5（家族史）改为对话4
"""
import json
import os
from pathlib import Path

def reorganize_evaluation_file(file_path):
    """
    重新组织单个评测文件
    - 删除对话4（医疗总结）
    - 将对话5（家族史）改为对话4
    - 只保留对话1,2,3,4

    Args:
        file_path: 评测文件路径
    """
    print(f"处理文件: {file_path}")

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查conversations字段
    if 'conversations' not in data:
        print(f"  跳过: 没有conversations字段")
        return

    conversations = data['conversations']

    # 检查是否有5个对话
    if not isinstance(conversations, dict):
        print(f"  跳过: conversations不是字典格式")
        return

    if '5' not in conversations:
        print(f"  跳过: 没有对话5，可能已经处理过")
        return

    # 创建新的conversations字典
    # 保留1,2,3，删除4，将5改为4
    new_conversations = {
        '1': conversations['1'],
        '2': conversations['2'],
        '3': conversations['3'],
        '4': conversations['5']  # 将原来的对话5改为对话4
    }

    # 更新conversations
    data['conversations'] = new_conversations

    # 更新result字段（如果存在）
    if 'result' in data:
        outputs = [new_conversations[k]['Output'] for k in ['1', '2', '3', '4']]
        data['result'] = '\n'.join(outputs)

    print(f"  已处理: 删除对话4（医疗总结），对话5（家族史）改为对话4")

    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"  已保存")

def main():
    """主函数"""
    output_dir = Path("./output/raw")

    if not output_dir.exists():
        print(f"错误: 输出目录不存在: {output_dir}")
        return

    # 获取所有评测文件
    json_files = list(output_dir.glob("*.json"))

    # 排除gemini-3-pro-preview的文件（这些已经是正确的4个对话）
    files_to_process = [
        f for f in json_files
        if 'gemini-3-pro-preview' not in f.name
    ]

    print(f"找到 {len(files_to_process)} 个文件需要处理")
    print(f"排除了 {len(json_files) - len(files_to_process)} 个 gemini-3-pro-preview 文件")
    print()

    # 处理每个文件
    for file_path in sorted(files_to_process):
        try:
            reorganize_evaluation_file(file_path)
        except Exception as e:
            print(f"  错误: {e}")
        print()

    print("处理完成！")

if __name__ == "__main__":
    main()
