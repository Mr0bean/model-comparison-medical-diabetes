# 配置迁移指南

## 概述

为了更好地管理项目配置，我们将所有配置文件统一整合到 `config/` 目录下。

## 目录变更

### 之前

```
.
├── config.py                           # 环境配置
├── cross_evaluation/
│   ├── config.py                       # 评测配置
│   └── model_registry.py               # 模型注册表
├── batch_config.json                   # 批量配置
├── batch_config_baichuan.json
├── batch_config_doubao.json
├── batch_config_kimi.json
├── batch_config_qwen.json
└── model_registry_export.json
```

### 之后

```
config/
├── __init__.py                         # 配置模块入口
├── settings.py                         # 环境配置
├── evaluation.py                       # 评测配置
├── models.py                           # 模型注册表
├── models_export.json                  # 导出的模型配置
├── batch/                              # 批量配置目录
│   ├── batch_config.json
│   ├── batch_config_baichuan.json
│   ├── batch_config_doubao.json
│   ├── batch_config_kimi.json
│   └── batch_config_qwen.json
├── README.md                           # 配置说明文档
├── CONFIG_OVERVIEW.md                  # 配置快速参考
├── INDEX.md                            # 配置索引
└── MIGRATION_GUIDE.md                  # 本文档
```

## 代码迁移

### 旧的导入方式

```python
# 导入环境配置
from config import settings

# 导入评测配置
from cross_evaluation.config import EVALUATION_DIMENSIONS

# 导入模型注册表
from cross_evaluation.model_registry import registry
```

### 新的导入方式（推荐）

```python
# 统一从config模块导入
from config import (
    settings,
    EVALUATION_DIMENSIONS,
    get_model_registry
)

# 使用模型注册表
registry = get_model_registry()
```

## 文件对照表

| 旧路径 | 新路径 | 说明 |
|--------|--------|------|
| `config.py` | `config/settings.py` | 环境配置 |
| `cross_evaluation/config.py` | `config/evaluation.py` | 评测配置 |
| `cross_evaluation/model_registry.py` | `config/models.py` | 模型注册表 |
| `batch_config*.json` | `config/batch/batch_config*.json` | 批量配置 |
| `model_registry_export.json` | `config/models_export.json` | 模型配置导出 |

## 迁移步骤

### 1. 更新导入语句

在你的代码中搜索并替换：

```bash
# 全局搜索
grep -r "from config import" .
grep -r "from cross_evaluation.config import" .
grep -r "from cross_evaluation.model_registry import" .
```

### 2. 更新批量配置路径

如果你的脚本中硬编码了配置文件路径：

```python
# 旧路径
config_path = "batch_config_qwen.json"

# 新路径
config_path = "config/batch/batch_config_qwen.json"
```

### 3. 测试验证

运行测试确保迁移成功：

```bash
# 测试配置导入
python -c "from config import settings, EVALUATION_DIMENSIONS, get_model_registry; print('OK')"

# 测试模型注册表
python -c "from config import get_model_registry; print(get_model_registry().list_models())"
```

## 向后兼容

为了保持向后兼容，旧的导入路径仍然可用（通过软链接或重定向）：

- `config.py` → `config/settings.py`
- `cross_evaluation/config.py` → `config/evaluation.py`
- `cross_evaluation/model_registry.py` → `config/models.py`

**注意**: 建议尽快迁移到新的导入方式，旧方式可能在未来版本中移除。

## 好处

1. **集中管理**: 所有配置在一个目录下，易于查找和管理
2. **模块化**: 配置按功能分类，结构清晰
3. **文档完善**: 配置目录包含详细文档
4. **易于维护**: 统一的配置接口，减少重复代码

## 常见问题

### Q: 我的代码会不会因为这个改动而报错？
A: 不会。我们保留了向后兼容性，旧的导入路径仍然可用。

### Q: 何时需要强制迁移？
A: 建议在下次修改相关代码时顺便更新导入语句。

### Q: 批量配置文件需要修改吗？
A: 不需要。配置文件的内容格式没有变化，只是路径改变了。

### Q: 如何快速更新所有导入？
A: 使用IDE的全局搜索替换功能，或使用脚本批量替换。

## 帮助

如果在迁移过程中遇到问题：

1. 查看 [config/README.md](README.md) 了解详细配置说明
2. 参考 [config/CONFIG_OVERVIEW.md](CONFIG_OVERVIEW.md) 快速查找配置
3. 提交Issue寻求帮助

---

**版本**: v1.0.0
**更新日期**: 2024-11-21
