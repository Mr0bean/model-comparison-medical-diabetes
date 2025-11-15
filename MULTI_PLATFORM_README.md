# 多平台 LLM 批量处理系统

支持多个 LLM 平台的批量处理系统，每个平台使用独立的配置文件和实现代码。

## 支持的平台

| 平台 | 脚本文件 | 配置文件 | API 文档 |
|------|---------|---------|---------|
| **Kimi (月之暗面)** | `batch_process_new_format_kimi.py` | `batch_config_kimi.json` | [Kimi API 文档](https://platform.moonshot.cn/docs/api/chat) |
| **豆包 (火山引擎)** | `batch_process_new_format_doubao.py` | `batch_config_doubao.json` | [豆包 API 文档](https://www.volcengine.com/docs/82379/1263482) |
| **百川智能** | `batch_process_new_format_baichuan.py` | `batch_config_baichuan.json` | [百川 API 文档](https://platform.baichuan-ai.com/docs/api) |
| **JieKou (原有)** | `batch_process_new_format.py` | `batch_config.json` | - |

## 快速开始

### 1. 安装依赖

```bash
pip install openai python-dotenv
```

### 2. 配置 API Key

每个平台需要单独配置 API Key，有两种方式：

#### 方式一：环境变量（推荐）

创建或编辑 `.env` 文件：

```env
# Kimi (月之暗面)
MOONSHOT_API_KEY=your_kimi_api_key

# 豆包 (火山引擎)
ARK_API_KEY=your_doubao_api_key
# 或
DOUBAO_API_KEY=your_doubao_api_key

# 百川智能
BAICHUAN_API_KEY=your_baichuan_api_key
```

#### 方式二：配置文件

直接在对应的配置文件中设置 `api_key`：

```json
{
  "api_config": {
    "api_key": "your_actual_api_key_here"
  }
}
```

### 3. 配置模型

编辑对应平台的配置文件，选择要使用的模型：

**Kimi (`batch_config_kimi.json`):**
```json
{
  "models": [
    "moonshot-v1-8k",
    "moonshot-v1-32k",
    "moonshot-v1-128k"
  ]
}
```

**豆包 (`batch_config_doubao.json`):**
```json
{
  "models": [
    "doubao-pro-4k",
    "doubao-pro-32k",
    "doubao-pro-128k"
  ],
  "api_config": {
    "endpoint_id": "your_endpoint_id"
  }
}
```

**百川 (`batch_config_baichuan.json`):**
```json
{
  "models": [
    "Baichuan2-Turbo",
    "Baichuan3-Turbo",
    "Baichuan4"
  ]
}
```

### 4. 运行批量处理

```bash
# Kimi 平台
python batch_process_new_format_kimi.py

# 豆包平台
python batch_process_new_format_doubao.py

# 百川平台
python batch_process_new_format_baichuan.py
```

## 配置文件说明

所有平台的配置文件结构类似：

```json
{
  "prompts_file": "多个Prompt.json",
  "records_dir": "测试输入问答记录",
  "output_dir": "./output/raw_<platform>",
  "api_config": {
    "api_key": null,
    "base_url": "<platform_api_url>",
    // 其他平台特定配置
  },
  "models": [
    "model-1",
    "model-2"
  ],
  "max_retries": 5,
  "max_tokens": 2000,
  "log_file": "batch_process_<platform>.log",
  "log_level": "INFO"
}
```

### 通用配置参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `prompts_file` | string | Prompt 模板文件路径 |
| `records_dir` | string | 患者问答记录目录 |
| `output_dir` | string | 输出文件目录 |
| `models` | array | 要使用的模型列表 |
| `max_retries` | integer | 最大重试次数 |
| `max_tokens` | integer | 最大 Token 数 |
| `log_file` | string | 日志文件名 |
| `log_level` | string | 日志级别 |

### 平台特定配置

#### Kimi

```json
{
  "api_config": {
    "api_key": null,
    "base_url": "https://api.moonshot.cn/v1"
  }
}
```

#### 豆包

```json
{
  "api_config": {
    "api_key": null,
    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
    "endpoint_id": null  // 豆包特有：接入点ID
  }
}
```

#### 百川

```json
{
  "api_config": {
    "api_key": null,
    "base_url": "https://api.baichuan-ai.com/v1"
  }
}
```

## 输出格式

所有平台使用统一的输出格式：

### 文件命名

```
{output_dir}/{model}-{people}.json
```

示例：
- `output/raw_kimi/moonshot-v1-8k-患者1.json`
- `output/raw_doubao/doubao-pro-4k-患者1.json`
- `output/raw_baichuan/Baichuan4-患者1.json`

### JSON 结构

```json
{
  "model": "模型名称",
  "people": "患者编号",
  "conversations": {
    "1": {
      "model": "模型名称",
      "prompt": "Prompt内容",
      "people": "患者编号",
      "chat": "患者问答记录",
      "Input": "完整输入",
      "Output": "AI回复"
    },
    "2": {...},
    ...
  },
  "result": "所有对话输出拼接结果（换行分隔）"
}
```

## 使用示例

### 示例 1：使用 Kimi 处理患者数据

```bash
# 1. 配置 API Key
export MOONSHOT_API_KEY="your_kimi_api_key"

# 2. 编辑配置文件选择模型
vim batch_config_kimi.json

# 3. 运行处理
python batch_process_new_format_kimi.py
```

输出：
```
================================================================================
批量处理系统 - Kimi (月之暗面) 基座
================================================================================

配置信息:
  API地址: https://api.moonshot.cn/v1
  使用模型: moonshot-v1-8k, moonshot-v1-32k
  最大重试次数: 5
  最大Token数: 2000

开始批量处理: 2 个模型 × 2 个患者 = 4 个文件
...
处理完成！
共生成 4 个JSON文件
```

### 示例 2：使用豆包处理（需要 endpoint ID）

```bash
# 1. 在火山引擎控制台获取 endpoint ID

# 2. 配置环境变量
export ARK_API_KEY="your_doubao_api_key"

# 3. 编辑配置文件设置 endpoint_id
vim batch_config_doubao.json

# 4. 运行处理
python batch_process_new_format_doubao.py
```

### 示例 3：使用百川处理

```bash
# 1. 配置 API Key
export BAICHUAN_API_KEY="your_baichuan_api_key"

# 2. 运行处理
python batch_process_new_format_baichuan.py
```

## 平台对比

### 模型支持

| 平台 | 上下文长度 | 特点 |
|------|-----------|------|
| **Kimi** | 8K - 128K | 长文本能力强 |
| **豆包** | 4K - 128K | 火山引擎生态 |
| **百川** | 标准 - 192K | 国产模型先驱 |

### API 兼容性

所有平台都兼容 OpenAI SDK，使用统一的调用方式：

```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="platform_api_url"
)

completion = client.chat.completions.create(
    model="model_name",
    messages=[{"role": "user", "content": "..."}]
)
```

## 错误处理

所有脚本都包含自动重试机制：

1. **第1次失败**：等待 1 秒后重试
2. **第2次失败**：等待 2 秒后重试
3. **第3-5次失败**：等待 4-16 秒后重试
4. **所有重试失败**：记录错误，输出包含 `ERROR:` 前缀

错误日志示例：
```
2025-11-16 10:00:00 - WARNING - [model][患者1] 对话 1 失败 (第1次尝试): Connection timeout
2025-11-16 10:00:00 - INFO - [model][患者1] 将在 1 秒后重试...
2025-11-16 10:00:02 - INFO - [model][患者1] 对话 1 重试成功 (第2次尝试，耗时: 3.5秒)
```

## 常见问题

### Q1: 如何选择使用哪个平台？

根据需求选择：
- **长文本处理**：选择 Kimi (moonshot-v1-128k)
- **成本考虑**：对比各平台定价
- **模型能力**：测试不同平台的输出质量

### Q2: 可以同时运行多个平台吗？

可以！每个平台使用独立的输出目录，不会冲突：

```bash
# 终端 1
python batch_process_new_format_kimi.py

# 终端 2
python batch_process_new_format_doubao.py

# 终端 3
python batch_process_new_format_baichuan.py
```

### Q3: 如何添加新的平台？

参考现有实现，创建新的脚本和配置文件：

1. 复制 `batch_process_new_format_kimi.py` 为模板
2. 修改 API 调用部分
3. 创建对应的配置文件
4. 测试运行

### Q4: 豆包的 endpoint_id 是什么？

豆包使用接入点（endpoint）系统，每个模型需要创建对应的接入点：

1. 登录火山引擎控制台
2. 进入「模型推理」服务
3. 创建或查看接入点
4. 复制 endpoint ID 到配置文件

### Q5: 如何调整并发数量？

修改脚本中的 `process_all()` 方法，添加并发控制：

```python
# 限制同时处理的任务数
semaphore = asyncio.Semaphore(5)  # 最多5个并发

async def process_with_limit(...):
    async with semaphore:
        return await self.process_single_conversation(...)
```

## 性能优化

### 并发处理

所有脚本默认并发处理：
- 不同模型并发
- 同一患者的不同 Prompt 并发
- 自动保持输出顺序

### 重试策略

使用指数退避策略：
- 避免频繁重试导致限流
- 自动处理临时网络问题
- 保证最终成功率

### 日志管理

- 实时输出到控制台和文件
- 不同平台使用不同日志文件
- 支持调整日志级别（DEBUG/INFO/WARNING/ERROR）

## 许可证

本项目仅供内部使用。

## 更新日志

### v1.0.0 (2025-11-16)

- 创建 Kimi 基座实现
- 创建豆包基座实现
- 创建百川基座实现
- 统一输出格式
- 完善配置文件
- 创建使用文档
