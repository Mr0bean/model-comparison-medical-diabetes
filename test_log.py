"""测试日志输出"""
from batch_model_test import PromptManager, VERBOSE_LOGGING
import logging

print(f"VERBOSE_LOGGING = {VERBOSE_LOGGING}")
print(f"Root logger level: {logging.root.level}")
print(f"Logger level names: {logging.getLevelName(logging.root.level)}")

# 测试加载Prompt
pm = PromptManager("多个Prompt")
print(f"\n加载了 {len(pm.prompts)} 个Prompt")
