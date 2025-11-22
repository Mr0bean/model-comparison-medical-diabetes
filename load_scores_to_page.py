#!/usr/bin/env python3
"""将评估分数数据注入到HTML页面中"""

import json
from pathlib import Path

# 读取报告数据
report_file = Path("FINAL_COMPLETE_640_REPORT_V2.json")

if not report_file.exists():
    print("❌ 错误: FINAL_COMPLETE_640_REPORT_V2.json 不存在")
    print("   请先运行 generate_final_report.py")
    exit(1)

with open(report_file, 'r', encoding='utf-8') as f:
    report_data = json.load(f)

# 读取HTML模板
html_file = Path("evaluation_scores.html")

if not html_file.exists():
    print("❌ 错误: evaluation_scores.html 不存在")
    exit(1)

with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 创建数据注入脚本
data_json = json.dumps(report_data, ensure_ascii=False, indent=2)

inject_script = f"""
    <script>
        // 自动加载评估数据到localStorage
        (function() {{
            const reportData = {data_json};
            localStorage.setItem('FINAL_COMPLETE_640_REPORT_V2', JSON.stringify(reportData));
            console.log('✅ 评估数据已加载到localStorage');
        }})();
    </script>
"""

# 在</head>之前插入脚本
html_with_data = html_content.replace('</head>', inject_script + '\n</head>')

# 保存新的HTML文件
output_file = Path("evaluation_scores_with_data.html")
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_with_data)

print(f"✅ 已生成包含数据的页面: {output_file}")
print()
print("📊 数据统计:")
print(f"   总评估数: {report_data.get('total_evaluations', 0)}")
print(f"   有效评估: {report_data.get('valid_evaluations', 0)}")
print(f"   零分评估: {report_data.get('zero_evaluations', 0)}")
print(f"   完成率: {report_data.get('completion_status', 'N/A')}")
print()
print(f"🌐 访问地址: http://localhost:8000/{output_file.name}")
print(f"   或者直接双击打开 {output_file.name}")
