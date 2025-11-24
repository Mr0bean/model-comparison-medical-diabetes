#!/usr/bin/env python3
import json
from pathlib import Path

results_dir = Path("output/cross_evaluation_results")
sample_files = list(results_dir.glob("患者1/*_aggregated.json"))[:3]

for f in sample_files:
    print(f"\n{'='*60}")
    print(f"文件: {f.name}")
    print('='*60)
    with open(f, 'r', encoding='utf-8') as file:
        data = json.load(file)
        print(f"总分: {data.get('总分', 'N/A')}")
        print(f"维度数: {len(data.get('维度评分', {}))}")
        for dim, score in data.get('维度评分', {}).items():
            print(f"  - {dim}: {score}")
