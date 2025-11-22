# 医疗AI模型评测系统 - 架构文档

## 项目概述

医疗AI模型评测系统是一个全栈应用，用于评估多个大语言模型在医疗场景（如病历生成、诊断建议等）中的表现。系统支持多模型对比、交叉评测、可视化展示和评分管理。

## 技术栈

### 后端
- **语言**: Python 3.x
- **核心框架**:
  - `pydantic-settings`: 配置管理
  - `openai`: API客户端库
- **Node.js服务**: Express.js + MongoDB
  - 数据持久化
  - RESTful API

### 前端
- **纯HTML/CSS/JavaScript**: 无框架依赖
- **可视化**: 原生Canvas/SVG
- **响应式设计**: 支持多屏幕尺寸

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                 │
├─────────────────────────────────────────────────────────────┤
│  index.html          - 导航主页                              │
│  model_comparison.html - 模型横评对比（带对话展示）           │
│  model_evaluation_chat.html - 单模型评测界面                 │
│  admin.html          - 管理面板                              │
│  user-guide.html     - 用户手册                              │
│  cross_evaluation_viewer.html - 交叉评测查看器               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API服务层                               │
├─────────────────────────────────────────────────────────────┤
│  server/server.js    - Express后端服务                       │
│  - MongoDB数据库操作                                          │
│  - 评测数据CRUD API                                           │
│  - CORS支持                                                   │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Python评测引擎                            │
├─────────────────────────────────────────────────────────────┤
│  cross_evaluation/                                           │
│  ├── engine.py              - 评测核心引擎                    │
│  ├── report_evaluation_engine.py - 报告评测引擎              │
│  ├── model_registry.py      - 模型注册表                     │
│  ├── model_client_factory.py - 模型客户端工厂                │
│  ├── prompt_template.py     - 提示词模板                     │
│  └── conversation_indexer.py - 对话索引器                    │
│                                                              │
│  主执行脚本:                                                  │
│  ├── run_cross_evaluation.py - 交叉评测                      │
│  ├── run_report_cross_evaluation.py - 报告评测               │
│  └── run_batch_evaluation.py - 批量评测                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                     数据存储层                               │
├─────────────────────────────────────────────────────────────┤
│  MongoDB (通过Express)                                       │
│  ├── evaluations 集合 - 评测结果                             │
│  └── metadata 集合 - 元数据                                  │
│                                                              │
│  文件系统                                                     │
│  ├── output/cross_evaluation_results/ - 评测结果JSON         │
│  ├── output/raw/ - 原始对话数据                              │
│  ├── output/markdown/ - Markdown格式结果                     │
│  └── evaluation_results/ - 结果汇总                          │
└─────────────────────────────────────────────────────────────┘
```

## 核心模块详解

### 1. 配置管理 (`config.py`)

```python
class Settings(BaseSettings):
    # API配置
    jiekou_api_key: str
    jiekou_base_url: str

    # 默认模型设置
    default_model: str = "gpt-5.1"
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = 2048

    # 从.env文件加载
    model_config = SettingsConfigDict(env_file=".env")
```

**功能**:
- 统一管理API密钥和配置
- 支持环境变量覆盖
- Pydantic验证确保配置正确性

### 2. 模型注册表 (`cross_evaluation/model_registry.py`)

**功能**:
- 管理所有可用的AI模型
- 存储模型API配置（endpoint、key、参数）
- 支持导入/导出模型配置

**主要模型**:
- GPT系列: gpt-5.1, gpt-4o-mini
- Qwen系列: qwen3-max, qwen3-72b
- DeepSeek系列: deepseek-seed, deepseek-chat
- Baichuan、Doubao等国产模型

### 3. 模型客户端工厂 (`cross_evaluation/model_client_factory.py`)

**功能**:
- 根据模型配置创建API客户端
- 统一不同模型的调用接口
- 处理API认证和请求

### 4. 评测引擎 (`cross_evaluation/engine.py`)

**核心流程**:
```
加载对话数据 → 选择模型组合 → 调用模型生成 → 保存结果
```

**关键方法**:
- `run_evaluation()`: 执行单次评测
- `batch_evaluate()`: 批量评测
- `save_results()`: 保存结果到JSON

### 5. 报告评测引擎 (`cross_evaluation/report_evaluation_engine.py`)

**功能**:
- 加载已生成的模型报告
- 交叉评测：用模型A评判模型B的输出
- 生成评分矩阵

**评测维度**:
- 专业性和准确性 (30%)
- 完整性和深度 (25%)
- 逻辑性和条理性 (20%)
- 实用性和可操作性 (15%)
- 格式规范性 (10%)

### 6. 对话索引器 (`cross_evaluation/conversation_indexer.py`)

**功能**:
- 扫描对话数据文件
- 建立患者-对话类型索引
- 快速检索对话内容

### 7. 前端页面

#### model_comparison.html
**功能**: 模型横评对比
- 多患者、多模型、多对话类型选择
- 对话可视化展示（聊天气泡界面）
- 模型输出并列对比
- 响应式布局，横向滚动

**核心特性**:
- 对话面板固定在左侧第一列
- 对话面板高度自适应最高模型卡片
- 支持患者基本信息展示
- 实时筛选和对比

#### model_evaluation_chat.html
**功能**: 单模型评测界面
- 选择患者和对话类型
- 查看模型生成的报告
- 在线评分（五个维度）
- 自动保存评分到数据库
- 评测进度跟踪

#### admin.html
**功能**: 管理面板
- 查看所有评测数据
- 统计完成进度
- 删除/编辑评测记录
- 导出数据

#### cross_evaluation_viewer.html
**功能**: 交叉评测矩阵查看器
- 可视化评分矩阵
- 热力图展示
- 统计分析

## 数据流

### 评测流程

```
1. 用户选择参数
   ├── 患者列表
   ├── 对话类型
   └── 模型列表

2. Python引擎执行
   ├── 加载对话数据
   ├── 调用模型API
   ├── 生成报告
   └── 保存JSON

3. 前端展示
   ├── 加载JSON数据
   ├── 渲染对比界面
   └── 提供评分入口

4. 用户评分
   ├── 五维度打分
   ├── 提交到MongoDB
   └── 更新统计数据
```

### 数据格式

**评测结果JSON** (`output/cross_evaluation_results/`):
```json
{
  "患者1": {
    "1": {  // 对话类型ID
      "gpt-5.1": {
        "title": "病历标题",
        "output": "模型生成的报告内容",
        "chat": "原始对话记录"
      },
      "qwen3-max": { ... }
    }
  }
}
```

**评分数据** (MongoDB):
```json
{
  "patient": "患者1",
  "conversationId": "1",
  "model": "gpt-5.1",
  "scores": {
    "professionalism": 85,
    "completeness": 90,
    "logic": 88,
    "practicality": 87,
    "format": 92
  },
  "totalScore": 88.4,
  "timestamp": "2024-11-20T..."
}
```

## 部署架构

### 开发环境
```bash
# 前端 - 直接打开HTML
open index.html

# 后端服务
cd server && npm install && npm start

# Python评测
python run_cross_evaluation.py --models gpt-5.1 qwen3-max --patients 患者1
```

### 生产环境
```bash
# MongoDB
mongod --dbpath /data/db

# Express服务（PM2）
cd server && pm2 start server.js --name medical-eval

# Nginx反向代理
# 静态HTML → Nginx
# API请求 → Express:3000
```

## 关键配置文件

### `.env` (Python)
```
JIEKOU_API_KEY=your_api_key
JIEKOU_BASE_URL=https://api.jiekou.ai/openai
DEFAULT_MODEL=gpt-5.1
LOG_LEVEL=INFO
```

### `server/.env` (Node.js)
```
MONGODB_URI=mongodb://localhost:27017/medical-evaluation
PORT=3000
```

### `deploy.sh` (部署脚本)
```bash
#!/bin/bash
# 服务器IP配置
# rsync同步文件
# 重启服务
```

## API接口

### Express API

#### 获取评测数据
```
GET /api/evaluations
Query: patient, conversationId, model
Response: { evaluations: [...] }
```

#### 提交评测
```
POST /api/evaluations
Body: { patient, conversationId, model, scores }
Response: { success: true, id: "..." }
```

#### 删除评测
```
DELETE /api/evaluations/:id
Response: { success: true }
```

#### 统计数据
```
GET /api/stats
Response: { total, completed, progress }
```

## 性能优化

### 前端
- 懒加载大型JSON数据
- 虚拟滚动（对于长列表）
- 防抖搜索和筛选
- 本地缓存已加载数据

### 后端
- MongoDB索引优化
- API响应压缩
- 连接池管理
- 缓存热点数据

### Python引擎
- 并发API请求（asyncio）
- 结果增量保存
- 错误重试机制
- 进度日志输出

## 扩展性设计

### 添加新模型
1. 在 `model_registry.py` 注册模型
2. 配置API endpoint和key
3. 系统自动识别和调用

### 添加新评测维度
1. 修改 `prompt_template.py` 评分标准
2. 更新前端评分表单
3. 调整数据库schema

### 多语言支持
- 提示词模板国际化
- 前端UI多语言切换
- 评测标准本地化

## 安全考虑

- **API密钥**: 环境变量存储，不提交代码
- **输入验证**: Pydantic模型验证
- **CORS**: Express配置白名单
- **认证**: 基础HTTP认证（生产环境）
- **数据加密**: 敏感数据MongoDB加密

## 监控和日志

### 日志级别
- DEBUG: 详细调试信息
- INFO: 常规操作日志
- WARNING: 潜在问题
- ERROR: 错误和异常

### 日志输出
- Python: 标准输出 + 文件
- Express: Morgan中间件
- 前端: Console + 错误上报

## 备份策略

### 数据备份
```bash
# MongoDB导出
mongodump --db medical-evaluation --out backup/

# 结果文件备份
tar -czf results_backup.tar.gz output/
```

### 代码版本控制
- Git仓库管理
- 关键版本打tag
- 生产代码分支保护

## 故障排查

### 常见问题

**API调用失败**:
- 检查 `.env` 配置
- 验证API密钥有效性
- 查看模型配额限制

**数据库连接失败**:
- 确认MongoDB运行状态
- 检查连接字符串
- 验证网络连接

**前端加载失败**:
- 检查JSON文件路径
- 查看浏览器控制台
- 验证CORS配置

## 开发规范

### Python代码
- PEP 8 代码风格
- Type hints类型注解
- Docstring文档字符串

### JavaScript代码
- ES6+ 语法
- 函数式编程优先
- 注释清晰完整

### Git提交
- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
- test: 测试

## 未来规划

- [ ] 实时评测（WebSocket）
- [ ] 用户权限管理
- [ ] 评测报告自动生成
- [ ] 机器学习评分模型
- [ ] 多租户支持
- [ ] 国际化i18n
- [ ] 移动端适配
- [ ] 数据可视化dashboard

## 参考资料

- [OpenAI API文档](https://platform.openai.com/docs)
- [Express.js文档](https://expressjs.com/)
- [MongoDB文档](https://docs.mongodb.com/)
- [Pydantic文档](https://docs.pydantic.dev/)

---

**维护者**: 项目团队
**最后更新**: 2024-11-21
**版本**: v1.0.0
