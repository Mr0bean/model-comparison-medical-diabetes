"""
生成模型对比页面
读取 output/raw/ 目录下的所有JSON文件，生成HTML对比页面
X轴：患者（患者1-10）
Y轴：模型
"""
import json
import os
from pathlib import Path
from typing import Dict, List
from collections import defaultdict


def load_all_results(output_dir: str = "./output/raw") -> Dict[str, Dict[str, dict]]:
    """
    加载所有结果文件

    返回结构: {
        '模型名': {
            '患者1': {...},
            '患者2': {...},
            ...
        }
    }
    """
    results = defaultdict(dict)
    output_path = Path(output_dir)

    print(f"正在扫描目录: {output_dir}")

    for file_path in sorted(output_path.glob("*.json")):
        print(f"  读取: {file_path.name}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        model = data.get('model', '')
        people = data.get('people', '')

        if model and people:
            results[model][people] = data

    print(f"\n成功加载 {len(results)} 个模型的数据")
    for model, patients in results.items():
        print(f"  {model}: {len(patients)} 个患者")

    return dict(results)


def generate_html(results: Dict[str, Dict[str, dict]], output_file: str = "comparison.html"):
    """生成HTML对比页面"""

    # 获取所有模型和患者
    models = sorted(results.keys())
    all_patients = set()
    for patients in results.values():
        all_patients.update(patients.keys())
    patients = sorted(all_patients, key=lambda x: (len(x), x))  # 按长度和名称排序

    print(f"\n生成对比页面:")
    print(f"  模型数: {len(models)}")
    print(f"  患者数: {len(patients)}")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM模型对比 - 患者病历生成</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 95%;
            margin: 0 auto;
        }}

        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 36px;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .stats {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }}

        .stat-item {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 8px;
            color: white;
            transition: transform 0.2s;
        }}

        .stat-item:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        }}

        .stat-label {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 8px;
            font-weight: 500;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: bold;
        }}

        .comparison-wrapper {{
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}

        .table-container {{
            display: flex;
            overflow: hidden;
            max-height: 800px;
        }}

        .table-left {{
            flex-shrink: 0;
            overflow-y: auto;
            overflow-x: hidden;
            border-right: 2px solid #e9ecef;
        }}

        .table-left::-webkit-scrollbar {{
            display: none;
        }}

        .table-right {{
            flex: 1;
            overflow: auto;
        }}

        .table-left table, .table-right table {{
            table-layout: auto;
        }}

        .table-right::-webkit-scrollbar {{
            height: 8px;
        }}

        .table-right::-webkit-scrollbar-track {{
            background: #f1f1f1;
        }}

        .table-right::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}

        .table-right::-webkit-scrollbar-thumb:hover {{
            background: #764ba2;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 16px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}

        th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
            white-space: nowrap;
        }}

        .table-left th {{
            background: linear-gradient(135deg, #5568d3 0%, #6a3f91 100%);
        }}

        tr:hover {{
            background: #f8f9ff;
        }}

        .model-cell {{
            font-weight: 600;
            color: #495057;
            background: linear-gradient(135deg, #f8f9ff 0%, #e9ecef 100%);
            white-space: nowrap;
        }}

        .result-cell {{
            cursor: pointer;
            position: relative;
            min-width: 300px;
            max-width: 500px;
            transition: background 0.2s;
        }}

        .result-cell:hover {{
            background: #e9ecff;
        }}

        .result-preview {{
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
            line-height: 1.6;
            color: #495057;
            font-size: 14px;
            word-wrap: break-word;
            white-space: normal;
        }}

        .empty-result {{
            color: #dc3545;
            font-style: italic;
        }}

        .result-stats {{
            display: flex;
            gap: 8px;
            margin-top: 8px;
            font-size: 11px;
            color: #6c757d;
            flex-wrap: wrap;
        }}

        .stat-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 500;
        }}

        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.6);
            z-index: 1000;
            overflow: auto;
            animation: fadeIn 0.2s;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        .modal-content {{
            background: white;
            margin: 50px auto;
            padding: 35px;
            max-width: 1000px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            animation: slideDown 0.3s;
        }}

        @keyframes slideDown {{
            from {{
                transform: translateY(-50px);
                opacity: 0;
            }}
            to {{
                transform: translateY(0);
                opacity: 1;
            }}
        }}

        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 3px solid;
            border-image: linear-gradient(90deg, #667eea 0%, #764ba2 100%) 1;
        }}

        .modal-title {{
            font-size: 26px;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .close {{
            font-size: 36px;
            color: #6c757d;
            cursor: pointer;
            background: none;
            border: none;
            transition: all 0.2s;
            line-height: 1;
        }}

        .close:hover {{
            color: #dc3545;
            transform: rotate(90deg);
        }}

        .conversation-output {{
            background: #f8f9ff;
            padding: 25px;
            border-radius: 8px;
            white-space: pre-wrap;
            line-height: 1.8;
            border: 2px solid #e9ecef;
            font-size: 15px;
            color: #2c3e50;
            max-height: 600px;
            overflow-y: auto;
        }}

        .conversation-output::-webkit-scrollbar {{
            width: 8px;
        }}

        .conversation-output::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 4px;
        }}

        .conversation-output::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}

        .conversation-output::-webkit-scrollbar-thumb:hover {{
            background: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔬 LLM 模型对比分析</h1>

        <div class="stats">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">模型总数</div>
                    <div class="stat-value">{len(models)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">患者总数</div>
                    <div class="stat-value">{len(patients)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">总对话数</div>
                    <div class="stat-value">{len(models) * len(patients)}</div>
                </div>
            </div>
        </div>

        <div class="comparison-wrapper">
            <div class="table-container">
                <!-- 左侧固定列：模型名称 -->
                <div class="table-left">
                    <table id="leftTable">
                        <thead>
                            <tr>
                                <th>模型</th>
                            </tr>
                        </thead>
                        <tbody id="leftBody">
"""

    # 左侧表格：模型名称列
    for model in models:
        html += f"""                            <tr>
                                <td class=\"model-cell\">{model}</td>
                            </tr>
"""

    html += """                        </tbody>
                    </table>
                </div>

                <!-- 右侧可滚动区域：患者数据 -->
                <div class="table-right" id="rightTable">
                    <table>
                        <thead>
                            <tr>
"""

    # 表头：患者列
    for patient in patients:
        html += f"                                <th>{patient}</th>\n"

    html += """                            </tr>
                        </thead>
                        <tbody>
"""

    # 表格内容：每个模型一行
    for model in models:
        html += f"                            <tr>\n"

        for patient in patients:
            data = results[model].get(patient, {})

            if data:
                # 获取结果预览
                result = data.get('result', '')
                conversations = data.get('conversations', {})
                conv_count = len(conversations)

                # 计算总字符数
                total_chars = sum(len(conv.get('Output', '')) for conv in conversations.values())

                # 检查是否有空输出
                empty_count = sum(1 for conv in conversations.values() if not conv.get('Output', '').strip())

                preview = result[:200] if result else '(无内容)'

                html += f"""                                <td class=\"result-cell\" onclick=\"showModal('{model}', '{patient}')\">
                                    <div class=\"result-preview {'empty-result' if empty_count > 0 else ''}\">{preview}...</div>
                                    <div class=\"result-stats\">
                                        <span class=\"stat-badge\">对话: {conv_count}</span>
                                        <span class=\"stat-badge\">字符: {total_chars}</span>
"""
                if empty_count > 0:
                    html += f"                                        <span class=\"stat-badge\" style=\"background: #ffe5e5; color: #dc3545;\">空: {empty_count}</span>\n"

                html += """                                    </div>
                                </td>
"""
            else:
                html += """                                <td class=\"result-cell\">
                                    <div class=\"empty-result\">数据缺失</div>
                                </td>
"""

        html += "                            </tr>\n"

    html += """                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- 弹窗 -->
    <div id="modal" class="modal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h2 class="modal-title" id="modalTitle"></h2>
                <button class="close" onclick="closeModal()">&times;</button>
            </div>
            <div id="modalBody"></div>
        </div>
    </div>

    <script>
        // 数据存储
        const data = """ + json.dumps(results, ensure_ascii=False) + """;

        // 联动滚动：同步左右表格的垂直和水平滚动
        const leftTable = document.querySelector('.table-left');
        const rightTable = document.getElementById('rightTable');

        let isLeftScrolling = false;
        let isRightScrolling = false;

        rightTable.addEventListener('scroll', () => {
            if (isLeftScrolling) {
                isLeftScrolling = false;
                return;
            }
            isRightScrolling = true;
            // 同步垂直滚动
            leftTable.scrollTop = rightTable.scrollTop;
        });

        leftTable.addEventListener('scroll', () => {
            if (isRightScrolling) {
                isRightScrolling = false;
                return;
            }
            isLeftScrolling = true;
            // 同步垂直滚动
            rightTable.scrollTop = leftTable.scrollTop;
        });

        function showModal(model, patient) {
            const modalData = data[model][patient];
            if (!modalData) return;

            document.getElementById('modalTitle').textContent = `${model} - ${patient}`;

            // 直接显示result字段
            const result = modalData.result || '（无内容）';

            const html = `
                <div class="conversation-output" style="white-space: pre-wrap; line-height: 1.8;">
                    ${result}
                </div>
            `;

            document.getElementById('modalBody').innerHTML = html;
            document.getElementById('modal').style.display = 'block';
        }

        function closeModal(event) {
            if (!event || event.target.id === 'modal') {
                document.getElementById('modal').style.display = 'none';
            }
        }

        // ESC键关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') closeModal();
        });
    </script>
</body>
</html>
"""

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ 对比页面已生成: {output_file}")
    print(f"   请在浏览器中打开此文件查看")


def main():
    print("=" * 80)
    print("生成模型对比页面")
    print("=" * 80)
    print()

    # 加载数据
    results = load_all_results("./output/raw")

    if not results:
        print("\n❌ 未找到任何结果文件！")
        return

    # 生成HTML
    generate_html(results, "comparison.html")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
