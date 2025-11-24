# 前后端架构速查表

## 🎯 核心架构

本系统采用**混合架构**，包含两个独立的子系统：

```
┌─────────────────────────────────────────────────────┐
│              医疗AI模型评测系统                       │
├─────────────────────────────────────────────────────┤
│                                                       │
│  📊 交叉评测系统          │  👤 人工评测系统          │
│  ──────────────────      │  ──────────────────      │
│  • Python离线批处理       │  • Node.js实时API         │
│  • 生成静态JSON          │  • MongoDB数据库          │
│  • 640个评测任务         │  • 人工打分管理           │
│                                                       │
│  ─────────────────── 前端 ───────────────────        │
│                                                       │
│  🌐 纯HTML + JavaScript（无框架）                     │
│  • 静态页面 + Fetch API                               │
│  • 读取JSON文件 或 调用REST API                       │
│                                                       │
└─────────────────────────────────────────────────────┘
```

---

## 📁 前端页面列表

| 页面 | 功能 | 数据源 | 类型 |
|------|------|--------|------|
| **index.html** | 首页/导航 | `statistics.json` | 静态JSON |
| **cross_evaluation_viewer.html** | 交叉评测查看器 | `cross_evaluation_matrix.json`<br>`cross_evaluation_results/*` | 静态JSON |
| **model_comparison.html** | 模型对比 | `comparison_data.json` | 静态JSON |
| **model_evaluation_chat.html** | 人工评测打分 | `comparison_data.json` (报告)<br>`/api/evaluations/` (保存) | 混合 |
| **admin.html** | 管理员面板 | `/api/admin/*` | REST API |

**位置**: `web/pages/*.html`

---

## 🔧 后端系统

### 后端类型一：Python离线批处理

| 组件 | 功能 | 输出 |
|------|------|------|
| **run_cross_evaluation.py** | 执行640个交叉评测任务 | `output/cross_evaluation_results/` (3840个文件) |
| **generate_frontend_data.py** | 聚合数据生成前端JSON | `output/*.json` (4个文件) |
| **cross_evaluation/模块** | 评测引擎、模型客户端等 | 支持并发执行 |

**执行方式**: 命令行运行，不是常驻服务
```bash
python3 run_cross_evaluation.py --resume -y
python3 generate_frontend_data.py
```

### 后端类型二：Node.js实时API服务

| 组件 | 功能 | 端口 |
|------|------|------|
| **server/server.js** | Express + MongoDB API服务 | 3001 |
| **MongoDB** | 持久化人工评测数据 | 27017 |

**启动方式**: 常驻服务
```bash
cd server
npm start  # 或 npm run dev
```

---

## 📊 数据文件

### 前端数据文件（output/目录）

| 文件名 | 大小 | 用途 | 生成方式 |
|--------|------|------|---------|
| `statistics.json` | 3.1KB | 首页统计数据 | `generate_frontend_data.py` |
| `cross_evaluation_matrix.json` | 149KB | 评测矩阵热力图 | `generate_frontend_data.py` |
| `comparison_data.json` | 1.3MB | 模型对比报告 | `generate_frontend_data.py` |
| `evaluation_details.json` | 39MB | 详细评测数据（备用） | `generate_frontend_data.py` |

### 评测结果文件（output/cross_evaluation_results/）

```
患者1-10/
├── {模型A}_by_{模型B}_{患者}_aggregated.json  (640个)
├── {模型A}_by_{模型B}_{患者}_准确性.json      (640个)
├── {模型A}_by_{模型B}_{患者}_逻辑性.json      (640个)
├── {模型A}_by_{模型B}_{患者}_完整性.json      (640个)
├── {模型A}_by_{模型B}_{患者}_格式规范性.json  (640个)
└── {模型A}_by_{模型B}_{患者}_语言表达.json    (640个)

总计: 3840个JSON文件
```

---

## 🔄 数据流转

### 交叉评测流程

```
1. 执行评测
   python3 run_cross_evaluation.py
   ↓
2. 生成评测结果
   output/cross_evaluation_results/ (3840个文件)
   ↓
3. 聚合数据
   python3 generate_frontend_data.py
   ↓
4. 生成前端文件
   output/*.json (4个文件)
   ↓
5. 前端展示
   web/pages/*.html (读取JSON)
```

### 人工评测流程

```
1. 管理员生成完成码
   admin.html → POST /api/admin/generate-codes
   ↓
2. 用户获取完成码
   ↓
3. 用户评测打分
   model_evaluation_chat.html
   ↓
4. 提交评分
   POST /api/submit-evaluation → MongoDB
   ↓
5. 管理员查看
   admin.html → GET /api/admin/evaluations
```

---

## 🚀 快速启动

### 完整开发环境（4个终端）

```bash
# 终端1: MongoDB
mongod

# 终端2: Node.js API服务器
cd server && npm run dev

# 终端3: 静态文件服务器
python3 -m http.server 8000

# 终端4: 执行评测（可选）
python3 run_cross_evaluation.py --resume -y
```

### 访问地址

- 前端: http://localhost:8000/web/pages/index.html
- API: http://localhost:3001/api/admin/stats
- MongoDB: mongodb://localhost:27017/medical_evaluation

---

## 📈 端口使用

| 端口 | 服务 | 说明 |
|------|------|------|
| 8000 | Python HTTP Server | 开发环境静态文件服务 |
| 3001 | Node.js + Express | REST API服务 |
| 27017 | MongoDB | 数据库服务 |
| 80/443 | Nginx | 生产环境Web服务器 |

---

## 🔑 关键概念

### 前端是什么？

✅ **纯静态HTML页面**
- 位置: `web/pages/*.html`
- 技术: HTML + CSS + JavaScript (无框架)
- 数据加载: Fetch API
- 部署: 任何HTTP服务器即可

### 后端是什么？

#### 后端1: Python批处理（不是Web服务器）
- 功能: 执行交叉评测任务
- 运行: 命令行脚本，运行完就结束
- 输出: 静态JSON文件

#### 后端2: Node.js API服务器（Web服务器）
- 功能: 提供REST API，管理人工评测数据
- 运行: 常驻进程，持续监听端口3001
- 存储: MongoDB数据库

### 它们如何协作？

```
前端页面
  ├─ 交叉评测相关页面 → 读取Python生成的静态JSON文件
  └─ 人工评测相关页面 → 调用Node.js的REST API
```

---

## 📝 文档索引

| 文档 | 内容 |
|------|------|
| `ARCHITECTURE.md` | 完整架构说明（本文档） |
| `FRONTEND_REFACTORING_SUMMARY.md` | 前端重构详细说明 |
| `DATA_STRUCTURE_ANALYSIS.md` | 数据结构分析 |
| `CROSS_EVALUATION_REPORT.md` | 评测结果报告 |

---

**快速理解要点**:
1. 前端是纯静态HTML，可以用任何HTTP服务器部署
2. 有两个后端：Python批处理（生成数据）+ Node.js API（管理人工评测）
3. 大部分页面只读取静态JSON文件，只有admin.html需要API服务器
4. 可以只启动静态文件服务器查看交叉评测结果，不需要启动Node.js和MongoDB

---

**最后更新**: 2025-11-24
