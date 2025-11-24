# 统一模型服务架构总结

## 核心理念

> **"基座模型不一定是只服务于cross evaluation,它可以服务所有场景。只要传入模型名称,它就可以加载对应的模型,再输入参数,就可以返回结果。"**

这个新架构实现了你的这个愿景。

## 架构对比

### 旧架构 (分散式)

```
项目结构:
├── chat_client.py                          # 基础客户端
├── batch_process_new_format.py             # JieKou AI专用
├── batch_process_new_format_baichuan.py    # 百川专用
├── batch_process_new_format_doubao.py      # 豆包专用
├── batch_process_new_format_kimi.py        # Kimi专用
├── batch_process_new_format_qwen.py        # Qwen专用
├── batch_config.json                       # JieKou配置
├── batch_config_baichuan.json              # 百川配置
├── batch_config_doubao.json                # 豆包配置
└── ...                                     # 更多配置文件

问题:
✗ 每个API提供商需要单独的处理器
✗ 每个提供商需要单独的配置文件
✗ 代码重复,难以维护
✗ 添加新模型需要创建新文件
✗ 不同提供商的调用方式不统一
```

### 新架构 (统一式)

```
项目结构:
├── model_service.py                # 核心 - 统一模型服务
│   ├── ModelRegistry               # 模型注册表
│   └── UniversalModelService       # 通用服务接口
│
├── unified_batch_processor.py      # 统一批量处理器
├── model_registry.json             # 统一的模型配置
├── unified_batch_config.json       # 统一的批处理配置
│
├── test_model_service.py           # 测试套件
├── demo_unified_service.py         # 演示脚本
└── UNIFIED_MODEL_SERVICE_README.md # 完整文档

优势:
✓ 一个服务调用所有模型
✓ 一个配置文件管理所有模型
✓ 统一的接口,零学习成本
✓ 添加新模型只需修改配置
✓ 代码简洁,易于维护
```

## 核心组件详解

### 1. ModelRegistry (模型注册表)

**作用**: 管理所有模型的元数据和路由信息

**数据结构**:
```json
{
  "模型名称": {
    "provider": "提供商",
    "api_key_env": "API Key环境变量",
    "base_url": "API基础URL",
    "description": "模型描述"
  }
}
```

**支持的操作**:
- `get_model_config(model_name)` - 获取模型配置
- `register_model(...)` - 注册新模型
- `list_models(provider)` - 列出模型
- `list_providers()` - 列出提供商

### 2. UniversalModelService (通用模型服务)

**作用**: 提供统一的模型调用接口

**核心方法**:

#### `call()` - 调用模型
```python
response = service.call(
    model="任意模型名",
    prompt="问题",
    system_prompt="系统角色(可选)",
    stream=False,
    temperature=0.7,
    max_tokens=2000
)
```

#### `batch_call()` - 批量调用
```python
results = service.batch_call(
    model="模型名",
    prompts=["问题1", "问题2", "问题3"],
    system_prompt="系统角色"
)
```

#### `list_models()` - 列出可用模型
```python
# 列出所有模型
all_models = service.list_models()

# 列出特定提供商的模型
jiekou_models = service.list_models(provider="jiekou")
```

#### `get_model_info()` - 获取模型信息
```python
info = service.get_model_info("gpt-5.1")
# 返回: {"provider": "jiekou", "base_url": "...", ...}
```

### 3. UnifiedBatchProcessor (统一批量处理器)

**作用**: 基于UniversalModelService的批量处理

**特性**:
- 使用统一模型服务
- 支持所有注册的模型
- 自动重试机制
- 完整的日志记录
- 统一的输出格式

## 使用场景

### 场景1: 快速调用单个模型

```python
from model_service import call_model

# 一行代码搞定!
response = call_model("gpt-5.1", "什么是AI?")
```

### 场景2: 对比不同模型

```python
from model_service import UniversalModelService

service = UniversalModelService()
question = "解释量子计算"

# 使用JieKou的模型
response1 = service.call("gpt-5.1", question)

# 使用百川的模型
response2 = service.call("Baichuan4", question)

# 使用DeepSeek的模型
response3 = service.call("deepseek-reasoner", question)

# 完全相同的调用方式!
```

### 场景3: 批量处理

```python
from unified_batch_processor import UnifiedBatchProcessor

processor = UnifiedBatchProcessor(
    prompts_file="prompts.json",
    records_dir="./records",
    output_dir="./output/unified",
    models=[
        "gpt-5.1",
        "gemini-2.5-pro",
        "Baichuan4",
        "deepseek-reasoner"
    ]
)

await processor.run()
```

### 场景4: 动态扩展

```python
service = UniversalModelService()

# 动态注册新模型
service.registry.register_model(
    model_name="claude-3-opus",
    provider="anthropic",
    api_key_env="ANTHROPIC_API_KEY",
    base_url="https://api.anthropic.com/v1",
    description="Claude 3 Opus"
)

# 立即使用
response = service.call("claude-3-opus", "测试问题")
```

## 数据流

```
用户代码
   ↓
service.call(model="gpt-5.1", prompt="...")
   ↓
UniversalModelService
   ↓
ModelRegistry.get_model_config("gpt-5.1")
   ↓
{
  "provider": "jiekou",
  "api_key_env": "JIEKOU_API_KEY",
  "base_url": "https://api.jiekou.ai/openai"
}
   ↓
创建/获取 OpenAI 客户端
   ↓
client.chat.completions.create(
    model="gpt-5.1",
    messages=[...],
    ...
)
   ↓
返回响应
```

## 目前支持的模型

### JieKou AI (5个模型)
- gpt-5.1
- gemini-2.5-pro
- deepseek/deepseek-v3.1
- moonshotai/kimi-k2-0905
- grok-4-0709

### 百川智能 (5个模型)
- Baichuan2-Turbo
- Baichuan2-Turbo-192k
- Baichuan3-Turbo
- Baichuan3-Turbo-128k
- Baichuan4

### DeepSeek官方 (2个模型)
- deepseek-reasoner
- deepseek-chat

**总计: 12个模型,3个提供商**

## 如何添加新提供商

### 方法1: 通过代码

```python
service = UniversalModelService()

service.registry.register_model(
    model_name="doubao-pro",
    provider="doubao",
    api_key_env="DOUBAO_API_KEY",
    base_url="https://api.doubao.com/v1",
    description="豆包 Pro"
)
```

### 方法2: 编辑配置文件

编辑 `model_registry.json`:

```json
{
  "doubao-pro": {
    "provider": "doubao",
    "api_key_env": "DOUBAO_API_KEY",
    "base_url": "https://api.doubao.com/v1",
    "description": "豆包 Pro"
  }
}
```

## 环境变量配置

`.env` 文件:

```bash
# JieKou AI (必需)
JIEKOU_API_KEY=your_jiekou_api_key

# 百川智能 (可选,如果使用百川模型)
BAICHUAN_API_KEY=your_baichuan_api_key

# DeepSeek官方 (可选,如果使用DeepSeek官方API)
DEEPSEEK_API_KEY=your_deepseek_api_key

# 未来可以添加更多...
DOUBAO_API_KEY=your_doubao_api_key
KIMI_API_KEY=your_kimi_api_key
```

## 批量处理配置

`unified_batch_config.json`:

```json
{
  "prompts_file": "prompts.json",
  "records_dir": "./records",
  "output_dir": "./output/unified",

  "models": [
    "gpt-5.1",
    "gemini-2.5-pro",
    "Baichuan4",
    "deepseek-reasoner"
  ],

  "max_retries": 3,
  "max_tokens": 2000,
  "temperature": 0.3,
  "log_file": "unified_batch.log",
  "log_level": "INFO"
}
```

## 与旧系统的兼容性

**输出格式**: 完全兼容

旧系统输出:
```json
{
  "model": "Baichuan4",
  "people": "患者1",
  "conversations": {...},
  "result": "..."
}
```

新系统输出:
```json
{
  "model": "Baichuan4",
  "people": "患者1",
  "conversations": {...},
  "result": "..."
}
```

**迁移路径**:

1. 保留旧代码(向后兼容)
2. 新功能使用新系统
3. 逐步迁移旧功能
4. 最终废弃旧代码

## 性能优化

### 客户端缓存
```python
# 每个模型的客户端只创建一次,后续调用重用
self.clients = {}  # 缓存字典

# 第一次调用: 创建客户端
service.call("gpt-5.1", "问题1")  # 创建客户端

# 后续调用: 重用客户端
service.call("gpt-5.1", "问题2")  # 重用缓存的客户端
service.call("gpt-5.1", "问题3")  # 重用缓存的客户端
```

### 智能重试
```python
# 空响应: 无限重试(指数退避)
while response is empty:
    retry with exponential backoff

# API错误: 最大重试次数后放弃
for attempt in range(max_retries):
    try:
        call_api()
    except:
        retry with backoff
```

## 测试和验证

### 运行完整测试
```bash
python test_model_service.py
```

测试内容:
1. 列出所有模型
2. 简单调用测试
3. 流式输出测试
4. 批量调用测试
5. 系统提示词测试
6. 便捷函数测试
7. 动态注册测试

### 运行演示
```bash
python demo_unified_service.py
```

演示内容:
1. 快捷函数调用
2. 多模型对比
3. 流式输出
4. 跨提供商调用
5. 批量处理
6. 模型发现

## 关键代码示例

### 最简调用
```python
from model_service import call_model
response = call_model("gpt-5.1", "什么是AI?")
```

### 完整控制
```python
from model_service import UniversalModelService

service = UniversalModelService()

response = service.call(
    model="deepseek-reasoner",
    prompt="复杂问题",
    system_prompt="你是专家",
    stream=False,
    temperature=0.3,
    max_tokens=2000,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0
)
```

### 流式输出
```python
for chunk in service.call(model="gpt-5.1", prompt="...", stream=True):
    print(chunk, end="", flush=True)
```

### 批量处理
```python
results = service.batch_call(
    model="Baichuan4",
    prompts=["Q1", "Q2", "Q3"],
    system_prompt="角色定义"
)
```

## 总结

### 实现了什么

✅ **统一接口** - 一个方法调用所有模型
✅ **自动路由** - 根据模型名自动选择API
✅ **配置中心** - 集中管理所有模型配置
✅ **动态扩展** - 运行时注册新模型
✅ **向后兼容** - 不影响现有代码
✅ **类型安全** - 完整的错误处理
✅ **高性能** - 客户端缓存和智能重试

### 架构优势

1. **简单** - 一个接口,学习成本低
2. **灵活** - 支持所有OpenAI兼容的API
3. **可扩展** - 轻松添加新模型和提供商
4. **可维护** - 统一代码,易于管理
5. **可测试** - 完整的测试套件
6. **可观察** - 详细的日志记录

### 下一步

建议:
1. ✅ 测试新系统 (`python test_model_service.py`)
2. ✅ 运行演示 (`python demo_unified_service.py`)
3. ✅ 阅读完整文档 (`UNIFIED_MODEL_SERVICE_README.md`)
4. ⏭️ 在小范围使用新系统
5. ⏭️ 逐步迁移现有功能
6. ⏭️ 根据需要添加新模型

---

这个新架构完全实现了你的愿景:**"只要传入模型名称,它就可以加载对应的模型,返回结果"** 🎯
