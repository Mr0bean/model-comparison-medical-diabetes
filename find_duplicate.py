#!/usr/bin/env python3
from pathlib import Path
from collections import Counter

patient1_dir = Path("output/cross_evaluation_results/患者1")
accuracy_files = list(patient1_dir.glob("*_准确性.json"))

print(f"准确性维度文件数: {len(accuracy_files)}")

# 提取模型对
model_pairs = []
for f in accuracy_files:
    parts = f.stem.replace("_患者1_准确性", "").split("_by_")
    if len(parts) == 2:
        evaluated, evaluator = parts
        model_pairs.append((evaluated, evaluator))

# 找出重复
counter = Counter(model_pairs)
duplicates = [(pair, count) for pair, count in counter.items() if count > 1]

if duplicates:
    print(f"\n发现{len(duplicates)}对重复的模型评测:")
    for (evaluated, evaluator), count in duplicates:
        print(f"  {evaluated} by {evaluator}: {count}次")
        # 列出具体文件
        pattern = f"{evaluated}_by_{evaluator}_患者1_准确性.json"
        files = list(patient1_dir.glob(pattern))
        for f in files:
            print(f"    - {f.name} ({f.stat().st_size} bytes, {f.stat().st_mtime})")
else:
    print("\n未找到完全重复的文件名")
    print("\n所有模型对:")
    all_models = ["Baichuan-M2", "deepseek_deepseek-v3.1", "doubao-seed-1-6-251015",
                  "gemini-3-pro-preview", "gpt-5.1", "grok-4-0709",
                  "moonshotai_kimi-k2-0905", "qwen3-max"]
    
    missing = []
    for evaluated in all_models:
        for evaluator in all_models:
            if (evaluated, evaluator) not in model_pairs:
                missing.append(f"{evaluated} by {evaluator}")
    
    if missing:
        print(f"\n缺失的模型对 ({len(missing)}个):")
        for m in missing:
            print(f"  - {m}")
    
    print(f"\n实际有 {len(model_pairs)} 对，预期 {len(all_models)**2} 对")
