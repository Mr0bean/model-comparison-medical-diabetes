# DeepSeek官方API使用指南

## 概述

本项目现已支持 **DeepSeek 官方 API**，可以直接使用 DeepSeek 提供的原生接口，享受更稳定、更快速的服务。

## 特性

- ✅ 官方API支持，稳定可靠
- ✅ 支持流式输出
- ✅ 多种模型可选（chat、coder、reasoner）
- ✅ 完整的错误处理
- ✅ 与现有系统无缝集成

## 快速开始

### 1. 获取API密钥

访问 [DeepSeek平台](https://platform.deepseek.com/) 注册并获取API密钥。

### 2. 安装依赖

```bash
pip install openai
```

DeepSeek官方API兼容OpenAI SDK格式。

### 3. 配置环境变量

编辑 `.env` 文件：

```bash
# DeepSeek官方API配置
DEEPSEEK_API_KEY=sk-your-actual-key-here
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_DEFAULT_MODEL=deepseek-chat
```

### 4. 基础使用

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
)

print(response.choices[0].message.content)
```

## 可用模型

| 模型名称 | 说明 | 上下文窗口 | 适用场景 |
|---------|------|------------|---------|
| `deepseek-chat` | 通用对话模型 | 32K | 日常对话、文本生成 |
| `deepseek-coder` | 代码专用模型 | 16K | 代码生成、调试 |
| `deepseek-reasoner` | 推理增强模型 | 64K | 复杂推理、数学问题 |

## 使用示例

### 示例1: 基础对话

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "介绍一下DeepSeek"}
    ]
)

print(response.choices[0].message.content)
```

### 示例2: 流式输出

```python
stream = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "写一首诗"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 示例3: 医疗助手

```python
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {
            "role": "system",
            "content": "你是一名经验丰富的医疗助手，擅长生成规范的病历记录。"
        },
        {
            "role": "user",
            "content": "患者主诉：胸闷气短一周。请生成病历记录。"
        }
    ],
    temperature=0.7,
    max_tokens=2048
)

print(response.choices[0].message.content)
```

### 示例4: 使用配置类

```python
from config.deepseek import deepseek_settings
from openai import OpenAI

# 验证配置
if not deepseek_settings.validate_api_key():
    print("错误: API密钥未配置")
    exit(1)

client = OpenAI(
    api_key=deepseek_settings.api_key,
    base_url=deepseek_settings.base_url
)

# 使用配置中的参数
model_config = deepseek_settings.get_model_config()

response = client.chat.completions.create(
    messages=[
        {"role": "user", "content": "Hello"}
    ],
    **model_config
)
```

## 完整示例脚本

我们提供了完整的示例脚本：

```bash
python examples/deepseek_official_example.py
```

该脚本包含：
- ✅ 基础对话
- ✅ 流式输出
- ✅ 医疗助手
- ✅ 多轮对话
- ✅ 使用配置类
- ✅ 错误处理

## 集成到评测系统

### 注册DeepSeek官方模型

在 `config/models.py` 中添加：

```python
registry.register_model(
    name="deepseek-official",
    api_endpoint="https://api.deepseek.com/v1",
    api_key=os.environ.get('DEEPSEEK_API_KEY'),
    model_id="deepseek-chat",
    max_tokens=4096,
    supports_streaming=True
)
```

### 在评测中使用

```bash
# 运行评测
python run_cross_evaluation.py \
  --models deepseek-official \
  --patients 患者1 患者2 \
  --conversations 1 2 3
```

## 与JieKou API的对比

| 特性 | DeepSeek官方API | JieKou AI |
|-----|----------------|-----------|
| 稳定性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 响应速度 | 快 | 一般 |
| 模型选择 | DeepSeek系列 | 10+ 主流模型 |
| 价格 | 优惠 | 统一定价 |
| 接口格式 | OpenAI兼容 | OpenAI兼容 |

**建议**:
- 单独使用DeepSeek模型 → 使用官方API
- 多模型对比评测 → 使用JieKou AI

## 参数配置

### 环境变量

```bash
# 必填参数
DEEPSEEK_API_KEY=sk-xxxxx               # API密钥

# 可选参数（使用默认值即可）
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_DEFAULT_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=1.0                # 0.0-2.0
DEEPSEEK_MAX_TOKENS=4096
DEEPSEEK_STREAM=False
```

### Python配置

```python
from config.deepseek import deepseek_settings

# 修改配置
deepseek_settings.temperature = 0.7
deepseek_settings.max_tokens = 2048
deepseek_settings.stream = True
```

## 错误处理

```python
from openai import APIError, APIConnectionError, RateLimitError

try:
    response = client.chat.completions.create(...)
except RateLimitError:
    print("速率限制，请稍后重试")
except APIConnectionError:
    print("网络连接失败")
except APIError as e:
    print(f"API错误: {e}")
```

## 最佳实践

### 1. 安全管理API密钥

```bash
# ✅ 推荐：使用环境变量
export DEEPSEEK_API_KEY=sk-xxxxx

# ❌ 不推荐：硬编码在代码中
api_key = "sk-xxxxx"  # 不要这样做！
```

### 2. 合理设置参数

```python
# 需要创造性的任务
temperature = 1.0  # 较高的随机性

# 需要准确性的任务（如病历生成）
temperature = 0.3  # 较低的随机性

# 限制输出长度
max_tokens = 2048  # 根据需求调整
```

### 3. 使用流式输出提升体验

```python
# 长文本生成时使用流式输出
stream = True  # 实时显示生成内容
```

### 4. 错误重试机制

```python
import time

max_retries = 3
for i in range(max_retries):
    try:
        response = client.chat.completions.create(...)
        break
    except Exception as e:
        if i < max_retries - 1:
            time.sleep(2 ** i)  # 指数退避
        else:
            raise
```

## 性能优化

### 批量请求

```python
import asyncio
from openai import AsyncOpenAI

async def batch_generate(prompts):
    client = AsyncOpenAI(
        api_key=os.environ.get('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com"
    )

    tasks = [
        client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}]
        )
        for prompt in prompts
    ]

    return await asyncio.gather(*tasks)
```

### 缓存常用对话

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_response(prompt):
    return client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}]
    )
```

## 价格说明

DeepSeek官方API定价（参考）：

| 模型 | 输入价格 | 输出价格 |
|------|---------|---------|
| deepseek-chat | ¥0.001/1K tokens | ¥0.002/1K tokens |
| deepseek-coder | ¥0.001/1K tokens | ¥0.002/1K tokens |
| deepseek-reasoner | ¥0.002/1K tokens | ¥0.004/1K tokens |

**注意**: 实际价格以官网为准。

## 常见问题

### Q: 如何申请API密钥？
A: 访问 https://platform.deepseek.com/ 注册账号并申请。

### Q: API调用失败怎么办？
A:
1. 检查API密钥是否正确
2. 确认账户余额是否充足
3. 检查网络连接
4. 查看错误信息详情

### Q: 可以同时使用官方API和JieKou API吗？
A: 可以！两者相互独立，可以在不同场景下使用。

### Q: 官方API是否支持所有DeepSeek模型？
A: 支持主要的chat、coder、reasoner模型，具体请查看官方文档。

## 参考资源

- [DeepSeek官方网站](https://www.deepseek.com/)
- [DeepSeek平台](https://platform.deepseek.com/)
- [API文档](https://platform.deepseek.com/api-docs/)
- [OpenAI SDK文档](https://platform.openai.com/docs/api-reference)

## 更新日志

### v1.0.0 (2024-11-21)
- ✅ 添加DeepSeek官方API支持
- ✅ 提供完整示例和文档
- ✅ 集成到配置系统

---

**维护者**: 项目团队
**最后更新**: 2024-11-21

**注意**: 请妥善保管您的API密钥，不要将其提交到代码仓库！
