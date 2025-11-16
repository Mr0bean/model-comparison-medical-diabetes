"""
评测结果可视化工具
生成各类图表展示模型对比
"""
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
from typing import List, Dict, Any
import numpy as np

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


class EvaluationVisualizer:
    """评测结果可视化器"""

    def __init__(self, results_file: str):
        """
        初始化可视化器

        Args:
            results_file: 评测结果JSON文件路径
        """
        with open(results_file, 'r', encoding='utf-8') as f:
            self.results = json.load(f)

        self.df = pd.DataFrame(self.results)
        self.output_dir = Path("./evaluation_results/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_radar_chart(self):
        """绘制雷达图 - 多维度能力对比"""
        # 计算每个模型的平均分
        metrics = ['structure_score', 'entity_score', 'numeric_score', 'format_score']
        metric_labels = ['结构完整性', '实体覆盖率', '数值准确性', '格式质量']

        model_scores = self.df.groupby('model')[metrics].mean()

        # 创建雷达图
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

        # 角度设置
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # 闭合

        # 为每个模型绘制
        colors = plt.cm.Set3(np.linspace(0, 1, len(model_scores)))

        for idx, (model, scores) in enumerate(model_scores.iterrows()):
            values = scores.tolist()
            values += values[:1]  # 闭合

            ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metric_labels, size=12)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'])
        ax.grid(True)

        plt.title('模型多维度能力雷达图', size=16, pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

        output_file = self.output_dir / "radar_chart.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ 雷达图已保存: {output_file}")

    def plot_ranking_bar(self):
        """绘制排名柱状图"""
        # 计算平均总分
        model_avg = self.df.groupby('model')['overall_score'].mean().sort_values(ascending=False)

        fig, ax = plt.subplots(figsize=(12, 6))

        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(model_avg)))
        bars = ax.barh(range(len(model_avg)), model_avg.values, color=colors)

        # 添加数值标签
        for i, (bar, value) in enumerate(zip(bars, model_avg.values)):
            ax.text(value + 1, i, f'{value:.1f}', va='center', fontsize=10, fontweight='bold')

        ax.set_yticks(range(len(model_avg)))
        ax.set_yticklabels(model_avg.index, fontsize=11)
        ax.set_xlabel('综合得分', fontsize=12)
        ax.set_title('模型综合得分排名', fontsize=16, pad=15)
        ax.set_xlim(0, 110)
        ax.grid(axis='x', alpha=0.3)

        output_file = self.output_dir / "ranking_bar.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ 排名柱状图已保存: {output_file}")

    def plot_heatmap(self):
        """绘制热力图 - 模型×患者表现矩阵"""
        # 创建数据透视表
        pivot_table = self.df.pivot_table(
            values='overall_score',
            index='model',
            columns='patient',
            aggfunc='mean'
        )

        # 对患者列进行排序
        patient_order = sorted(pivot_table.columns, key=lambda x: (len(x), x))
        pivot_table = pivot_table[patient_order]

        fig, ax = plt.subplots(figsize=(14, 8))

        im = ax.imshow(pivot_table.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

        # 设置坐标轴
        ax.set_xticks(np.arange(len(pivot_table.columns)))
        ax.set_yticks(np.arange(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.columns, fontsize=10)
        ax.set_yticklabels(pivot_table.index, fontsize=10)

        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # 添加数值
        for i in range(len(pivot_table.index)):
            for j in range(len(pivot_table.columns)):
                text = ax.text(j, i, f'{pivot_table.values[i, j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)

        ax.set_title("模型×患者得分热力图", fontsize=16, pad=15)
        ax.set_xlabel("患者", fontsize=12)
        ax.set_ylabel("模型", fontsize=12)

        # 添加色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('得分', rotation=270, labelpad=20, fontsize=11)

        output_file = self.output_dir / "heatmap.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ 热力图已保存: {output_file}")

    def plot_dimension_comparison(self):
        """绘制各维度对比图"""
        metrics = {
            'structure_score': '结构完整性',
            'entity_score': '实体覆盖率',
            'numeric_score': '数值准确性',
            'format_score': '格式质量'
        }

        model_scores = self.df.groupby('model')[list(metrics.keys())].mean()

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        axes = axes.flatten()

        colors = plt.cm.Set2(np.linspace(0, 1, len(model_scores)))

        for idx, (metric, label) in enumerate(metrics.items()):
            ax = axes[idx]

            scores = model_scores[metric].sort_values(ascending=False)
            bars = ax.bar(range(len(scores)), scores.values, color=colors)

            # 添加数值标签
            for i, (bar, value) in enumerate(zip(bars, scores.values)):
                ax.text(i, value + 1.5, f'{value:.1f}', ha='center', fontsize=9, fontweight='bold')

            ax.set_xticks(range(len(scores)))
            ax.set_xticklabels(scores.index, rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('得分', fontsize=11)
            ax.set_title(label, fontsize=13, fontweight='bold')
            ax.set_ylim(0, 110)
            ax.grid(axis='y', alpha=0.3)

        plt.suptitle('各维度详细对比', fontsize=16, fontweight='bold')

        output_file = self.output_dir / "dimension_comparison.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ 维度对比图已保存: {output_file}")

    def plot_score_distribution(self):
        """绘制得分分布箱线图"""
        fig, ax = plt.subplots(figsize=(12, 6))

        # 准备数据
        models = sorted(self.df['model'].unique())
        data = [self.df[self.df['model'] == model]['overall_score'].values for model in models]

        # 绘制箱线图
        bp = ax.boxplot(data, labels=models, patch_artist=True, showmeans=True)

        # 美化箱线图
        colors = plt.cm.Pastel1(np.linspace(0, 1, len(models)))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)

        ax.set_xlabel('模型', fontsize=12)
        ax.set_ylabel('综合得分', fontsize=12)
        ax.set_title('模型得分分布箱线图', fontsize=16, pad=15)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')

        output_file = self.output_dir / "score_distribution.png"
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"✓ 得分分布图已保存: {output_file}")

    def plot_all(self):
        """生成所有图表"""
        print("=" * 80)
        print("生成可视化图表")
        print("=" * 80)
        print()

        self.plot_radar_chart()
        self.plot_ranking_bar()
        self.plot_heatmap()
        self.plot_dimension_comparison()
        self.plot_score_distribution()

        print()
        print("=" * 80)
        print(f"所有图表已保存到: {self.output_dir}/")
        print("=" * 80)


def main():
    """主函数"""
    results_file = "./evaluation_results/detailed_results.json"

    if not Path(results_file).exists():
        print(f"错误: 找不到评测结果文件: {results_file}")
        print("请先运行 auto_eval.py 生成评测结果")
        return

    visualizer = EvaluationVisualizer(results_file)
    visualizer.plot_all()


if __name__ == "__main__":
    main()
