# 统一模型服务 - 快速开始指南

## 5分钟上手

### 第1步: 安装依赖

```bash
pip install -r requirements.txt
```

### 第2步: 配置API Key

编辑 `.env` 文件:

```bash
JIEKOU_API_KEY=your_api_key_here
```

### 第3步: 开始使用

#### 最简单的方式 - 一行代码

```python
from model_service import call_model

response = call_model("gpt-5.1", "什么是人工智能?")
print(response)
```

**就这么简单!** 🎉

## 常用操作

### 1. 调用不同的模型

```python
from model_service import call_model

# JieKou AI的模型
r1 = call_model("gpt-5.1", "问题")
r2 = call_model("gemini-2.5-pro", "问题")

# 百川的模型(需要配置BAICHUAN_API_KEY)
r3 = call_model("Baichuan4", "问题")

# DeepSeek的模型(需要配置DEEPSEEK_API_KEY)
r4 = call_model("deepseek-reasoner", "问题")
```

### 2. 流式输出

```python
from model_service import UniversalModelService

service = UniversalModelService()

for chunk in service.call(
    model="gpt-5.1",
    prompt="详细解释量子计算",
    stream=True
):
    print(chunk, end="", flush=True)
```

### 3. 批量处理

```python
service = UniversalModelService()

questions = ["问题1", "问题2", "问题3"]
answers = service.batch_call("gpt-5.1", questions)

for q, a in zip(questions, answers):
    print(f"Q: {q}")
    print(f"A: {a}\n")
```

### 4. 使用系统提示词

```python
response = service.call(
    model="gpt-5.1",
    prompt="如何治疗糖尿病?",
    system_prompt="你是一个专业的医学AI助手",
    temperature=0.7,
    max_tokens=1000
)
```

### 5. 查看可用模型

```python
service = UniversalModelService()

# 列出所有模型
all_models = service.list_models()
print(f"可用模型: {all_models}")

# 按提供商筛选
jiekou_models = service.list_models(provider="jiekou")
print(f"JieKou模型: {jiekou_models}")

# 查看提供商
providers = service.registry.list_providers()
print(f"提供商: {providers}")
```

### 6. 获取模型信息

```python
info = service.get_model_info("gpt-5.1")
print(f"提供商: {info['provider']}")
print(f"API URL: {info['base_url']}")
print(f"描述: {info['description']}")
```

### 7. 注册新模型

```python
service.registry.register_model(
    model_name="my-model",
    provider="my-provider",
    api_key_env="MY_API_KEY",
    base_url="https://api.my-provider.com/v1",
    description="我的自定义模型"
)

# 立即使用
response = service.call("my-model", "测试")
```

## 批量处理配置

### 创建配置文件 (unified_batch_config.json)

```json
{
  "prompts_file": "prompts.json",
  "records_dir": "./records",
  "output_dir": "./output/unified",
  "models": [
    "gpt-5.1",
    "gemini-2.5-pro"
  ],
  "max_retries": 3,
  "max_tokens": 2000,
  "temperature": 0.3
}
```

### 运行批量处理

```bash
python unified_batch_processor.py
```

## 测试和演示

### 运行测试

```bash
python test_model_service.py
```

选择测试项目:
1. 列出所有模型
2. 简单调用
3. 流式调用
4. 批量调用
5. 系统提示词
6. 便捷函数
7. 注册新模型

### 运行演示

```bash
python demo_unified_service.py
```

选择演示:
1. 快捷函数调用
2. 多模型对比
3. 流式输出
4. 跨提供商调用
5. 批量处理
6. 模型发现

## 核心API速查

### call_model() - 快捷函数

```python
call_model(model, prompt, **kwargs) -> str
```

### UniversalModelService

```python
service = UniversalModelService()

# 调用模型
service.call(model, prompt, system_prompt=None, stream=False,
             temperature=0.7, max_tokens=2000, **kwargs)

# 批量调用
service.batch_call(model, prompts, system_prompt=None, **kwargs)

# 列出模型
service.list_models(provider=None)

# 获取信息
service.get_model_info(model)
```

### ModelRegistry

```python
registry = service.registry

# 注册模型
registry.register_model(model_name, provider, api_key_env,
                       base_url, description)

# 获取配置
registry.get_model_config(model_name)

# 列出模型
registry.list_models(provider=None)

# 列出提供商
registry.list_providers()
```

## 环境变量

必需的环境变量(在 `.env` 文件中配置):

```bash
# JieKou AI (必需)
JIEKOU_API_KEY=your_key

# 百川智能 (可选,如果使用百川模型)
BAICHUAN_API_KEY=your_key

# DeepSeek (可选,如果使用DeepSeek官方API)
DEEPSEEK_API_KEY=your_key
```

## 目前支持的模型

### JieKou AI (5个)
- `gpt-5.1`
- `gemini-2.5-pro`
- `deepseek/deepseek-v3.1`
- `moonshotai/kimi-k2-0905`
- `grok-4-0709`

### 百川智能 (5个)
- `Baichuan2-Turbo`
- `Baichuan2-Turbo-192k`
- `Baichuan3-Turbo`
- `Baichuan3-Turbo-128k`
- `Baichuan4`

### DeepSeek官方 (2个)
- `deepseek-reasoner`
- `deepseek-chat`

## 常见问题

### Q: API Key在哪里配置?

A: 在项目根目录的 `.env` 文件中

### Q: 如何添加新模型?

A: 方法1 - 使用代码:
```python
service.registry.register_model(...)
```

方法2 - 编辑 `model_registry.json`

### Q: 可以同时使用多个提供商的模型吗?

A: 可以!这正是统一服务的优势:
```python
r1 = service.call("gpt-5.1", "问题")      # JieKou
r2 = service.call("Baichuan4", "问题")    # 百川
r3 = service.call("deepseek-reasoner", "问题")  # DeepSeek
```

### Q: 出现API Key错误怎么办?

A: 检查:
1. `.env` 文件是否存在
2. 环境变量名是否正确
3. API Key是否有效

### Q: 如何切换模型?

A: 只需改变 `model` 参数:
```python
# 从 gpt-5.1 切换到 Baichuan4
response = service.call("Baichuan4", prompt)  # 就这么简单!
```

## 文件结构

```
chat/
├── model_service.py                    # 核心服务
├── unified_batch_processor.py          # 统一批处理
├── model_registry.json                 # 模型注册表
├── unified_batch_config.json           # 批处理配置
│
├── test_model_service.py               # 测试套件
├── demo_unified_service.py             # 演示脚本
│
├── QUICK_START_GUIDE.md                # 本文件
├── UNIFIED_MODEL_SERVICE_README.md     # 完整文档
└── ARCHITECTURE_SUMMARY.md             # 架构总结
```

## 下一步

1. ✅ 配置API Key (`.env`)
2. ✅ 运行演示 (`python demo_unified_service.py`)
3. ✅ 运行测试 (`python test_model_service.py`)
4. ✅ 阅读完整文档 (`UNIFIED_MODEL_SERVICE_README.md`)
5. ✅ 开始使用!

## 获取帮助

- 完整文档: `UNIFIED_MODEL_SERVICE_README.md`
- 架构说明: `ARCHITECTURE_SUMMARY.md`
- 代码示例: `demo_unified_service.py`
- 测试用例: `test_model_service.py`

---

**统一模型服务** - 让AI模型调用变得简单! 🚀
