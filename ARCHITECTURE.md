# 医疗AI模型评测系统 - 前后端架构说明

## 系统概述

本系统是一个**混合架构**的医疗AI模型评测平台，包含两个独立的子系统：

1. **交叉评测系统**（离线批处理 + 静态前端）
2. **人工评测系统**（Node.js后端 + MongoDB + 动态前端）

---

## 一、整体架构图

```
┌──────────────────────────────────────────────────────────────────────┐
│                        医疗AI评测系统                                   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌─────────────────────┐         ┌─────────────────────────────┐    │
│  │  交叉评测系统        │         │  人工评测系统                 │    │
│  │  (离线批处理)        │         │  (在线实时)                   │    │
│  ├─────────────────────┤         ├─────────────────────────────┤    │
│  │                     │         │                             │    │
│  │  Python脚本         │         │  Node.js + Express          │    │
│  │  ├ run_cross_*.py   │         │  ├ server/server.js         │    │
│  │  ├ generate_*.py    │         │  └ MongoDB数据库             │    │
│  │  └ 多线程并发执行     │         │                             │    │
│  │      ↓              │         │      ↑                      │    │
│  │  生成JSON文件        │         │  REST API                   │    │
│  │  ├ statistics.json  │         │  ├ /api/admin/*             │    │
│  │  ├ matrix.json      │         │  ├ /api/evaluations/*       │    │
│  │  ├ comparison.json  │         │  └ /api/submit-evaluation   │    │
│  │  └ details.json     │         │                             │    │
│  │      ↓              │         │      ↑                      │    │
│  └──────┬──────────────┘         └──────┬──────────────────────┘    │
│         │                               │                            │
│         └───────────────┬───────────────┘                            │
│                         │                                            │
│                         ▼                                            │
│         ┌───────────────────────────────────────┐                   │
│         │         前端静态页面 (web/pages/)       │                   │
│         ├───────────────────────────────────────┤                   │
│         │  • index.html (首页)                   │                   │
│         │  • cross_evaluation_viewer.html (查看器)│  → 读取JSON文件   │
│         │  • model_comparison.html (对比视图)     │                   │
│         │  • model_evaluation_chat.html (打分)   │  → 调用API        │
│         │  • admin.html (管理面板)               │  → 调用API        │
│         └───────────────────────────────────────┘                   │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 二、前端详细说明

### 前端位置
```
web/pages/
├── index.html                      # 首页/导航页
├── cross_evaluation_viewer.html    # 交叉评测查看器
├── model_comparison.html           # 模型对比视图
├── model_evaluation_chat.html      # 人工评测打分界面
├── admin.html                      # 管理员控制面板
├── user-guide.html                 # 用户使用手册
├── comparison.html                 # (旧版本，可能已废弃)
├── model_evaluation.html           # (旧版本，可能已废弃)
├── model_evaluation_custom.html    # (旧版本，可能已废弃)
├── model_scoring_form.html         # (旧版本，可能已废弃)
└── model_scoring_table.html        # (旧版本，可能已废弃)
```

### 前端技术栈
- **纯HTML + CSS + JavaScript** (无框架)
- **Fetch API** 用于数据加载
- **ES6+** 现代JavaScript特性
- **响应式设计** 支持移动端

### 前端数据源映射

| 页面 | 数据来源 | 数据类型 | 说明 |
|------|---------|---------|------|
| `index.html` | `../../output/statistics.json` | 静态JSON | 统计数据，动态加载 |
| `cross_evaluation_viewer.html` | `../../output/cross_evaluation_matrix.json` | 静态JSON | 640个交叉评测结果矩阵 |
| `cross_evaluation_viewer.html` | `../../output/cross_evaluation_results/{患者}/*_aggregated.json` | 静态JSON | 详细评测数据（modal） |
| `model_comparison.html` | `../../output/comparison_data.json` | 静态JSON | 80个原始报告对比 |
| `model_evaluation_chat.html` | `../../output/comparison_data.json` | 静态JSON | 80个原始报告（打分用） |
| `model_evaluation_chat.html` | `/api/evaluations/` | REST API | 保存/读取人工评分 |
| `model_evaluation_chat.html` | `/api/submit-evaluation` | REST API | 提交评测数据 |
| `admin.html` | `/api/admin/*` | REST API | 管理员功能（MongoDB数据） |

### 前端部署

**方式一：静态HTTP服务器**（推荐用于开发）
```bash
cd /Users/ruanchuhao/Downloads/Codes/Agents/chat
python3 -m http.server 8000

# 访问: http://localhost:8000/web/pages/index.html
```

**方式二：Nginx/Apache**（推荐用于生产）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/chat;

    location / {
        try_files $uri $uri/ =404;
    }

    location /api/ {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 三、后端详细说明

### 后端类型一：离线批处理系统（Python）

#### 位置
```
根目录下的Python脚本 + cross_evaluation/模块
```

#### 核心脚本

| 脚本文件 | 功能 | 输出 |
|---------|------|------|
| `run_cross_evaluation.py` | 主评测脚本，执行640个交叉评测任务 | `output/cross_evaluation_results/` |
| `generate_frontend_data.py` | 数据聚合脚本，生成前端JSON文件 | `output/*.json` (4个文件) |
| `run_batch_evaluation.py` | 批量评测脚本 | 批量评测结果 |
| `test_cross_evaluation.py` | 测试脚本 | 测试输出 |

#### cross_evaluation/模块结构

```python
cross_evaluation/
├── __init__.py
├── config.py              # 配置加载
├── engine.py              # 评测引擎（多线程）
├── model_client.py        # 模型API客户端
├── report_loader.py       # 报告加载器
├── prompt_loader.py       # Prompt加载器
├── dimension_evaluator.py # 维度评测器
├── aggregator.py          # 分数聚合器
└── module_parser.py       # 模块解析器
```

#### 工作流程

```
1. 加载配置 (config.json)
   ↓
2. 加载8个模型 × 10个患者的报告 (output/raw/)
   ↓
3. 加载5个维度的评测Prompt (Prompts/PromptForReportTest/Prompts/)
   ↓
4. 创建640个评测任务 (8×8×10)
   ↓
5. 使用50个并发worker执行评测
   ↓
6. 保存结果到 output/cross_evaluation_results/
   ├── 患者1/
   │   ├── *_aggregated.json (聚合文件)
   │   ├── *_准确性.json
   │   ├── *_逻辑性.json
   │   ├── *_完整性.json
   │   ├── *_格式规范性.json
   │   └── *_语言表达.json
   ├── 患者2/
   └── ...
   ↓
7. 运行 generate_frontend_data.py 聚合数据
   ↓
8. 生成4个前端JSON文件
   ├── cross_evaluation_matrix.json (149KB)
   ├── comparison_data.json (1.3MB)
   ├── evaluation_details.json (39MB)
   └── statistics.json (3.1KB)
```

#### 执行命令

```bash
# 运行完整交叉评测（640个任务）
python3 run_cross_evaluation.py --resume -y

# 生成前端数据文件
python3 generate_frontend_data.py

# 运行特定患者的评测
python3 run_cross_evaluation.py --patients 患者1 --resume -y
```

#### 技术栈
- **Python 3.x**
- **threading** (多线程并发)
- **requests** (HTTP客户端)
- **json** (数据处理)
- **OpenAI API** (统一接口访问多个LLM)

---

### 后端类型二：在线API服务器（Node.js + MongoDB）

#### 位置
```
server/server.js
web/server/server.js  (相同文件的副本)
```

#### 技术栈
- **Node.js** + Express.js
- **MongoDB** (数据持久化)
- **Mongoose** (ODM)
- **CORS** (跨域支持)
- **body-parser** (请求解析)

#### API端点

| 方法 | 路径 | 功能 | 说明 |
|------|------|------|------|
| GET | `/api/admin/stats` | 获取统计数据 | 评测总数、代码数等 |
| POST | `/api/admin/generate-codes` | 生成完成码 | 批量生成4位完成码 |
| GET | `/api/admin/codes` | 获取所有完成码 | 支持分页、筛选 |
| GET | `/api/admin/evaluations` | 获取所有评测 | 支持分页、筛选 |
| GET | `/api/admin/evaluation/:id` | 获取单个评测详情 | 返回完整评测数据 |
| GET | `/api/admin/evaluation-matrix` | 获取评测矩阵 | 模型×患者统计数据 |
| POST | `/api/admin/clear-database` | 清空数据库 | 危险操作，需确认 |
| GET | `/api/evaluations/:code` | 获取用户评测数据 | 根据完成码查询 |
| POST | `/api/submit-evaluation` | 提交评测数据 | 保存用户打分 |

#### 数据模型

**1. Code Schema（完成码）**
```javascript
{
  code: String (4位字符, unique, 索引),
  createdAt: Date,
  status: 'active' | 'used' | 'expired',
  usedAt: Date,
  description: String,
  batchId: String
}
```

**2. Evaluation Schema（评测数据）**
```javascript
{
  code: String (关联完成码),
  patient: String,
  model: String,
  scores: {
    accuracy: {
      score: Number (1-5星),
      comment: String,
      weight: Number,
      max: Number
    },
    completeness: { ... },
    standard: { ... }
  },
  total_score: Number (0-100),
  overall_comment: String,
  timestamp: Date,
  submittedAt: Date
}
```

#### 启动服务器

```bash
cd server

# 安装依赖（首次）
npm install

# 启动服务器
npm start

# 开发模式（自动重启）
npm run dev
```

**默认端口**: `3001`
**MongoDB连接**: `mongodb://localhost:27017/medical_evaluation`

#### 环境变量配置

创建 `server/.env` 文件：
```bash
PORT=3001
MONGODB_URI=mongodb://localhost:27017/medical_evaluation
```

---

## 四、数据流转图

### 交叉评测数据流

```
┌──────────────────┐
│  原始患者数据     │
│  data/patients/  │ (10个JSON文件)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  报告生成（已完成）        │
│  output/raw/             │ (80个JSON文件: 8模型×10患者)
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  交叉评测执行                          │
│  run_cross_evaluation.py             │
│  • 50个并发worker                     │
│  • 640个任务 (8×8×10)                 │
│  • 每个任务评测5个维度                 │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  评测结果文件                          │
│  output/cross_evaluation_results/    │
│  • 640个aggregated.json               │
│  • 3200个维度.json                     │
│  • 按患者分组目录                      │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  数据聚合                              │
│  generate_frontend_data.py           │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  前端数据文件                          │
│  output/                              │
│  • statistics.json (3.1KB)            │
│  • cross_evaluation_matrix.json (149KB)│
│  • comparison_data.json (1.3MB)       │
│  • evaluation_details.json (39MB)     │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  前端页面展示                          │
│  web/pages/*.html                     │
│  • Fetch API加载JSON                  │
│  • 客户端渲染                          │
└──────────────────────────────────────┘
```

### 人工评测数据流

```
┌─────────────────┐
│  用户访问页面    │
│  admin.html     │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  管理员生成完成码     │
│  POST /api/admin/   │
│  generate-codes     │
└────────┬────────────┘
         │
         ▼  保存到MongoDB
┌─────────────────────┐
│  Code集合            │
│  {code, status,...} │
└────────┬────────────┘
         │
         ├────────────────────────────┐
         │                            │
         ▼                            ▼
┌──────────────────┐      ┌──────────────────┐
│  用户获取完成码   │      │  管理员查看统计   │
│                  │      │  GET /api/admin/ │
└────────┬─────────┘      │  stats           │
         │                └──────────────────┘
         ▼
┌──────────────────────┐
│  用户进行评测         │
│  model_evaluation_   │
│  chat.html           │
└────────┬─────────────┘
         │
         ▼  提交评分
┌─────────────────────┐
│  POST /api/submit-  │
│  evaluation         │
└────────┬────────────┘
         │
         ▼  保存到MongoDB
┌─────────────────────┐
│  Evaluation集合      │
│  {code, patient,    │
│   model, scores}    │
└────────┬────────────┘
         │
         ▼  管理员查询
┌─────────────────────┐
│  GET /api/admin/    │
│  evaluations        │
└─────────────────────┘
```

---

## 五、部署架构

### 开发环境

```
┌────────────────────────────────────────┐
│  macOS 开发机                           │
├────────────────────────────────────────┤
│                                         │
│  终端1: Python HTTP Server              │
│  python3 -m http.server 8000           │
│  └─ 提供静态文件服务                     │
│                                         │
│  终端2: Node.js API Server              │
│  cd server && npm run dev              │
│  └─ 提供REST API服务 (端口3001)         │
│                                         │
│  终端3: MongoDB                         │
│  mongod                                │
│  └─ 数据库服务 (端口27017)              │
│                                         │
│  终端4: 评测脚本执行                     │
│  python3 run_cross_evaluation.py       │
│  └─ 后台批处理任务                       │
│                                         │
└────────────────────────────────────────┘
```

### 生产环境（推荐）

```
┌──────────────────────────────────────────────────────┐
│  云服务器 / VPS                                        │
├──────────────────────────────────────────────────────┤
│                                                        │
│  Nginx (端口80/443)                                    │
│  ├─ 静态文件: /web/pages/*.html                        │
│  │  └─ 读取: /output/*.json                           │
│  │                                                     │
│  └─ 反向代理: /api/* → http://localhost:3001          │
│                                                        │
│  Node.js + PM2 (端口3001)                              │
│  └─ REST API服务 (server/server.js)                   │
│     ├─ Express应用                                     │
│     └─ 连接MongoDB                                     │
│                                                        │
│  MongoDB (端口27017)                                   │
│  └─ 数据持久化                                         │
│     ├─ Code集合                                        │
│     └─ Evaluation集合                                  │
│                                                        │
│  Cron Jobs                                            │
│  └─ 定期执行交叉评测脚本（可选）                         │
│                                                        │
└──────────────────────────────────────────────────────┘
```

---

## 六、端口映射

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| Python HTTP Server | 8000 | HTTP | 开发用静态文件服务器 |
| Node.js API Server | 3001 | HTTP | REST API服务 |
| MongoDB | 27017 | TCP | 数据库服务 |
| Nginx (生产) | 80 | HTTP | 前端静态文件 + API反向代理 |
| Nginx (生产) | 443 | HTTPS | SSL加密访问 |

---

## 七、关键文件位置汇总

### 前端文件
```
web/pages/
├── index.html                      # 首页
├── cross_evaluation_viewer.html    # 交叉评测查看器
├── model_comparison.html           # 模型对比
├── model_evaluation_chat.html      # 人工评测
└── admin.html                      # 管理面板
```

### 后端文件（Python）
```
根目录/
├── run_cross_evaluation.py         # 主评测脚本
├── generate_frontend_data.py       # 数据聚合脚本
├── cross_evaluation/               # 评测模块
│   ├── engine.py                  # 评测引擎
│   ├── model_client.py            # API客户端
│   └── ...
└── config/
    └── cross_evaluation_config.json # 配置文件
```

### 后端文件（Node.js）
```
server/
├── server.js                       # Express服务器
├── package.json                    # 依赖配置
└── .env                           # 环境变量
```

### 数据文件
```
output/
├── raw/                            # 原始报告 (80个)
├── cross_evaluation_results/       # 评测结果 (3840个)
├── statistics.json                 # 统计数据
├── cross_evaluation_matrix.json    # 评测矩阵
├── comparison_data.json            # 对比数据
└── evaluation_details.json         # 详细数据
```

### 配置文件
```
config/
├── cross_evaluation_config.json    # 交叉评测配置
├── models/
│   └── model_registry.json        # 模型注册表
└── prompts/
    └── *.md                       # 评测Prompt
```

---

## 八、技术栈总结

### 前端
- HTML5 + CSS3 + JavaScript (ES6+)
- Fetch API
- 无框架（原生JS）

### 后端（Python）
- Python 3.x
- threading (多线程)
- requests (HTTP客户端)
- json (数据处理)

### 后端（Node.js）
- Node.js + Express.js
- MongoDB + Mongoose
- CORS, body-parser

### 数据库
- MongoDB 8.x

### 部署工具
- PM2 (Node.js进程管理)
- Nginx (Web服务器)
- Python http.server (开发环境)

---

## 九、快速启动命令

### 启动完整开发环境

```bash
# 1. 启动MongoDB
mongod

# 2. 启动Node.js API服务器（新终端）
cd server
npm install  # 首次执行
npm run dev

# 3. 启动静态文件服务器（新终端）
python3 -m http.server 8000

# 4. 访问系统
# 前端: http://localhost:8000/web/pages/index.html
# API: http://localhost:3001/api/admin/stats
```

### 运行交叉评测

```bash
# 生成评测数据
python3 run_cross_evaluation.py --resume -y

# 生成前端文件
python3 generate_frontend_data.py
```

---

## 十、常见问题

### Q1: 前端页面无法加载数据？
**A**: 检查：
1. 数据文件是否存在: `ls -lh output/*.json`
2. HTTP服务器是否启动
3. 浏览器控制台是否有CORS错误
4. 文件路径是否正确（`../../output/`）

### Q2: API调用返回404？
**A**: 检查：
1. Node.js服务器是否启动: `netstat -an | grep 3001`
2. MongoDB是否运行: `mongod --version`
3. API路径是否正确: `/api/admin/stats`
4. CORS配置是否正确

### Q3: 交叉评测脚本执行失败？
**A**: 检查：
1. Python版本: `python3 --version`
2. 依赖是否安装: `pip list | grep requests`
3. API密钥是否配置: `cat .env`
4. 并发数是否过高（降低到30）

### Q4: 前端显示数据不更新？
**A**: 解决方法：
1. 重新生成前端数据: `python3 generate_frontend_data.py`
2. 清除浏览器缓存
3. 强制刷新: Ctrl+F5 (Windows) 或 Cmd+Shift+R (Mac)

---

## 十一、维护建议

1. **定期备份MongoDB数据**
   ```bash
   mongodump --db medical_evaluation --out backup/$(date +%Y%m%d)
   ```

2. **监控Node.js服务状态**
   ```bash
   pm2 status
   pm2 logs
   ```

3. **清理旧的评测数据**（可选）
   ```bash
   # 删除30天前的评测结果
   find output/cross_evaluation_results -name "*.json" -mtime +30 -delete
   ```

4. **更新依赖包**
   ```bash
   # Python
   pip install --upgrade requests

   # Node.js
   cd server && npm update
   ```

---

**文档版本**: v1.0
**最后更新**: 2025-11-24
**维护者**: Claude (Anthropic)
