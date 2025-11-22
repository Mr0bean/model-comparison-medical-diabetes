# DeepSeek官方API集成架构

## 概述

DeepSeek官方API已完整集成到项目的模型注册表基座中，通过统一的接口访问，配置分离，易于管理和扩展。

## 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层                                   │
│  (run_cross_evaluation.py, 评测脚本等)                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  客户端工厂层                                 │
│          ModelClientFactory                                  │
│  ┌──────────────────────────────────────────────┐           │
│  │ create_client(model_name)                    │           │
│  │   ├─ 判断模型类型                             │           │
│  │   ├─ DeepSeek官方? → DeepSeekClient          │           │
│  │   └─ 其他模型? → ChatClient                   │           │
│  └──────────────────────────────────────────────┘           │
└────────────────────┬────────────────────────────────────────┘
                     │
      ┌──────────────┴──────────────┐
      ▼                              ▼
┌─────────────────┐          ┌─────────────────┐
│ DeepSeekClient  │          │   ChatClient    │
│  (官方API)      │          │   (通用客户端)   │
└────────┬────────┘          └────────┬────────┘
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│ OpenAI SDK      │          │ OpenAI SDK      │
│ (兼容接口)      │          │                 │
└────────┬────────┘          └────────┬────────┘
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌─────────────────┐
│ DeepSeek API    │          │ JieKou API      │
│ api.deepseek.com│          │ api.jiekou.ai   │
└─────────────────┘          └─────────────────┘
```

```
┌─────────────────────────────────────────────────────────────┐
│                     配置层                                    │
│                                                              │
│  ┌────────────────────────────────────────────────┐         │
│  │  ModelRegistry (模型注册表)                     │         │
│  │  ┌──────────────────────────────────────────┐  │         │
│  │  │ _load_configurations()                   │  │         │
│  │  │  ├─ 加载 Doubao 配置                      │  │         │
│  │  │  ├─ 加载 Qwen 配置                        │  │         │
│  │  │  ├─ 加载 Baichuan 配置                    │  │         │
│  │  │  ├─ 加载 DeepSeek官方 配置 ⭐             │  │         │
│  │  │  └─ 加载 其他默认配置                     │  │         │
│  │  └──────────────────────────────────────────┘  │         │
│  └────────────────────────────────────────────────┘         │
│                                                              │
│  配置文件:                                                    │
│  └─ config/batch/batch_config_deepseek_official.json        │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 配置文件 (`config/batch/batch_config_deepseek_official.json`)

**职责**: 存储DeepSeek官方API的配置信息

**内容**:
- API配置（base_url、api_key环境变量）
- 模型列表（deepseek-chat、deepseek-coder、deepseek-reasoner）
- 模型元数据（max_tokens、context_window、provider等）
- 默认参数（temperature、top_p、stream）

**示例**:
```json
{
  "api_config": {
    "api_key": "${DEEPSEEK_API_KEY}",
    "base_url": "https://api.deepseek.com"
  },
  "models": [
    {
      "name": "deepseek-chat",
      "display_name": "DeepSeek Chat",
      "max_tokens": 4096,
      "provider": "DeepSeek官方"
    }
  ]
}
```

### 2. 模型注册表 (`cross_evaluation/model_registry.py`)

**职责**: 加载和管理所有模型配置

**核心方法**:
```python
def _load_configurations(self):
    # 1. 加载 Kimi 配置
    # 2. 加载 Doubao 配置
    # 3. 加载 Qwen 配置
    # 4. 加载 Baichuan 配置
    # 5. 加载 DeepSeek官方 配置 ⭐ NEW
    # 6. 加载其他默认配置
```

**DeepSeek加载逻辑**:
```python
deepseek_config = self._load_json_config(
    "config/batch/batch_config_deepseek_official.json"
)
if deepseek_config:
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    for model_info in deepseek_config.get("models", []):
        if deepseek_api_key:  # 只有配置了API密钥才注册
            self.register_model(
                model_name=model_info.get("name"),
                api_key=deepseek_api_key,
                base_url=api_config.get("base_url"),
                provider=model_info.get("provider"),
                max_tokens=model_info.get("max_tokens", 4096)
            )
```

### 3. DeepSeek客户端 (`cross_evaluation/deepseek_client.py`)

**职责**: 封装DeepSeek官方API的调用逻辑

**核心类**:
- `DeepSeekClient`: DeepSeek客户端封装
- `DeepSeekClientFactory`: 客户端工厂（单例模式）
- `get_deepseek_client()`: 便捷函数

**特性**:
- ✅ OpenAI SDK兼容
- ✅ 流式输出支持
- ✅ 简化的聊天接口
- ✅ 错误处理
- ✅ 客户端缓存

**示例**:
```python
from cross_evaluation.deepseek_client import get_deepseek_client

client = get_deepseek_client()
response = client.chat_completion("Hello, DeepSeek!")
print(response)
```

### 4. 客户端工厂 (`cross_evaluation/model_client_factory.py`)

**职责**: 根据模型配置创建正确的客户端

**核心逻辑**:
```python
def create_client(self, model_name: str, **kwargs):
    config = self.registry.get_model_config(model_name)

    # 判断是否是DeepSeek官方API
    if self._is_deepseek_official(model_name, config):
        return DeepSeekClient(...)
    else:
        return ChatClient(...)
```

**判断条件**:
```python
def _is_deepseek_official(self, model_name: str, config: ModelConfig) -> bool:
    return (
        "api.deepseek.com" in config.base_url and
        model_name.startswith("deepseek-")
    )
```

## 数据流

### 使用流程

```
1. 用户调用评测脚本
   └─> run_cross_evaluation.py --models deepseek-chat

2. 创建客户端工厂
   └─> factory = ModelClientFactory('.')
       └─> 初始化ModelRegistry
           └─> 加载配置文件
               └─> 读取 batch_config_deepseek_official.json
                   └─> 从环境变量获取 DEEPSEEK_API_KEY
                       └─> 注册模型到registry

3. 创建客户端
   └─> client = factory.create_client('deepseek-chat')
       └─> 获取模型配置
           └─> 判断是否DeepSeek官方
               └─> 是 → 创建DeepSeekClient
                   └─> 初始化OpenAI客户端
                       └─> base_url = "https://api.deepseek.com"

4. 调用API
   └─> response = client.chat_completion("Hello")
       └─> 发送请求到DeepSeek官方API
           └─> 返回结果
```

## 配置分离设计

### 为什么分离配置？

1. **安全性**: API密钥通过环境变量管理，不硬编码
2. **灵活性**: 修改配置无需改代码
3. **可维护性**: 配置集中管理，易于查找和修改
4. **可扩展性**: 添加新模型只需修改JSON文件

### 配置层次

```
环境变量 (.env)
  └─> DEEPSEEK_API_KEY=sk-xxxxx

配置文件 (batch_config_deepseek_official.json)
  └─> 模型列表、参数配置

代码 (model_registry.py)
  └─> 加载逻辑、注册逻辑

客户端 (deepseek_client.py)
  └─> API调用逻辑
```

## 与现有系统的集成

### 无缝集成

```python
# 旧的方式（仍然支持）
from cross_evaluation.model_client_factory import ModelClientFactory
factory = ModelClientFactory('.')

# 使用JieKou API的DeepSeek
client = factory.create_client('deepseek/deepseek-v3.1')

# 使用DeepSeek官方API
client = factory.create_client('deepseek-chat')  # ⭐ 自动识别并使用官方客户端
```

### 兼容性

- ✅ 与现有评测脚本完全兼容
- ✅ 与现有模型注册表完全兼容
- ✅ 可与JieKou API的DeepSeek共存
- ✅ 统一的接口，无需修改业务代码

## 优势总结

### 对比传统方式

| 方面 | 传统方式 | 新架构 |
|-----|---------|--------|
| 配置管理 | 硬编码在代码中 | JSON配置文件 |
| API密钥 | 代码中明文 | 环境变量 |
| 添加新模型 | 修改代码 | 修改配置文件 |
| 客户端选择 | 手动判断 | 自动识别 |
| 代码复用 | 低 | 高 |

### 核心优势

1. **配置与代码分离**: 修改配置不需要改代码
2. **自动化客户端选择**: 根据配置自动选择正确的客户端
3. **统一接口**: 所有模型通过相同的接口访问
4. **易于扩展**: 添加新模型只需修改配置文件
5. **安全**: API密钥通过环境变量管理

## 使用示例

### 基础使用

```python
from cross_evaluation.model_client_factory import ModelClientFactory

# 创建工厂
factory = ModelClientFactory('.')

# 查看可用模型
models = factory.list_available_models()
print("DeepSeek模型:", [m for m in models if m.startswith('deepseek-')])

# 创建客户端（自动识别DeepSeek官方）
client = factory.create_client('deepseek-chat')

# 发送请求
response = client.chat_completion("介绍一下你自己")
print(response)
```

### 在评测中使用

```bash
# 使用DeepSeek官方API进行评测
python run_cross_evaluation.py \
  --models deepseek-chat deepseek-coder \
  --patients 患者1 患者2 \
  --conversations 1 2 3
```

## 测试

### 集成测试

```bash
# 完整集成测试
python test_deepseek_integration.py

# 测试内容：
# 1. 模型注册表加载DeepSeek配置
# 2. 客户端工厂创建DeepSeek客户端
# 3. 实际API调用
# 4. 完整使用流程
```

### 单元测试

```bash
# DeepSeek客户端测试
python test_deepseek.py

# 配置测试
python -c "from config import deepseek_settings; print(deepseek_settings.base_url)"
```

## 故障排查

### 常见问题

**Q: 模型注册表未加载DeepSeek配置？**
```bash
# 检查配置文件
ls -la config/batch/batch_config_deepseek_official.json

# 检查环境变量
echo $DEEPSEEK_API_KEY
```

**Q: 客户端工厂创建了ChatClient而不是DeepSeekClient？**
```bash
# 检查模型配置
python -c "
from cross_evaluation.model_registry import ModelRegistry
registry = ModelRegistry('.')
config = registry.get_model_config('deepseek-chat')
print('Base URL:', config.base_url)
print('Provider:', config.provider)
"
```

**Q: API调用失败？**
```bash
# 测试连接
python test_deepseek.py

# 检查API密钥
python -c "
import os
key = os.getenv('DEEPSEEK_API_KEY')
print('Key starts with sk-:', key and key.startswith('sk-'))
"
```

## 未来扩展

### 支持更多官方API

使用相同的架构可以轻松添加其他厂商的官方API：

1. 创建配置文件: `config/batch/batch_config_xxx_official.json`
2. 在`model_registry.py`中添加加载逻辑
3. 创建专门的客户端: `cross_evaluation/xxx_client.py`
4. 在`model_client_factory.py`中添加判断逻辑

### 配置版本管理

```json
{
  "version": "1.0.0",
  "last_updated": "2024-11-21",
  "api_config": { ... }
}
```

### 自动化测试

- 配置验证
- API连接测试
- 性能基准测试

---

**作者**: 项目团队
**最后更新**: 2024-11-21
**版本**: v1.0.0
