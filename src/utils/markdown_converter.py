"""
将 output/raw/ 中的 JSON 文件转换为 Markdown 格式
保持原有的文件结构，每个 JSON 对应一个 Markdown 文件
"""
import json
import os
from pathlib import Path


def extract_conversation_title(prompt):
    """从 prompt 中提取对话类型作为标题"""
    # 优先检查总结类型，避免被"主诉"误判
    if "预问诊情况总结" in prompt or ("总结" in prompt and "模板" not in prompt):
        return "医疗总结"
    elif "现病史" in prompt:
        return "现病史"
    elif "既往史" in prompt or "即往史" in prompt:
        return "既往史"
    elif "家族史" in prompt:
        return "家族史"
    elif "主诉" in prompt:
        return "主诉"
    else:
        return "其他"


def convert_json_to_markdown(json_file_path, output_dir):
    """将单个 JSON 文件转换为 Markdown"""
    try:
        # 读取 JSON 文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        model = data.get("model", "未知模型")
        people = data.get("people", "未知患者")
        conversations = data.get("conversations", {})

        # 创建 Markdown 内容
        md_content = f"# {model} - {people}\n\n"
        md_content += f"**模型**: {model}  \n"
        md_content += f"**患者**: {people}\n\n"
        md_content += "---\n\n"

        # 按对话 ID 排序
        sorted_conversations = sorted(conversations.items(), key=lambda x: int(x[0]))

        for conv_id, conv in sorted_conversations:
            conv_output = conv.get("Output", "")
            conv_prompt = conv.get("prompt", "")

            # 提取标题
            title = extract_conversation_title(conv_prompt)

            md_content += f"## {title} (对话 {conv_id})\n\n"
            md_content += f"{conv_output}\n\n"
            md_content += "---\n\n"

        # 生成输出文件名（保持原文件名，只改扩展名）
        output_filename = json_file_path.stem + ".md"
        output_file = output_dir / output_filename

        # 写入 Markdown 文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"✓ {json_file_path.name} -> {output_filename}")
        return True

    except Exception as e:
        print(f"✗ 转换失败 {json_file_path.name}: {e}")
        return False


def main():
    """主函数"""
    # 定义路径
    input_dir = Path("output/raw")
    output_dir = Path("output/markdown")

    print("\n" + "="*60)
    print("JSON 转 Markdown 工具")
    print("保持原有文件结构")
    print("="*60 + "\n")

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取所有 JSON 文件
    json_files = list(input_dir.glob("*.json"))
    total_files = len(json_files)

    print(f"找到 {total_files} 个 JSON 文件\n")
    print("开始转换...\n")

    # 转换每个文件
    success_count = 0
    for json_file in sorted(json_files):
        if convert_json_to_markdown(json_file, output_dir):
            success_count += 1

    print("\n" + "="*60)
    print(f"转换完成！")
    print(f"  成功: {success_count}/{total_files}")
    print(f"  输出目录: {output_dir}/")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
