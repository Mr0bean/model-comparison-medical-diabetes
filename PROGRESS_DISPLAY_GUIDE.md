# 进度显示功能使用指南

## 🎯 功能概述

已为交叉评估系统添加了完善的进度显示和异常处理功能，确保：
- ✅ 实时显示评估进度
- ✅ 清晰展示当前任务状态
- ✅ 全面的异常捕获和处理
- ✅ 详细的错误日志输出

## 📊 主要改进

### 1. **实时进度条** (使用 tqdm)

- **总体进度条**: 显示所有评估任务的整体进度
- **动态描述**: 实时显示当前处理的患者、生成者和评估者
- **时间估算**: 显示已用时间、剩余时间和处理速度

进度条格式：
```
🔄 总体进度 |████████████        | 12/30 [00:45<01:23, 2.4it/s]
📋 患者 1/3: 患者1 | 生成者:Baichuan-M2... | 评估者:doubao-seed...
```

### 2. **多层异常处理**

所有关键操作都增加了 try-catch 保护：

#### a. 患者循环层
```python
try:
    # 处理患者
except Exception as patient_loop_error:
    tqdm.write(f"✗ 患者循环异常: {patient} - {patient_loop_error}")
    # 自动跳过该患者的剩余任务
```

#### b. 生成者循环层
```python
try:
    # 读取报告
except Exception as gen_loop_error:
    tqdm.write(f"✗ 生成者循环异常: {generated_by_model} - {gen_loop_error}")
    # 跳过剩余的评估者
```

#### c. 评估者循环层
```python
try:
    # 执行评估
except Exception as eval_loop_error:
    tqdm.write(f"✗ 评估循环异常: {evaluator_model} - {eval_loop_error}")
    # 继续下一个评估
finally:
    pbar.update(1)  # 无论成功失败都更新进度
```

#### d. 文件操作层
- 读取文件失败时返回 None 并记录日志
- 保存文件失败时尝试保存到临时目录
- 解析失败时返回默认结构

### 3. **详细日志控制**

可通过配置文件控制日志详细程度：

```python
# cross_evaluation/config.py
EVALUATION_CONFIG = {
    ...
    "verbose_logging": False  # True: 显示API入参出参预览
}
```

- `verbose_logging = False`: 仅显示关键信息和错误
- `verbose_logging = True`: 显示完整的API调用详情（包括Prompt和Response预览）

### 4. **智能缓存检测**

```python
if EVALUATION_CONFIG["enable_caching"] and eval_file.exists():
    try:
        # 读取并使用缓存
        tqdm.write(f"✓ 已缓存: {evaluator_model} (评分: {avg_score:.2f})")
    except Exception as cache_error:
        tqdm.write(f"⚠️ 缓存读取失败: {cache_error}，重新评估")
```

### 5. **进度条与日志兼容**

所有输出都使用 `tqdm.write()` 而不是 `print()`，确保：
- 日志不会破坏进度条显示
- 进度条始终显示在底部
- 日志输出清晰可读

## 🚀 使用示例

### 基本用法

```bash
# 运行完整评估（带进度显示）
python run_cross_evaluation.py

# 测试模式（仅评估第一个患者）
python run_cross_evaluation.py --test-mode

# 指定患者和模型
python run_cross_evaluation.py --patients 患者1 --models Baichuan-M2 doubao-seed-1-6-251015
```

### 测试进度显示

```bash
# 运行测试脚本
python test_progress_display.py
```

## 📝 日志输出示例

### 正常运行
```
🔄 总体进度 |████████████        | 12/30 [00:45<01:23, 2.4it/s]
📋 患者 1/3: 患者1 | 生成者:Baichuan-M2... | 评估者:doubao-seed...
    ✓ 已缓存: doubao-seed-1-6-251015 (评分: 4.20)
    ✓ 完成: qwen3-max (评分: 4.50)
```

### 错误处理
```
  ⚠️ 未找到报告: unknown-model-患者1.md
    ✗ 评估失败: evaluator-model - API调用超时
    ⚠️ 缓存读取失败: JSON解析错误，重新评估
```

## 🛡️ 错误恢复策略

1. **文件读取失败**
   - 记录警告日志
   - 跳过该文件的所有相关评估
   - 继续处理下一个文件

2. **API调用失败**
   - 记录详细错误信息
   - 标记该评估为失败
   - 继续下一个评估任务

3. **文件保存失败**
   - 尝试保存到系统临时目录
   - 记录临时文件位置
   - 如果仍失败，抛出异常但不中断整个流程

4. **解析失败**
   - 保存原始响应到文件
   - 返回默认评分结构（分数为0）
   - 继续下一个评估

## 📊 统计信息

评估结束后会显示详细统计：

```
====================================================================
✨ 完整报告交叉评估系统运行完成！
====================================================================
总评估次数: 30
成功: 28
失败: 2
成功率: 93.3%
====================================================================
```

## 🔧 配置选项

在 `cross_evaluation/config.py` 中可以调整：

```python
EVALUATION_CONFIG = {
    "include_self_evaluation": True,  # 是否包含自我评估
    "enable_caching": True,           # 是否启用缓存
    "verbose_logging": False          # 是否显示详细日志
}

API_CONFIG = {
    "temperature": 0.0,
    "retry_delay": 2,  # API调用间隔（秒）
    "timeout": 60      # API超时时间（秒）
}
```

## ⚠️ 注意事项

1. **进度条模式**: 确保终端支持 ANSI 转义序列
2. **日志输出**: 使用 `tqdm.write()` 而不是 `print()` 来输出日志
3. **异常恢复**: 系统会尽可能继续执行，不会因单个错误而中断
4. **缓存机制**: 启用缓存后，已评估的任务不会重复执行

## 🎉 优势

1. ✅ **可靠性**: 全面的异常处理，确保系统稳定运行
2. ✅ **可观测性**: 实时进度显示，清楚了解执行状态
3. ✅ **可恢复性**: 失败任务不影响其他任务执行
4. ✅ **可调试性**: 详细的错误日志，便于问题定位
5. ✅ **用户体验**: 清晰的进度反馈，估算剩余时间

## 📞 问题排查

如果遇到问题：

1. 检查 `output/comparison_data.json` 是否存在
2. 检查 `output/markdown/` 目录是否有对应的报告文件
3. 查看详细日志输出中的错误信息
4. 启用 `verbose_logging` 查看API调用详情
5. 检查临时目录是否有保存的原始响应
