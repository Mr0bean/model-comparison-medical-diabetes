# 📊 完整报告交叉评估系统

## 🎯 系统说明

这个系统用于评估 `output/raw/` 目录下已经生成的完整医疗报告，而不是重新生成报告。

### 评估对象

- **输入**: `output/raw/{model}-{患者}.json` (80个报告文件)
- **评估粒度**: 每个模型对每个患者的完整报告（5个对话合并）
- **评估方式**: 8个模型的报告互相评估，生成 8×8 矩阵

## 🚀 快速开始

### 1. 测试模式（推荐首次使用）

```bash
# 测试2个模型对1个患者的报告评估
python run_report_cross_evaluation.py \
  --test-mode \
  --models Baichuan-M2 qwen3-max
```

### 2. 评估单个患者

```bash
# 使用所有8个模型评估患者1
python run_report_cross_evaluation.py \
  --patients 患者1
```

### 3. 完整评估（推荐）

```bash
# 评估所有10个患者，使用所有8个模型
# 总评估次数: 10患者 × (8×8-8) = 560次 (不含自我评估)
python run_report_cross_evaluation.py
```

### 4. 自定义评估

```bash
# 评估3个患者，使用4个模型
python run_report_cross_evaluation.py \
  --patients 患者1 患者2 患者3 \
  --models Baichuan-M2 qwen3-max gpt-5.1 deepseek/deepseek-v3.1
```

## 📁 输出结构

```
output/report_cross_evaluation/
├── summary/
│   └── overall_statistics.json          # 跨患者的总体统计
├── 患者1/
│   ├── complete_result.json             # 完整结果（包含所有信息）
│   └── evaluations/
│       ├── Baichuan-M2_evaluated_by_qwen3-max.json
│       ├── qwen3-max_evaluated_by_Baichuan-M2.json
│       └── ...
├── 患者2/
│   └── ...
└── ...
```

## 📊 JSON数据结构

### complete_result.json (患者完整结果)

```json
{
  "patient": "患者1",
  "evaluation_time": "2025-11-18T19:30:35.196",
  "models": ["Baichuan-M2", "qwen3-max", ...],

  "reports": {
    "Baichuan-M2": {
      "full_report": "主诉：...\n现病史：...\n既往史：...",
      "metadata": {
        "model": "Baichuan-M2",
        "patient": "患者1",
        "conversation_count": 5,
        "source_file": "Baichuan-M2-患者1.json"
      },
      "conversation_details": {
        "1": {
          "title": "主诉",
          "output": "小便泡沫多12年，体重减轻2月",
          "prompt": "...",
          "input": "...",
          "chat": "..."
        },
        "2": {...},
        ...
      }
    },
    ...
  },

  "evaluations": {
    "Baichuan-M2_evaluated_by_qwen3-max": {
      "patient": "患者1",
      "generated_by": "Baichuan-M2",
      "evaluated_by": "qwen3-max",
      "report_content": "完整报告内容...",
      "report_metadata": {...},
      "evaluation": {
        "dimensions": {
          "accuracy": {
            "score": 3,
            "reasoning": "医学信息准确，但..."
          },
          "completeness": {...},
          "format": {...},
          "language": {...},
          "logic": {...}
        },
        "overall_comment": "总体评价...",
        "strengths": ["优点1", "优点2"],
        "weaknesses": ["不足1", "不足2"],
        "suggestions": ["建议1", "建议2"]
      },
      "average_score": 3.2,
      "metadata": {
        "evaluation_timestamp": "2025-11-18T19:30:35.196",
        "evaluator_model": "qwen3-max"
      }
    },
    ...
  },

  "matrix": {
    "score_matrix": [
      [0.0, 2.4],  // Baichuan-M2: [自评, qwen3-max评]
      [1.2, 0.0]   // qwen3-max:  [Baichuan-M2评, 自评]
    ],
    "dimension_matrices": {
      "accuracy": [[...], [...]],
      "completeness": [[...], [...]],
      ...
    },
    "statistics": {
      "model_average_scores": {
        "Baichuan-M2": 1.2,
        "qwen3-max": 2.4
      },
      "model_rankings": [
        {"rank": 1, "model": "qwen3-max", "score": 2.4},
        {"rank": 2, "model": "Baichuan-M2", "score": 1.2}
      ],
      "score_consistency": {
        "overall_std": 1.04,
        "overall_mean": 1.8
      }
    }
  },

  "statistics": {
    "total_evaluations": 2,
    "successful": 2,
    "failed": 0,
    "success_rate": "100.0%"
  }
}
```

### overall_statistics.json (总体统计)

```json
{
  "patients": ["患者1", "患者2", ...],
  "models": ["Baichuan-M2", "qwen3-max", ...],
  "overall_rankings": [
    {
      "model": "qwen3-max",
      "mean": 3.2,
      "std": 0.5,
      "count": 10
    },
    ...
  ],
  "patient_results": [
    {
      "patient": "患者1",
      "statistics": {...},
      "rankings": [...]
    },
    ...
  ]
}
```

## 💡 与原系统的区别

| 特性 | 原交叉评估系统 | 新报告评估系统 |
|------|--------------|--------------|
| **评估对象** | 从原始对话重新生成 | 评估已生成的报告 |
| **评估粒度** | 单个对话（40个prompt） | 完整报告（5个对话合并） |
| **评估次数** | 10患者 × 40对话 × 8×8 = 25,600 | 10患者 × 1报告 × 8×8 = 640 |
| **输入数据** | `测试输入问答记录/*.txt` | `output/raw/*.json` |
| **输出位置** | `output/cross_evaluation_results/` | `output/report_cross_evaluation/` |
| **适用场景** | 需要重新生成和评估 | 评估已有的报告质量 |

## 📈 评估规模

### 默认配置（不含自我评估）

- **每个患者**: 8个模型 → 8×8-8 = 56次评估
- **10个患者**: 10 × 56 = **560次评估**
- **预计时间**: ~2-4小时（取决于模型响应速度）

### 包含自我评估

- **每个患者**: 8个模型 → 8×8 = 64次评估
- **10个患者**: 10 × 64 = **640次评估**

## 🎨 前端展示建议

JSON结构已包含完整的metadata和数据，方便各种前端展示：

### 1. 评分矩阵热力图
```javascript
// 使用 matrix.score_matrix
// 行：被评估模型，列：评估者
```

### 2. 模型排名图表
```javascript
// 使用 matrix.statistics.model_rankings
// 按平均分排序
```

### 3. 维度雷达图
```javascript
// 使用 matrix.dimension_matrices
// 展示各模型在5个维度的表现
```

### 4. 详细评估展示
```javascript
// 使用 evaluations[key].evaluation
// 展示每个评估的详细reasoning
```

### 5. 报告原文对比
```javascript
// 使用 reports[model].full_report
// 并列展示不同模型生成的报告
```

## 🔧 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--test-mode` | 只评估第一个患者 | False |
| `--patients` | 指定患者列表 | 所有患者 |
| `--models` | 指定模型列表 | 所有模型 |
| `--reports-dir` | 报告目录 | output/raw |
| `--output-dir` | 输出目录 | output/report_cross_evaluation |
| `--include-self-evaluation` | 包含自我评估 | False |
| `--log-level` | 日志级别 | INFO |

## 📝 使用示例

### 场景1：快速验证系统

```bash
# 使用2个快速模型测试1个患者
python run_report_cross_evaluation.py \
  --test-mode \
  --models Baichuan-M2 qwen3-max
```

### 场景2：评估特定患者

```bash
# 评估患者1-3，使用所有模型
python run_report_cross_evaluation.py \
  --patients 患者1 患者2 患者3
```

### 场景3：完整评估（生产环境）

```bash
# 评估所有患者和模型
python run_report_cross_evaluation.py

# 包含自我评估
python run_report_cross_evaluation.py --include-self-evaluation
```

## 🎯 下一步

1. **运行评估**: 使用测试模式验证系统
2. **查看结果**: 检查 JSON 数据结构
3. **开发前端**: 基于 JSON 数据创建可视化界面
4. **完整评估**: 评估所有患者和模型

---

**更新时间**: 2025-11-18
**系统版本**: v2.0 - 完整报告评估系统
