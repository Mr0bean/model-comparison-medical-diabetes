# 批量多模型测试工具使用说明

## 功能概述

这个工具用于批量测试多个AI模型对患者问答记录的分析能力。主要功能：

1. **读取多个Prompt** - 从"多个Prompt"文件中读取不同的分析任务
2. **加载患者数据** - 从"测试输入问答记录"文件夹加载所有患者的问答记录
3. **多模型测试** - 对每个患者使用每个Prompt测试多个AI模型
4. **生成结构化报告** - 输出包含所有输入和输出的JSON格式结果

## 文件结构

```
chat/
├── batch_model_test.py          # 批量测试主程序
├── 多个Prompt                    # Prompt文件（每行一个独立Prompt）
├── 测试输入问答记录/              # 患者问答记录文件夹
│   ├── 患者1_问答记录.txt
│   ├── 患者2_问答记录.txt
│   └── ...
└── batch_test_results_*.json    # 输出结果文件
```

## 支持的模型

当前支持以下6个模型（通过JieKou AI统一接口）：

1. `gpt-4o` - OpenAI GPT-4o
2. `gpt-4o-mini` - OpenAI GPT-4o Mini
3. `claude-3-5-sonnet-20241022` - Anthropic Claude 3.5 Sonnet
4. `deepseek/deepseek-r1` - DeepSeek R1
5. `deepseek/deepseek-chat` - DeepSeek Chat
6. `gemini/gemini-2.0-flash-exp` - Google Gemini 2.0 Flash

## 使用步骤

### 1. 准备Prompt文件

编辑 `多个Prompt` 文件，每行写一个独立的分析任务。例如：

```
请根据患者的问答记录，分析患者的糖尿病病情严重程度，包括血糖控制情况、并发症风险、用药依从性等方面，并给出1-10分的严重程度评分（1分最轻，10分最严重）。
请评估患者当前的用药方案是否合理，包括药物种类、剂量、用药频率等，并指出是否存在潜在的药物相互作用或不合理用药情况。
请根据患者的病史、家族史、生活方式等信息，识别患者面临的主要健康风险因素，并按风险等级排序。
```

### 2. 确保患者数据已准备好

确保 `测试输入问答记录/` 文件夹中包含患者问答记录文件，文件命名格式：`患者X_问答记录.txt`

### 3. 配置API Key

确保 `.env` 文件或 `config.py` 中已正确配置 API Key：

```bash
JIEKOU_API_KEY=your_api_key_here
```

### 4. 运行测试

```bash
python batch_model_test.py
```

### 5. 自定义配置（可选）

在 `batch_model_test.py` 的 `main()` 函数中可以自定义：

```python
# 指定特定模型进行测试
MODELS_TO_TEST = ["gpt-4o", "claude-3-5-sonnet-20241022"]

# 修改输出文件名
OUTPUT_FILE = "my_custom_results.json"
```

## 输出结果格式

生成的JSON文件结构如下：

```json
{
  "meta": {
    "timestamp": "2025-11-15T23:30:00",
    "total_prompts": 5,
    "total_patients": 10,
    "total_models": 6,
    "models": ["gpt-4o", "claude-3-5-sonnet-20241022", ...]
  },
  "prompts": [
    "Prompt 1内容...",
    "Prompt 2内容...",
    ...
  ],
  "patients": [
    {
      "patient_id": "患者1",
      "patient_info": {
        "name": "患者1",
        "age": "50-55岁",
        "gender": "男",
        "height": "182.0cm",
        "weight": "64.0kg",
        "bmi": "19.3"
      },
      "conversation": "完整的问答记录...",
      "prompt_results": [
        {
          "prompt_index": 0,
          "prompt": "Prompt内容...",
          "model_responses": [
            {
              "model": "gpt-4o",
              "success": true,
              "response": "模型的分析结果...",
              "error": null,
              "timestamp": "2025-11-15T23:30:01"
            },
            {
              "model": "claude-3-5-sonnet-20241022",
              "success": true,
              "response": "模型的分析结果...",
              "error": null,
              "timestamp": "2025-11-15T23:30:05"
            },
            ...
          ]
        },
        ...
      ]
    },
    ...
  ]
}
```

## 示例Prompt

文件中已包含5个示例Prompt：

1. **病情严重程度分析** - 评估患者糖尿病的严重程度并打分
2. **用药方案评估** - 分析用药的合理性和潜在问题
3. **健康风险识别** - 识别并排序主要健康风险因素
4. **诊疗建议** - 提供个性化的诊疗和生活方式建议
5. **患者诉求分析** - 总结患者关注的问题和诉求

## 运行时间估算

- 单个模型响应时间：约5-15秒
- 测试配置：10个患者 × 5个Prompt × 6个模型 = 300次API调用
- 预计总时间：约25-75分钟（取决于网络速度和API响应时间）

## 注意事项

1. **API配额** - 确保API账户有足够的配额，大批量测试会消耗较多token
2. **网络稳定性** - 建议在网络稳定的环境下运行
3. **错误处理** - 程序会自动记录失败的调用，不会中断整体流程
4. **进度显示** - 使用tqdm显示实时进度，方便监控
5. **结果备份** - 每次运行会生成带时间戳的新文件，不会覆盖旧结果

## 故障排查

### 问题1：API Key错误
```
ValueError: API Key未配置
```
**解决方案**：检查 `.env` 文件或 `config.py` 中的API Key配置

### 问题2：找不到患者文件
```
没有找到患者记录，无法继续
```
**解决方案**：确认 `测试输入问答记录/` 文件夹存在且包含正确命名的文件

### 问题3：Prompt文件为空
```
没有找到Prompt，无法继续
```
**解决方案**：在 `多个Prompt` 文件中添加至少一行Prompt内容

### 问题4：某个模型持续失败
- 查看控制台输出的错误信息
- 检查该模型在JieKou AI平台是否可用
- 尝试在 `MODELS_TO_TEST` 中排除该模型

## 高级用法

### 只测试部分模型

```python
# 只测试GPT-4o和Claude
processor = BatchProcessor(
    prompt_file=PROMPT_FILE,
    patients_dir=PATIENTS_DIR,
    models=["gpt-4o", "claude-3-5-sonnet-20241022"],
    output_file=OUTPUT_FILE
)
```

### 只测试部分患者

修改 `_load_patient_records` 方法：

```python
def _load_patient_records(self) -> List[PatientRecord]:
    # 只加载患者1-3
    pattern = "患者[1-3]_问答记录.txt"
    patient_files = sorted(Path(self.patients_dir).glob(pattern))
    ...
```

### 自定义温度等参数

在 `test_single_case` 方法中修改：

```python
response = client.simple_chat(
    message=user_message,
    stream=False,
    temperature=0.5,  # 调整温度
    max_tokens=8192   # 调整最大token数
)
```

## 后续分析

生成的JSON文件可以用于：

1. **横向对比** - 比较不同模型对同一患者的分析差异
2. **纵向分析** - 分析同一模型对不同患者的一致性
3. **质量评估** - 评估各模型的回答质量和准确性
4. **报告生成** - 自动生成患者分析报告
5. **模型选择** - 为特定任务选择最合适的模型

## 技术支持

如有问题，请检查：
1. 日志输出 - 程序会输出详细的日志信息
2. 错误信息 - JSON结果中包含每个失败调用的错误详情
3. API状态 - 访问 JieKou AI 平台检查服务状态
