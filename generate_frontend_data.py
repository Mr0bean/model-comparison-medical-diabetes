#!/usr/bin/env python3
"""
生成前端所需的数据文件
从交叉评测结果和原始报告生成前端JSON文件
"""
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import statistics

# 配置
RESULTS_DIR = Path("output/cross_evaluation_results")
RAW_DIR = Path("output/raw")
OUTPUT_DIR = Path("output")
CONFIG_FILE = Path("config/cross_evaluation_config.json")

def load_config():
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_raw_reports():
    """加载所有原始报告"""
    reports = {}
    for report_file in RAW_DIR.glob("*.json"):
        # 文件名格式: {模型}-{患者}.json
        parts = report_file.stem.split('-')
        if len(parts) < 2:
            continue

        patient = parts[-1]  # 最后一部分是患者
        model = '-'.join(parts[:-1])  # 前面的部分是模型名

        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 提取关键信息
            reports[f"{model}_{patient}"] = {
                "model": model,
                "patient": patient,
                "conversations": data.get("conversations", {}),
                "result": data.get("result", ""),
                "people": data.get("people", {})
            }
        except Exception as e:
            print(f"⚠️  加载报告失败 {report_file}: {e}")

    return reports

def load_evaluation_results():
    """加载所有评测结果"""
    evaluations = []

    # 遍历所有患者目录
    for patient_dir in sorted(RESULTS_DIR.glob("患者*")):
        patient = patient_dir.name

        # 查找所有聚合文件
        for agg_file in patient_dir.glob("*_aggregated.json"):
            try:
                with open(agg_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                evaluations.append({
                    "evaluated_model": data.get("evaluated_model"),
                    "evaluator_model": data.get("evaluator_model"),
                    "patient": patient,
                    "total_score": data.get("total_score", 0),
                    "max_total_score": data.get("max_total_score", 100),
                    "dimensions": data.get("dimensions", {}),
                    "critical_feedbacks": data.get("critical_feedbacks", []),
                    "timestamp": data.get("timestamp")
                })
            except Exception as e:
                print(f"⚠️  加载评测失败 {agg_file}: {e}")

    return evaluations

def generate_cross_evaluation_matrix(evaluations, models, patients):
    """生成交叉评测矩阵数据"""
    print("\n📊 生成交叉评测矩阵...")

    # 全局矩阵
    global_matrix = defaultdict(lambda: defaultdict(lambda: {
        "scores": [],
        "count": 0
    }))

    # 按患者分组的矩阵
    patient_matrices = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        "scores": [],
        "count": 0
    })))

    # 聚合数据
    for eval_data in evaluations:
        evaluated = eval_data["evaluated_model"]
        evaluator = eval_data["evaluator_model"]
        patient = eval_data["patient"]
        score = eval_data["total_score"]

        # 全局矩阵
        global_matrix[evaluator][evaluated]["scores"].append(score)
        global_matrix[evaluator][evaluated]["count"] += 1

        # 患者矩阵
        patient_matrices[patient][evaluator][evaluated]["scores"].append(score)
        patient_matrices[patient][evaluator][evaluated]["count"] += 1

    # 计算统计值
    def compute_stats(data_dict):
        result = {}
        for evaluator in data_dict:
            result[evaluator] = {}
            for evaluated in data_dict[evaluator]:
                scores = data_dict[evaluator][evaluated]["scores"]
                if scores:
                    result[evaluator][evaluated] = {
                        "score": round(statistics.mean(scores), 2),
                        "count": len(scores),
                        "stddev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
                        "min": min(scores),
                        "max": max(scores),
                        "details": scores
                    }
        return result

    global_stats = compute_stats(global_matrix)
    patient_stats = {p: compute_stats(patient_matrices[p]) for p in patient_matrices}

    # 生成完整矩阵数据
    matrix_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_evaluations": len(evaluations),
            "evaluation_type": "100-point",
            "dimensions": [
                {"name": "准确性", "max_points": 40, "weight": 0.4},
                {"name": "逻辑性", "max_points": 25, "weight": 0.25},
                {"name": "完整性", "max_points": 15, "weight": 0.15},
                {"name": "格式规范性", "max_points": 15, "weight": 0.15},
                {"name": "语言表达", "max_points": 5, "weight": 0.05}
            ]
        },
        "models": models,
        "patients": patients,
        "global_matrix": global_stats,
        "matrices": patient_stats
    }

    # 保存文件
    output_file = OUTPUT_DIR / "cross_evaluation_matrix.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(matrix_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 交叉评测矩阵已保存: {output_file}")
    print(f"   - 总评测数: {len(evaluations)}")
    print(f"   - 模型数: {len(models)}")
    print(f"   - 患者数: {len(patients)}")

    return matrix_data

def generate_comparison_data(reports, models, patients):
    """生成模型对比数据"""
    print("\n📊 生成模型对比数据...")

    # 参考模型（用于提取标题）
    REFERENCE_MODEL = "gemini-3-pro-preview"

    # 重组数据结构
    comparison_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_reports": len(reports),
            "models_count": len(models),
            "patients_count": len(patients),
            "reference_model": REFERENCE_MODEL
        },
        "models": models,
        "patients": patients,
        "data": {}
    }

    # 第一步：收集参考模型的标题
    reference_titles = {}  # {patient: {conv_id: title}}

    for key, report in reports.items():
        patient = report["patient"]
        model = report["model"]

        # 从参考模型提取标题
        if model == REFERENCE_MODEL:
            conversations = report["conversations"]
            if patient not in reference_titles:
                reference_titles[patient] = {}

            for conv_id, conv_data in conversations.items():
                # 从Output字段提取标题（Output的第一行通常是标题）
                output = conv_data.get("Output", "")
                # 清理所有换行符，然后获取第一行
                cleaned_output = output.replace('\\n', '').replace('\n', ' ').strip() if output else ""

                # 如果清理后的文本太长（超过30字），截取前30字并添加省略号
                if cleaned_output and len(cleaned_output) <= 30:
                    title = cleaned_output
                elif cleaned_output and len(cleaned_output) > 30:
                    title = cleaned_output[:30] + "..."
                else:
                    title = f"对话{conv_id}"

                reference_titles[patient][conv_id] = title

    print(f"✅ 从参考模型 {REFERENCE_MODEL} 提取了标题")

    # 第二步：按患者分组，使用参考标题
    for key, report in reports.items():
        patient = report["patient"]
        model = report["model"]
        conversations = report["conversations"]

        if patient not in comparison_data["data"]:
            comparison_data["data"][patient] = {}

        # 按对话轮次组织
        for conv_id, conv_data in conversations.items():
            if conv_id not in comparison_data["data"][patient]:
                comparison_data["data"][patient][conv_id] = {}

            # 使用参考模型的标题，如果没有则使用默认标题
            title = reference_titles.get(patient, {}).get(conv_id, f"对话{conv_id}")

            comparison_data["data"][patient][conv_id][model] = {
                "title": title,
                "output": conv_data.get("Output", ""),
                "chat": conv_data.get("chat", "")
            }

    # 保存文件
    output_file = OUTPUT_DIR / "comparison_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 模型对比数据已保存: {output_file}")
    print(f"   - 报告数: {len(reports)}")

    return comparison_data

def generate_evaluation_details(evaluations, reports):
    """生成详细评测数据（用于评测页面）"""
    print("\n📊 生成详细评测数据...")

    details_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_evaluations": len(evaluations)
        },
        "evaluations": []
    }

    for eval_data in evaluations:
        model = eval_data["evaluated_model"]
        patient = eval_data["patient"]

        # 查找对应的报告
        report_key = f"{model}_{patient}"
        report = reports.get(report_key, {})

        details_data["evaluations"].append({
            "model": model,
            "patient": patient,
            "evaluator": eval_data["evaluator_model"],
            "scores": {
                "dimensions": [
                    {
                        "name": dim_name,
                        "score": dim_data.get("score", 0),
                        "max_score": dim_data.get("max_score", 0),
                        "issues": dim_data.get("issues", "")
                    }
                    for dim_name, dim_data in eval_data["dimensions"].items()
                ],
                "total_score": eval_data["total_score"],
                "max_total_score": eval_data["max_total_score"]
            },
            "feedbacks": eval_data.get("critical_feedbacks", []),
            "report": report.get("result", ""),
            "conversations": report.get("conversations", {}),
            "timestamp": eval_data.get("timestamp")
        })

    # 保存文件
    output_file = OUTPUT_DIR / "evaluation_details.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(details_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 详细评测数据已保存: {output_file}")

    return details_data

def generate_statistics(evaluations, models, patients):
    """生成统计数据（用于首页）"""
    print("\n📊 生成统计数据...")

    # 计算各种统计指标
    all_scores = [e["total_score"] for e in evaluations]

    # 模型排名
    model_scores = defaultdict(list)
    for eval_data in evaluations:
        model_scores[eval_data["evaluated_model"]].append(eval_data["total_score"])

    model_rankings = []
    for model, scores in model_scores.items():
        if scores:
            model_rankings.append({
                "model": model,
                "avg_score": round(statistics.mean(scores), 2),
                "min_score": min(scores),
                "max_score": max(scores),
                "stddev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0,
                "count": len(scores)
            })

    model_rankings.sort(key=lambda x: x["avg_score"], reverse=True)

    # 评测者特征
    evaluator_stats = defaultdict(list)
    for eval_data in evaluations:
        evaluator_stats[eval_data["evaluator_model"]].append(eval_data["total_score"])

    evaluator_features = []
    for evaluator, scores in evaluator_stats.items():
        if scores:
            evaluator_features.append({
                "evaluator": evaluator,
                "avg_given_score": round(statistics.mean(scores), 2),
                "count": len(scores),
                "min_score": min(scores),
                "max_score": max(scores),
                "stddev": round(statistics.stdev(scores), 2) if len(scores) > 1 else 0
            })

    evaluator_features.sort(key=lambda x: x["avg_given_score"], reverse=True)

    # 评分分布
    score_distribution = {
        "0-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-100": 0
    }

    for score in all_scores:
        if score <= 20:
            score_distribution["0-20"] += 1
        elif score <= 40:
            score_distribution["21-40"] += 1
        elif score <= 60:
            score_distribution["41-60"] += 1
        elif score <= 80:
            score_distribution["61-80"] += 1
        else:
            score_distribution["81-100"] += 1

    statistics_data = {
        "metadata": {
            "generated_at": datetime.now().isoformat()
        },
        "overview": {
            "total_models": len(models),
            "total_patients": len(patients),
            "total_evaluations": len(evaluations),
            "total_files": len(evaluations) * 6,  # 每个评测6个文件
            "completion_rate": 100.0
        },
        "scores": {
            "average": round(statistics.mean(all_scores), 2) if all_scores else 0,
            "median": round(statistics.median(all_scores), 2) if all_scores else 0,
            "min": min(all_scores) if all_scores else 0,
            "max": max(all_scores) if all_scores else 0,
            "stddev": round(statistics.stdev(all_scores), 2) if len(all_scores) > 1 else 0
        },
        "distribution": score_distribution,
        "model_rankings": model_rankings,
        "evaluator_features": evaluator_features
    }

    # 保存文件
    output_file = OUTPUT_DIR / "statistics.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(statistics_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 统计数据已保存: {output_file}")
    print(f"   - 平均分: {statistics_data['scores']['average']}")
    print(f"   - 最高分: {statistics_data['scores']['max']}")
    print(f"   - 最低分: {statistics_data['scores']['min']}")

    return statistics_data

def main():
    print("=" * 80)
    print("🔄 开始生成前端数据文件")
    print("=" * 80)

    # 加载配置
    config = load_config()
    models = config["models"]
    patients = config["patients"]

    print(f"\n📋 配置信息:")
    print(f"   - 模型数: {len(models)}")
    print(f"   - 患者数: {len(patients)}")

    # 加载原始数据
    print("\n📂 加载原始数据...")
    reports = load_raw_reports()
    evaluations = load_evaluation_results()

    print(f"   - 原始报告: {len(reports)}")
    print(f"   - 评测结果: {len(evaluations)}")

    # 生成各种数据文件
    generate_cross_evaluation_matrix(evaluations, models, patients)
    generate_comparison_data(reports, models, patients)
    generate_evaluation_details(evaluations, reports)
    generate_statistics(evaluations, models, patients)

    print("\n" + "=" * 80)
    print("✅ 所有前端数据文件生成完成！")
    print("=" * 80)
    print("\n生成的文件:")
    print("  📄 output/cross_evaluation_matrix.json - 交叉评测矩阵")
    print("  📄 output/comparison_data.json - 模型对比数据")
    print("  📄 output/evaluation_details.json - 详细评测数据")
    print("  📄 output/statistics.json - 统计数据")
    print()

if __name__ == "__main__":
    main()
