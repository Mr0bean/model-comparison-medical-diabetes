# 交叉评测数据结构与流程分析

## 目录

1. [数据概览](#数据概览)
2. [原始数据源](#原始数据源)
3. [生成报告数据](#生成报告数据)
4. [评测结果数据](#评测结果数据)
5. [数据流程](#数据流程)
6. [完整目录树](#完整目录树)

---

## 数据概览

### 数据规模统计

| 数据类型 | 位置 | 文件数 | 大小 | 说明 |
|---------|------|--------|------|------|
| 患者原始数据 | `data/patients/` | 10个 | ~50KB | 患者对话脚本 |
| 生成的医疗报告 | `output/raw/` | 80个 | ~8MB | 8个模型×10个患者 |
| 评测结果 | `output/cross_evaluation_results/` | 3,840个 | 31MB | 完整交叉评测 |
| 评测配置 | `config/` | ~10个 | ~100KB | 系统配置文件 |
| 评测Prompts | `Prompts/` | 5个 | ~20KB | 评测标准 |

---

## 原始数据源

### 1. 患者数据

**位置**: `data/patients/患者{1-10}.json`

**结构**:
```json
{
  "patient_id": "患者1",
  "conversations": {
    "对话1": {
      "round": 1,
      "title": "主诉采集",
      "doctor_question": "您好，请问您哪里不舒服？",
      "patient_answer": "我最近一段时间总是觉得口渴...",
      "keywords": ["口渴", "多饮", "多尿"],
      "clinical_significance": "典型的糖尿病\"三多一少\"症状"
    },
    "对话2": { ... },
    "对话3": { ... },
    "对话4": { ... }
  },
  "patient_info": {
    "age": 45,
    "gender": "男",
    "chief_complaint": "口渴、多饮、多尿3个月"
  }
}
```

**说明**:
- 每个患者有4轮对话
- 每轮对话包含医生问题和患者回答
- 包含关键词和临床意义标注

### 2. 评测标准Prompts

**位置**: `Prompts/PromptForReportTest/Prompts/`

**文件列表**:
```
01-准确性.md       (40分)
02-逻辑性.md       (25分)
03-完整性.md       (15分)
04-格式规范性.md   (15分)
05-语言表达.md     (5分)
```

**结构示例** (01-准确性.md):
```markdown
【角色设定】
你是一位资深的医疗专家，擅长评估医疗报告的质量...

【任务目标】
评估给定医疗报告的准确性...

【评测维度与评分标准 (总分100分, 本次评测打分40分)】
**1. 准确性—— 40分**
* 时序与数值核对 (15分)
* 事实一致性 (15分)
* 症状/病史准确性 (10分)

【输出要求】
严格按照以下JSON格式输出:
{
  "分数": <分数>,
  "扣分原因": "<详细说明>",
  "关键问题": ["问题1", "问题2"]
}
```

---

## 生成报告数据

### 位置

`output/raw/{模型名}-患者{N}.json`

**命名规范**: `{model_name}-患者{patient_id}.json`

**示例文件**:
```
output/raw/
├── Baichuan-M2-患者1.json
├── Baichuan-M2-患者2.json
├── ...
├── deepseek_deepseek-v3.1-患者1.json
├── doubao-seed-1-6-251015-患者1.json
├── gemini-3-pro-preview-患者1.json
├── gpt-5.1-患者1.json
├── grok-4-0709-患者1.json
├── moonshotai_kimi-k2-0905-患者1.json
└── qwen3-max-患者1.json
```

### 数据结构

```json
{
  "model_name": "gpt-5.1",
  "patient_id": "患者1",
  "timestamp": "2025-11-18T14:23:45",
  "conversations": {
    "1": {
      "round": 1,
      "title": "主诉采集",
      "Input": "【医生】您好，请问您哪里不舒服？\n【患者】我最近总是觉得口渴...",
      "Output": "**主诉 (Chief Complaint):**\n患者，男性，45岁，因\"反复口渴、多饮、多尿3个月\"就诊。",
      "model": "gpt-5.1",
      "timestamp": "2025-11-18T14:23:50"
    },
    "2": {
      "round": 2,
      "title": "现病史采集",
      "Input": "...",
      "Output": "**现病史 (Present Illness History):**\n患者于3个月前无明显诱因出现口渴...",
      "model": "gpt-5.1"
    },
    "3": {
      "round": 3,
      "title": "既往史采集",
      "Input": "...",
      "Output": "**既往史 (Past Medical History):**\n- 否认高血压、冠心病...",
      "model": "gpt-5.1"
    },
    "4": {
      "round": 4,
      "title": "家族史与个人史采集",
      "Input": "...",
      "Output": "- **家族史 (Family History):** 母亲患有糖尿病...\n- **个人史:** 无烟酒嗜好...",
      "model": "gpt-5.1"
    }
  },
  "metadata": {
    "total_tokens": 2456,
    "completion_time": "12.3s"
  }
}
```

**关键字段说明**:
- `conversations`: 包含4轮对话的完整记录
- `Input`: 医患对话原文
- `Output`: 模型生成的报告片段
- 每轮对话独立记录，便于追溯

---

## 评测结果数据

### 目录结构

```
output/cross_evaluation_results/
├── .progress.json                    # 进度追踪文件
├── 患者1/                            # 按患者分组
│   ├── {被评测模型}_by_{评测模型}_患者1_准确性.json
│   ├── {被评测模型}_by_{评测模型}_患者1_逻辑性.json
│   ├── {被评测模型}_by_{评测模型}_患者1_完整性.json
│   ├── {被评测模型}_by_{评测模型}_患者1_格式规范性.json
│   ├── {被评测模型}_by_{评测模型}_患者1_语言表达.json
│   └── {被评测模型}_by_{评测模型}_患者1_aggregated.json  # 聚合文件
├── 患者2/
│   └── ...
├── ...
└── 患者10/
    └── ...
```

### 文件数量统计

```
每个患者目录:
  - 64个聚合文件 (8×8个模型组合)
  - 320个维度文件 (64×5个维度)
  
全部10个患者:
  - 640个聚合文件
  - 3,200个维度文件
  - 总计: 3,840个JSON文件
```

### 数据结构

#### 1. 维度评分文件

**文件名**: `{evaluated_model}_by_{evaluator_model}_{patient}_准确性.json`

**结构**:
```json
{
  "dimension": "准确性",
  "evaluated_model": "gpt-5.1",
  "evaluator_model": "deepseek_deepseek-v3.1",
  "patient": "患者1",
  "score": 35,
  "max_score": 40,
  "issues": "1. 时间描述存在轻微不一致...\n2. 部分数值精确度不够...",
  "critical_feedbacks": [
    "建议将\"3个月前\"改为更精确的时间描述",
    "体重变化应明确数值范围"
  ],
  "evaluator_response": {
    "分数": 35,
    "扣分原因": "时序描述不够精确(扣3分)，部分症状未量化(扣2分)",
    "关键问题": ["时间不精确", "缺少量化"]
  },
  "timestamp": "2025-11-23T22:15:34",
  "prompt_tokens": 2150,
  "completion_tokens": 380
}
```

#### 2. 聚合评分文件

**文件名**: `{evaluated_model}_by_{evaluator_model}_{patient}_aggregated.json`

**结构**:
```json
{
  "evaluated_model": "gpt-5.1",
  "evaluator_model": "deepseek_deepseek-v3.1",
  "patient": "患者1",
  "total_score": 83,
  "max_total_score": 100,
  "dimensions": {
    "准确性": {
      "score": 35,
      "max_score": 40,
      "weight": 0.4,
      "issues": "..."
    },
    "逻辑性": {
      "score": 22,
      "max_score": 25,
      "weight": 0.25,
      "issues": "..."
    },
    "完整性": {
      "score": 13,
      "max_score": 15,
      "weight": 0.15,
      "issues": "..."
    },
    "格式规范性": {
      "score": 10,
      "max_score": 15,
      "weight": 0.15,
      "issues": "..."
    },
    "语言表达": {
      "score": 3,
      "max_score": 5,
      "weight": 0.05,
      "issues": "..."
    }
  },
  "critical_feedbacks": [
    "整体报告质量较高，结构清晰",
    "建议加强时序描述的精确性",
    "部分专业术语使用可以更规范"
  ],
  "timestamp": "2025-11-23T22:16:12"
}
```

#### 3. 进度追踪文件

**文件**: `.progress.json`

**结构**:
```json
{
  "last_updated": "2025-11-23T23:07:45",
  "total_tasks": 640,
  "completed_tasks": 640,
  "failed_tasks": 0,
  "tasks": {
    "gpt-5.1_by_deepseek_deepseek-v3.1_患者1": {
      "status": "completed",
      "completed": true,
      "timestamp": "2025-11-23T22:16:12",
      "dimensions_completed": 5
    },
    "gpt-5.1_by_deepseek_deepseek-v3.1_患者2": {
      "status": "completed",
      "completed": true,
      "timestamp": "2025-11-23T22:18:35"
    }
    // ... 640 tasks total
  }
}
```

---

## 数据流程

### 完整数据处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. 患者数据准备阶段                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        data/patients/患者{1-10}.json (原始患者数据)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    2. 报告生成阶段                                │
│   使用各个模型生成医疗报告 (批处理脚本)                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        output/raw/{model}-患者{N}.json (80个报告文件)
        └─ 8个模型 × 10个患者 = 80个医疗报告
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    3. 交叉评测阶段                                │
│   run_cross_evaluation.py (50并发workers)                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  对于每个 (被评测模型, 评测者, 患者)    │
        │  组合执行以下流程:                       │
        └─────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────────────────┐
        │ 3.1 加载报告                                      │
        │     report_loader.py 从 output/raw/ 加载报告    │
        │     ├─ 读取4轮对话的Output                       │
        │     └─ 拼接成标准格式报告                        │
        └──────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────────────────┐
        │ 3.2 模块解析                                      │
        │     module_parser.py 识别报告各部分              │
        │     ├─ 主诉                                       │
        │     ├─ 现病史                                     │
        │     ├─ 既往史                                     │
        │     └─ 家族史                                     │
        └──────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────────────────┐
        │ 3.3 维度评分 (并行)                              │
        │     dimension_evaluator.py                       │
        │     ├─ 准确性 (40分)   →  模型API调用            │
        │     ├─ 逻辑性 (25分)   →  模型API调用            │
        │     ├─ 完整性 (15分)   →  模型API调用            │
        │     ├─ 格式规范性(15分)→  模型API调用            │
        │     └─ 语言表达 (5分)  →  模型API调用            │
        │                                                   │
        │     保存: {model}_by_{evaluator}_{patient}_{dim}.json
        └──────────────────────────────────────────────────┘
                              ↓
        ┌──────────────────────────────────────────────────┐
        │ 3.4 分数聚合                                      │
        │     aggregator.py                                │
        │     ├─ 读取5个维度评分                           │
        │     ├─ 按权重计算总分                            │
        │     └─ 合并反馈意见                              │
        │                                                   │
        │     保存: {model}_by_{evaluator}_{patient}_aggregated.json
        └──────────────────────────────────────────────────┘
                              ↓
        output/cross_evaluation_results/患者{N}/ (3,840个文件)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    4. 结果分析阶段                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ├─ final_report.py        → 生成综合排名报告
        ├─ data_validation.py     → 验证数据完整性
        └─ CROSS_EVALUATION_REPORT.md  → 最终分析报告
```

### 关键处理步骤

#### 步骤1: 报告加载与标准化

```python
# cross_evaluation/report_loader.py
def extract_result(model_name, patient):
    """从raw文件提取并标准化报告"""
    # 1. 读取 output/raw/{model}-{patient}.json
    # 2. 提取4轮对话的Output
    # 3. 拼接成标准格式:
    #    1. 主诉 (Chief Complaint)
    #    2. 现病史 (Present Illness History)
    #    3. 既往史 (Past Medical History)
    #    4. 家族史 (Family History)
    return formatted_report
```

#### 步骤2: 维度评分

```python
# cross_evaluation/dimension_evaluator.py
def evaluate_dimension(report, dimension, evaluator_model):
    """使用评测模型对单个维度打分"""
    # 1. 加载维度prompt (如 01-准确性.md)
    # 2. 构建评测请求
    # 3. 调用evaluator_model API
    # 4. 解析JSON响应
    # 5. 保存结果到 {}_by_{}_{}_准确性.json
    return {
        "score": 35,
        "max_score": 40,
        "issues": "...",
        "critical_feedbacks": [...]
    }
```

#### 步骤3: 分数聚合

```python
# cross_evaluation/aggregator.py
def aggregate_scores(evaluated, evaluator, patient):
    """聚合5个维度的评分"""
    # 1. 读取5个维度文件
    # 2. 按权重计算总分
    #    总分 = 准确性×0.4 + 逻辑性×0.25 + 完整性×0.15 
    #          + 格式×0.15 + 语言×0.05
    # 3. 合并所有反馈
    # 4. 保存聚合结果
    return {
        "total_score": 83,
        "dimensions": {...}
    }
```

---

## 配置文件

### 1. 交叉评测配置

**文件**: `config/cross_evaluation_config.json`

```json
{
  "models": [
    "Baichuan-M2",
    "deepseek_deepseek-v3.1",
    "doubao-seed-1-6-251015",
    "gemini-3-pro-preview",
    "gpt-5.1",
    "grok-4-0709",
    "moonshotai_kimi-k2-0905",
    "qwen3-max"
  ],
  "patients": [
    "患者1", "患者2", "患者3", "患者4", "患者5",
    "患者6", "患者7", "患者8", "患者9", "患者10"
  ],
  "dimensions": [
    {
      "name": "准确性",
      "weight": 40,
      "file": "Prompts/PromptForReportTest/Prompts/01-准确性.md"
    },
    {
      "name": "逻辑性",
      "weight": 25,
      "file": "Prompts/PromptForReportTest/Prompts/02-逻辑性.md"
    },
    {
      "name": "完整性",
      "weight": 15,
      "file": "Prompts/PromptForReportTest/Prompts/03-完整性.md"
    },
    {
      "name": "格式规范性",
      "weight": 15,
      "file": "Prompts/PromptForReportTest/Prompts/04-格式规范性.md"
    },
    {
      "name": "语言表达",
      "weight": 5,
      "file": "Prompts/PromptForReportTest/Prompts/05-语言表达.md"
    }
  ],
  "output_dir": "output/cross_evaluation_results",
  "raw_reports_dir": "output/raw",
  "api_config": {
    "temperature": 0,
    "max_tokens": 4000,
    "retry_attempts": 3,
    "retry_delay": 2
  }
}
```

### 2. 模型注册表

**文件**: `config/models/model_registry.json`

```json
{
  "gpt-5.1": {
    "provider": "jiekou",
    "api_key_env": "JIEKOU_API_KEY",
    "base_url": "https://api.jiekou.ai/openai",
    "description": "JieKou AI GPT-5.1"
  },
  "deepseek_deepseek-v3.1": {
    "provider": "jiekou",
    "api_key_env": "JIEKOU_API_KEY",
    "base_url": "https://api.jiekou.ai/openai",
    "description": "DeepSeek V3.1 via JieKou"
  },
  "doubao-seed-1-6-251015": {
    "provider": "volcengine",
    "api_key_env": "DOUBAO_API_KEY",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "description": "豆包 Seed (火山引擎)"
  },
  "qwen3-max": {
    "provider": "aliyun",
    "api_key_env": "QWEN_API_KEY",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "description": "通义千问 Qwen3 Max (阿里云)"
  }
  // ... 其他模型配置
}
```

---

## 完整目录树

```
.
├── data/                                    # 原始数据源
│   └── patients/
│       ├── 患者1.json                       # 患者对话脚本
│       ├── 患者2.json
│       ├── ...
│       └── 患者10.json
│
├── output/                                  # 输出数据
│   ├── raw/                                 # 生成的医疗报告
│   │   ├── Baichuan-M2-患者1.json          # 8×10=80个报告
│   │   ├── Baichuan-M2-患者2.json
│   │   ├── ...
│   │   ├── gpt-5.1-患者1.json
│   │   └── qwen3-max-患者10.json
│   │
│   └── cross_evaluation_results/           # 交叉评测结果
│       ├── .progress.json                  # 进度追踪
│       ├── 患者1/                          # 按患者分组
│       │   ├── Baichuan-M2_by_Baichuan-M2_患者1_准确性.json
│       │   ├── Baichuan-M2_by_Baichuan-M2_患者1_逻辑性.json
│       │   ├── Baichuan-M2_by_Baichuan-M2_患者1_完整性.json
│       │   ├── Baichuan-M2_by_Baichuan-M2_患者1_格式规范性.json
│       │   ├── Baichuan-M2_by_Baichuan-M2_患者1_语言表达.json
│       │   ├── Baichuan-M2_by_Baichuan-M2_患者1_aggregated.json
│       │   ├── ...                         # 64×6=384个文件/患者
│       │   └── qwen3-max_by_qwen3-max_患者1_aggregated.json
│       ├── 患者2/
│       ├── ...
│       └── 患者10/
│
├── Prompts/                                 # 评测标准
│   └── PromptForReportTest/
│       ├── Prompts/
│       │   ├── 01-准确性.md                # 40分
│       │   ├── 02-逻辑性.md                # 25分
│       │   ├── 03-完整性.md                # 15分
│       │   ├── 04-格式规范性.md            # 15分
│       │   ├── 05-语言表达.md              # 5分
│       │   └── README.md
│       └── human_prompt                    # 人工评测问卷
│
├── config/                                  # 配置文件
│   ├── cross_evaluation_config.json        # 评测配置
│   ├── models/
│   │   └── model_registry.json             # 模型注册表
│   └── batch/
│       ├── batch_config_baichuan.json
│       ├── batch_config_doubao.json
│       ├── batch_config_qwen.json
│       └── unified_batch_config.json
│
├── cross_evaluation/                        # 核心代码
│   ├── __init__.py
│   ├── engine.py                           # 评测引擎
│   ├── dimension_evaluator.py              # 维度评分器
│   ├── aggregator.py                       # 分数聚合器
│   ├── report_loader.py                    # 报告加载器
│   ├── module_parser.py                    # 报告模块解析
│   ├── prompt_loader.py                    # Prompt加载器
│   ├── model_client.py                     # 统一模型客户端
│   └── config.py                           # 配置管理
│
├── run_cross_evaluation.py                  # 主执行脚本
├── final_report.py                          # 结果分析
├── data_validation.py                       # 数据验证
│
├── CROSS_EVALUATION_REPORT.md               # 评测总报告
└── DATA_STRUCTURE_ANALYSIS.md               # 本文档
```

---

## 数据访问示例

### 1. 查看某个患者的原始数据

```bash
cat data/patients/患者1.json | jq '.'
```

### 2. 查看某个模型生成的报告

```bash
cat output/raw/gpt-5.1-患者1.json | jq '.conversations["1"].Output'
```

### 3. 查看某个维度的评分

```bash
cat output/cross_evaluation_results/患者1/gpt-5.1_by_deepseek_deepseek-v3.1_患者1_准确性.json | jq '.'
```

### 4. 查看聚合评分

```bash
cat output/cross_evaluation_results/患者1/gpt-5.1_by_deepseek_deepseek-v3.1_患者1_aggregated.json | jq '.total_score, .dimensions'
```

### 5. 统计某个模型的平均分

```bash
find output/cross_evaluation_results -name "gpt-5.1_by_*_aggregated.json" \
  | xargs jq '.total_score' \
  | awk '{sum+=$1; count++} END {print "平均分:", sum/count}'
```

---

## 数据完整性保障

### 1. 进度追踪

- `.progress.json` 实时记录每个任务的完成状态
- 支持断点续传（`--resume`参数）
- 自动检测已完成的任务并跳过

### 2. 错误处理

- API调用失败自动重试3次
- 失败任务单独标记，不影响其他任务
- 详细的错误日志记录

### 3. 数据验证

```python
# data_validation.py 验证项目
✓ 文件数量检查 (3,840个)
✓ JSON格式验证
✓ 必要字段完整性
✓ 评分范围合理性 (0-100)
✓ 维度数量正确性 (5个)
```

---

## 性能优化

### 1. 并发执行

- 使用ThreadPoolExecutor实现50并发workers
- 预先创建所有患者目录，避免竞争条件
- 按患者分组输出，减少目录冲突

### 2. API限流

- 单个模型RPM限制: 100
- 8个模型总容量: 800 RPM
- 实际运行: 128 RPM (安全裕度充足)

### 3. 存储优化

- JSON格式压缩存储
- 按患者分目录，便于查找和管理
- 聚合文件独立保存，快速访问总分

---

## 总结

### 数据层级

```
原始层 (data/)
  └─> 生成层 (output/raw/)
       └─> 评测层 (output/cross_evaluation_results/)
            └─> 分析层 (reports/)
```

### 核心特点

1. **完整性**: 从原始数据到最终评分，全链路可追溯
2. **标准化**: 统一的JSON格式，便于程序处理
3. **可扩展**: 易于增加新模型、新患者、新维度
4. **高性能**: 50并发worker，40分钟完成640个评测
5. **可靠性**: 进度追踪、断点续传、数据验证

### 关键指标

- **数据完整率**: 100% (3,840/3,840)
- **数据有效率**: 100% (640/640聚合文件有效)
- **处理效率**: 128 RPM
- **存储大小**: 31MB (未压缩)
- **平均评分**: 80.42/100

