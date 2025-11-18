"""
准备模型对比数据
将 markdown 文件转换为前端可用的 JSON 数据
"""
import json
import re
from pathlib import Path
from collections import defaultdict


def parse_markdown_file(md_file):
    """解析单个 Markdown 文件"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取标题中的模型和患者信息
    title_match = re.match(r'# (.+?) - (.+?)\n', content)
    if not title_match:
        return None

    model = title_match.group(1).strip()
    patient = title_match.group(2).strip()

    # 提取所有对话部分
    conversations = {}
    pattern = r'## (.+?) \(对话 (\d+)\)\n\n(.*?)(?=\n---|\Z)'

    for match in re.finditer(pattern, content, re.DOTALL):
        title = match.group(1).strip()
        conv_id = match.group(2).strip()
        output = match.group(3).strip()

        conversations[conv_id] = {
            "title": title,
            "output": output
        }

    return {
        "model": model,
        "patient": patient,
        "conversations": conversations
    }


def load_raw_conversations(raw_dir):
    """从raw目录加载原始对话数据"""
    conversations_map = {}
    raw_path = Path(raw_dir)

    for json_file in raw_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            model = data.get("model", "")
            patient = data.get("people", "")
            conversations = data.get("conversations", {})

            key = f"{model}-{patient}"
            conversations_map[key] = conversations
        except Exception as e:
            print(f"警告: 无法读取 {json_file}: {e}")

    return conversations_map


def organize_data_for_comparison(markdown_dir, raw_dir="output/raw"):
    """组织数据以便于对比"""
    # 数据结构: {patient: {conv_id: {model: output}}}
    comparison_data = defaultdict(lambda: defaultdict(dict))

    # 收集所有模型和患者信息
    all_models = set()
    all_patients = set()

    # 加载原始对话数据
    print(f"加载原始对话数据从: {raw_dir}")
    conversations_map = load_raw_conversations(raw_dir)
    print(f"  - 加载了 {len(conversations_map)} 个原始对话文件")

    markdown_path = Path(markdown_dir)

    for md_file in markdown_path.glob("*.md"):
        data = parse_markdown_file(md_file)
        if not data:
            continue

        model = data["model"]
        patient = data["patient"]
        all_models.add(model)
        all_patients.add(patient)

        # 获取原始对话数据
        conv_key = f"{model}-{patient}"
        raw_conversations = conversations_map.get(conv_key, {})

        for conv_id, conv_data in data["conversations"].items():
            # 从原始数据中获取对话内容
            raw_conv = raw_conversations.get(conv_id, {})
            chat_content = raw_conv.get("chat", "")

            comparison_data[patient][conv_id][model] = {
                "title": conv_data["title"],
                "output": conv_data["output"],
                "chat": chat_content  # 添加对话内容
            }

    return {
        "models": sorted(list(all_models)),
        "patients": sorted(list(all_patients), key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0),
        "data": dict(comparison_data)
    }


def main():
    """主函数"""
    print("\n" + "="*60)
    print("准备模型对比数据")
    print("="*60 + "\n")

    markdown_dir = "output/markdown"
    output_file = "output/comparison_data.json"

    print(f"读取目录: {markdown_dir}")

    # 组织数据
    comparison_data = organize_data_for_comparison(markdown_dir)

    print(f"\n找到:")
    print(f"  - 模型数量: {len(comparison_data['models'])}")
    print(f"  - 患者数量: {len(comparison_data['patients'])}")
    print(f"\n模型列表:")
    for model in comparison_data['models']:
        print(f"  - {model}")

    # 保存为 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 数据已保存到: {output_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
