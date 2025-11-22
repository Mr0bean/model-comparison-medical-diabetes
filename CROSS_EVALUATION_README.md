# 模型交叉评估系统

## 📋 功能概述

本系统实现了AI模型间的交叉评估功能：
- ✅ N个模型的输出互相评估
- ✅ 生成N×N评分矩阵
- ✅ 统一的评估标准（5个维度）
- ✅ 详细的评估推理过程
- ✅ 支持查看原始对话内容
- ✅ 可视化评分结果
- ✅ **多API提供商支持**（自动识别并使用正确的API配置）

## 🏗️ 系统架构

```
cross_evaluation/
├── __init__.py              # 模块初始化
├── config.py                # 配置文件（评估维度、API设置等）
├── prompt_template.py       # 评估prompt模板生成器
├── conversation_indexer.py  # 对话内容索引器
├── engine.py                # 交叉评估引擎（核心）
├── matrix.py                # 评分矩阵生成器
├── model_registry.py        # 模型注册表（管理不同API配置）
└── model_client_factory.py  # 客户端工厂（创建正确配置的客户端）

run_cross_evaluation.py      # 主执行脚本
test_multi_api.py           # 多API支持测试脚本
cross_evaluation_viewer.html # 可视化界面（待实现）
```

## 📊 评估维度

系统使用5个维度进行评估（每个维度1-5分）：

1. **准确性 (Accuracy)**: 医学信息的准确性
2. **完整性 (Completeness)**: 信息的完整程度
3. **格式规范 (Format)**: 符合病历书写规范
4. **语言表达 (Language)**: 专业术语使用准确性
5. **逻辑性 (Logic)**: 结构和逻辑清晰度

## 🚀 快速开始

### 1. 测试模式（推荐首次使用）

测试模式只评估1个患者的1个对话，快速验证系统功能：

```bash
python run_cross_evaluation.py --test-mode
```

### 2. 指定患者和对话

```bash
# 评估患者1的主诉（对话1）
python run_cross_evaluation.py --patients 患者1 --conversations 1

# 评估患者1和患者2的主诉和现病史
python run_cross_evaluation.py --patients 患者1 患者2 --conversations 1 2
```

### 3. 指定模型范围

```bash
# 只让gpt-5.1和deepseek进行交叉评估
python run_cross_evaluation.py --models gpt-5.1 deepseek/deepseek-v3.1 --test-mode
```

### 4. 完整评估

```bash
# 评估所有患者、所有对话、所有模型
python run_cross_evaluation.py
```

**注意**: 完整评估会产生大量API调用！
- 8个模型 × 8个模型 × 10个患者 × 5个对话 = 3200次评估
- 建议先用测试模式验证

### 5. 仅生成矩阵（不重新评估）

```bash
# 使用已有的评估结果生成矩阵
python run_cross_evaluation.py --skip-evaluation
```

## 📁 输出结构

```
output/cross_evaluation_results/
├── 患者1/
│   ├── conv_1_主诉/
│   │   ├── evaluations/                    # 详细评估结果
│   │   │   ├── gpt-5.1_by_deepseek.json   # gpt-5.1的输出被deepseek评估
│   │   │   ├── gpt-5.1_by_gemini.json
│   │   │   ├── deepseek_by_gpt-5.1.json
│   │   │   └── ...                         # 共N×N个文件
│   │   └── matrix.json                     # 评分矩阵
│   ├── conv_2_现病史/
│   └── ...
├── 患者2/
├── ...
└── summary/
    └── statistics.json                     # 汇总统计
```

## 📄 评估结果格式

每个评估结果文件 (`{generated_by}_by_{evaluated_by}.json`) 包含：

```json
{
  "patient": "患者1",
  "conversation_id": "1",
  "conversation_title": "主诉",
  "generated_by": "gpt-5.1",
  "evaluated_by": "deepseek/deepseek-v3.1",
  "original_output": "发现血糖升高2月...",
  "evaluation": {
    "dimensions": {
      "accuracy": {
        "score": 5,
        "reasoning": "信息准确，时间单位明确..."
      },
      "completeness": {
        "score": 4,
        "reasoning": "包含主要症状..."
      },
      ...
    },
    "overall_comment": "整体质量优秀...",
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1"],
    "suggestions": ["建议1"]
  },
  "average_score": 4.8,
  "metadata": {
    "evaluation_timestamp": "2025-11-18T10:30:00",
    "evaluator_model_version": "deepseek-v3.1"
  }
}
```

## 🔧 配置选项

### 评估配置 (`cross_evaluation/config.py`)

```python
EVALUATION_CONFIG = {
    "include_self_evaluation": True,    # 是否包含模型自我评估
    "save_intermediate_results": True,  # 是否保存中间结果
    "batch_size": 5,                    # 批量处理大小
    "enable_caching": True              # 是否启用缓存
}

API_CONFIG = {
    "temperature": 0.0,  # 固定为0提高评估一致性
    "max_retries": 3,
    "retry_delay": 2
}
```

## 📊 评分矩阵格式

`matrix.json` 包含：

```json
{
  "patient": "患者1",
  "conversation_id": "1",
  "models": ["gpt-5.1", "deepseek", "gemini", ...],
  "score_matrix": [
    [4.2, 4.5, 4.3, ...],  # gpt-5.1被各模型评估的分数
    [4.3, 4.1, 4.4, ...],  # deepseek被各模型评估的分数
    ...
  ],
  "dimension_matrices": {
    "accuracy": [[5, 5, 4, ...], ...],
    "completeness": [[4, 4, 5, ...], ...]
  },
  "statistics": {
    "model_average_scores": {      # 每个模型的平均得分
      "gpt-5.1": 4.35,
      "deepseek": 4.28
    },
    "model_evaluator_strictness": {  # 每个模型作为评估者的严格程度
      "gpt-5.1": 4.20,
      "deepseek": 4.50
    },
    "model_rankings": [...]           # 模型排名
  }
}
```

## 🎨 可视化界面（待实现）

`cross_evaluation_viewer.html` 将提供：
- 热力图展示评分矩阵
- 点击分数查看详细评估（弹窗）
- 弹窗内可查看原始对话内容
- 筛选功能（按患者/对话类型/模型）
- 导出功能

## 💡 使用建议

1. **首次使用**：用 `--test-mode` 快速验证系统
2. **逐步扩大**：先评估1-2个患者，再评估全部
3. **成本控制**：注意API调用量，建议启用缓存
4. **错误处理**：如遇失败，系统会继续其他评估
5. **增量评估**：启用缓存后，重复运行只会评估新增部分

## 🐛 常见问题

### Q: 评估很慢怎么办？
A:
- 使用 `--test-mode` 先测试
- 减少患者/对话/模型数量
- 检查API限流设置

### Q: 评估结果JSON解析失败？
A:
- 检查模型输出是否符合JSON格式
- 查看 `parse_error` 和 `raw_response` 字段
- 调整prompt模板使其更严格要求JSON格式

### Q: 如何跳过已完成的评估？
A:
- 启用缓存: `EVALUATION_CONFIG["enable_caching"] = True`
- 系统会自动跳过已存在的评估文件

### Q: 如何查看评估进度？
A:
- 观察终端输出
- 检查输出目录中的文件数量
- 查看评估结果的时间戳

## 📞 支持

如有问题，请检查：
1. `config.py` 中的API配置是否正确
2. `output/comparison_data.json` 是否存在
3. `output/raw/*.json` 原始数据是否完整
4. Python依赖是否已安装: `pip install -r requirements.txt`

## 🌐 多API提供商配置

系统自动识别并使用不同模型对应的API配置：

### 支持的API提供商

| 提供商 | 模型示例 | 配置文件 | API基础URL |
|--------|----------|----------|------------|
| JieKou API | gpt-5.1, deepseek, gemini, grok | .env | 从环境变量读取 |
| 通义千问 | qwen3-max | batch_config_qwen.json | dashscope.aliyuncs.com |
| 豆包 | doubao-seed-1-6-251015 | batch_config_doubao.json | ark.cn-beijing.volces.com |
| 百川智能 | Baichuan-M2 | batch_config_baichuan.json | api.baichuan-ai.com |
| Kimi | moonshotai/kimi-k2-0905 | batch_config_kimi.json | api.moonshot.cn |

### 测试多API支持

```bash
# 运行多API测试脚本
python test_multi_api.py

# 查看模型注册信息
cat model_registry_export.json
```

### 配置说明

1. **自动加载**: 系统启动时自动从各个 `batch_config_*.json` 文件加载配置
2. **API密钥**: 确保在对应配置文件中设置正确的API密钥
3. **模型映射**: 系统自动将模型名称映射到正确的API提供商
4. **客户端缓存**: 每个模型的客户端会被缓存，避免重复创建

### 添加新的API提供商

1. 创建配置文件 `batch_config_新提供商.json`
2. 在 `model_registry.py` 中添加加载逻辑
3. 运行测试验证配置

## 🎯 下一步开发

- [ ] 实现可视化界面 `cross_evaluation_viewer.html`
- [ ] 添加评估质量检查（检测异常评分）
- [ ] 支持自定义评估维度
- [ ] 添加评估报告生成功能
- [ ] 实现评估结果对比分析
