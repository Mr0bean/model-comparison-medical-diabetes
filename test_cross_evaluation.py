#!/usr/bin/env python3
"""
交叉评测测试脚本
用于小规模测试系统是否正常工作
"""
import sys
import os
from pathlib import Path
import json

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 加载.env文件
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    print(f"加载环境变量文件: {env_file}")
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
    print("环境变量已加载")

from cross_evaluation.engine import engine

def test_small_scale():
    """小规模测试：2个模型 × 1个患者 × 1个维度"""

    print("=" * 60)
    print("开始小规模测试")
    print("=" * 60)

    # 只测试2个模型和1个患者
    test_models = ["gpt-5.1", "deepseek_deepseek-v3.1"]
    test_patients = ["患者1"]

    print(f"测试模型: {test_models}")
    print(f"测试患者: {test_patients}")
    print(f"预计生成: 2 × 2 × 1 × 6 = 24个文件")
    print("\n开始评测...")

    try:
        # 运行评测
        engine.run(
            models=test_models,
            patients=test_patients,
            resume=False
        )

        print("\n" + "=" * 60)
        print("测试完成！检查结果文件...")
        print("=" * 60)

        # 检查生成的文件
        output_dir = Path("output/cross_evaluation_results/患者1")
        if output_dir.exists():
            files = list(output_dir.glob("*.json"))
            print(f"\n生成了 {len(files)} 个文件：")

            # 显示第一个文件的内容示例
            if files:
                sample_file = files[0]
                print(f"\n示例文件: {sample_file.name}")
                print("-" * 60)

                with open(sample_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 显示关键字段
                print(f"source_llm: {data.get('source_llm', 'N/A')}")
                print(f"target_llm: {data.get('target_llm', 'N/A')}")
                print(f"dimension: {data.get('dimension', 'N/A')}")
                print(f"score: {data.get('score', 'N/A')}/{data.get('max_score', 'N/A')}")
                print(f"issues: {data.get('issues', 'N/A')[:100]}...")
                print(f"\nprompt_input前100字符: {data.get('prompt_input', 'N/A')[:100]}...")
                print(f"output前100字符: {data.get('output', 'N/A')[:100]}...")

    except Exception as e:
        print(f"\n测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_small_scale()
