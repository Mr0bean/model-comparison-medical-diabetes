"""
配置模块 - 统一管理所有配置

此模块集中管理系统的所有配置，包括：
- 环境配置（API密钥、URL等）
- 模型注册表
- 评测参数
- 批量处理配置
- DeepSeek官方API配置
"""

# 导入主要配置
from .settings import settings, Settings
from .evaluation import (
    EVALUATION_DIMENSIONS,
    SCORE_RANGE,
    OUTPUT_CONFIG,
    API_CONFIG,
    EVALUATION_CONFIG
)

# DeepSeek官方API配置
try:
    from .deepseek import deepseek_settings, DeepSeekSettings, DEEPSEEK_MODELS
    _deepseek_available = True
except ImportError:
    _deepseek_available = False
    deepseek_settings = None
    DeepSeekSettings = None
    DEEPSEEK_MODELS = {}

# 模型注册表将在首次导入时初始化
_model_registry = None

def get_model_registry():
    """获取模型注册表单例"""
    global _model_registry
    if _model_registry is None:
        from .models import ModelRegistry
        _model_registry = ModelRegistry()
    return _model_registry

def is_deepseek_configured():
    """检查DeepSeek官方API是否配置"""
    if not _deepseek_available:
        return False
    return deepseek_settings.validate_api_key()

# 导出所有配置
__all__ = [
    # 环境配置
    'settings',
    'Settings',

    # 评测配置
    'EVALUATION_DIMENSIONS',
    'SCORE_RANGE',
    'OUTPUT_CONFIG',
    'API_CONFIG',
    'EVALUATION_CONFIG',

    # DeepSeek配置
    'deepseek_settings',
    'DeepSeekSettings',
    'DEEPSEEK_MODELS',
    'is_deepseek_configured',

    # 模型注册表
    'get_model_registry',
]

# 版本信息
__version__ = '1.0.0'
