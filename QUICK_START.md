# 🚀 交叉评估系统 - 快速开始指南

## 📋 系统状态

✅ **8个模型已配置并可用** (2025-11-18)

---

## 🎯 两种评估系统

### 1. 完整报告评估系统 ⭐ **推荐**

评估 `output/raw/` 中已生成的完整医疗报告。

```bash
# 测试模式
python run_report_cross_evaluation.py --test-mode

# 完整评估（10患者 × 8×8模型 = 560次评估）
python run_report_cross_evaluation.py
```

**详细文档**: 查看 `REPORT_EVALUATION_README.md`

### 2. 原始对话评估系统

从原始对话数据重新生成并评估（更细粒度，40个prompt）。

```bash
# 测试模式
python run_cross_evaluation.py --test-mode
```

---

## ⚡ 快速开始（完整报告评估）

### 1. 测试模式（推荐首次使用）

测试1个患者的1个对话，验证系统是否正常：

```bash
python run_cross_evaluation.py --test-mode
```

### 2. 使用特定模型

```bash
# 使用3个快速模型（推荐）
python run_cross_evaluation.py \
  --models Baichuan-M2 qwen3-max gpt-5.1 \
  --test-mode

# 使用所有8个模型
python run_cross_evaluation.py \
  --models Baichuan-M2 deepseek/deepseek-v3.1 doubao-seed-1-6-251015 \
           gemini-2.5-pro gpt-5.1 grok-4-0709 moonshotai/kimi-k2-0905 qwen3-max \
  --test-mode
```

### 3. 评估特定患者

```bash
# 评估患者1的所有对话
python run_cross_evaluation.py \
  --models Baichuan-M2 qwen3-max gpt-5.1 \
  --patients 患者1

# 评估多个患者
python run_cross_evaluation.py \
  --models Baichuan-M2 qwen3-max gpt-5.1 \
  --patients 患者1 患者2 患者3
```

### 4. 完整评估

评估所有患者的所有对话（预计2-4小时）：

```bash
python run_cross_evaluation.py \
  --models Baichuan-M2 deepseek/deepseek-v3.1 doubao-seed-1-6-251015 \
           gemini-2.5-pro gpt-5.1 grok-4-0709 moonshotai/kimi-k2-0905 qwen3-max
```

---

## 📊 查看结果

### 评估结果位置

```
output/cross_evaluation_results/
├── 患者1/
│   ├── conv_1/
│   │   ├── evaluations/        # 详细评估结果
│   │   └── matrix.json         # 评分矩阵
│   └── conv_2/
├── 患者2/
└── summary/
    └── statistics.json         # 汇总统计
```

### 查看评分矩阵

```bash
# 查看患者1对话1的评分矩阵
cat output/cross_evaluation_results/患者1/conv_1/matrix.json | python -m json.tool
```

### 查看总体排名

```bash
# 查看所有模型的排名
cat output/cross_evaluation_results/summary/statistics.json | python -m json.tool
```

---

## 🔧 常用参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--test-mode` | 只评估第一个患者的第一个对话 | `--test-mode` |
| `--models` | 指定使用的模型列表 | `--models Baichuan-M2 qwen3-max` |
| `--patients` | 指定评估的患者列表 | `--patients 患者1 患者2` |
| `--conversations` | 指定评估的对话类型（1-40） | `--conversations 1 2 3` |
| `--skip-evaluation` | 跳过评估，只生成矩阵 | `--skip-evaluation` |
| `--no-context` | 评估时不包含对话上下文 | `--no-context` |

---

## 💡 使用建议

### 首次使用

1. **验证系统**: `python run_cross_evaluation.py --test-mode`
2. **小规模测试**: 使用2-3个模型，1-2个患者
3. **检查结果**: 确认输出格式和评分合理
4. **扩大规模**: 逐步增加模型和患者数量

### 性能优化

- **快速模型**: Baichuan-M2 (0.59秒), qwen3-max (0.60秒)
- **中速模型**: gpt-5.1 (2.63秒), moonshotai/kimi-k2-0905 (3.59秒)
- **慢速模型**: grok-4-0709 (8.31秒) - 大规模评估时可考虑排除

### 成本控制

- 使用 `--test-mode` 进行初步验证
- 系统会缓存评估结果，重复运行不产生额外费用
- 评估次数 = 模型数 × 模型数 × 患者数 × 对话数

**示例**: 3个模型 × 3个模型 × 1个患者 × 1个对话 = 9次API调用

---

## 🔍 检查系统状态

### 测试模型连通性

```bash
python test_model_connectivity.py
```

### 查看可用模型

```bash
python -c "from cross_evaluation.model_registry import ModelRegistry; \
           r = ModelRegistry(); \
           print('\\n'.join(r.list_models().keys()))"
```

---

## ❓ 常见问题

### Q: 评估失败怎么办？

**A**: 检查以下几点：
1. 查看日志文件了解错误详情
2. 确认API密钥配置正确（`.env` 和 `batch_config_*.json`）
3. 检查网络连接
4. 使用 `test_model_connectivity.py` 测试模型连通性

### Q: 如何只重新评估部分内容？

**A**: 系统会缓存已完成的评估。如需重新评估：
1. 删除对应的评估文件
2. 或使用 `--skip-evaluation` 跳过评估，只重新生成矩阵

### Q: 评估需要多长时间？

**A**: 取决于：
- 模型数量和响应速度
- 患者数量和对话数量
- 网络状况

**参考**:
- 测试模式（1患者1对话3模型）: ~2分钟
- 中等规模（3患者5对话5模型）: ~30分钟
- 完整评估（10患者40对话8模型）: ~2-4小时

---

## 📚 更多文档

- **完整报告**: `MODEL_CONNECTIVITY_FINAL_REPORT.md` - 系统配置和模型状态
- **详细说明**: `CROSS_EVALUATION_README.md` - 系统架构和设计
- **连通性测试**: `connectivity_report_*.md` - 最新的模型测试报告

---

**更新时间**: 2025-11-18
**系统版本**: v1.0
**状态**: ✅ 就绪
