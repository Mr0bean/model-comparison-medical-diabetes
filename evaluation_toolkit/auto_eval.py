"""
自动化评测主脚本
评测所有模型的输出质量，生成评测报告
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import pandas as pd


class AutoEvaluator:
    """自动化评测器"""

    def __init__(self, markdown_dir: str = "./output/markdown"):
        self.markdown_dir = markdown_dir
        self.results = []

        # 必需字段列表
        self.required_fields = [
            "基本信息", "性别", "年龄", "身高", "体重",
            "主诉", "现病史", "既往病史", "家族病史"
        ]

        # 关键医疗实体
        self.medical_entities = {
            "疾病": ["糖尿病", "高血压", "高甘油三酯", "高脂血症"],
            "症状": ["泡沫", "体重下降", "体重减轻", "手麻", "脚麻", "视物模糊"],
            "药物": ["二甲双胍", "胰岛素", "司美格鲁肽", "格列齐特", "多格列艾汀"],
            "检查": ["血糖", "甘油三酯", "空腹血糖", "餐后血糖"]
        }

    def load_markdown_files(self) -> Dict[str, Dict[str, str]]:
        """加载所有Markdown文件"""
        data = defaultdict(dict)
        markdown_path = Path(self.markdown_dir)

        for md_file in sorted(markdown_path.glob("*.md")):
            # 解析文件名: {model}-{patient}.md
            filename = md_file.stem

            # 找到最后一个'-'作为分隔符
            parts = filename.rsplit('-', 1)
            if len(parts) == 2:
                model = parts[0]
                patient = parts[1]
            else:
                continue

            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            data[model][patient] = content

        return dict(data)

    def check_structure_completeness(self, content: str) -> Dict[str, Any]:
        """检查结构完整性"""
        score_details = {}
        found_fields = []

        for field in self.required_fields:
            if field in content:
                found_fields.append(field)
                score_details[field] = True
            else:
                score_details[field] = False

        score = len(found_fields) / len(self.required_fields) * 100

        return {
            "score": score,
            "found_count": len(found_fields),
            "total_count": len(self.required_fields),
            "details": score_details
        }

    def check_entity_coverage(self, content: str) -> Dict[str, Any]:
        """检查关键医疗实体覆盖率"""
        entity_results = {}
        total_found = 0
        total_entities = 0

        for category, entities in self.medical_entities.items():
            found_entities = []
            for entity in entities:
                if entity in content:
                    found_entities.append(entity)
                    total_found += 1
                total_entities += 1

            entity_results[category] = {
                "found": found_entities,
                "count": len(found_entities),
                "total": len(entities)
            }

        coverage_score = (total_found / total_entities * 100) if total_entities > 0 else 0

        return {
            "score": coverage_score,
            "total_found": total_found,
            "total_entities": total_entities,
            "by_category": entity_results
        }

    def check_numeric_accuracy(self, content: str) -> Dict[str, Any]:
        """检查数值信息准确性"""
        checks = {
            "has_age": False,
            "has_height": False,
            "has_weight": False,
            "has_glucose": False,
            "age_reasonable": False,
            "height_reasonable": False,
            "weight_reasonable": False,
            "glucose_reasonable": False
        }

        # 年龄检查
        age_match = re.search(r'年龄[：:]\s*(\d+)', content)
        if age_match:
            checks["has_age"] = True
            age = int(age_match.group(1))
            if 0 < age < 120:
                checks["age_reasonable"] = True

        # 身高检查
        height_match = re.search(r'身高[：:]\s*([\d.]+)', content)
        if height_match:
            checks["has_height"] = True
            height = float(height_match.group(1))
            if 100 < height < 250:
                checks["height_reasonable"] = True

        # 体重检查
        weight_match = re.search(r'体重[：:]\s*([\d.]+)', content)
        if weight_match:
            checks["has_weight"] = True
            weight = float(weight_match.group(1))
            if 30 < weight < 200:
                checks["weight_reasonable"] = True

        # 血糖检查
        glucose_match = re.search(r'血糖[：:]?\s*([\d.]+)', content)
        if glucose_match:
            checks["has_glucose"] = True
            glucose = float(glucose_match.group(1))
            if 0 < glucose < 50:
                checks["glucose_reasonable"] = True

        passed_checks = sum(1 for v in checks.values() if v)
        score = passed_checks / len(checks) * 100

        return {
            "score": score,
            "passed": passed_checks,
            "total": len(checks),
            "details": checks
        }

    def check_format_quality(self, content: str) -> Dict[str, Any]:
        """检查格式规范性"""
        checks = {
            "has_title": False,
            "has_sections": False,
            "has_lists": False,
            "proper_markdown": False
        }

        # 检查是否有标题
        if re.search(r'^#\s+', content, re.MULTILINE):
            checks["has_title"] = True

        # 检查是否有分节（二级标题）
        if re.search(r'^##\s+', content, re.MULTILINE):
            checks["has_sections"] = True

        # 检查是否有列表
        if re.search(r'^[-*]\s+', content, re.MULTILINE) or re.search(r'^\d+\.\s+', content, re.MULTILINE):
            checks["has_lists"] = True

        # 检查是否有基本的Markdown格式
        if checks["has_title"] and checks["has_sections"]:
            checks["proper_markdown"] = True

        passed_checks = sum(1 for v in checks.values() if v)
        score = passed_checks / len(checks) * 100

        return {
            "score": score,
            "passed": passed_checks,
            "total": len(checks),
            "details": checks
        }

    def calculate_length_metrics(self, content: str) -> Dict[str, Any]:
        """计算长度指标"""
        # 去掉标题行
        lines = content.split('\n')
        content_lines = [l for l in lines if not l.startswith('#')]
        content_text = '\n'.join(content_lines)

        return {
            "total_chars": len(content),
            "content_chars": len(content_text),
            "total_lines": len(lines),
            "content_lines": len(content_lines),
            "avg_line_length": len(content_text) / len(content_lines) if content_lines else 0
        }

    def evaluate_single(self, model: str, patient: str, content: str) -> Dict[str, Any]:
        """评测单个输出"""
        result = {
            "model": model,
            "patient": patient
        }

        # 结构完整性
        structure = self.check_structure_completeness(content)
        result["structure_score"] = structure["score"]
        result["structure_details"] = structure

        # 实体覆盖率
        entity = self.check_entity_coverage(content)
        result["entity_score"] = entity["score"]
        result["entity_details"] = entity

        # 数值准确性
        numeric = self.check_numeric_accuracy(content)
        result["numeric_score"] = numeric["score"]
        result["numeric_details"] = numeric

        # 格式质量
        format_check = self.check_format_quality(content)
        result["format_score"] = format_check["score"]
        result["format_details"] = format_check

        # 长度指标
        length = self.calculate_length_metrics(content)
        result["length_metrics"] = length

        # 综合得分（加权平均）
        result["overall_score"] = (
            structure["score"] * 0.30 +
            entity["score"] * 0.30 +
            numeric["score"] * 0.25 +
            format_check["score"] * 0.15
        )

        return result

    def evaluate_all(self) -> List[Dict[str, Any]]:
        """评测所有模型和患者"""
        data = self.load_markdown_files()
        results = []

        print("=" * 80)
        print("自动化评测开始")
        print("=" * 80)
        print()

        for model, patients in sorted(data.items()):
            print(f"评测模型: {model}")
            for patient, content in sorted(patients.items()):
                result = self.evaluate_single(model, patient, content)
                results.append(result)
                print(f"  {patient}: 总分 {result['overall_score']:.1f}")
            print()

        self.results = results
        return results

    def generate_summary(self) -> pd.DataFrame:
        """生成汇总统计"""
        df = pd.DataFrame(self.results)

        # 按模型分组统计
        summary = df.groupby('model').agg({
            'overall_score': ['mean', 'std', 'min', 'max'],
            'structure_score': 'mean',
            'entity_score': 'mean',
            'numeric_score': 'mean',
            'format_score': 'mean'
        }).round(2)

        summary.columns = [
            '总分均值', '总分标准差', '总分最小值', '总分最大值',
            '结构完整性', '实体覆盖率', '数值准确性', '格式质量'
        ]

        return summary

    def save_results(self, output_dir: str = "./evaluation_results"):
        """保存评测结果"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存详细结果
        detailed_file = output_path / "detailed_results.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"✓ 详细结果已保存: {detailed_file}")

        # 保存汇总统计
        summary = self.generate_summary()
        summary_file = output_path / "summary_statistics.csv"
        summary.to_csv(summary_file, encoding='utf-8-sig')

        print(f"✓ 汇总统计已保存: {summary_file}")

        # 保存简化表格
        df = pd.DataFrame(self.results)
        simple_df = df[['model', 'patient', 'overall_score', 'structure_score',
                        'entity_score', 'numeric_score', 'format_score']]
        simple_df.columns = ['模型', '患者', '总分', '结构', '实体', '数值', '格式']
        simple_file = output_path / "scores_table.csv"
        simple_df.to_csv(simple_file, index=False, encoding='utf-8-sig')

        print(f"✓ 得分表已保存: {simple_file}")

        return output_path


def main():
    """主函数"""
    evaluator = AutoEvaluator(markdown_dir="./output/markdown")

    # 执行评测
    results = evaluator.evaluate_all()

    # 生成汇总
    print("=" * 80)
    print("评测汇总")
    print("=" * 80)
    summary = evaluator.generate_summary()
    print(summary)
    print()

    # 保存结果
    print("=" * 80)
    print("保存结果")
    print("=" * 80)
    output_dir = evaluator.save_results()

    print()
    print("=" * 80)
    print(f"评测完成! 结果保存在: {output_dir}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
