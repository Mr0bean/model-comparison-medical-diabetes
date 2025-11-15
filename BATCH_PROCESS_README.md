# 医疗问答批量处理系统

基于多模型对比的医疗问答记录批量处理系统，支持自动重试、并发处理和详细日志记录。

## 功能特性

- **多模型对比**：同时使用多个AI模型（如 gpt-4o-mini, gpt-5.1）处理相同患者数据
- **批量处理**：自动处理多个患者的问答记录
- **自动重试**：网络异常时自动重试（指数退避策略）
- **并发执行**：提高处理效率，同时保证输出顺序
- **配置文件**：通过 JSON 配置文件灵活配置
- **详细日志**：记录完整的处理过程和错误信息

## 系统要求

- Python 3.7+
- 依赖包：
  - asyncio（Python 内置）
  - chat_client（自定义聊天客户端）
  - openai
  - pydantic
  - python-dotenv

## 目录结构

```
.
├── batch_process_new_format.py  # 主程序
├── batch_config.json            # 配置文件
├── chat_client.py               # 聊天客户端
├── config.py                    # 配置管理
├── 多个Prompt.json              # Prompt模板文件
├── 测试输入问答记录/            # 患者问答记录目录
│   ├── 患者1_问答记录.txt
│   ├── 患者2_问答记录.txt
│   └── ...
└── output/                      # 输出目录
    └── raw/                     # 原始输出
        ├── gpt-4o-mini-患者1.json
        ├── gpt-5.1-患者1.json
        └── ...
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

复制 `.env.example` 为 `.env` 并填入你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
JIEKOU_API_KEY=your_actual_api_key_here
JIEKOU_BASE_URL=https://api.jiekou.ai/openai
DEFAULT_MODEL=gpt-4o-mini
```

### 3. 配置批量处理参数

编辑 `batch_config.json` 文件：

```json
{
  "prompts_file": "多个Prompt.json",
  "records_dir": "测试输入问答记录",
  "output_dir": "./output/raw",
  "models": [
    "gpt-4o-mini",
    "gpt-5.1"
  ],
  "max_retries": 3,
  "max_tokens": 2000,
  "log_file": "batch_process_new.log",
  "log_level": "INFO"
}
```

### 4. 运行批量处理

```bash
python batch_process_new_format.py
```

## 配置文件详解

### batch_config.json 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| prompts_file | string | 是 | - | Prompt模板文件路径 |
| records_dir | string | 是 | - | 患者问答记录目录 |
| output_dir | string | 否 | "./output/raw" | 输出文件保存目录 |
| models | array | 否 | ["gpt-4o-mini", "gpt-5.1"] | 使用的AI模型列表 |
| max_retries | integer | 否 | 3 | API调用失败时的最大重试次数 |
| max_tokens | integer | 否 | 2000 | 单次对话的最大Token数 |
| log_file | string | 否 | "batch_process_new.log" | 日志文件名 |
| log_level | string | 否 | "INFO" | 日志级别（DEBUG/INFO/WARNING/ERROR/CRITICAL） |

### 配置示例

#### 1. 基础配置（默认）

```json
{
  "prompts_file": "多个Prompt.json",
  "records_dir": "测试输入问答记录",
  "output_dir": "./output/raw",
  "models": ["gpt-4o-mini", "gpt-5.1"],
  "max_retries": 3,
  "max_tokens": 2000,
  "log_file": "batch_process_new.log",
  "log_level": "INFO"
}
```

#### 2. 多模型对比配置

```json
{
  "prompts_file": "多个Prompt.json",
  "records_dir": "测试输入问答记录",
  "output_dir": "./output/raw",
  "models": [
    "gpt-4o-mini",
    "gpt-5.1",
    "gpt-4-turbo",
    "deepseek/deepseek-r1"
  ],
  "max_retries": 5,
  "max_tokens": 3000,
  "log_file": "batch_process_new.log",
  "log_level": "INFO"
}
```

#### 3. 调试配置

```json
{
  "prompts_file": "多个Prompt.json",
  "records_dir": "测试输入问答记录",
  "output_dir": "./output/raw",
  "models": ["gpt-4o-mini"],
  "max_retries": 1,
  "max_tokens": 500,
  "log_file": "batch_debug.log",
  "log_level": "DEBUG"
}
```

## 输入文件格式

### 1. Prompt文件 (`多个Prompt.json`)

JSON数组格式，每个元素是一个Prompt模板：

```json
[
  "根据以下对话，提取患者的主诉：...",
  "根据以下对话，总结现病史：...",
  "根据以下对话，总结既往史：...",
  "根据以下对话，生成完整预病历：...",
  "根据以下对话，总结家族史：..."
]
```

### 2. 患者问答记录 (`患者X_问答记录.txt`)

纯文本格式，包含患者与医生的完整对话记录。

**文件命名规则：**
- 格式：`{患者编号}_问答记录.txt`
- 示例：`患者1_问答记录.txt`、`患者2_问答记录.txt`
- 系统会自动去掉 `_问答记录` 后缀作为患者编号

## 输出格式

### 文件命名

每个（模型 + 患者）组合生成一个独立的JSON文件：

```
{model}-{people}.json
```

示例：
- `gpt-4o-mini-患者1.json`
- `gpt-5.1-患者1.json`
- `gpt-4o-mini-患者2.json`
- `gpt-5.1-患者2.json`

### JSON结构

```json
{
  "model": "gpt-4o-mini",
  "people": "患者1",
  "conversations": {
    "1": {
      "model": "gpt-4o-mini",
      "prompt": "根据以下对话，提取患者的主诉：...",
      "people": "患者1",
      "chat": "患者与医生的完整对话记录...",
      "Input": "Prompt + Chat 合并后的输入",
      "Output": "AI生成的主诉"
    },
    "2": {
      "model": "gpt-4o-mini",
      "prompt": "根据以下对话，总结现病史：...",
      "people": "患者1",
      "chat": "患者与医生的完整对话记录...",
      "Input": "Prompt + Chat 合并后的输入",
      "Output": "AI生成的现病史"
    },
    "3": {...},
    "4": {...},
    "5": {...}
  },
  "result": "主诉内容\n现病史内容\n既往史内容\n完整预病历内容\n家族史内容"
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| model | string | 使用的AI模型名称 |
| people | string | 患者编号（从文件名提取） |
| conversations | object | 对话记录对象，键为字符串 "1", "2", "3"... |
| conversations.{index}.model | string | 该对话使用的模型 |
| conversations.{index}.prompt | string | 使用的Prompt模板 |
| conversations.{index}.people | string | 患者编号 |
| conversations.{index}.chat | string | 患者问答记录 |
| conversations.{index}.Input | string | 发送给AI的完整输入（Prompt + Chat） |
| conversations.{index}.Output | string | AI的回复内容 |
| result | string | 所有对话输出的拼接结果（换行分隔） |

## 工作流程

1. **加载配置**：从 `batch_config.json` 读取配置参数
2. **初始化日志**：根据配置设置日志级别和输出文件
3. **读取Prompts**：从 `多个Prompt.json` 加载所有Prompt模板
4. **扫描患者记录**：自动扫描指定目录下的所有患者文件
5. **并发处理**：
   - 为每个（模型 × 患者）组合创建处理任务
   - 对于每个患者，所有Prompt并发执行
   - 自动保持输出顺序
6. **保存结果**：每个组合生成独立的JSON文件

## 错误处理

### 自动重试机制

当API调用失败时，系统会自动重试：

1. **第1次失败**：等待 1 秒后重试
2. **第2次失败**：等待 2 秒后重试
3. **第3次失败**：等待 4 秒后重试
4. **3次重试后仍失败**：记录错误，Output字段填充 "ERROR: 错误信息"

### 错误日志

所有错误都会记录到日志文件中，包括：

- API调用失败
- 重试信息
- 最终失败记录

**示例日志：**

```
2025-11-16 02:43:57 - WARNING - [gpt-5.1][患者1] 对话 4 失败 (第1次尝试): Request timed out.
2025-11-16 02:43:57 - INFO - [gpt-5.1][患者1] 将在 1 秒后重试...
2025-11-16 02:46:15 - INFO - [gpt-5.1][患者1] 对话 4 重试成功 (第2次尝试，耗时: 21.00秒)
```

## 性能优化

### 并发处理

系统采用 AsyncIO 实现并发处理：

- **所有模型并发处理**
- **同一患者的多个Prompt并发执行**
- **自动保持输出顺序**

### 处理时间估算

假设条件：
- 2个模型
- 2个患者
- 5个Prompt
- 单个请求平均耗时 10秒

**串行处理时间：** 2 × 2 × 5 × 10 = 200秒

**并发处理时间：** 约 50-60秒（取决于API限流）

**性能提升：** 约 3-4倍

## 常见问题

### Q1: 如何添加新的模型？

编辑 `batch_config.json`，在 `models` 数组中添加模型名称：

```json
{
  "models": [
    "gpt-4o-mini",
    "gpt-5.1",
    "gpt-4-turbo",
    "deepseek/deepseek-r1"
  ]
}
```

### Q2: 如何修改重试次数？

编辑 `batch_config.json`，修改 `max_retries` 值：

```json
{
  "max_retries": 5
}
```

### Q3: 如何查看详细的调试信息？

编辑 `batch_config.json`，将 `log_level` 改为 `DEBUG`：

```json
{
  "log_level": "DEBUG"
}
```

### Q4: 输出文件太大怎么办？

可以减少 `max_tokens` 值来限制单次输出的长度：

```json
{
  "max_tokens": 1000
}
```

### Q5: 某个患者处理失败，会影响其他患者吗？

不会。每个患者独立处理，即使某个失败，其他患者仍会正常处理。

### Q6: 如何暂停和恢复处理？

当前版本不支持断点续传，建议：
- 使用较小的批次
- 定期备份输出目录
- 失败后根据已有文件判断进度

### Q7: API Key 错误怎么办？

确保 `.env` 文件中正确设置了 `JIEKOU_API_KEY`：

```env
JIEKOU_API_KEY=your_actual_api_key_here
```

### Q8: 如何更改输出目录？

编辑 `batch_config.json`：

```json
{
  "output_dir": "./my_custom_output"
}
```

## 注意事项

1. **API限流**：某些API有频率限制，可能需要调整并发数或增加延迟
2. **文件编码**：所有文本文件必须使用 UTF-8 编码
3. **磁盘空间**：确保输出目录有足够空间（每个文件约 50-100KB）
4. **网络稳定**：建议在稳定网络环境下运行，避免频繁重试
5. **配置备份**：修改配置前建议备份原配置文件
6. **模型限制**：gpt-5.1 等模型可能有 beta 限制，系统已自动处理

## 日志分析

### 成功案例

```
2025-11-16 02:38:30 - INFO - 初始化新格式批量处理器
2025-11-16 02:38:30 - INFO -   Prompts文件: 多个Prompt.json
2025-11-16 02:38:30 - INFO -   患者记录目录: 测试输入问答记录
2025-11-16 02:38:30 - INFO -   输出目录: ./output/raw
2025-11-16 02:38:30 - INFO -   使用模型: gpt-4o-mini, gpt-5.1
2025-11-16 02:38:30 - INFO -   最大重试次数: 3
2025-11-16 02:38:30 - INFO -   最大Token数: 2000
2025-11-16 02:38:33 - INFO - [gpt-4o-mini][患者1] 完成对话 1 (耗时: 3.50秒)
2025-11-16 02:45:54 - INFO - [gpt-4o-mini][患者1] 处理完成 (成功: 5/5, 耗时: 443.94秒)
```

### 重试成功案例

```
2025-11-16 02:43:57 - WARNING - [gpt-5.1][患者1] 对话 4 失败 (第1次尝试): Request timed out.
2025-11-16 02:43:57 - INFO - [gpt-5.1][患者1] 将在 1 秒后重试...
2025-11-16 02:46:15 - INFO - [gpt-5.1][患者1] 对话 4 重试成功 (第2次尝试，耗时: 21.00秒)
```

### 最终失败案例

```
2025-11-16 02:50:00 - ERROR - [gpt-5.1][患者2] 对话 3 最终失败 (已重试3次): Connection timeout
```

## 示例执行输出

```
================================================================================
批量处理系统 - 新输出格式
================================================================================

配置信息:
  配置文件: batch_config.json
  Prompts文件: 多个Prompt.json
  患者记录目录: 测试输入问答记录
  输出目录: ./output/raw
  使用模型: gpt-4o-mini, gpt-5.1
  最大重试次数: 3
  最大Token数: 2000

================================================================================
处理完成！
共生成 4 个JSON文件
输出目录: ./output/raw/

生成的文件：
  - gpt-4o-mini-患者1.json
  - gpt-4o-mini-患者2.json
  - gpt-5.1-患者1.json
  - gpt-5.1-患者2.json
================================================================================
```

## 故障排查

### 问题1: 模型参数限制错误

**错误信息：**
```
Error code: 400 - {'message': 'this model has beta-limitations, temperature, top_p and n are fixed at 1...'}
```

**解决方案：**
确保 `config.py` 中的参数设置正确：

```python
default_temperature: Optional[float] = Field(default=None, ...)
```

### 问题2: API Key 未配置

**错误信息：**
```
ValueError: API Key未配置
```

**解决方案：**
检查 `.env` 文件中是否正确设置了 `JIEKOU_API_KEY`

### 问题3: 文件编码错误

**错误信息：**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**解决方案：**
确保所有输入文件使用 UTF-8 编码

### 问题4: 配置文件不存在

**错误信息：**
```
FileNotFoundError: [Errno 2] No such file or directory: 'batch_config.json'
```

**解决方案：**
创建 `batch_config.json` 文件或使用默认配置

## 许可证

本项目仅供内部使用。

## 更新日志

### v1.1.0 (2025-11-16)

- 添加配置文件支持（batch_config.json）
- 支持动态配置重试次数和Token限制
- 改进日志系统，支持自定义日志级别
- 优化代码结构，提高可维护性

### v1.0.0 (2025-11-16)

- 实现基础批量处理功能
- 支持多模型对比
- 添加自动重试机制
- 完善日志系统
