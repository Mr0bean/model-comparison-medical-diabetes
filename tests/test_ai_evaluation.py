#!/usr/bin/env python3
"""
测试AI自动评测功能
演示如何使用deepseek-reasoner对病历摘要进行自动评分
"""

import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 示例数据
SAMPLE_CONVERSATION = """
医生：您好，请问您有什么不舒服吗？
患者：医生您好，我最近总是感觉口渴，喝水特别多，而且上厕所也很频繁。
医生：这种情况持续多久了？
患者：大概有3个月了。
医生：之前有检查过血糖吗？
患者：去年10月体检的时候查过，空腹血糖是7.2，医生说有点高。
医生：那当时有开始治疗吗？
患者：没有，医生说让我先控制饮食，多运动。但我工作太忙，一直没怎么注意。
医生：您现在有在吃什么药吗？
患者：没有吃药。
医生：家里有人得糖尿病吗？
患者：我爸爸有糖尿病，已经吃药10多年了。
医生：您有高血压吗？
患者：有的，3年前查出来的，现在在吃降压药。
医生：血压控制得怎么样？
患者：还可以，一般是130/85左右。
医生：好的，我给您测一下血糖。
患者：好的。
医生：您的随机血糖是12.5，确实偏高了。我建议您做一个详细的检查，包括糖化血红蛋白和其他指标。
患者：好的，那我需要吃药吗？
医生：根据您的情况，可能需要开始药物治疗。我先给您开二甲双胍，从小剂量开始，500mg每天两次，早晚饭后服用。
患者：好的，谢谢医生。
"""

SAMPLE_MEDICAL_RECORD_GOOD = """
主诉：口渴、多饮、多尿3个月

现病史：患者3个月前无明显诱因出现口渴、多饮、多尿症状。去年10月体检发现空腹血糖7.2mmol/L，医生建议控制饮食和运动，患者未予重视，未进行药物治疗。近期上述症状持续存在。今日就诊，随机血糖12.5mmol/L，拟诊断为糖尿病。现予二甲双胍片500mg每日2次早晚餐后口服治疗。

既往史：3年前诊断高血压，目前口服降压药治疗，血压控制在130/85mmHg左右。否认冠心病、高血脂病史。

家族史：父亲患2型糖尿病10余年，药物治疗中。

个人史：工作繁忙，缺乏运动。否认吸烟、饮酒史。
"""

SAMPLE_MEDICAL_RECORD_BAD = """
主诉：口渴、尿多3个月

现病史：患者3个月前开始口渴，喝水多，上厕所次数增加。去年体检血糖7.2，有点高。最近还是这样。今天来看病，血糖12.5。医生开了二甲双胍，一天两次。

既往史：高血压3年，糖尿病去年发现。吃降压药，血压130/85。

家族史：爸爸有糖尿病，吃药很多年了。

个人史：工作忙，没时间运动。
"""


def test_evaluation():
    """测试AI评测功能"""
    print("=" * 60)
    print("AI病历评测系统测试")
    print("=" * 60)

    # 检查环境配置
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ DEEPSEEK_API_KEY 未设置")
        print("请在 .env 文件中配置 DEEPSEEK_API_KEY")
        return

    print("✅ DeepSeek API已配置\n")

    try:
        # 导入评测配置
        from config.ai_evaluation_prompt import (
            EVALUATION_SYSTEM_MESSAGE,
            FULL_EVALUATION_PROMPT,
            score_to_stars
        )
        from cross_evaluation.model_client_factory import ModelClientFactory

        print("✅ 评测模块加载成功\n")

        # 创建评测客户端
        print("创建评测客户端（deepseek-reasoner）...")
        factory = ModelClientFactory('.')
        evaluator = factory.create_client('deepseek-reasoner')
        print("✅ 评测客户端创建成功\n")

        # 测试1：评测优质病历
        print("=" * 60)
        print("测试1: 评测优质病历摘要")
        print("=" * 60)

        prompt1 = FULL_EVALUATION_PROMPT.format(
            conversation=SAMPLE_CONVERSATION,
            medical_record=SAMPLE_MEDICAL_RECORD_GOOD
        )

        print("正在调用AI评测...")
        response1 = evaluator.chat_completion(
            prompt=prompt1,
            system_message=EVALUATION_SYSTEM_MESSAGE,
            max_tokens=2000,
            temperature=0.3
        )

        # 解析结果
        try:
            # 提取JSON部分
            json_start = response1.find('{')
            json_end = response1.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response1[json_start:json_end]
                result1 = json.loads(json_str)

                print("\n✅ 评测完成！结果如下：\n")
                print(f"准确性：{result1['accuracy']['score']}/40 (⭐ {result1['accuracy']['stars']}星)")
                print(f"  评语：{result1['accuracy']['comment']}")

                print(f"\n完整性：{result1['completeness']['score']}/35 (⭐ {result1['completeness']['stars']}星)")
                print(f"  评语：{result1['completeness']['comment']}")

                print(f"\n规范性：{result1['standardization']['score']}/25 (⭐ {result1['standardization']['stars']}星)")
                print(f"  评语：{result1['standardization']['comment']}")

                print(f"\n📊 总分：{result1['total_score']}/100")
                print(f"📝 总评：{result1['overall_comment']}")

            else:
                print("⚠️  无法解析JSON格式")
                print("原始响应：", response1)
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败：{e}")
            print("原始响应：", response1)

        # 测试2：评测问题病历
        print("\n" + "=" * 60)
        print("测试2: 评测问题病历摘要")
        print("=" * 60)

        prompt2 = FULL_EVALUATION_PROMPT.format(
            conversation=SAMPLE_CONVERSATION,
            medical_record=SAMPLE_MEDICAL_RECORD_BAD
        )

        print("正在调用AI评测...")
        response2 = evaluator.chat_completion(
            prompt=prompt2,
            system_message=EVALUATION_SYSTEM_MESSAGE,
            max_tokens=2000,
            temperature=0.3
        )

        # 解析结果
        try:
            json_start = response2.find('{')
            json_end = response2.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response2[json_start:json_end]
                result2 = json.loads(json_str)

                print("\n✅ 评测完成！结果如下：\n")
                print(f"准确性：{result2['accuracy']['score']}/40 (⭐ {result2['accuracy']['stars']}星)")
                print(f"  评语：{result2['accuracy']['comment']}")

                if result2['accuracy'].get('deductions'):
                    print("  扣分项：")
                    for deduction in result2['accuracy']['deductions']:
                        print(f"    - {deduction['item']}：-{deduction['points']}分 ({deduction['reason']})")

                print(f"\n完整性：{result2['completeness']['score']}/35 (⭐ {result2['completeness']['stars']}星)")
                print(f"  评语：{result2['completeness']['comment']}")

                if result2['completeness'].get('missing_modules'):
                    print(f"  缺失模块：{', '.join(result2['completeness']['missing_modules'])}")

                print(f"\n规范性：{result2['standardization']['score']}/25 (⭐ {result2['standardization']['stars']}星)")
                print(f"  评语：{result2['standardization']['comment']}")

                if result2['standardization'].get('issues'):
                    print(f"  问题项：{', '.join(result2['standardization']['issues'])}")

                print(f"\n📊 总分：{result2['total_score']}/100")
                print(f"📝 总评：{result2['overall_comment']}")

            else:
                print("⚠️  无法解析JSON格式")
                print("原始响应：", response2)
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败：{e}")
            print("原始响应：", response2)

        # 对比分析
        print("\n" + "=" * 60)
        print("对比分析")
        print("=" * 60)
        print("优质病历 vs 问题病历：")
        try:
            if 'result1' in locals() and 'result2' in locals():
                print(f"总分差距：{result1['total_score'] - result2['total_score']}分")
                print(f"准确性差距：{result1['accuracy']['score'] - result2['accuracy']['score']}分")
                print(f"完整性差距：{result1['completeness']['score'] - result2['completeness']['score']}分")
                print(f"规范性差距：{result1['standardization']['score'] - result2['standardization']['score']}分")
        except:
            print("无法进行对比分析")

    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_evaluation()
