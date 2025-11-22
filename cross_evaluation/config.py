"""
交叉评估系统配置
"""

# 评估维度定义
EVALUATION_DIMENSIONS = {
    "accuracy": {
        "name": "准确性",
        "description": "医学信息的准确性，包括症状、时间、数值等是否准确无误",
        "weight": 1.0
    },
    "completeness": {
        "name": "完整性",
        "description": "信息的完整程度，是否包含了对话中的关键信息",
        "weight": 1.0
    },
    "format": {
        "name": "格式规范",
        "description": "是否符合病历书写规范和格式要求",
        "weight": 1.0
    },
    "language": {
        "name": "语言表达",
        "description": "专业术语使用是否准确，表达是否规范",
        "weight": 1.0
    },
    "logic": {
        "name": "逻辑性",
        "description": "结构和逻辑是否清晰，信息组织是否合理",
        "weight": 1.0
    }
}

# 评分范围
SCORE_RANGE = {
    "min": 1,
    "max": 5,
    "description": "1-非常差, 2-较差, 3-一般, 4-良好, 5-优秀"
}

# 输出目录配置
OUTPUT_CONFIG = {
    "base_dir": "output/cross_evaluation_results",
    "evaluations_dir": "evaluations",
    "matrices_dir": "matrices",
    "summary_dir": "summary"
}

# API配置
API_CONFIG = {
    "temperature": 0.0,  # 固定为0以提高评估一致性
    "max_retries": 3,
    "retry_delay": 2,  # 秒
    "timeout": 60  # 秒
}

# 评估配置
EVALUATION_CONFIG = {
    "include_self_evaluation": True,  # 是否包含模型自我评估
    "save_intermediate_results": True,  # 是否保存中间结果
    "batch_size": 5,  # 批量处理大小
    "enable_caching": True,  # 是否启用缓存（避免重复评估）
    "verbose_logging": False  # 是否显示详细日志（包括API入参出参预览）
}
