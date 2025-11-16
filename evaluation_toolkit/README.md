# LLM 医疗病历信息提取评测工具包

完整的自动化评测系统,用于评估多个LLM模型在医疗问诊记录信息提取任务中的表现。

## 目录结构

```
evaluation_toolkit/
├── README.md                  # 本文件
├── auto_eval.py              # 自动化评测主脚本
├── visualizer.py             # 可视化图表生成器
├── report_generator.py       # 评测报告生成器
└── (未来扩展)
    ├── semi_auto_eval.py     # 半自动化评测
    └── manual_eval_app.py    # 人工评测界面
```

## 快速开始

### 1. 安装依赖

```bash
pip install pandas matplotlib numpy
```

### 2. 准备数据

确保已经运行批处理脚本生成了Markdown结果文件:

```bash
python3 extract_results_to_markdown.py
```

这将在 `./output/markdown/` 目录下生成所有模型的输出文件。

### 3. 运行自动化评测

```bash
python3 evaluation_toolkit/auto_eval.py
```

这将:
- 扫描所有Markdown文件
- 对每个模型×患者组合进行评测
- 生成评测结果到 `./evaluation_results/` 目录

输出文件:
- `detailed_results.json` - 详细评测结果
- `summary_statistics.csv` - 汇总统计
- `scores_table.csv` - 简化得分表

### 4. 生成可视化图表

```bash
python3 evaluation_toolkit/visualizer.py
```

这将在 `./evaluation_results/charts/` 目录下生成:
- `radar_chart.png` - 多维度能力雷达图
- `ranking_bar.png` - 综合排名柱状图
- `heatmap.png` - 模型×患者表现热力图
- `dimension_comparison.png` - 各维度详细对比
- `score_distribution.png` - 得分分布箱线图

### 5. 生成评测报告

```bash
python3 evaluation_toolkit/report_generator.py
```

这将生成完整的Markdown格式评测报告: `./evaluation_results/evaluation_report.md`

## 评测维度说明

### 1. 结构完整性 (权重: 30%)

检查输出是否包含所有必需字段:
- 基本信息(性别、年龄、身高、体重)
- 主诉
- 现病史
- 既往病史
- 家族病史

**评分:** 存在字段数 / 总字段数 × 100

### 2. 实体覆盖率 (权重: 30%)

检查是否提取了关键医疗实体:
- 疾病: 糖尿病、高血压、高甘油三酯等
- 症状: 泡沫尿、体重下降、手麻等
- 药物: 二甲双胍、胰岛素、司美格鲁肽等
- 检查: 血糖、甘油三酯等

**评分:** 提取实体数 / 应存在实体数 × 100

### 3. 数值准确性 (权重: 25%)

检查数值信息的准确性和合理性:
- 年龄是否在合理范围(0-120)
- 身高是否在合理范围(100-250cm)
- 体重是否在合理范围(30-200kg)
- 血糖是否在合理范围(0-50mmol/L)

**评分:** 准确数值数 / 总数值数 × 100

### 4. 格式质量 (权重: 15%)

检查Markdown格式规范性:
- 是否有标题(# 一级标题)
- 是否有分节(## 二级标题)
- 是否有列表(- 或 1.)
- 整体Markdown格式是否规范

**评分:** 符合规范项 / 总检查项 × 100

### 综合得分计算

```
综合得分 = 结构完整性 × 0.30 + 实体覆盖率 × 0.30 + 数值准确性 × 0.25 + 格式质量 × 0.15
```

## 评测结果解读

### 汇总统计表

```csv
模型,总分均值,总分标准差,总分最小值,总分最大值,结构完整性,实体覆盖率,数值准确性,格式质量
qwen3-max,67.84,2.59,63.95,73.36,100.0,57.37,22.5,100.0
grok-4-0709,67.04,3.33,63.88,74.93,100.0,52.63,25.0,100.0
...
```

**关键指标:**
- **总分均值**: 该模型在所有患者上的平均表现
- **总分标准差**: 波动性指标,越小越稳定
- **各维度得分**: 分项能力评估

### 排名说明

1. **Qwen3-max (67.84分)** - 综合表现最佳
2. **Grok-4 (67.04分)** - 第二名
3. **Baichuan-M2 (66.92分)** - 第三名
4. **Kimi-k2 (66.72分)** - 第四名
5. **Doubao (66.57分)** - 第五名
6. **GPT-5.1 (64.87分)** - 第六名
7. **DeepSeek-v3.1 (64.70分)** - 第七名

## 当前评测的局限性

1. **仅自动化评测**: 缺少人工专家评分
2. **简化的实体库**: 实际医疗实体远比当前检测的多
3. **缺少语义理解**: 未评估逻辑推理和因果关系
4. **无标准答案**: 缺少人工标注的Golden Standard
5. **成本效率未考虑**: 未纳入API成本和响应时间

## 未来改进方向

### 短期 (1-2周)

- [ ] 扩展实体词典(从20+扩展到100+)
- [ ] 添加语义相似度评测(使用Sentence-BERT)
- [ ] 引入逻辑一致性检测
- [ ] 建立部分患者的标准答案

### 中期 (1-2月)

- [ ] 开发人工评测Web界面
- [ ] 组织医疗专业人员进行人工评测
- [ ] 完善标准答案库(全部10个患者)
- [ ] 添加成本-效益分析

### 长期 (3-6月)

- [ ] 细分场景评测(按疾病类型)
- [ ] 建立持续评测流程(CI/CD)
- [ ] 开发评测平台Dashboard
- [ ] 与真实临床使用反馈结合

## 使用示例

### 批量评测流程

```bash
# 1. 生成Markdown结果
python3 extract_results_to_markdown.py

# 2. 运行评测
python3 evaluation_toolkit/auto_eval.py

# 3. 生成图表
python3 evaluation_toolkit/visualizer.py

# 4. 生成报告
python3 evaluation_toolkit/report_generator.py

# 5. 查看报告
open evaluation_results/evaluation_report.md
```

### 单独查看某个模型

```python
import pandas as pd

# 加载详细结果
df = pd.read_csv('evaluation_results/scores_table.csv')

# 查看Qwen3-max的所有得分
qwen_scores = df[df['模型'] == 'qwen3-max']
print(qwen_scores)
```

### 自定义评测维度权重

修改 `auto_eval.py` 中的权重:

```python
result["overall_score"] = (
    structure["score"] * 0.30 +  # 结构完整性
    entity["score"] * 0.30 +     # 实体覆盖率
    numeric["score"] * 0.25 +    # 数值准确性
    format_check["score"] * 0.15 # 格式质量
)
```

## 常见问题

### Q: 为什么所有模型的结构完整性都是100%?

A: 因为当前只检查字段是否存在(如"基本信息"、"主诉"等关键词),所有模型都能输出这些标题。这个指标偏简单,未来会改进为检查字段内容的质量。

### Q: 为什么数值准确性普遍很低?

A: 原因有二:
1. 当前检测逻辑较严格,要求数值完全匹配
2. 很多模型将数值提取为范围(如"50-55岁")而非精确值

未来会改进检测逻辑,允许范围匹配。

### Q: 如何添加新的评测维度?

A: 在 `auto_eval.py` 中添加新的检测函数,例如:

```python
def check_custom_metric(self, content: str) -> Dict[str, Any]:
    # 你的检测逻辑
    score = ...
    return {"score": score, "details": ...}
```

然后在 `evaluate_single()` 中调用并纳入综合得分计算。

## 贡献指南

欢迎提交改进建议和Pull Request!

重点关注领域:
- 更精确的实体识别
- 语义相似度评测
- 人工评测界面开发
- 标准答案库建设

## 许可证

MIT License

## 联系方式

有问题或建议请提Issue
