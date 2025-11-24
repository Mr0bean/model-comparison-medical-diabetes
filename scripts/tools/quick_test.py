"""
快速测试脚本 - 只测试1个患者、1个Prompt、1个模型
用于验证批量测试程序是否能正常工作
"""
from batch_model_test import BatchProcessor

def main():
    print("开始快速测试...")
    print("配置：1个患者 × 1个Prompt × 2个模型（并发测试）")
    print("-" * 60)

    # 测试2个模型验证并发功能
    processor = BatchProcessor(
        prompt_file="多个Prompt",
        patients_dir="测试输入问答记录",
        models=["qwen/qwen3-next-80b-a3b-instruct", "claude-haiku-4-5-20251001"],  # 测试2个模型
        output_file="quick_test_result.json",
        concurrent=True,  # 启用并发
        max_workers=2  # 2个并发worker
    )

    # 只测试第一个患者和第一个Prompt
    if processor.patient_records and processor.prompt_manager.prompts:
        # 临时修改为只处理第一个
        processor.patient_records = processor.patient_records[:1]
        processor.prompt_manager.prompts = processor.prompt_manager.prompts[:1]

        print(f"患者: {processor.patient_records[0].patient_id}")
        print(f"Prompt: {processor.prompt_manager.prompts[0][:50]}...")
        print("-" * 60)

        processor.run()
    else:
        print("错误：没有找到患者记录或Prompt")

if __name__ == "__main__":
    main()
