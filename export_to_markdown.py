#!/usr/bin/env python3
"""
将评测数据的result字段导出为Markdown文件
"""
import json
from pathlib import Path

def export_to_markdown(json_file, output_dir):
    """
    将单个JSON文件的result字段导出为Markdown文件

    Args:
        json_file: JSON文件路径
        output_dir: 输出目录
    """
    print(f"处理文件: {json_file.name}")

    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 获取result字段
    result = data.get('result', '')

    if not result:
        print(f"  警告: result字段为空")
        return

    # 生成Markdown文件名（保持原文件名，只改扩展名）
    md_filename = json_file.stem + '.md'
    md_filepath = output_dir / md_filename

    # 直接使用result内容，不添加额外描述
    markdown_content = result

    # 写入Markdown文件
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    print(f"  已导出: {md_filename}")

def main():
    """主函数"""
    # 输入和输出目录
    input_dir = Path("./output/raw")
    output_dir = Path("./output/markdown/raw")

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {output_dir}")
    print()

    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        return

    # 获取所有JSON文件
    json_files = list(input_dir.glob("*.json"))
    print(f"找到 {len(json_files)} 个JSON文件")
    print()

    # 处理每个文件
    success_count = 0
    for json_file in sorted(json_files):
        try:
            export_to_markdown(json_file, output_dir)
            success_count += 1
        except Exception as e:
            print(f"  错误: {e}")

    print()
    print(f"导出完成！成功导出 {success_count}/{len(json_files)} 个Markdown文件")
    print(f"文件保存位置: {output_dir.absolute()}")

if __name__ == "__main__":
    main()
