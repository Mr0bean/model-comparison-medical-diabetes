# 配置文件索引

快速导航到各配置文件和文档。

## 📋 配置文件

| 文件 | 用途 | 说明 |
|------|------|------|
| `settings.py` | 环境配置 | API密钥、默认参数、日志配置 |
| `evaluation.py` | 评测配置 | 评分维度、评测流程、输出目录 |
| `models.py` | 模型注册表 | 所有可用模型的配置和管理 |
| `models_export.json` | 模型配置导出 | JSON格式的模型配置 |

## 📁 子目录

| 目录 | 内容 | 说明 |
|------|------|------|
| `batch/` | 批量配置 | 不同模型/场景的批量评测配置 |

## 📖 文档

| 文档 | 内容 |
|------|------|
| [README.md](README.md) | 配置目录完整说明 |
| [CONFIG_OVERVIEW.md](CONFIG_OVERVIEW.md) | 配置快速参考和调优指南 |
| [INDEX.md](INDEX.md) | 本文档 - 配置索引 |

## 🚀 快速开始

### 1. 环境配置

```bash
# 复制环境变量模板
cp ../.env.example ../.env

# 编辑API密钥
# 填写 JIEKOU_API_KEY
```

### 2. 使用配置

```python
# 导入配置
from config import settings, EVALUATION_DIMENSIONS, get_model_registry

# 使用
api_key = settings.jiekou_api_key
dimensions = EVALUATION_DIMENSIONS
registry = get_model_registry()
```

### 3. 批量配置

```python
# 加载批量配置
import json
with open('config/batch/batch_config_qwen.json') as f:
    config = json.load(f)
```

## 📚 相关文档

- [项目主文档](../README.md)
- [架构文档](../ARCHITECTURE.md)
- [快速开始](../GETTING_STARTED.md)

## 🔗 常用链接

| 链接 | 说明 |
|------|------|
| [评测维度](#评测维度) | 5个评分维度说明 |
| [支持的模型](#支持的模型) | 10+主流模型列表 |
| [批量配置模板](#批量配置) | 批量评测配置示例 |
| [API配置](#api配置) | API调用参数 |

详细内容请查看 [CONFIG_OVERVIEW.md](CONFIG_OVERVIEW.md)

---

**快速查找**: 使用 `Ctrl+F` / `Cmd+F` 搜索配置项
