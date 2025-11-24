# 统一模型服务 - Universal Model Service

## 概述

统一模型服务提供了一个**通用的模型调用接口**,可以通过传入模型名称自动路由到正确的API提供商,实现对所有AI模型的统一管理和调用。

### 核心理念

> "基座模型不一定是只服务于cross, 我认为它都可以服务, 只要传入模型名称它就可以加载对应的模型, 再输入入参出参, 就可以返回结果"

### 架构优势

#### 之前的架构

```
batch_process_new_format.py          # JieKou AI 模型
batch_process_new_format_baichuan.py # 百川模型
batch_process_new_format_doubao.py   # 豆包模型
batch_process_new_format_kimi.py     # Kimi模型
batch_process_new_format_qwen.py     # Qwen模型
...
```

每个API提供商需要单独的:
- 批处理脚本
- 配置文件
- 客户端实例
- 错误处理逻辑

#### 现在的统一架构

```
UniversalModelService (通用模型服务)
    ↓
ModelRegistry (模型注册表)
    ↓
自动路由到正确的API
```

所有模型使用**统一接口**:

```python
service.call(model="任意模型名", prompt="问题")
```

## 核心组件

### 1. ModelRegistry (模型注册表)

管理所有模型的配置和路由信息。

```python
{
  "gpt-5.1": {
    "provider": "jiekou",
    "api_key_env": "JIEKOU_API_KEY",
    "base_url": "https://api.jiekou.ai/openai",
    "description": "JieKou AI GPT-5.1"
  },
  "Baichuan4": {
    "provider": "baichuan",
    "api_key_env": "BAICHUAN_API_KEY",
    "base_url": "https://api.baichuan-ai.com/v1",
    "description": "百川4"
  }
}
```

### 2. UniversalModelService (通用模型服务)

提供统一的调用接口。

**核心方法**:
- `call()` - 调用模型
- `batch_call()` - 批量调用
- `list_models()` - 列出可用模型
- `get_model_info()` - 获取模型信息

### 3. UnifiedBatchProcessor (统一批量处理器)

基于 UniversalModelService 的批量处理器,替代所有专用处理器。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在 `.env` 文件中配置所需的API Keys:

```bash
# JieKou AI
JIEKOU_API_KEY=your_jiekou_api_key

# 百川智能 (可选)
BAICHUAN_API_KEY=your_baichuan_api_key

# DeepSeek 官方 (可选)
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 3. 基本使用

#### 方法1: 快速调用

```python
from model_service import call_model

# 一行代码调用任意模型
response = call_model("gpt-5.1", "什么是人工智能?")
print(response)
```

#### 方法2: 服务实例

```python
from model_service import UniversalModelService

# 创建服务
service = UniversalModelService()

# 列出所有可用模型
models = service.list_models()
print(f"可用模型: {models}")

# 调用模型
response = service.call(
    model="gpt-5.1",
    prompt="解释量子计算",
    temperature=0.7,
    max_tokens=500
)
print(response)
```

#### 方法3: 流式输出

```python
# 流式调用
for chunk in service.call(
    model="deepseek-reasoner",
    prompt="详细解释机器学习",
    stream=True
):
    print(chunk, end="", flush=True)
```

#### 方法4: 批量调用

```python
# 批量处理
questions = ["问题1", "问题2", "问题3"]
results = service.batch_call(
    model="Baichuan4",
    prompts=questions,
    system_prompt="你是一个AI助手"
)
```

### 4. 批量处理

#### 配置文件 (unified_batch_config.json)

```json
{
  "prompts_file": "prompts.json",
  "records_dir": "./records",
  "output_dir": "./output/unified",
  "models": [
    "gpt-5.1",
    "gemini-2.5-pro",
    "Baichuan4"
  ],
  "max_retries": 3,
  "max_tokens": 2000,
  "temperature": 0.3
}
```

#### 运行批量处理

```bash
python unified_batch_processor.py
```

## 高级功能

### 注册新模型

```python
service = UniversalModelService()

# 动态注册新模型
service.registry.register_model(
    model_name="my-custom-model",
    provider="custom",
    api_key_env="CUSTOM_API_KEY",
    base_url="https://api.custom.com/v1",
    description="我的自定义模型"
)

# 立即使用
response = service.call("my-custom-model", "测试问题")
```

### 按提供商筛选模型

```python
# 列出所有提供商
providers = service.registry.list_providers()
print(providers)  # ['jiekou', 'baichuan', 'deepseek', ...]

# 只列出JieKou的模型
jiekou_models = service.list_models(provider="jiekou")
print(jiekou_models)
```

### 获取模型详细信息

```python
info = service.get_model_info("Baichuan4")
print(f"提供商: {info['provider']}")
print(f"API URL: {info['base_url']}")
print(f"API Key变量: {info['api_key_env']}")
```

## 测试

### 运行测试套件

```bash
python test_model_service.py
```

测试包括:
1. 列出所有模型
2. 简单调用
3. 流式调用
4. 批量调用
5. 系统提示词
6. 便捷函数
7. 注册新模型

### 交互式测试

```bash
python test_model_service.py
# 选择要运行的测试或运行所有测试
```

## 与旧架构的对比

### 旧方式

```python
# 需要针对不同提供商使用不同的处理器
from batch_process_new_format_baichuan import BaichuanBatchProcessor
from batch_process_new_format_doubao import DoubaoBatchProcessor

# 百川模型
baichuan_processor = BaichuanBatchProcessor(...)
await baichuan_processor.run()

# 豆包模型
doubao_processor = DoubaoBatchProcessor(...)
await doubao_processor.run()
```

### 新方式

```python
# 所有模型使用统一接口
from unified_batch_processor import UnifiedBatchProcessor

# 配置文件中指定要使用的模型即可
processor = UnifiedBatchProcessor(
    models=["Baichuan4", "doubao-pro", "gpt-5.1", "gemini-2.5-pro"]
)
await processor.run()
```

## 模型注册表

当前支持的模型提供商:

| 提供商 | 模型数量 | API Base URL |
|--------|----------|--------------|
| JieKou AI | 5+ | https://api.jiekou.ai/openai |
| 百川智能 | 5 | https://api.baichuan-ai.com/v1 |
| DeepSeek | 2 | https://api.deepseek.com |

查看完整模型列表:

```python
service = UniversalModelService()
for provider in service.registry.list_providers():
    models = service.list_models(provider)
    print(f"[{provider}] {len(models)} 个模型")
    for model in models:
        print(f"  - {model}")
```

## 配置文件

### model_registry.json

模型注册表配置文件,首次运行时自动生成。

可以手动编辑添加新模型:

```json
{
  "new-model-name": {
    "provider": "provider-name",
    "api_key_env": "API_KEY_ENV_VAR",
    "base_url": "https://api.provider.com/v1",
    "description": "Model description"
  }
}
```

### unified_batch_config.json

批量处理配置文件:

```json
{
  "prompts_file": "prompts.json",        // Prompt文件路径
  "records_dir": "./records",            // 患者记录目录
  "output_dir": "./output/unified",      // 输出目录
  "models": ["model1", "model2"],        // 要使用的模型列表
  "max_retries": 3,                      // 最大重试次数
  "max_tokens": 2000,                    // 最大Token数
  "temperature": 0.3,                    // 温度参数
  "model_registry_file": "model_registry.json"
}
```

## 最佳实践

### 1. 环境变量管理

使用 `.env` 文件管理所有API Keys:

```bash
# .env
JIEKOU_API_KEY=xxx
BAICHUAN_API_KEY=xxx
DEEPSEEK_API_KEY=xxx
```

### 2. 错误处理

服务内置了完整的错误处理和重试机制:

```python
try:
    response = service.call("model-name", "prompt")
except ValueError as e:
    # 模型未注册或配置错误
    print(f"配置错误: {e}")
except Exception as e:
    # API调用失败
    print(f"调用失败: {e}")
```

### 3. 日志配置

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 迁移指南

### 从旧批处理器迁移

1. **更新配置文件**:
   - 将旧的 `batch_config_xxx.json` 合并到 `unified_batch_config.json`
   - 只需在 `models` 数组中列出所有要使用的模型

2. **更新代码**:
   ```python
   # 旧代码
   from batch_process_new_format_baichuan import BaichuanBatchProcessor
   processor = BaichuanBatchProcessor(...)

   # 新代码
   from unified_batch_processor import UnifiedBatchProcessor
   processor = UnifiedBatchProcessor(...)
   ```

3. **验证输出**:
   - 输出格式保持一致
   - 文件名格式: `{model}-{patient}.json`
   - 特殊字符(如 `/`)会被替换为 `_`

## 常见问题

### Q: 如何添加新的API提供商?

A: 在 `model_registry.json` 中添加模型配置,或使用代码:

```python
service.registry.register_model(
    model_name="new-model",
    provider="new-provider",
    api_key_env="NEW_API_KEY",
    base_url="https://api.new-provider.com/v1",
    description="新模型"
)
```

### Q: API Key 未配置怎么办?

A: 确保在 `.env` 文件中设置了对应的环境变量。错误信息会提示需要哪个环境变量。

### Q: 如何查看支持的所有模型?

A:
```python
service = UniversalModelService()
print(service.list_models())
```

### Q: 可以同时使用多个提供商的模型吗?

A: 可以!这正是统一服务的优势:

```python
models = [
    "gpt-5.1",           # JieKou
    "Baichuan4",         # 百川
    "deepseek-reasoner"  # DeepSeek
]
processor = UnifiedBatchProcessor(models=models)
```

## 性能优化

1. **客户端缓存**: 每个模型的客户端会被缓存,避免重复创建
2. **智能重试**: 空响应会自动重试,API错误按指数退避重试
3. **顺序处理**: 避免并发导致的API限流

## 未来扩展

- [ ] 支持并发处理(可配置)
- [ ] 添加速率限制控制
- [ ] 支持更多API提供商
- [ ] 实时进度监控
- [ ] 结果缓存机制
- [ ] 成本追踪和报告

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request!

---

**统一模型服务** - 一个接口,调用所有AI模型
