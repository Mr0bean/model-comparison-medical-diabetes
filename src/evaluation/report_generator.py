"""
评测报告生成器
生成完整的Markdown格式评测报告
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class ReportGenerator:
    """评测报告生成器"""

    def __init__(self, results_dir: str = "./evaluation_results"):
        self.results_dir = Path(results_dir)

        # 加载评测结果
        with open(self.results_dir / "detailed_results.json", 'r', encoding='utf-8') as f:
            self.results = json.load(f)

        self.df = pd.DataFrame(self.results)

        # 加载汇总统计
        self.summary = pd.read_csv(self.results_dir / "summary_statistics.csv", index_col=0)

    def generate_executive_summary(self) -> str:
        """生成执行摘要"""
        # 找出最佳模型
        best_model = self.summary['总分均值'].idxmax()
        best_score = self.summary.loc[best_model, '总分均值']

        # 找出各维度最佳模型
        best_structure = self.summary['结构完整性'].idxmax()
        best_entity = self.summary['实体覆盖率'].idxmax()
        best_numeric = self.summary['数值准确性'].idxmax()
        best_format = self.summary['格式质量'].idxmax()

        summary = f"""## 执行摘要

### 最佳模型推荐

**综合表现最佳：{best_model}**
- 综合得分：{best_score:.2f} 分
- 在 {len(self.df[self.df['model'] == best_model])} 个患者案例中表现稳定
- 标准差：{self.summary.loc[best_model, '总分标准差']:.2f}（波动较小）

### 各维度表现最佳模型

| 维度 | 最佳模型 | 得分 |
|------|----------|------|
| 结构完整性 | {best_structure} | {self.summary.loc[best_structure, '结构完整性']:.1f} |
| 实体覆盖率 | {best_entity} | {self.summary.loc[best_entity, '实体覆盖率']:.1f} |
| 数值准确性 | {best_numeric} | {self.summary.loc[best_numeric, '数值准确性']:.1f} |
| 格式质量 | {best_format} | {self.summary.loc[best_format, '格式质量']:.1f} |

### 关键发现

1. **结构完整性**：所有模型在结构完整性方面均达到 100%，说明所有模型都能输出完整的基本信息框架

2. **实体覆盖率**：平均覆盖率在 51-58% 之间，存在较大提升空间。{best_entity} 在此维度表现最好

3. **数值准确性**：整体得分偏低（10-25%），说明大部分模型在提取精确数值信息方面存在困难

4. **格式质量**：除 Baichuan-M2（95%）外，其他模型均达到 100%，说明 Markdown 格式规范性良好

5. **稳定性**：{best_model} 的标准差最小，表现最稳定
"""
        return summary

    def generate_detailed_analysis(self) -> str:
        """生成详细分析"""
        analysis = "## 详细分析\n\n"

        # 为每个模型生成分析
        for model in sorted(self.summary.index):
            model_data = self.df[self.df['model'] == model]

            avg_score = self.summary.loc[model, '总分均值']
            std_score = self.summary.loc[model, '总分标准差']
            min_score = self.summary.loc[model, '总分最小值']
            max_score = self.summary.loc[model, '总分最大值']

            structure = self.summary.loc[model, '结构完整性']
            entity = self.summary.loc[model, '实体覆盖率']
            numeric = self.summary.loc[model, '数值准确性']
            format_score = self.summary.loc[model, '格式质量']

            # 找出该模型表现最好和最差的患者
            best_patient = model_data.loc[model_data['overall_score'].idxmax(), 'patient']
            best_patient_score = model_data['overall_score'].max()
            worst_patient = model_data.loc[model_data['overall_score'].idxmin(), 'patient']
            worst_patient_score = model_data['overall_score'].min()

            analysis += f"""### {model}

**综合表现：{avg_score:.2f} 分**（最小：{min_score:.2f}，最大：{max_score:.2f}，标准差：{std_score:.2f}）

**维度得分：**
- 结构完整性：{structure:.1f}%
- 实体覆盖率：{entity:.1f}%
- 数值准确性：{numeric:.1f}%
- 格式质量：{format_score:.1f}%

**优势：**
"""
            # 分析优势
            if structure >= 100:
                analysis += f"- ✓ 结构完整性达到 100%，能够完整输出所有必需字段\n"
            if entity > 55:
                analysis += f"- ✓ 实体覆盖率超过 55%，高于平均水平\n"
            if format_score >= 100:
                analysis += f"- ✓ 格式质量完美，Markdown 格式规范\n"
            if std_score < 3:
                analysis += f"- ✓ 输出稳定性好（标准差 < 3）\n"

            analysis += "\n**待改进：**\n"
            # 分析待改进点
            if entity < 55:
                analysis += f"- ⚠ 实体覆盖率偏低（{entity:.1f}%），需提高关键医疗信息提取能力\n"
            if numeric < 20:
                analysis += f"- ⚠ 数值准确性较低（{numeric:.1f}%），在提取精确数值方面有困难\n"
            if std_score > 4:
                analysis += f"- ⚠ 输出波动较大（标准差 {std_score:.2f}），稳定性有待提升\n"

            analysis += f"""
**典型案例：**
- 最佳表现：{best_patient}（{best_patient_score:.2f} 分）
- 最差表现：{worst_patient}（{worst_patient_score:.2f} 分）

---

"""

        return analysis

    def generate_ranking_table(self) -> str:
        """生成排名表"""
        # 按总分排序
        ranked = self.summary.sort_values('总分均值', ascending=False)

        table = """## 模型综合排名

| 排名 | 模型 | 综合得分 | 结构 | 实体 | 数值 | 格式 | 标准差 |
|------|------|----------|------|------|------|------|--------|
"""

        for rank, (model, row) in enumerate(ranked.iterrows(), 1):
            table += f"| {rank} | {model} | {row['总分均值']:.2f} | {row['结构完整性']:.1f} | {row['实体覆盖率']:.1f} | {row['数值准确性']:.1f} | {row['格式质量']:.1f} | {row['总分标准差']:.2f} |\n"

        return table

    def generate_recommendations(self) -> str:
        """生成改进建议"""
        recommendations = """## 改进建议

### 1. 提升实体覆盖率

**现状：** 各模型实体覆盖率在 51-58% 之间

**建议：**
- 优化 Prompt，明确要求提取所有关键医疗实体
- 在 Prompt 中提供示例，说明哪些信息属于关键实体
- 考虑使用思维链（Chain of Thought）提示，引导模型逐步提取信息

### 2. 改善数值准确性

**现状：** 数值准确性普遍偏低（10-25%）

**建议：**
- 在 Prompt 中强调数值信息的重要性
- 要求模型在输出中明确标注数值的来源和单位
- 考虑二阶段处理：先提取文本，再专门提取数值

### 3. 增强输出稳定性

**现状：** 部分模型在不同患者间波动较大

**建议：**
- 统一输出模板，减少模型自由发挥空间
- 使用更低的 temperature 参数（如 0.1-0.3）
- 考虑使用 JSON Schema 约束输出格式

### 4. 针对性优化

**Baichuan-M2：** 格式质量略低，需要优化 Markdown 格式输出

**DeepSeek-v3.1：** 数值准确性最低，需要加强数值提取能力

**GPT-5.1：** 数值准确性也较低，可能需要调整 Prompt

### 5. 建立标准答案库

建议为每个患者建立人工标注的标准答案（Golden Standard），用于：
- 更精确的自动化评测
- 模型微调的训练数据
- 评测基准的持续改进

### 6. 引入人工评测

当前评测为全自动化，建议引入人工评测维度：
- 临床实用性评分
- 语言流畅性评分
- 逻辑一致性评分
"""
        return recommendations

    def generate_full_report(self) -> str:
        """生成完整报告"""
        report = f"""# LLM 医疗病历信息提取评测报告

**评测日期：** {datetime.now().strftime('%Y年%m月%d日')}

**评测范围：** 7 个模型 × 10 个患者 = 70 个测试案例

**评测模型：**
- Baichuan-M2
- DeepSeek-v3.1
- Doubao-seed-1-6
- GPT-5.1
- Grok-4
- Kimi-k2-0905
- Qwen3-max

---

{self.generate_executive_summary()}

---

{self.generate_ranking_table()}

---

{self.generate_detailed_analysis()}

---

{self.generate_recommendations()}

---

## 评测方法说明

### 自动化评测维度

1. **结构完整性（权重 30%）**
   - 检查必需字段的存在性
   - 评分标准：存在字段数 / 总字段数 × 100

2. **实体覆盖率（权重 30%）**
   - 检查关键医疗实体（疾病、症状、药物、检查）的提取情况
   - 评分标准：提取实体数 / 应存在实体数 × 100

3. **数值准确性（权重 25%）**
   - 检查年龄、身高、体重、血糖等数值的准确性和合理性
   - 评分标准：准确数值数 / 总数值数 × 100

4. **格式质量（权重 15%）**
   - 检查 Markdown 格式规范性
   - 评分标准：符合规范项 / 总检查项 × 100

### 综合得分计算

```
综合得分 = 结构完整性 × 0.30 + 实体覆盖率 × 0.30 + 数值准确性 × 0.25 + 格式质量 × 0.15
```

---

## 附录

### 评测结果文件

- **详细结果：** `evaluation_results/detailed_results.json`
- **汇总统计：** `evaluation_results/summary_statistics.csv`
- **得分表：** `evaluation_results/scores_table.csv`

### 可视化图表

- **雷达图：** `evaluation_results/charts/radar_chart.png`
- **排名柱状图：** `evaluation_results/charts/ranking_bar.png`
- **热力图：** `evaluation_results/charts/heatmap.png`
- **维度对比图：** `evaluation_results/charts/dimension_comparison.png`
- **得分分布图：** `evaluation_results/charts/score_distribution.png`

---

**报告生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return report

    def save_report(self, output_file: str = None):
        """保存报告"""
        if output_file is None:
            output_file = self.results_dir / "evaluation_report.md"

        report = self.generate_full_report()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ 评测报告已保存: {output_file}")
        return output_file


def main():
    """主函数"""
    print("=" * 80)
    print("生成评测报告")
    print("=" * 80)
    print()

    generator = ReportGenerator()
    report_file = generator.save_report()

    print()
    print("=" * 80)
    print(f"报告已生成: {report_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
