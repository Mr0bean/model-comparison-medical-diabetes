# 快速开始指南

## 项目简介

医疗AI模型评测系统用于评估和对比多个大语言模型在医疗场景下的表现，包括病历生成、诊断建议等任务。

## 环境要求

- **Python**: 3.8+
- **Node.js**: 14+
- **MongoDB**: 4.4+
- **浏览器**: Chrome/Firefox/Safari最新版

## 快速安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd chat
```

### 2. Python环境配置

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. Node.js后端配置

```bash
cd server
npm install
```

### 4. 配置环境变量

**根目录 `.env`** (Python配置):
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

```env
JIEKOU_API_KEY=your_api_key_here
JIEKOU_BASE_URL=https://api.jiekou.ai/openai
DEFAULT_MODEL=gpt-5.1
LOG_LEVEL=INFO
```

**server/.env** (Node.js配置):
```bash
cd server
cp .env.example .env
```

```env
MONGODB_URI=mongodb://localhost:27017/medical-evaluation
PORT=3000
```

### 5. 启动MongoDB

```bash
# macOS (通过Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# 或直接运行
mongod --dbpath /data/db
```

### 6. 启动服务

**终端1 - 启动Express后端**:
```bash
cd server
npm start
# 服务运行在 http://localhost:3000
```

**终端2 - 打开前端界面**:
```bash
# 方法1: 直接在浏览器打开
open index.html

# 方法2: 使用简单HTTP服务器
python -m http.server 8080
# 访问 http://localhost:8080
```

## 使用流程

### 步骤1: 准备对话数据

将患者对话记录放在 `测试输入问答记录/` 目录下，格式示例：

```
患者1_问答记录.txt
患者2_问答记录.txt
...
```

文件内容格式：
```
============================
患者基本信息
============================
姓名: 张三
年龄: 45岁
性别: 男
主诉: 胸闷气短一周

============================
预问诊对话记录
============================
1. 患者: 医生您好，我最近一周总是感觉胸闷气短
2. 医助: 您好，请问这种症状是持续性的还是间歇性的？
...
```

### 步骤2: 运行模型评测

#### 方法1: 单次评测
```bash
python run_cross_evaluation.py \
  --models gpt-5.1 qwen3-max \
  --patients 患者1 患者2 \
  --conversations 1 2
```

#### 方法2: 批量评测
```bash
python run_batch_evaluation.py
```

#### 方法3: 报告交叉评测
```bash
python run_report_cross_evaluation.py --yes
```

结果保存在 `output/cross_evaluation_results/`

### 步骤3: 查看对比结果

1. 打开 `model_comparison.html`
2. 选择患者、模型和对话类型
3. 查看对比结果和对话可视化

### 步骤4: 人工评分

1. 打开 `model_evaluation_chat.html`
2. 选择患者和对话类型
3. 阅读模型生成的报告
4. 在五个维度上打分（0-100分）：
   - 专业性和准确性 (30%)
   - 完整性和深度 (25%)
   - 逻辑性和条理性 (20%)
   - 实用性和可操作性 (15%)
   - 格式规范性 (10%)
5. 点击"提交评测"保存

### 步骤5: 查看管理面板

1. 打开 `admin.html`
2. 查看所有评测数据
3. 查看完成进度统计
4. 管理评测记录

## 核心功能说明

### 1. 模型横评对比 (`model_comparison.html`)

**功能**:
- 同时查看多个模型对同一患者的输出
- 对话可视化展示（左侧固定）
- 支持多维度筛选

**使用技巧**:
- 对话面板固定在左侧，便于查看原始对话
- 模型卡片可以横向滚动
- 支持多患者切换对比

### 2. 模型评测界面 (`model_evaluation_chat.html`)

**功能**:
- 单模型深度评测
- 五维度评分系统
- 自动保存到数据库
- 进度跟踪

**评分标准**:
```
专业性和准确性 (30分): 医学术语准确性、诊断合理性
完整性和深度 (25分): 信息全面性、分析深度
逻辑性和条理性 (20分): 结构清晰度、逻辑连贯性
实用性和可操作性 (15分): 建议可行性、指导价值
格式规范性 (10分): 格式标准化、易读性
```

### 3. 交叉评测查看器 (`cross_evaluation_viewer.html`)

**功能**:
- 查看模型互评矩阵
- 热力图可视化
- 统计分析

### 4. 管理面板 (`admin.html`)

**功能**:
- 数据管理
- 进度统计
- 批量操作
- 数据导出

## 常用命令

### 模型注册管理

```bash
# 查看所有已注册模型
python -c "from cross_evaluation.model_registry import registry; print(registry.list_models())"

# 导出模型配置
python -c "from cross_evaluation.model_registry import registry; registry.export_to_file('models.json')"
```

### 数据处理

```bash
# 生成对比数据
python prepare_comparison_data.py

# 检查评测进度
python check_progress.py

# 查找缺失评测
python find_missing.py
```

### 测试连接

```bash
# 测试模型连接
python test_model_connectivity.py

# 测试多API
python test_multi_api.py
```

## 目录结构说明

```
.
├── cross_evaluation/          # 评测引擎核心代码
│   ├── engine.py             # 评测引擎
│   ├── model_registry.py     # 模型注册表
│   ├── prompt_template.py    # 提示词模板
│   └── ...
├── server/                    # Express后端服务
│   ├── server.js             # 主服务文件
│   └── package.json
├── output/                    # 评测结果输出
│   ├── cross_evaluation_results/  # 交叉评测结果
│   ├── raw/                  # 原始数据
│   └── comparison_data.json  # 对比数据
├── 测试输入问答记录/          # 患者对话数据
├── index.html                 # 主导航页
├── model_comparison.html      # 模型对比页
├── model_evaluation_chat.html # 评测界面
├── admin.html                 # 管理面板
├── config.py                  # Python配置
├── requirements.txt           # Python依赖
└── ARCHITECTURE.md            # 架构文档
```

## API接口说明

### 获取评测列表
```bash
curl http://localhost:3000/api/evaluations
```

### 提交评测
```bash
curl -X POST http://localhost:3000/api/evaluations \
  -H "Content-Type: application/json" \
  -d '{
    "patient": "患者1",
    "conversationId": "1",
    "model": "gpt-5.1",
    "scores": {
      "professionalism": 85,
      "completeness": 90,
      "logic": 88,
      "practicality": 87,
      "format": 92
    }
  }'
```

### 获取统计数据
```bash
curl http://localhost:3000/api/stats
```

## 常见问题

### Q: API调用失败，返回401错误？
A: 检查 `.env` 文件中的API密钥是否正确配置。

### Q: MongoDB连接失败？
A: 确保MongoDB服务正在运行，检查 `server/.env` 中的连接字符串。

### Q: 前端页面无法加载数据？
A:
1. 检查是否已运行评测生成数据
2. 确认Express服务已启动
3. 查看浏览器控制台错误信息

### Q: 评测运行很慢？
A:
1. 减少并发模型数量
2. 使用 `--test-mode` 快速测试
3. 检查网络连接和API配额

### Q: 如何添加新模型？
A:
1. 在 `cross_evaluation/model_registry.py` 注册模型
2. 配置API endpoint和密钥
3. 系统会自动识别新模型

## 最佳实践

### 评测流程建议

1. **小规模测试**: 先用1-2个患者和模型测试
2. **验证结果**: 检查生成的报告质量
3. **批量执行**: 确认无误后进行全量评测
4. **人工评分**: 至少对部分结果进行人工评分
5. **交叉验证**: 使用模型互评作为参考

### 性能优化

- 使用 `--batch-size` 控制并发数
- 定期清理临时文件
- MongoDB定期备份
- 合理设置API调用间隔

### 数据管理

- 定期备份评测结果
- 使用版本控制管理配置
- 记录每次评测的参数
- 保存原始对话数据

## 下一步

- 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解系统架构
- 查看 [用户手册](user-guide.html) 获取详细使用说明
- 参考 [examples/](examples/) 目录查看示例代码
- 加入项目讨论群获取帮助

## 技术支持

遇到问题？
- 查看 [常见问题](#常见问题)
- 提交 GitHub Issue
- 联系项目维护者

---

**祝你使用愉快！**
