#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI自动评分脚本
使用大模型API对医疗AI输出进行自动评分
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm
from datetime import datetime

# 支持多个API
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("警告: 未安装openai库，无法使用OpenAI API")

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False
    print("警告: 未安装anthropic库，无法使用Claude API")


class AIModelEvaluator:
    """AI模型输出自动评分器"""

    def __init__(self, api_provider='openai', model_name=None, api_key=None):
        """
        初始化评分器

        Args:
            api_provider: API提供商 ('openai', 'claude', 'local')
            model_name: 模型名称
            api_key: API密钥（可选，会从环境变量读取）
        """
        self.api_provider = api_provider
        self.api_key = api_key or self._get_api_key()

        # 默认模型
        if model_name is None:
            if api_provider == 'openai':
                model_name = 'gpt-4-turbo-preview'
            elif api_provider == 'claude':
                model_name = 'claude-3-5-sonnet-20241022'

        self.model_name = model_name

        # 初始化客户端
        self._init_client()

        # 加载评分标准
        self.scoring_prompt = self._load_scoring_prompt()

    def _get_api_key(self):
        """从环境变量获取API密钥"""
        if self.api_provider == 'openai':
            return os.getenv('OPENAI_API_KEY')
        elif self.api_provider == 'claude':
            return os.getenv('ANTHROPIC_API_KEY')
        return None

    def _init_client(self):
        """初始化API客户端"""
        if self.api_provider == 'openai':
            if not HAS_OPENAI:
                raise ImportError("请安装openai库: pip install openai")
            self.client = OpenAI(api_key=self.api_key)

        elif self.api_provider == 'claude':
            if not HAS_ANTHROPIC:
                raise ImportError("请安装anthropic库: pip install anthropic")
            self.client = anthropic.Anthropic(api_key=self.api_key)

        elif self.api_provider == 'local':
            # 本地模型（需要额外配置）
            print("使用本地模型...")
            self.client = None

    def _load_scoring_prompt(self):
        """加载评分标准Prompt"""
        prompt_file = Path(__file__).parent / 'ai_scoring_prompt.md'

        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 提取Prompt模板部分
                start = content.find('```markdown')
                end = content.find('```', start + 11)
                if start != -1 and end != -1:
                    return content[start+11:end].strip()

        # 如果文件不存在，返回简化版
        return self._get_default_prompt()

    def _get_default_prompt(self):
        """获取默认的评分Prompt"""
        return """你是一位专业的医疗AI模型输出质量评测专家。请对医疗AI模型生成的病历信息提取结果进行评分。

评分标准（总分100分）：
1. 信息准确性（30分）：无错误、无曲解
2. 信息完整性（25分）：无关键遗漏
3. 临床实用性（20分）：突出重点、助决策
4. 结构清晰度（15分）：层次分明、易查找
5. 语言专业性（10分）：专业简洁

请以JSON格式输出评分结果，包含：scores（各维度详细评分）、total_score、grade、overall_evaluation、strengths、weaknesses、recommendations。"""

    def evaluate(self, original_record: str, model_output: str) -> Dict:
        """
        评分单个案例

        Args:
            original_record: 原始问诊记录
            model_output: 模型输出

        Returns:
            评分结果字典
        """
        # 构建完整prompt
        full_prompt = f"""{self.scoring_prompt}

---

**原始问诊记录**：
```
{original_record}
```

**模型输出**：
```markdown
{model_output}
```

请你根据评分标准对模型输出进行评分，以JSON格式输出。"""

        # 调用API
        try:
            if self.api_provider == 'openai':
                result = self._evaluate_openai(full_prompt)
            elif self.api_provider == 'claude':
                result = self._evaluate_claude(full_prompt)
            else:
                raise ValueError(f"不支持的API提供商: {self.api_provider}")

            return result

        except Exception as e:
            print(f"评分失败: {e}")
            return self._get_error_result(str(e))

    def _evaluate_openai(self, prompt: str) -> Dict:
        """使用OpenAI API评分"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "你是专业的医疗AI评测专家，请严格按照评分标准进行评分。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,  # 低温度保证一致性
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        return json.loads(result_text)

    def _evaluate_claude(self, prompt: str) -> Dict:
        """使用Claude API评分"""
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            temperature=0.2,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        result_text = response.content[0].text
        # 提取JSON
        start = result_text.find('{')
        end = result_text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(result_text[start:end])
        else:
            return json.loads(result_text)

    def _get_error_result(self, error_msg: str) -> Dict:
        """返回错误结果"""
        return {
            "error": True,
            "error_message": error_msg,
            "total_score": 0,
            "grade": "ERROR",
            "scores": {}
        }

    def batch_evaluate(self, cases: List[Dict], output_file: str = None) -> pd.DataFrame:
        """
        批量评分

        Args:
            cases: 案例列表，每个案例包含 {id, original_record, model_output, model_name}
            output_file: 输出文件路径（JSON）

        Returns:
            评分结果DataFrame
        """
        results = []

        print(f"开始批量评分，共 {len(cases)} 个案例...")

        for case in tqdm(cases, desc="评分进度"):
            case_id = case.get('id', 'unknown')
            original = case['original_record']
            output = case['model_output']
            model_name = case.get('model_name', 'Unknown')

            # 评分
            score_result = self.evaluate(original, output)

            # 添加案例信息
            score_result['case_id'] = case_id
            score_result['model_name'] = model_name
            score_result['timestamp'] = datetime.now().isoformat()

            results.append(score_result)

        # 保存详细结果
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"详细结果已保存: {output_file}")

        # 生成汇总表
        df = self._generate_summary(results)

        # 保存汇总表
        if output_file:
            summary_file = output_file.replace('.json', '_summary.csv')
            df.to_csv(summary_file, index=False, encoding='utf-8-sig')
            print(f"汇总表已保存: {summary_file}")

        return df

    def _generate_summary(self, results: List[Dict]) -> pd.DataFrame:
        """生成汇总表"""
        summary_data = []

        for r in results:
            if r.get('error'):
                continue

            scores = r.get('scores', {})

            summary_data.append({
                'case_id': r.get('case_id'),
                'model': r.get('model_name'),
                'total': r.get('total_score', 0),
                'accuracy': scores.get('accuracy', {}).get('score', 0),
                'completeness': scores.get('completeness', {}).get('score', 0),
                'clinical': scores.get('clinical_utility', {}).get('score', 0),
                'structure': scores.get('structure', {}).get('score', 0),
                'language': scores.get('language', {}).get('score', 0),
                'grade': r.get('grade', ''),
                'usability': r.get('clinical_usability', '')
            })

        df = pd.DataFrame(summary_data)

        # 打印统计信息
        if len(df) > 0:
            print("\n=== 评分统计 ===")
            print(f"平均分: {df['total'].mean():.1f}")
            print(f"最高分: {df['total'].max()}")
            print(f"最低分: {df['total'].min()}")
            print(f"标准差: {df['total'].std():.1f}")

            print("\n各维度平均分:")
            for col in ['accuracy', 'completeness', 'clinical', 'structure', 'language']:
                print(f"  {col}: {df[col].mean():.1f}")

        return df


def main():
    """示例：使用评分器"""

    # 示例案例
    test_case = {
        'id': 'test_001',
        'model_name': 'TestModel',
        'original_record': """患者男，50多岁，182cm，64kg。12年前小便泡沫多发现糖尿病，
用过胰岛素后停，现用二甲双胍早晚各1次、司美格鲁肽每周1次、
格列齐特早2粒、多格列艾汀早晚各1次。空腹血糖11，未测餐后。
5个月前住院，出院后2月内瘦了10多斤。母亲、舅舅、哥哥都有糖尿病。
甘油三酯高，未治疗。""",
        'model_output': """# 患者基本信息
- 性别：男
- 年龄：50-55岁
- 身高：182 cm
- 体重：64 kg

## 主诉
配药

## 现病史
患者12年前因小便泡沫多就诊，发现血糖升高，诊断为2型糖尿病。

### 治疗经过
- 既往使用胰岛素（已停用）
- 当前方案：二甲双胍早晚各1次、司美格鲁肽每周1次、格列齐特早2粒、多格列艾汀早晚各1次

### 近期变化
- 5个月前住院
- 出院后2月内体重下降10余斤

## 既往史
- 高甘油三酯血症（未服药治疗）

## 家族史
- 母亲、舅舅、哥哥均有糖尿病"""
    }

    # 初始化评分器（使用OpenAI）
    # 请先设置环境变量: export OPENAI_API_KEY=your-key
    evaluator = AIModelEvaluator(
        api_provider='openai',
        model_name='gpt-4-turbo-preview'
    )

    # 单个评分
    print("开始评分...")
    result = evaluator.evaluate(
        test_case['original_record'],
        test_case['model_output']
    )

    print(f"\n总分: {result['total_score']}/100")
    print(f"等级: {result['grade']}")
    print(f"\n总体评价: {result.get('overall_evaluation', '')}")

    print("\n优点:")
    for s in result.get('strengths', []):
        print(f"  ✓ {s}")

    print("\n不足:")
    for w in result.get('weaknesses', []):
        print(f"  ✗ {w}")

    # 批量评分示例
    # cases = [test_case]  # 可以添加更多案例
    # df = evaluator.batch_evaluate(cases, 'evaluation_results.json')
    # print(df)


if __name__ == '__main__':
    main()
