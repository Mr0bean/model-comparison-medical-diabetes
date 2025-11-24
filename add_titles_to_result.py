#!/usr/bin/env python3
"""
为评测数据的result字段添加中英文双语标题
"""
import json
from pathlib import Path

# 标题映射（中英文双语）
TITLE_MAPPING = {
    '1': '## 主诉 Chief Complaint',
    '2': '## 现病史 Present Illness History',
    '3': '## 既往史 Past Medical History',
    '4': '## 家族史 Family History'
}

def add_titles_to_result(file_path):
    """
    为单个评测文件的result字段添加标题

    Args:
        file_path: 评测文件路径
    """
    print(f"处理文件: {file_path.name}")

    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 检查必要字段
    if 'conversations' not in data:
        print(f"  跳过: 没有conversations字段")
        return

    conversations = data['conversations']

    # 构建带标题的result
    result_parts = []
    for i in ['1', '2', '3', '4']:
        if i not in conversations:
            print(f"  警告: 缺少对话{i}")
            continue

        # 获取标题
        title = TITLE_MAPPING[i]

        # 获取输出内容
        output = conversations[i].get('Output', '')

        # 组合标题和内容
        result_parts.append(f"{title}\n{output}")

    # 用两个换行符分隔各部分
    new_result = '\n\n'.join(result_parts)

    # 更新result字段
    data['result'] = new_result

    # 保存文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"  已完成: 添加了{len(result_parts)}个标题")

def main():
    """主函数"""
    output_dir = Path("./output/raw")

    if not output_dir.exists():
        print(f"错误: 输出目录不存在: {output_dir}")
        return

    # 获取所有评测文件
    json_files = list(output_dir.glob("*.json"))

    print(f"找到 {len(json_files)} 个文件需要处理")
    print()

    # 处理每个文件
    success_count = 0
    for file_path in sorted(json_files):
        try:
            add_titles_to_result(file_path)
            success_count += 1
        except Exception as e:
            print(f"  错误: {e}")
        print()

    print(f"处理完成！成功处理 {success_count}/{len(json_files)} 个文件")

if __name__ == "__main__":
    main()
