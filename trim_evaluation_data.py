#!/usr/bin/env python3
"""
批量处理评测数据文件，只保留前4个对话
"""
import json
import os
from pathlib import Path

def trim_evaluation_file(file_path):
    """
    处理单个评测文件，只保留前4个对话

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
    original_count = len(conversations)

    # 如果conversations是字典格式（索引为key）
    if isinstance(conversations, dict):
        # 只保留前4个
        keys_to_keep = ['1', '2', '3', '4']
        new_conversations = {k: v for k, v in conversations.items() if k in keys_to_keep}

        if len(new_conversations) == 0:
            print(f"  跳过: 没有找到索引1-4的对话")
            return

        # 更新conversations
        data['conversations'] = new_conversations

        # 更新result字段（如果存在）
        if 'result' in data:
            outputs = [new_conversations[k]['Output'] for k in sorted(new_conversations.keys())]
            data['result'] = '\\n'.join(outputs)

        print(f"  已处理: {original_count} -> {len(new_conversations)} 个对话")

        # 保存文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"  已保存")

    elif isinstance(conversations, list):
        # 如果是列表格式，只保留前4个
        new_conversations = conversations[:4]
        data['conversations'] = new_conversations

        # 更新result字段
        if 'result' in data:
            outputs = [conv['Output'] for conv in new_conversations]
            data['result'] = '\\n'.join(outputs)

        print(f"  已处理: {original_count} -> {len(new_conversations)} 个对话")

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

    # 排除gemini-3-pro-preview的文件（这些已经只有4个对话）
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
            trim_evaluation_file(file_path)
        except Exception as e:
            print(f"  错误: {e}")
        print()

    print("处理完成！")

if __name__ == "__main__":
    main()
