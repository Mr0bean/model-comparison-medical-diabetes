# 项目结构设计方案

## 📋 设计理念

### 当前问题
- ❌ 根目录平铺14个HTML文件
- ❌ Python脚本混杂
- ❌ 配置文件散落各处
- ❌ Web资源未集中管理
- ❌ 功能模块边界不清晰

### 解决方案
✅ **按功能分层**: 核心/业务/界面/配置/数据分离
✅ **模块化组织**: 每个模块独立目录
✅ **清晰的依赖关系**: 从底层到应用层
✅ **便于维护**: 一目了然的文件归属

## 🏗️ 新目录结构

```
chat/
│
├── 📦 src/                              # 源代码根目录
│   │
│   ├── 🎯 core/                         # 核心服务层
│   │   ├── __init__.py
│   │   ├── model_service.py             # 统一模型服务
│   │   ├── chat_client.py               # 基础聊天客户端
│   │   └── config_manager.py            # 配置管理器
│   │
│   ├── ⚙️ batch/                        # 批处理模块
│   │   ├── __init__.py
│   │   ├── unified_processor.py         # 统一批处理器
│   │   └── legacy/                      # 旧版批处理器
│   │       ├── __init__.py
│   │       ├── jiekou_processor.py      # JieKou处理器
│   │       ├── baichuan_processor.py    # 百川处理器
│   │       ├── doubao_processor.py      # 豆包处理器
│   │       ├── kimi_processor.py        # Kimi处理器
│   │       └── qwen_processor.py        # Qwen处理器
│   │
│   ├── 📊 evaluation/                   # 评测系统
│   │   ├── __init__.py
│   │   ├── auto_evaluator.py            # 自动评测器
│   │   ├── report_generator.py          # 报告生成器
│   │   ├── visualizer.py                # 数据可视化
│   │   └── prompts.py                   # 评测Prompt
│   │
│   └── 🛠️ utils/                        # 工具模块
│       ├── __init__.py
│       ├── data_processor.py            # 数据处理
│       ├── markdown_converter.py        # Markdown转换
│       ├── comparison_generator.py      # 对比数据生成
│       └── validators.py                # 数据验证
│
├── 🌐 web/                              # Web界面
│   │
│   ├── server/                          # 后端服务
│   │   ├── server.js                    # Express服务器
│   │   ├── package.json
│   │   ├── routes/                      # API路由
│   │   └── middleware/                  # 中间件
│   │
│   ├── pages/                           # 前端页面
│   │   ├── index.html                   # 主页
│   │   ├── admin.html                   # 管理页面
│   │   ├── model_comparison.html        # 模型对比
│   │   ├── model_evaluation.html        # 模型评测
│   │   ├── model_evaluation_chat.html
│   │   ├── model_evaluation_custom.html
│   │   ├── model_scoring_form.html
│   │   ├── model_scoring_table.html
│   │   ├── cross_evaluation_viewer.html
│   │   ├── comparison.html
│   │   └── user-guide.html
│   │
│   └── static/                          # 静态资源
│       ├── js/
│       │   ├── config.js
│       │   └── evaluation-auth.js
│       ├── css/
│       └── assets/
│
├── ⚙️ config/                           # 配置文件
│   │
│   ├── models/                          # 模型配置
│   │   └── model_registry.json          # 模型注册表
│   │
│   ├── batch/                           # 批处理配置
│   │   ├── unified_batch_config.json    # 统一配置
│   │   ├── batch_config.json            # JieKou配置
│   │   ├── batch_config_baichuan.json
│   │   ├── batch_config_doubao.json
│   │   ├── batch_config_kimi.json
│   │   └── batch_config_qwen.json
│   │
│   ├── prompts/                         # Prompt配置
│   │   ├── ai_evaluation_prompts.py
│   │   └── templates/                   # Prompt模板
│   │       ├── medical_report/
│   │       └── report_test/
│   │
│   └── deployment/                      # 部署配置
│       └── ecosystem.config.js          # PM2配置
│
├── 💾 data/                             # 数据目录
│   │
│   ├── input/                           # 输入数据
│   │   ├── records/                     # 患者记录
│   │   └── test_records/                # 测试记录
│   │
│   ├── output/                          # 输出数据
│   │   ├── raw/                         # 原始输出
│   │   ├── unified/                     # 统一输出
│   │   ├── markdown/                    # Markdown格式
│   │   └── comparison/                  # 对比数据
│   │
│   └── evaluation/                      # 评测结果
│       ├── reports/                     # 评测报告
│       ├── charts/                      # 图表
│       └── detailed_results/            # 详细结果
│
├── 🔧 scripts/                          # 独立脚本
│   │
│   ├── cli/                             # 命令行工具
│   │   ├── simple_chat.py               # 简单聊天
│   │   ├── chat_cli.py                  # 聊天CLI
│   │   └── quick_start.py               # 快速启动
│   │
│   ├── tools/                           # 辅助工具
│   │   ├── check_prompts.py             # 检查Prompt
│   │   └── quick_test.py                # 快速测试
│   │
│   └── migration/                       # 迁移脚本
│       └── migrate_to_unified.py        # 迁移到统一服务
│
├── 🧪 tests/                            # 测试
│   ├── __init__.py
│   ├── test_model_service.py
│   ├── test_ai_evaluation.py
│   ├── test_conversation.py
│   └── test_log.py
│
├── 🎮 demos/                            # 演示
│   ├── demo_unified_service.py
│   └── demo_ai_evaluation.py
│
├── 📖 examples/                         # 示例代码
│   ├── basic_usage.py
│   ├── advanced_usage.py
│   ├── interactive_chat.py
│   └── session_manager_usage.py
│
├── 📚 docs/                             # 文档
│   ├── QUICK_START_GUIDE.md
│   ├── UNIFIED_MODEL_SERVICE_README.md
│   ├── ARCHITECTURE_SUMMARY.md
│   ├── AI_EVALUATION_STANDARD.md
│   ├── AI_EVALUATION_SUMMARY.md
│   └── API_REFERENCE.md                 # API参考文档(新增)
│
├── 📄 根目录文件
│   ├── README.md                        # 项目说明
│   ├── .env                             # 环境变量
│   ├── .env.example                     # 环境变量示例
│   ├── requirements.txt                 # Python依赖
│   ├── .gitignore
│   └── LICENSE
│
└── 🗑️ 临时/缓存
    ├── __pycache__/
    ├── .pytest_cache/
    └── logs/                            # 日志文件
```

## 📊 模块依赖关系

```
┌─────────────────────────────────────────────────────────┐
│                        应用层                            │
│  web/pages/  │  scripts/cli/  │  demos/  │  examples/  │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                       业务层                             │
│   src/batch/   │   src/evaluation/   │   src/utils/    │
└────────────────┬────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                      核心层                              │
│          src/core/ (model_service, chat_client)         │
└─────────────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────┐
│                     配置/数据层                          │
│          config/  │  data/                              │
└─────────────────────────────────────────────────────────┘
```

## 🎯 模块职责

### src/core/ - 核心服务层
**职责**: 提供底层AI模型调用能力
- `model_service.py`: 统一模型服务接口
- `chat_client.py`: OpenAI兼容客户端
- `config_manager.py`: 配置加载和管理

**依赖**: config/, .env
**被依赖**: src/batch/, src/evaluation/, scripts/

### src/batch/ - 批处理模块
**职责**: 批量处理AI任务
- `unified_processor.py`: 统一批处理器(推荐)
- `legacy/`: 旧版专用处理器(向后兼容)

**依赖**: src/core/, config/batch/
**被依赖**: scripts/, demos/

### src/evaluation/ - 评测系统
**职责**: AI输出质量评测
- `auto_evaluator.py`: 自动化评测
- `report_generator.py`: 生成评测报告
- `visualizer.py`: 数据可视化

**依赖**: src/core/, config/prompts/
**被依赖**: web/server/, scripts/

### src/utils/ - 工具模块
**职责**: 通用工具函数
- 数据处理、格式转换、验证等

**依赖**: 无
**被依赖**: 所有模块

### web/ - Web界面
**职责**: 提供可视化界面
- `server/`: Express后端API
- `pages/`: HTML前端页面
- `static/`: 静态资源

**依赖**: src/evaluation/, data/
**被依赖**: 无

### config/ - 配置管理
**职责**: 集中管理所有配置
- `models/`: 模型配置
- `batch/`: 批处理配置
- `prompts/`: Prompt模板

**依赖**: 无
**被依赖**: 所有模块

### data/ - 数据管理
**职责**: 存储输入输出数据
- `input/`: 输入数据
- `output/`: 处理结果
- `evaluation/`: 评测结果

**依赖**: 无
**被依赖**: src/batch/, src/evaluation/

### scripts/ - 独立脚本
**职责**: 命令行工具和辅助脚本
- `cli/`: 交互式命令行工具
- `tools/`: 独立工具脚本

**依赖**: src/core/, src/batch/
**被依赖**: 无

## 🚀 迁移步骤

### 阶段1: 创建新目录结构
```bash
# 创建所有目录
mkdir -p src/{core,batch/legacy,evaluation,utils}
mkdir -p web/{server,pages,static/{js,css,assets}}
mkdir -p config/{models,batch,prompts/templates,deployment}
mkdir -p data/{input/{records,test_records},output/{raw,unified,markdown,comparison},evaluation/{reports,charts,detailed_results}}
mkdir -p scripts/{cli,tools,migration}
```

### 阶段2: 移动核心文件
```bash
# 核心服务
mv model_service.py src/core/
mv chat_client.py src/core/
mv config.py src/core/config_manager.py

# 批处理
mv unified_batch_processor.py src/batch/unified_processor.py
mv legacy_batch_processors/*.py src/batch/legacy/

# 评测系统
mv evaluation_toolkit/*.py src/evaluation/

# 工具
mv prepare_comparison_data.py src/utils/comparison_generator.py
mv convert_to_markdown.py src/utils/markdown_converter.py
mv generate_comparison_page.py src/utils/comparison_generator.py
mv extract_results_to_markdown.py src/utils/markdown_converter.py
```

### 阶段3: 移动Web文件
```bash
# 后端
mv server/* web/server/

# 前端页面
mv *.html web/pages/

# 静态资源
mv config.js web/static/js/
mv evaluation-auth.js web/static/js/
mv ecosystem.config.js config/deployment/
```

### 阶段4: 移动配置文件
```bash
# 模型配置
mv model_registry.json config/models/

# 批处理配置
mv *batch_config*.json config/batch/

# Prompts
mv config/ai_evaluation_prompt.py config/prompts/ai_evaluation_prompts.py
mv Prompts/* config/prompts/templates/
```

### 阶段5: 移动数据和脚本
```bash
# 数据
mv 测试输入问答记录/* data/input/test_records/
mv output/* data/output/
mv evaluation_results/* data/evaluation/

# 脚本
mv simple_chat.py scripts/cli/
mv chat_cli.py scripts/cli/
mv quick_start.py scripts/cli/
mv check_prompts.py scripts/tools/
mv quick_test.py scripts/tools/
```

### 阶段6: 更新导入路径
需要更新所有Python文件的import语句:
```python
# 旧的
from model_service import UniversalModelService
from chat_client import ChatClient

# 新的
from src.core.model_service import UniversalModelService
from src.core.chat_client import ChatClient
```

### 阶段7: 创建__init__.py
为每个Python包创建__init__.py,方便导入:
```python
# src/core/__init__.py
from .model_service import UniversalModelService, ModelRegistry
from .chat_client import ChatClient
from .config_manager import ConfigManager

__all__ = ['UniversalModelService', 'ModelRegistry', 'ChatClient', 'ConfigManager']
```

## ✅ 迁移后的优势

### 清晰的结构
- ✅ 功能模块一目了然
- ✅ 文件归属清晰
- ✅ 便于新人理解

### 便于维护
- ✅ 修改影响范围明确
- ✅ 依赖关系清晰
- ✅ 测试覆盖完整

### 易于扩展
- ✅ 新功能有明确位置
- ✅ 模块化设计
- ✅ 插件化支持

### 部署友好
- ✅ Web资源集中
- ✅ 配置统一管理
- ✅ 数据独立存储

## 📝 注意事项

### 向后兼容
- 保留旧的批处理器在 `src/batch/legacy/`
- 提供迁移脚本和文档
- 渐进式迁移,不影响现有功能

### 文档更新
- 更新所有文档中的路径引用
- 更新README.md
- 添加迁移指南

### 测试覆盖
- 所有模块添加单元测试
- 集成测试验证迁移正确性
- CI/CD流程适配新结构

## 🎯 下一步行动

1. ✅ **审查方案** - 确认目录结构设计
2. ⏭️ **执行迁移** - 按阶段迁移文件
3. ⏭️ **更新导入** - 修改所有import语句
4. ⏭️ **测试验证** - 运行测试确保正常
5. ⏭️ **更新文档** - 更新所有文档
6. ⏭️ **提交变更** - Git提交新结构

---

**设计原则**: 模块化、分层清晰、便于维护、易于扩展
