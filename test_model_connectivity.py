#!/usr/bin/env python3
"""
模型连通性测试
测试所有注册模型的API连接状态
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from cross_evaluation.model_registry import ModelRegistry
from cross_evaluation.model_client_factory import ModelClientFactory


def test_single_model(factory: ModelClientFactory, model_name: str) -> Tuple[bool, str, float]:
    """
    测试单个模型的连通性

    Args:
        factory: 客户端工厂
        model_name: 模型名称

    Returns:
        (成功与否, 响应信息, 响应时间)
    """
    # 简单的测试prompt
    test_prompt = "请用一句话回答：1+1等于几？"

    start_time = time.time()

    try:
        # 创建客户端
        client = factory.create_client(model_name)

        # 发送测试请求（使用非流式模式以获取完整响应）
        response = client.chat(
            test_prompt,
            temperature=0.0,
            max_tokens=50,
            stream=False  # 确保使用非流式响应
        )

        end_time = time.time()
        response_time = round(end_time - start_time, 2)

        # 截取响应的前100个字符
        response_preview = response[:100] if len(response) > 100 else response
        response_preview = response_preview.replace('\n', ' ')

        return True, f"✅ 成功 | 响应: {response_preview}", response_time

    except Exception as e:
        end_time = time.time()
        response_time = round(end_time - start_time, 2)
        error_msg = str(e)[:200]  # 截取错误消息
        return False, f"❌ 失败 | 错误: {error_msg}", response_time


def run_connectivity_test():
    """运行完整的连通性测试"""
    print("\n" + "="*80)
    print("🔍 模型连通性测试")
    print("="*80 + "\n")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("测试内容: 发送简单问题测试API响应")
    print("-"*80 + "\n")

    # 初始化
    registry = ModelRegistry()
    factory = ModelClientFactory()

    # 获取所有模型
    all_models = registry.list_models()

    # 按提供商分组
    providers = {}
    for model, provider in all_models.items():
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)

    # 测试结果
    results = {
        "test_time": datetime.now().isoformat(),
        "total_models": len(all_models),
        "successful": 0,
        "failed": 0,
        "details": {}
    }

    # 按提供商测试
    for provider, models in sorted(providers.items()):
        print(f"\n📡 测试 {provider} 的模型:")
        print("-"*60)

        for model in sorted(models):
            print(f"\n测试 {model}...")

            # 获取模型信息
            model_info = registry.get_model_config(model)

            # 测试连通性
            success, message, response_time = test_single_model(factory, model)

            # 记录结果
            results["details"][model] = {
                "provider": provider,
                "base_url": model_info.base_url,
                "has_api_key": model_info.api_key is not None,
                "test_success": success,
                "response_time": response_time,
                "message": message
            }

            if success:
                results["successful"] += 1
                print(f"  {message}")
                print(f"  响应时间: {response_time}秒")
            else:
                results["failed"] += 1
                print(f"  {message}")

            # 避免API限流
            if success:
                time.sleep(1)

    # 生成报告
    print("\n" + "="*80)
    print("📊 测试报告")
    print("="*80 + "\n")

    print(f"总模型数: {results['total_models']}")
    print(f"✅ 成功: {results['successful']} ({results['successful']/results['total_models']*100:.1f}%)")
    print(f"❌ 失败: {results['failed']} ({results['failed']/results['total_models']*100:.1f}%)")

    # 按提供商统计
    print("\n按提供商统计:")
    print("-"*40)

    provider_stats = {}
    for model, detail in results["details"].items():
        provider = detail["provider"]
        if provider not in provider_stats:
            provider_stats[provider] = {"success": 0, "fail": 0, "models": []}

        if detail["test_success"]:
            provider_stats[provider]["success"] += 1
        else:
            provider_stats[provider]["fail"] += 1
        provider_stats[provider]["models"].append(model)

    for provider, stats in sorted(provider_stats.items()):
        total = stats["success"] + stats["fail"]
        print(f"\n{provider}:")
        print(f"  成功: {stats['success']}/{total}")
        if stats["fail"] > 0:
            print(f"  失败模型: {', '.join([m for m in stats['models'] if not results['details'][m]['test_success']])}")

    # 保存详细报告
    report_file = f"connectivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n📄 详细报告已保存: {report_file}")

    return results


def generate_markdown_report(results: Dict):
    """生成Markdown格式的报告"""
    report = []
    report.append("# 模型连通性测试报告\n")
    report.append(f"**测试时间**: {results['test_time']}\n")
    report.append(f"**测试模型数**: {results['total_models']}\n")
    report.append(f"**成功**: {results['successful']} | **失败**: {results['failed']}\n")

    report.append("\n## 详细结果\n")
    report.append("| 模型 | 提供商 | API状态 | 响应时间 | 备注 |\n")
    report.append("|------|--------|---------|----------|------|\n")

    for model, detail in sorted(results["details"].items()):
        status = "✅" if detail["test_success"] else "❌"
        time_str = f"{detail['response_time']}s" if detail["test_success"] else "N/A"
        has_key = "有" if detail["has_api_key"] else "无"

        # 简化消息
        if detail["test_success"]:
            note = "连接正常"
        else:
            # 提取主要错误原因
            if "API Key" in detail["message"]:
                note = "缺少API密钥"
            elif "timeout" in detail["message"].lower():
                note = "连接超时"
            elif "refused" in detail["message"].lower():
                note = "连接被拒绝"
            else:
                note = "连接失败"

        report.append(f"| {model} | {detail['provider']} | {status} | {time_str} | {note} |\n")

    report.append("\n## 问题诊断\n")

    # 找出失败的模型
    failed_models = {m: d for m, d in results["details"].items() if not d["test_success"]}

    if failed_models:
        report.append("\n### 失败的模型:\n")
        for model, detail in failed_models.items():
            report.append(f"- **{model}** ({detail['provider']}):\n")
            if not detail["has_api_key"]:
                report.append(f"  - 问题: 缺少API密钥\n")
                report.append(f"  - 解决: 在对应的配置文件中设置API密钥\n")
            else:
                report.append(f"  - 问题: {detail['message']}\n")
            report.append("\n")
    else:
        report.append("✅ 所有模型连接正常！\n")

    # 保存报告
    report_file = f"connectivity_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(''.join(report))

    print(f"\n📝 Markdown报告已生成: {report_file}")

    return report_file


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🚀 开始模型连通性测试")
    print("="*80)

    print("\n⚠️  注意事项:")
    print("  1. 此测试会对每个模型发送一个简单请求")
    print("  2. 会消耗少量API配额")
    print("  3. 测试时间取决于模型数量和响应速度")

    choice = input("\n是否继续？(Y/n): ")
    if choice.lower() == 'n':
        print("测试已取消")
        return

    # 运行测试
    results = run_connectivity_test()

    # 生成Markdown报告
    generate_markdown_report(results)

    # 给出建议
    print("\n" + "="*80)
    print("💡 建议")
    print("="*80)

    if results["failed"] > 0:
        print("\n⚠️  有模型连接失败，请检查:")
        print("  1. API密钥是否正确设置")
        print("  2. 网络连接是否正常")
        print("  3. API服务是否可用")
        print("  4. 配额是否充足")
    else:
        print("\n✅ 所有模型连接正常，可以开始交叉评估！")

    print("\n运行交叉评估:")
    print("  python run_cross_evaluation.py --test-mode")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()