# 医疗模型横评对比系统 - 糖尿病病历生成

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于对比不同AI模型在糖尿病病历生成任务中表现的可视化系统。

## ✨ 功能特点

- 🔄 **多维度对比**：支持多患者、多模型、多对话类型的灵活对比
- 🎨 **可视化界面**：现代化的渐变设计，模型颜色区分
- 📊 **两种布局模式**：
  - 自动换行布局 - 响应式网格，适合查看2-4个模型
  - 固定横向排列 - 支持同步滚动，方便多患者对比
- 🎯 **智能同步滚动**：横向布局下，相同对话类型自动同步滚动
- 📝 **数据导出**：支持将对话数据导出为Markdown格式

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js (可选，用于启动HTTP服务器)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置API密钥

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入您的API密钥：
```bash
JIEKOU_API_KEY=your_actual_api_key_here
```

### 运行系统

#### 1. 生成对话数据（可选）

如果需要生成新的对话数据：

```bash
# 使用交互式脚本
python simple_chat.py

# 或使用命令行脚本
python chat_cli.py --system "你是一名经验丰富的内分泌科医生" --user "患者主诉"
```

#### 2. 转换数据为Markdown

```bash
python convert_to_markdown.py
```

#### 3. 准备对比数据

```bash
python prepare_comparison_data.py
```

#### 4. 启动Web界面

使用Python内置服务器：
```bash
python -m http.server 8888
```

或使用Node.js的http-server：
```bash
npm install -g http-server
http-server -p 8888
```

然后在浏览器访问：`http://localhost:8888/model_comparison.html`

## 📁 项目结构

```
.
├── chat_client.py              # AI对话客户端
├── config.py                   # 配置管理
├── simple_chat.py              # 交互式对话脚本
├── chat_cli.py                 # 命令行对话脚本
├── convert_to_markdown.py      # JSON转Markdown工具
├── prepare_comparison_data.py  # 数据准备工具
├── model_comparison.html       # Web对比界面
├── output/
│   ├── raw/                    # 原始JSON数据
│   ├── markdown/               # Markdown格式数据
│   └── comparison_data.json    # 前端对比数据
├── .env.example                # 环境变量模板
├── .gitignore                  # Git忽略配置
├── requirements.txt            # Python依赖
└── README.md                   # 项目文档
```

## 🎯 支持的模型

系统目前支持以下AI模型：

- gpt-5.1
- deepseek/deepseek-v3.1
- gemini-2.5-pro
- qwen3-max
- grok-4-0709
- moonshotai/kimi-k2-0905
- doubao-seed-1-6-251015
- Baichuan-M2

每个模型都有独特的颜色标识，方便快速识别。

## 📖 使用指南

### Web界面操作

1. **选择患者**：点击或勾选要对比的患者（支持多选）
2. **选择模型**：勾选要对比的AI模型（支持多选）
3. **选择对话类型**：勾选要查看的病历部分（主诉、现病史、既往史等）
4. **切换布局**：选择"自动换行"或"固定横向排列"布局
5. **查看对比**：在下方查看不同模型的输出结果

### 布局模式说明

- **自动换行布局**：
  - 响应式网格，每行2-3个卡片
  - 适合详细对比2-4个模型
  - 超出自动换行

- **固定横向排列**：
  - 所有卡片横向排列，支持横向滚动
  - 相同对话类型自动同步滚动
  - 适合多患者同类型对比观察

## 🔧 配置说明

### 环境变量

编辑 `.env` 文件进行配置：

```bash
# API配置
JIEKOU_API_KEY=your_api_key_here
JIEKOU_BASE_URL=https://api.jiekou.ai/openai

# 模型配置
DEFAULT_MODEL=gpt-5.1
DEFAULT_TEMPERATURE=1.0
DEFAULT_MAX_TOKENS=2048
DEFAULT_STREAM=True

# 日志配置
LOG_LEVEL=INFO
```

### 模型颜色自定义

在 `model_comparison.html` 中的 `modelColors` 对象可以自定义模型颜色：

```javascript
const modelColors = {
    'gpt-5.1': { start: '#667eea', end: '#764ba2' },
    'your-model': { start: '#start-color', end: '#end-color' }
};
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 👨‍💻 作者

Mr0bean

## 🙏 致谢

- JieKou AI 提供API支持
- 所有贡献者和用户的支持

---

如有问题或建议，欢迎提交Issue！
