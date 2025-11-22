"""
评估Prompt模板
用于生成统一的评估指令
"""

from .config import EVALUATION_DIMENSIONS, SCORE_RANGE


class EvaluationPromptTemplate:
    """评估Prompt模板生成器"""

    @staticmethod
    def generate_evaluation_prompt(
        patient: str,
        conversation_title: str,
        conversation_id: str,
        original_output: str,
        conversation_context: str = None
    ) -> str:
        """
        生成评估prompt

        Args:
            patient: 患者名称（如"患者1"）
            conversation_title: 对话类型（如"主诉"）
            conversation_id: 对话ID（如"1"）
            original_output: 被评估的模型输出内容
            conversation_context: 原始对话内容（可选，用于参考）

        Returns:
            完整的评估prompt
        """

        # 构建评估维度说明
        dimensions_desc = []
        for dim_id, dim_info in EVALUATION_DIMENSIONS.items():
            dimensions_desc.append(
                f"{len(dimensions_desc) + 1}. **{dim_info['name']} ({dim_id})**: "
                f"{dim_info['description']}"
            )

        dimensions_text = "\n".join(dimensions_desc)

        # 构建对话上下文部分（如果提供）
        context_section = ""
        if conversation_context:
            context_section = f"""
【原始对话参考】
以下是生成该内容时的完整对话记录，供评估参考：

{conversation_context}

---
"""

        prompt = f"""你是一位专业的医疗AI评估专家。请客观、严格地评估以下AI模型生成的病历内容。

【评估场景】
- 患者: {patient}
- 对话类型: {conversation_title}
- 对话ID: {conversation_id}

{context_section}
【被评估内容】
{original_output}

---

【评估任务】
请从以下{len(EVALUATION_DIMENSIONS)}个维度对上述内容进行评分，每个维度的评分范围为{SCORE_RANGE['min']}-{SCORE_RANGE['max']}分：

{dimensions_text}

评分标准：{SCORE_RANGE['description']}

【评估要求】
1. **客观公正**: 基于医学标准和病历规范进行评估，不受模型偏好影响
2. **详细说明**: 每个维度必须提供具体的评分理由，说明优点和不足
3. **证据支持**: 评分理由应引用具体内容作为证据
4. **建设性**: 指出问题的同时，提供改进建议

【输出格式】
请严格按照以下JSON格式输出评估结果（不要包含markdown代码块标记）：

{{
  "dimensions": {{
    "accuracy": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "completeness": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "format": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "language": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "logic": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }}
  }},
  "overall_comment": "<综合评价，总结整体质量，100-200字>",
  "strengths": [
    "<优点1>",
    "<优点2>",
    "<优点3>"
  ],
  "weaknesses": [
    "<不足1>",
    "<不足2>"
  ],
  "suggestions": [
    "<改进建议1>",
    "<改进建议2>"
  ]
}}

请直接输出JSON，不要添加任何其他文字或解释。
"""

        return prompt

    @staticmethod
    def generate_report_evaluation_prompt(
        patient: str,
        report_content: str
    ) -> str:
        """
        生成完整报告评估prompt（不分对话）

        Args:
            patient: 患者名称（如"患者1"）
            report_content: 完整报告内容

        Returns:
            完整的评估prompt
        """

        # 构建评估维度说明
        dimensions_desc = []
        for dim_id, dim_info in EVALUATION_DIMENSIONS.items():
            dimensions_desc.append(
                f"{len(dimensions_desc) + 1}. **{dim_info['name']} ({dim_id})**: "
                f"{dim_info['description']}"
            )

        dimensions_text = "\n".join(dimensions_desc)

        prompt = f"""你是一位专业的医疗AI评估专家。请客观、严格地评估以下AI模型生成的完整医疗报告。

【评估场景】
- 患者: {patient}
- 内容类型: 完整医疗报告（包含主诉、现病史、既往史、医疗总结等）

【被评估报告】
{report_content}

---

【评估任务】
请从以下{len(EVALUATION_DIMENSIONS)}个维度对上述完整报告进行评分，每个维度的评分范围为{SCORE_RANGE['min']}-{SCORE_RANGE['max']}分：

{dimensions_text}

评分标准：{SCORE_RANGE['description']}

【评估要求】
1. **整体性评估**: 将报告作为一个完整的医疗文档进行评估，考虑各部分的连贯性和完整性
2. **客观公正**: 基于医学标准和病历规范进行评估，不受模型偏好影响
3. **详细说明**: 每个维度必须提供具体的评分理由，说明优点和不足
4. **证据支持**: 评分理由应引用具体内容作为证据
5. **建设性**: 指出问题的同时，提供改进建议

【输出格式】
请严格按照以下JSON格式输出评估结果（不要包含markdown代码块标记）：

{{
  "dimensions": {{
    "accuracy": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "completeness": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "format": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "language": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }},
    "logic": {{
      "score": <1-5的整数>,
      "reasoning": "<详细评分理由，至少50字>"
    }}
  }},
  "overall_comment": "<综合评价，总结整体质量，100-200字>",
  "strengths": [
    "<优点1>",
    "<优点2>",
    "<优点3>"
  ],
  "weaknesses": [
    "<不足1>",
    "<不足2>"
  ],
  "suggestions": [
    "<改进建议1>",
    "<改进建议2>"
  ]
}}

请直接输出JSON，不要添加任何其他文字或解释。
"""

        return prompt

    @staticmethod
    def generate_conversation_summary_prompt(conversation_history: list) -> str:
        """
        生成对话摘要prompt（用于简化对话上下文）

        Args:
            conversation_history: 对话历史列表

        Returns:
            对话摘要
        """

        # 格式化对话历史
        formatted_conv = []
        for i, turn in enumerate(conversation_history, 1):
            role = "医生" if turn.get("role") == "doctor" else "患者"
            content = turn.get("content", "")
            formatted_conv.append(f"Round {i} - {role}: {content}")

        conversation_text = "\n\n".join(formatted_conv)

        return f"""请简要总结以下医患对话的关键信息：

{conversation_text}

请提取：
1. 患者主要症状
2. 时间信息
3. 检查结果
4. 治疗信息

以简洁的文字形式输出。"""


def format_conversation_context(conversation_data: dict) -> str:
    """
    格式化对话上下文，用于评估prompt

    Args:
        conversation_data: 对话数据

    Returns:
        格式化的对话文本
    """
    if not conversation_data:
        return ""

    formatted_lines = []

    # 假设conversation_data包含对话轮次
    if "history" in conversation_data:
        for i, turn in enumerate(conversation_data["history"], 1):
            role = "👨‍⚕️ 医生" if turn.get("role") == "doctor" else "👤 患者"
            content = turn.get("content", "")
            formatted_lines.append(f"Round {i} - {role}:")
            formatted_lines.append(f"  {content}")
            formatted_lines.append("")

    return "\n".join(formatted_lines)
