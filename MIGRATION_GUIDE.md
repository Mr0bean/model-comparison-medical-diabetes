# 迁移指南 - Migration Guide

## 📋 概述

项目已从平铺结构重构为模块化分层结构。本指南帮助你快速适应新结构。

## 🔄 目录结构变化

### 旧结构 (v1.0) - 平铺式
```
chat/
├── model_service.py
├── chat_client.py
├── unified_batch_processor.py
├── admin.html
├── model_comparison.html
├── ... (64个文件平铺)
```

### 新结构 (v2.0) - 模块化
```
chat/
├── src/                  # 源代码
│   ├── core/            # 核心服务
│   ├── batch/           # 批处理
│   ├── evaluation/      # 评测系统
│   └── utils/           # 工具
├── web/                 # Web界面
│   ├── server/         # 后端
│   ├── pages/          # 前端
│   └── static/         # 静态资源
├── config/              # 配置
├── data/                # 数据
├── scripts/             # 脚本
├── tests/               # 测试
├── demos/               # 演示
└── docs/                # 文档
```

## 🔧 使用新结构

### 方式1: 使用新目录(推荐)

```python
# 从新位置导入
from src.core import UniversalModelService, call_model
from src.batch import UnifiedBatchProcessor
from src.evaluation import AutoEvaluator

# 使用方式不变
service = UniversalModelService()
response = service.call("gpt-5.1", "问题")
```

### 方式2: 兼容旧代码(临时)

根目录仍保留原文件,可继续使用旧的导入:

```python
# 旧的导入方式仍然有效
from model_service import UniversalModelService
from chat_client import ChatClient
```

## 📂 文件位置对照表

### Python模块

| 旧位置 | 新位置 | 说明 |
|-------|-------|------|
| `model_service.py` | `src/core/model_service.py` | 统一模型服务 |
| `chat_client.py` | `src/core/chat_client.py` | 聊天客户端 |
| `config.py` | `src/core/config_manager.py` | 配置管理 |
| `unified_batch_processor.py` | `src/batch/unified_processor.py` | 统一批处理 |
| `legacy_batch_processors/*.py` | `src/batch/legacy/*.py` | 旧版处理器 |
| `evaluation_toolkit/*.py` | `src/evaluation/*.py` | 评测工具 |
| `prepare_comparison_data.py` | `src/utils/comparison_generator.py` | 数据处理 |
| `convert_to_markdown.py` | `src/utils/markdown_converter.py` | 格式转换 |

### Web文件

| 旧位置 | 新位置 |
|-------|-------|
| `*.html` (14个HTML文件) | `web/pages/*.html` |
| `server/server.js` | `web/server/server.js` |
| `config.js` | `web/static/js/config.js` |
| `evaluation-auth.js` | `web/static/js/evaluation-auth.js` |

### 配置文件

| 旧位置 | 新位置 |
|-------|-------|
| `model_registry.json` | `config/models/model_registry.json` |
| `*batch_config*.json` | `config/batch/*.json` |
| `config/ai_evaluation_prompt.py` | `config/prompts/ai_evaluation_prompts.py` |
| `Prompts/*` | `config/prompts/templates/*` |
| `ecosystem.config.js` | `config/deployment/ecosystem.config.js` |

### 脚本和工具

| 旧位置 | 新位置 |
|-------|-------|
| `simple_chat.py` | `scripts/cli/simple_chat.py` |
| `chat_cli.py` | `scripts/cli/chat_cli.py` |
| `quick_start.py` | `scripts/cli/quick_start.py` |
| `check_prompts.py` | `scripts/tools/check_prompts.py` |
| `quick_test.py` | `scripts/tools/quick_test.py` |

## 🚀 快速开始

### 1. 使用统一模型服务(推荐新方式)

```python
# 新的导入方式
from src.core import call_model, UniversalModelService

# 快速调用
response = call_model("gpt-5.1", "什么是AI?")

# 完整使用
service = UniversalModelService()
response = service.call(
    model="gpt-5.1",
    prompt="问题",
    temperature=0.7
)
```

### 2. 运行批量处理

```bash
# 方式1: 直接运行(旧)
python unified_batch_processor.py

# 方式2: 使用新路径
python -m src.batch.unified_processor

# 方式3: 使用脚本
cd scripts/tools && python quick_test.py
```

### 3. 启动Web服务

```bash
# 进入web/server目录
cd web/server

# 安装依赖(如果还没安装)
npm install

# 启动服务
node server.js

# 访问页面
# http://localhost:3001/pages/admin.html
# http://localhost:3001/pages/model_comparison.html
```

### 4. 运行测试

```bash
# 测试仍在tests/目录
python tests/test_model_service.py
python tests/test_ai_evaluation.py
```

### 5. 查看演示

```bash
# 演示仍在demos/目录
python demos/demo_unified_service.py
python demos/demo_ai_evaluation.py
```

## 📝 配置文件更新

### 模型配置

```python
# 旧: model_registry.json
# 新: config/models/model_registry.json

# 代码中加载配置
from src.core import UniversalModelService

# 默认从config/models/model_registry.json加载
service = UniversalModelService()

# 或指定路径
service = UniversalModelService("config/models/model_registry.json")
```

### 批处理配置

```bash
# 旧: unified_batch_config.json
# 新: config/batch/unified_batch_config.json
```

## ⚠️ 注意事项

### 1. 向后兼容

根目录仍保留原文件,旧代码暂时可以正常运行。但建议逐步迁移到新结构。

### 2. 导入路径

如果使用新结构,需要更新导入语句:

```python
# ❌ 旧的(仍可用,但不推荐)
from model_service import UniversalModelService

# ✅ 新的(推荐)
from src.core import UniversalModelService
```

### 3. Web服务路径

Web服务器启动后,HTML页面路径变化:

```
旧: http://localhost:3001/admin.html
新: http://localhost:3001/pages/admin.html

或者在server.js中配置路由,保持旧路径
```

### 4. 数据路径

如果代码中有硬编码路径,需要更新:

```python
# ❌ 旧的
output_dir = "./output/raw"

# ✅ 新的
output_dir = "./data/output/raw"
```

## 🎯 迁移步骤建议

### 阶段1: 熟悉新结构(当前)
- 查看PROJECT_STRUCTURE.md了解设计
- 查看本文档了解变化
- 测试新导入方式是否工作

### 阶段2: 逐步迁移代码(推荐)
- 新功能使用新结构开发
- 旧代码继续使用旧路径
- 有时间时逐步迁移旧代码

### 阶段3: 完全切换(未来)
- 所有代码使用新导入
- 删除根目录的重复文件
- 只保留最小文件集

## 📚 相关文档

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 详细的结构设计
- [README.md](README.md) - 项目说明
- [docs/QUICK_START_GUIDE.md](docs/QUICK_START_GUIDE.md) - 快速开始
- [docs/UNIFIED_MODEL_SERVICE_README.md](docs/UNIFIED_MODEL_SERVICE_README.md) - 统一服务文档

## ❓ 常见问题

### Q: 旧代码还能用吗?

A: 能!根目录仍保留原文件,旧代码可以正常运行。

### Q: 必须马上迁移吗?

A: 不必!可以逐步迁移。新功能用新结构,旧代码保持不变。

### Q: 如何找到文件新位置?

A: 查看上面的"文件位置对照表",或者使用find命令:
```bash
find . -name "model_service.py"
```

### Q: Web服务如何访问新的HTML?

A: 两种方式:
1. 访问 `/pages/admin.html`
2. 或在server.js中配置路由保持旧路径

### Q: 配置文件路径改了怎么办?

A: 修改代码中的路径,或通过参数指定:
```python
service = UniversalModelService("config/models/model_registry.json")
```

## 💡 最佳实践

1. **新项目**: 直接使用新结构
2. **维护旧代码**: 保持原样,不强制迁移
3. **重构代码**: 逐步更新导入路径
4. **添加功能**: 放入对应的src/模块
5. **测试充分**: 迁移后运行完整测试

---

**核心理念**: 渐进式迁移,不影响现有功能 🚀
