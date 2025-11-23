"""
AI评测Prompt配置
用于自动评测AI生成的病历摘要质量
"""

# 评测系统消息
EVALUATION_SYSTEM_MESSAGE = """你是一位专业的医疗病历质量评测专家，负责评估AI生成的病历摘要质量。

你的任务是严格按照评分标准，对病历摘要的准确性、完整性和规范性进行客观评分。

评分体系：
- 准确性（40分）：病历内容与对话是否完全一致
- 完整性（35分）：是否包含所有必要的病历模块
- 规范性（25分）：是否符合医学书写规范
- 总分（100分）：三个维度分数相加

请保持客观公正，严格执行评分标准。"""

# 完整评测Prompt模板
FULL_EVALUATION_PROMPT = """
【评测任务】
请根据以下原始医患对话记录和AI生成的病历摘要，按照三个维度进行详细评分。

【原始医患对话】
{conversation}

【AI生成的病历摘要】
{medical_record}

【评分标准】

一、准确性维度（40分）

1. 数值准确性（最高扣8分）
   - 血糖、糖化、体重、血压等数值
   - 数值错误每处扣2分，单位错误扣1分

2. 药物信息（最高扣10分）
   - 药名错误每处扣3分
   - 剂量错误每处扣2分
   - 用法错误每处扣1.5分

3. 时间信息（最高扣8分）
   - 发病时间、就诊时间、病程
   - 每处错误扣2分

4. 诊断信息（最高扣8分）
   - 诊断类型、并发症、合并症
   - 每处错误扣3分

5. 病程描述（最高扣6分）
   - 病情发展、治疗调整、症状变化
   - 事实性错误每处扣2分

6. 固定扣分项
   - ⚠️ 将糖尿病写入既往史：直接扣10分

准确性评分 = 40 - 总扣分

二、完整性维度（35分）

必备模块检查：
1. 主诉（7分）：症状 + 时间
   - 缺少症状扣4分，缺少时间扣3分

2. 现病史（14分）
   - 初次诊断（3分）
   - 治疗历程（4分）
   - 近期病情（4分）
   - 并发症（3分）

3. 既往史（7分）
   - 高血压（2分）
   - 高血脂（2分）
   - 冠心病（2分）
   - 其他慢性病（1分）
   - ⚠️ 不得包含糖尿病

4. 家族史（4分）
   - 糖尿病家族史（3分）
   - 其他相关（1分）

5. 个人史（3分，可选）
   - 对话中提及但未记录扣1-2分

完整性评分 = 35 - 总扣分

三、规范性维度（25分）

1. 医学术语（8分）
   - 口语化每处扣1分，术语错误扣2分
   - 规范示例：多饮、多尿、视物模糊
   - 不规范示例：口渴、尿多、看不清

2. 结构规范（7分）
   - 顺序错误扣2分，结构混乱扣3分
   - 标准顺序：主诉→现病史→既往史→家族史→个人史

3. 药物书写（5分）
   - 每处不规范扣1分
   - 规范格式：药名 剂量 频率 方式

4. 时间表述（3分）
   - 不明确每处扣1分

5. 整体专业性（2分）
   - 不够专业扣1-2分

规范性评分 = 25 - 总扣分

【输出要求】

请严格按照以下JSON格式输出评分结果（不要有任何额外文字）：

```json
{{
  "accuracy": {{
    "score": <0-40之间的分数>,
    "stars": <1-5星级>,
    "deductions": [
      {{"item": "扣分项名称", "points": <扣分>, "reason": "扣分原因"}}
    ],
    "comment": "准确性评语（100字以内）"
  }},
  "completeness": {{
    "score": <0-35之间的分数>,
    "stars": <1-5星级>,
    "missing_modules": ["缺失的模块"],
    "incomplete_parts": ["不完整的部分"],
    "comment": "完整性评语（100字以内）"
  }},
  "standardization": {{
    "score": <0-25之间的分数>,
    "stars": <1-5星级>,
    "issues": ["不规范之处"],
    "comment": "规范性评语（100字以内）"
  }},
  "total_score": <0-100之间的总分>,
  "overall_comment": "总体评价（200字以内）"
}}
```

【评分步骤】
1. 仔细阅读原始对话和病历摘要
2. 逐项检查准确性、完整性、规范性
3. 列出所有扣分项及理由
4. 计算各维度得分
5. 转换为星级（5星40/35/25，4星32/28/20，3星24/21/15，2星16/14/10，1星8/7/5）
6. 输出JSON格式结果

请开始评测。
"""

# 简化版评测Prompt（用于快速评测）
QUICK_EVALUATION_PROMPT = """
请评测以下AI生成的病历摘要质量，对比原始对话记录。

【对话记录】
{conversation}

【病历摘要】
{medical_record}

【评分要求】
1. 准确性（40分）：内容与对话是否一致，数值、药物、时间、诊断是否准确。⚠️ 糖尿病写入既往史扣10分
2. 完整性（35分）：是否包含主诉、现病史、既往史、家族史等模块
3. 规范性（25分）：医学术语是否规范，结构是否清晰

输出JSON格式评分结果：
```json
{{
  "accuracy": {{"score": 0-40, "stars": 1-5, "comment": "评语"}},
  "completeness": {{"score": 0-35, "stars": 1-5, "comment": "评语"}},
  "standardization": {{"score": 0-25, "stars": 1-5, "comment": "评语"}},
  "total_score": 0-100,
  "overall_comment": "总评"
}}
```
"""

# 准确性专项评测Prompt
ACCURACY_EVALUATION_PROMPT = """
请专门评估病历摘要的准确性（满分40分）。

【对话记录】
{conversation}

【病历摘要】
{medical_record}

【检查项目】
1. 所有数值（血糖、糖化、体重等）是否准确
2. 药物名称、剂量、用法是否准确
3. 时间信息（发病时间、就诊时间）是否准确
4. 诊断和并发症是否准确
5. 病程描述是否符合对话内容
6. ⚠️ 是否将糖尿病错误写入既往史

【扣分规则】
- 数值错误：每处-2分
- 药名错误：每处-3分
- 剂量错误：每处-2分
- 时间错误：每处-2分
- 诊断错误：每处-3分
- 事实错误：每处-2分
- 糖尿病写入既往史：-10分

输出格式：
```json
{{
  "score": 0-40,
  "stars": 1-5,
  "errors": [
    {{"type": "错误类型", "content": "错误内容", "deduction": 扣分}}
  ],
  "comment": "准确性评价"
}}
```
"""

# 完整性专项评测Prompt
COMPLETENESS_EVALUATION_PROMPT = """
请专门评估病历摘要的完整性（满分35分）。

【对话记录】
{conversation}

【病历摘要】
{medical_record}

【必备模块检查】
1. 主诉（7分）：是否包含症状+时间
2. 现病史（14分）：
   - 初次诊断情况（3分）
   - 治疗历程（4分）
   - 近期病情（4分）
   - 并发症（3分）
3. 既往史（7分）：高血压、高血脂、冠心病等（⚠️ 不得包含糖尿病）
4. 家族史（4分）：糖尿病家族史等
5. 个人史（3分）：对话中提到的生活习惯

输出格式：
```json
{{
  "score": 0-35,
  "stars": 1-5,
  "missing_modules": ["缺失模块"],
  "incomplete_parts": ["不完整部分"],
  "module_scores": {{
    "chief_complaint": 0-7,
    "present_illness": 0-14,
    "past_history": 0-7,
    "family_history": 0-4,
    "personal_history": 0-3
  }},
  "comment": "完整性评价"
}}
```
"""

# 规范性专项评测Prompt
STANDARDIZATION_EVALUATION_PROMPT = """
请专门评估病历摘要的规范性（满分25分）。

【病历摘要】
{medical_record}

【评估要点】
1. 医学术语（8分）：是否使用规范术语，避免口语化
   - 规范：多饮、多尿、视物模糊
   - 不规范：口渴、尿多、看不清

2. 结构规范（7分）：
   - 模块顺序：主诉→现病史→既往史→家族史→个人史
   - 层次清晰，逻辑连贯

3. 药物书写（5分）：
   - 格式：药名 + 剂量 + 频率 + 方式
   - 示例：二甲双胍片 500mg 每日2次 餐后口服

4. 时间表述（3分）：
   - 明确具体：3年前、近6个月
   - 避免模糊：很久、最近

5. 整体专业性（2分）：语言简洁专业

输出格式：
```json
{{
  "score": 0-25,
  "stars": 1-5,
  "terminology_issues": ["术语问题"],
  "structure_issues": ["结构问题"],
  "format_issues": ["格式问题"],
  "comment": "规范性评价"
}}
```
"""

# 星级转换映射
SCORE_TO_STARS_MAPPING = {
    "accuracy": {  # 40分制
        (38, 40): 5,
        (32, 37): 4,
        (24, 31): 3,
        (16, 23): 2,
        (0, 15): 1
    },
    "completeness": {  # 35分制
        (34, 35): 5,
        (28, 33): 4,
        (21, 27): 3,
        (14, 20): 2,
        (0, 13): 1
    },
    "standardization": {  # 25分制
        (24, 25): 5,
        (20, 23): 4,
        (15, 19): 3,
        (10, 14): 2,
        (0, 9): 1
    }
}

def score_to_stars(dimension: str, score: int) -> int:
    """
    将分数转换为星级

    Args:
        dimension: 维度名称（accuracy/completeness/standardization）
        score: 分数

    Returns:
        星级（1-5）
    """
    if dimension not in SCORE_TO_STARS_MAPPING:
        raise ValueError(f"Invalid dimension: {dimension}")

    mapping = SCORE_TO_STARS_MAPPING[dimension]
    for (min_score, max_score), stars in mapping.items():
        if min_score <= score <= max_score:
            return stars

    return 1  # 默认返回1星


def stars_to_score(dimension: str, stars: int) -> int:
    """
    将星级转换为分数（取中间值）

    Args:
        dimension: 维度名称
        stars: 星级（1-5）

    Returns:
        对应分数
    """
    if dimension == "accuracy":
        return [8, 16, 24, 32, 40][stars - 1]
    elif dimension == "completeness":
        return [7, 14, 21, 28, 35][stars - 1]
    elif dimension == "standardization":
        return [5, 10, 15, 20, 25][stars - 1]
    else:
        raise ValueError(f"Invalid dimension: {dimension}")


# 评测结果模板
EVALUATION_RESULT_TEMPLATE = {
    "accuracy": {
        "score": 0,
        "stars": 1,
        "deductions": [],
        "comment": ""
    },
    "completeness": {
        "score": 0,
        "stars": 1,
        "missing_modules": [],
        "incomplete_parts": [],
        "comment": ""
    },
    "standardization": {
        "score": 0,
        "stars": 1,
        "issues": [],
        "comment": ""
    },
    "total_score": 0,
    "overall_comment": ""
}


# 使用示例
USAGE_EXAMPLE = """
# 使用示例

from config.ai_evaluation_prompt import (
    EVALUATION_SYSTEM_MESSAGE,
    FULL_EVALUATION_PROMPT,
    score_to_stars,
    stars_to_score
)
from cross_evaluation.model_client_factory import ModelClientFactory

# 1. 创建评测客户端（推荐使用deepseek-reasoner）
factory = ModelClientFactory('.')
evaluator = factory.create_client('deepseek-reasoner')

# 2. 准备评测数据
conversation = "医患对话内容..."
medical_record = "AI生成的病历摘要..."

# 3. 构建评测prompt
prompt = FULL_EVALUATION_PROMPT.format(
    conversation=conversation,
    medical_record=medical_record
)

# 4. 调用评测AI
response = evaluator.chat_completion(
    system_message=EVALUATION_SYSTEM_MESSAGE,
    prompt=prompt,
    max_tokens=2000,
    temperature=0.3  # 降低随机性，保持评分稳定
)

# 5. 解析评测结果
import json
result = json.loads(response)

# 6. 验证和调整
# 验证星级是否匹配分数
result['accuracy']['stars'] = score_to_stars('accuracy', result['accuracy']['score'])
result['completeness']['stars'] = score_to_stars('completeness', result['completeness']['score'])
result['standardization']['stars'] = score_to_stars('standardization', result['standardization']['score'])

# 验证总分
total = result['accuracy']['score'] + result['completeness']['score'] + result['standardization']['score']
result['total_score'] = total

print(f"评测完成！总分：{result['total_score']}/100")
"""

if __name__ == "__main__":
    print(USAGE_EXAMPLE)
