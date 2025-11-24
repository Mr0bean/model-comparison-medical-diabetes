"""
从JSON结果文件中提取result字段,保存为Markdown文件
输入: ./output/raw/*.json
输出: ./output/markdown/{model}-{people}.md
"""
import json
import os
from pathlib import Path
from typing import Dict


def extract_results_to_markdown(
    input_dir: str = "./output/raw",
    output_dir: str = "./output/markdown"
):
    """
    提取所有结果文件的result字段,保存为Markdown

    Args:
        input_dir: 输入JSON文件目录
        output_dir: 输出Markdown文件目录
    """
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    input_path = Path(input_dir)

    print(f"正在扫描目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print()

    processed_count = 0

    # 遍历所有JSON文件
    for json_file in sorted(input_path.glob("*.json")):
        print(f"  处理: {json_file.name}")

        # 读取JSON
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 提取信息
        model = data.get('model', 'unknown')
        people = data.get('people', 'unknown')
        result = data.get('result', '')

        # 构建Markdown内容
        markdown_content = f"""# {model} - {people}

---

{result}
"""

        # 生成Markdown文件名 (与JSON文件名一致,只是后缀不同)
        markdown_filename = json_file.stem + ".md"
        markdown_filepath = output_path / markdown_filename

        # 写入Markdown文件
        with open(markdown_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        print(f"    ✓ 已保存: {markdown_filename}")
        processed_count += 1

    print()
    print(f"✅ 完成! 共处理 {processed_count} 个文件")
    print(f"   Markdown文件保存在: {output_dir}/")


def main():
    print("=" * 80)
    print("提取Result到Markdown")
    print("=" * 80)
    print()

    extract_results_to_markdown(
        input_dir="./output/raw",
        output_dir="./output/markdown"
    )

    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
