# 医疗AI模型评测系统

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-14+-green.svg)](https://nodejs.org/)

一个全栈评测平台，用于评估和对比多个大语言模型在医疗场景（病历生成、诊断建议等）下的表现。支持多模型对比、交叉评测、可视化展示和评分管理。

## ✨ 功能特点

- 🔄 **多模型对比**：支持10+主流大语言模型同时对比
- 💬 **对话可视化**：聊天气泡界面展示医患对话，左侧固定，高度自适应
- 📊 **五维度评分**：专业性、完整性、逻辑性、实用性、格式规范
- 🔁 **交叉评测**：模型互评机制，自动生成评分矩阵
- 📈 **实时统计**：评测进度跟踪和数据分析
- 🎨 **响应式设计**：支持多屏幕尺寸，横向滚动查看
- 💾 **数据持久化**：MongoDB存储评测结果，支持导出
- 🔧 **易扩展**：模块化设计，轻松添加新模型

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 14+
- MongoDB 4.4+

### 1. 安装依赖

```bash
# Python依赖
pip install -r requirements.txt

# Node.js依赖
cd server && npm install
```

### 2. 配置环境

**Python配置** (根目录 `.env`):
```bash
cp .env.example .env
# 编辑.env，填入API密钥
```

**Node.js配置** (`server/.env`):
```bash
cd server && cp .env.example .env
# 编辑server/.env，配置MongoDB连接
```

### 3. 启动服务

```bash
# 启动MongoDB
mongod --dbpath /data/db

# 启动Express后端
cd server && npm start

# 打开前端页面
open index.html
```

### 4. 运行评测

```bash
# 单次评测
python run_cross_evaluation.py --models gpt-5.1 qwen3-max --patients 患者1

# 批量评测
python run_batch_evaluation.py

# 交叉评测
python run_report_cross_evaluation.py --yes
```

**详细教程**: 查看 [GETTING_STARTED.md](GETTING_STARTED.md)

## 📁 项目结构

```
.
├── cross_evaluation/               # 评测引擎核心代码
│   ├── engine.py                  # 评测引擎
│   ├── report_evaluation_engine.py # 报告评测引擎
│   ├── model_registry.py          # 模型注册表
│   ├── model_client_factory.py    # 模型客户端工厂
│   ├── prompt_template.py         # 提示词模板
│   └── conversation_indexer.py    # 对话索引器
├── server/                         # Express后端服务
│   ├── server.js                  # 主服务文件
│   ├── package.json               # Node.js依赖
│   └── .env                       # 数据库配置
├── output/                         # 评测结果输出
│   ├── cross_evaluation_results/  # 交叉评测结果JSON
│   ├── raw/                       # 原始对话数据
│   ├── markdown/                  # Markdown格式结果
│   └── comparison_data.json       # 前端对比数据
├── 测试输入问答记录/               # 患者对话数据
├── *.html                          # 前端页面
│   ├── index.html                 # 主导航页
│   ├── model_comparison.html      # 模型横评对比
│   ├── model_evaluation_chat.html # 评测界面
│   ├── admin.html                 # 管理面板
│   └── user-guide.html            # 用户手册
├── config.py                       # Python配置管理
├── requirements.txt                # Python依赖
├── ARCHITECTURE.md                 # 架构文档
├── GETTING_STARTED.md              # 快速开始指南
└── README.md                       # 项目文档
```

**详细架构**: 查看 [ARCHITECTURE.md](ARCHITECTURE.md)

## 🎯 支持的模型

| 厂商 | 模型 | 状态 |
|------|------|------|
| OpenAI | GPT-4o, GPT-4o-mini, GPT-5.1 | ✅ |
| 阿里 | Qwen3-max, Qwen3-72b, Qwen3-14b | ✅ |
| DeepSeek | DeepSeek-v3, DeepSeek-chat | ✅ |
| 百川 | Baichuan2-13B, Baichuan-M2 | ✅ |
| 字节 | Doubao系列 | ✅ |
| 月之暗面 | Moonshot-v1 | ✅ |
| 零一万物 | Yi-Lightning, Yi-Large | ✅ |
| 智谱 | GLM-4-Plus | ✅ |

每个模型都有独特的渐变色标识，方便快速识别。

## 📖 核心功能

### 1. 模型横评对比 (`model_comparison.html`)

**特性**:
- 对话面板固定在左侧第一列，宽450px
- 对话面板高度自适应最高的模型卡片
- 模型卡片横向滚动查看
- 聊天气泡界面可视化对话

**使用步骤**:
1. 选择患者（支持多选）
2. 选择模型和对话类型
3. 查看对话记录和模型输出对比

### 2. 人工评测 (`model_evaluation_chat.html`)

**评分维度**:
- 专业性和准确性 (30%)
- 完整性和深度 (25%)
- 逻辑性和条理性 (20%)
- 实用性和可操作性 (15%)
- 格式规范性 (10%)

**特性**:
- 自动保存到MongoDB
- 进度跟踪
- 自动关闭评测窗口

### 3. 交叉评测 (`cross_evaluation_viewer.html`)

**功能**:
- 模型互评矩阵
- 热力图可视化
- 统计分析

### 4. 管理面板 (`admin.html`)

**功能**:
- 查看所有评测数据
- 完成进度统计
- 删除/编辑记录
- 数据导出

## 🔧 配置说明

### Python配置 (`.env`)

```bash
JIEKOU_API_KEY=your_api_key_here
JIEKOU_BASE_URL=https://api.jiekou.ai/openai
DEFAULT_MODEL=gpt-5.1
LOG_LEVEL=INFO
```

### Node.js配置 (`server/.env`)

```bash
MONGODB_URI=mongodb://localhost:27017/medical-evaluation
PORT=3000
```

### 添加新模型

在 `cross_evaluation/model_registry.py` 中注册：

```python
registry.register_model(
    name="your-model",
    api_endpoint="https://api.example.com/v1",
    api_key="your-key",
    model_id="model-id"
)
```

## 📡 API接口

### 获取评测数据
```http
GET /api/evaluations?patient=患者1&model=gpt-5.1
```

### 提交评测
```http
POST /api/evaluations
Content-Type: application/json

{
  "patient": "患者1",
  "conversationId": "1",
  "model": "gpt-5.1",
  "scores": {...}
}
```

### 统计数据
```http
GET /api/stats
```

## 🤝 贡献

欢迎贡献代码！

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 📚 文档

- [ARCHITECTURE.md](ARCHITECTURE.md) - 系统架构详解
- [GETTING_STARTED.md](GETTING_STARTED.md) - 快速开始指南
- [user-guide.html](user-guide.html) - 用户使用手册

## ❓ 常见问题

**Q: 如何添加新模型？**
A: 在 `model_registry.py` 注册模型，系统自动识别。

**Q: 评测结果保存在哪里？**
A: `output/cross_evaluation_results/` 目录下的JSON文件和MongoDB数据库。

**Q: 如何批量评测？**
A: 使用 `run_batch_evaluation.py` 脚本。

更多问题请查看 [GETTING_STARTED.md](GETTING_STARTED.md#常见问题)

## 🙏 致谢

- OpenAI 提供API接口标准
- 各大模型厂商提供优质服务
- 开源社区贡献的工具和库

## 📧 联系方式

- 问题反馈: [GitHub Issues](../../issues)
- 项目讨论: [GitHub Discussions](../../discussions)

---

**⭐ Star本项目如果对你有帮助！**

**版本**: v1.0.0 | **最后更新**: 2024-11-21
