# 配置目录说明

此目录统一管理系统的所有配置文件。

## 目录结构

```
config/
├── __init__.py              # 配置模块入口，统一导出所有配置
├── settings.py              # 环境配置（API密钥、默认参数等）
├── evaluation.py            # 评测配置（评分维度、评测参数等）
├── models.py                # 模型注册表（所有可用模型配置）
├── models_export.json       # 导出的模型配置JSON
├── batch/                   # 批量处理配置
│   ├── batch_config.json           # 默认批量配置
│   ├── batch_config_baichuan.json  # 百川模型批量配置
│   ├── batch_config_doubao.json    # 豆包模型批量配置
│   ├── batch_config_kimi.json      # Kimi模型批量配置
│   └── batch_config_qwen.json      # 通义千问批量配置
└── README.md                # 本文档
```

## 配置文件说明

### 1. settings.py - 环境配置

**用途**: 管理环境变量和全局配置

**主要内容**:
```python
from config import settings

# API配置
settings.jiekou_api_key      # API密钥
settings.jiekou_base_url     # API基础URL

# 默认模型设置
settings.default_model       # 默认使用的模型
settings.default_temperature # 默认温度参数
settings.default_max_tokens  # 默认最大token数

# 日志配置
settings.log_level          # 日志级别
```

**依赖文件**: 根目录的 `.env` 文件

### 2. evaluation.py - 评测配置

**用途**: 定义评测维度、评分标准和评测参数

**主要内容**:
```python
from config import (
    EVALUATION_DIMENSIONS,  # 评估维度定义
    SCORE_RANGE,           # 评分范围
    OUTPUT_CONFIG,         # 输出目录配置
    API_CONFIG,            # API调用配置
    EVALUATION_CONFIG      # 评估流程配置
)
```

**评测维度** (5个维度):
- 准确性 (accuracy)
- 完整性 (completeness)
- 格式规范 (format)
- 语言表达 (language)
- 逻辑性 (logic)

**评分范围**: 1-5分
- 1: 非常差
- 2: 较差
- 3: 一般
- 4: 良好
- 5: 优秀

### 3. models.py - 模型注册表

**用途**: 管理所有可用的AI模型配置

**主要内容**:
```python
from config import get_model_registry

# 获取模型注册表
registry = get_model_registry()

# 注册新模型
registry.register_model(
    name="your-model",
    api_endpoint="https://api.example.com/v1",
    api_key="your-key",
    model_id="model-id"
)

# 获取模型配置
model_config = registry.get_model("gpt-5.1")

# 列出所有模型
all_models = registry.list_models()
```

**支持的模型厂商**:
- OpenAI (GPT系列)
- 阿里 (通义千问系列)
- DeepSeek
- 百川智能
- 字节跳动 (豆包系列)
- 月之暗面 (Moonshot)
- 零一万物 (Yi系列)
- 智谱AI (GLM系列)

### 4. batch/ - 批量处理配置

**用途**: 定义不同模型的批量评测配置

**配置格式**:
```json
{
  "models": ["model-1", "model-2"],
  "patients": ["患者1", "患者2"],
  "conversations": [1, 2, 3],
  "batch_size": 5,
  "parallel": true
}
```

**使用场景**:
- 批量评测特定厂商的所有模型
- 预设常用的评测组合
- 快速复现评测实验

## 使用方法

### 基础用法

```python
# 导入配置
from config import settings, EVALUATION_DIMENSIONS, get_model_registry

# 使用环境配置
api_key = settings.jiekou_api_key

# 使用评测配置
for dim_name, dim_config in EVALUATION_DIMENSIONS.items():
    print(f"{dim_config['name']}: {dim_config['description']}")

# 使用模型注册表
registry = get_model_registry()
models = registry.list_models()
```

### 高级用法

```python
# 动态修改配置
from config import API_CONFIG, EVALUATION_CONFIG

# 修改API配置
API_CONFIG['temperature'] = 0.5
API_CONFIG['max_retries'] = 5

# 修改评估配置
EVALUATION_CONFIG['batch_size'] = 10
EVALUATION_CONFIG['verbose_logging'] = True
```

### 加载批量配置

```python
import json

# 加载批量配置
with open('config/batch/batch_config_qwen.json', 'r') as f:
    batch_config = json.load(f)

# 使用配置运行评测
models = batch_config['models']
patients = batch_config['patients']
```

## 配置最佳实践

### 1. 环境变量管理

**开发环境**:
- 使用 `.env` 文件存储本地配置
- 不要提交 `.env` 文件到Git

**生产环境**:
- 使用环境变量或配置管理服务
- 定期轮换API密钥

### 2. 模型配置

**添加新模型**:
1. 在 `models.py` 中注册模型
2. 导出配置: `registry.export_to_file('config/models_export.json')`
3. 提交配置到Git

**更新模型配置**:
1. 修改 `models.py`
2. 重新导出JSON
3. 测试验证

### 3. 批量配置

**创建新配置**:
1. 复制 `batch_config.json` 作为模板
2. 修改模型、患者和对话类型
3. 保存为新文件

**命名规范**:
- `batch_config_{厂商}.json`: 按厂商分类
- `batch_config_{场景}.json`: 按场景分类
- `batch_config_{实验名}.json`: 按实验分类

## 配置迁移

### 从旧版本迁移

如果你的代码中使用了旧的导入路径：

```python
# 旧版本
from config import settings
from cross_evaluation.config import EVALUATION_DIMENSIONS
from cross_evaluation.model_registry import registry

# 新版本 (推荐)
from config import settings, EVALUATION_DIMENSIONS, get_model_registry

registry = get_model_registry()
```

### 向后兼容

为保持向后兼容，旧的导入路径仍然可用：
- `config.py` 仍存在于根目录（软链接到 `config/settings.py`）
- `cross_evaluation/config.py` 仍存在（软链接到 `config/evaluation.py`）
- `cross_evaluation/model_registry.py` 仍存在（软链接到 `config/models.py`）

## 配置验证

### 验证环境配置

```python
from config import settings

# 验证API密钥
if not settings.validate_api_key():
    print("错误: API密钥未配置或无效")
```

### 验证模型配置

```python
from config import get_model_registry

registry = get_model_registry()

# 验证模型是否存在
if not registry.has_model("gpt-5.1"):
    print("错误: 模型不存在")
```

## 常见问题

### Q: 如何添加新的评测维度？
A: 在 `config/evaluation.py` 的 `EVALUATION_DIMENSIONS` 字典中添加新维度。

### Q: 如何修改默认模型？
A: 编辑根目录的 `.env` 文件，修改 `DEFAULT_MODEL` 变量。

### Q: 批量配置文件的作用是什么？
A: 用于预定义常用的评测组合，避免每次手动指定参数。

### Q: 可以在运行时修改配置吗？
A: 可以，但只影响当前进程。永久修改需要编辑配置文件。

## 更新日志

### v1.0.0 (2024-11-21)
- 创建统一的配置目录
- 整合所有配置文件
- 添加配置文档

---

**维护者**: 项目团队
**最后更新**: 2024-11-21
