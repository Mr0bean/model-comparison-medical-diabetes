# 交叉评测系统

8个模型相互评测系统，支持5个维度的医疗报告质量评估。

## 系统架构

```
cross_evaluation/
├── __init__.py              # 模块初始化
├── config.py                # 配置加载器
├── prompt_loader.py         # Prompt加载和格式化
├── report_loader.py         # 报告数据加载
├── model_client.py          # 模型API客户端
├── dimension_evaluator.py   # 单维度评测器
├── aggregator.py            # 评分聚合器
└── engine.py                # 主评测引擎
```

## 评测规模

- **模型数量**: 8个
  - Baichuan-M2
  - deepseek_deepseek-v3.1
  - doubao-seed-1-6-251015
  - gemini-3-pro-preview
  - gpt-5.1
  - grok-4-0709
  - moonshotai_kimi-k2-0905
  - qwen3-max

- **患者数量**: 10个
- **评测维度**: 5个
  - 准确性 (40分)
  - 逻辑性 (25分)
  - 完整性 (15分)
  - 格式规范性 (15分)
  - 语言表达 (5分)

- **总文件数**: 8 × 8 × 10 × 6 = **3840个文件**

## 使用方法

### 1. 基础用法

```bash
# 运行完整评测
python run_cross_evaluation.py

# 列出可用模型
python run_cross_evaluation.py --list-models

# 列出可用患者
python run_cross_evaluation.py --list-patients
```

### 2. 指定评测范围

```bash
# 只评测指定模型
python run_cross_evaluation.py --models gpt-5.1 deepseek_deepseek-v3.1

# 只评测指定患者
python run_cross_evaluation.py --patients 患者1 患者2 患者3

# 组合使用
python run_cross_evaluation.py --models gpt-5.1 --patients 患者1
```

### 3. 断点续传

```bash
# 从上次中断处继续
python run_cross_evaluation.py --resume
```

### 4. 并行模式

```bash
# 使用并行模式（推荐）
python run_cross_evaluation.py --parallel

# 指定并发数
python run_cross_evaluation.py --parallel --max-workers 5

# 并行 + 断点续传
python run_cross_evaluation.py --parallel --resume
```

## 输出结构

```
output/cross_evaluation_results/
├── .progress.json                          # 进度文件
├── 患者1/
│   ├── gpt-5.1_by_deepseek_deepseek-v3.1_患者1_准确性.json
│   ├── gpt-5.1_by_deepseek_deepseek-v3.1_患者1_逻辑性.json
│   ├── gpt-5.1_by_deepseek_deepseek-v3.1_患者1_完整性.json
│   ├── gpt-5.1_by_deepseek_deepseek-v3.1_患者1_格式规范性.json
│   ├── gpt-5.1_by_deepseek_deepseek-v3.1_患者1_语言表达.json
│   ├── gpt-5.1_by_deepseek_deepseek-v3.1_患者1_aggregated.json
│   └── ... (每个患者384个文件)
├── 患者2/
└── ...
```

## 评测结果格式

### 单维度结果

```json
{
  "evaluated_model": "gpt-5.1",
  "evaluator_model": "deepseek_deepseek-v3.1",
  "patient": "患者1",
  "dimension": "准确性",
  "max_score": 40,
  "score": 38,
  "issues": "无明显准确性错误",
  "critical_feedback": "报告质量良好",
  "timestamp": "2025-11-23T20:00:00"
}
```

### 聚合结果

```json
{
  "evaluated_model": "gpt-5.1",
  "evaluator_model": "deepseek_deepseek-v3.1",
  "patient": "患者1",
  "total_score": 95,
  "max_total_score": 100,
  "dimensions": {
    "准确性": {"score": 38, "max_score": 40, "issues": "无"},
    "逻辑性": {"score": 24, "max_score": 25, "issues": "无"},
    "完整性": {"score": 15, "max_score": 15, "issues": "无"},
    "格式规范性": {"score": 14, "max_score": 15, "issues": "轻微格式问题"},
    "语言表达": {"score": 4, "max_score": 5, "issues": "个别口语化"}
  },
  "critical_feedbacks": ["质量良好", "逻辑清晰", ...],
  "timestamp": "2025-11-23T20:00:15"
}
```

## 配置文件

配置文件位于 `config/cross_evaluation_config.json`，可以修改以下内容：

- `models`: 参与评测的模型列表
- `patients`: 参与评测的患者列表
- `dimensions`: 评测维度及其权重
- `api_config`: API调用参数（temperature=0、max_tokens=4000、重试次数=3等）
- `concurrency.max_workers`: 并行模式下的最大并发数

## 环境要求

### Python依赖

```bash
pip install openai
```

### 环境变量

需要设置以下环境变量（根据使用的模型）：

```bash
export JIEKOU_API_KEY="your_jiekou_api_key"
export BAICHUAN_API_KEY="your_baichuan_api_key"
export DEEPSEEK_API_KEY="your_deepseek_api_key"
```

## 注意事项

1. **API限流**: 建议使用并行模式时设置合理的并发数（3-5）
2. **断点续传**: 评测会自动保存进度，中断后可以使用 `--resume` 继续
3. **模型名映射**: 某些模型名包含斜杠（如 `deepseek/deepseek-v3.1`），系统会自动转换为下划线
4. **报告文件**: 确保 `output/raw` 目录下有对应的报告文件

## 故障排除

### 问题1: 报告文件不存在

```
跳过: gpt-5.1 (报告不存在)
```

**解决方法**: 检查 `output/raw` 目录下是否有对应的报告文件（如 `gpt-5.1-患者1.json`）

### 问题2: API调用失败

```
调用模型失败 (尝试 1/3): deepseek-chat
```

**解决方法**:
- 检查环境变量是否正确设置
- 检查API密钥是否有效
- 检查网络连接

### 问题3: JSON解析失败

```
警告: 无法解析JSON响应，维度=准确性
```

**解决方法**: 系统会自动记录原始响应，可以手动检查并修正

## 进度查看

进度文件保存在 `output/cross_evaluation_results/.progress.json`，包含每个任务的完成状态。
