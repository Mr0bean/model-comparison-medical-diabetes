# 医疗报告Prompt说明

本目录存放用于生成糖尿病医疗报告的Prompt模板。

## 文件说明

### 4个Prompt.json
包含4个用于生成病历不同部分的Prompt：

1. **主诉（Chief Complaint）**
   - 生成患者就诊时最主要、最核心的、与糖尿病直接相关的不适症状及持续时间
   - 特点：简洁明了，突出主要症状，时间单位明确

2. **现病史（Present Illness History）**
   - 描述糖尿病的既往情况和现状
   - 包含：发病经过、诊疗经过、病情演变、近期变化等
   - 特点：结构分明，时间与量化表达精准

3. **既往史（Past Medical History）**
   - 记录除糖尿病以外的其他疾病情况
   - 包含：疾病名称、病程时间、治疗情况、控制效果等
   - 特点：使用规范医学术语，记录准确

4. **家族史（Family History）**
   - 记录糖尿病家族遗传情况
   - 包含：是否有家族史、代数、父系/母系、同胞情况等
   - 特点：格式标准化

## 使用说明

这些Prompt用于AI模型评测，通过医生助手与患者的对话记录，自动生成标准化的病历文档。

### 评测流程
1. 准备患者问答记录（存放在 `测试输入问答记录` 目录）
2. 使用 `unified_batch_processor.py` 进行批量处理
3. 配置文件中指定 `prompts_file: "PromptForMedicalReport/4个Prompt.json"`
4. 生成的评测结果存放在 `output/raw` 目录

### 配置示例
```json
{
  "prompts_file": "PromptForMedicalReport/4个Prompt.json",
  "records_dir": "测试输入问答记录",
  "output_dir": "./output/raw",
  "models": ["gemini-3-pro-preview"],
  "max_retries": 50,
  "max_tokens": 8000
}
```

## 注意事项

- 所有Prompt都强调**只输出指定内容**，不输出思考过程
- 使用专业医学术语，避免口语化表达
- 严格按照医学文书规范进行格式化输出
- 如果问诊中未提及某些内容，则不在病历中显示相关字段
