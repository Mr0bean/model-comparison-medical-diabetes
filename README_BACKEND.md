# 医疗AI评测系统 - 完整后端解决方案

## 🎯 系统概述

这是一个完整的医疗AI模型评测数据收集系统，包含：
- ✅ **后端API服务**（Node.js + Express + MongoDB）
- ✅ **管理面板**（生成和管理完成码）
- ✅ **身份验证**（4位完成码验证）
- ✅ **数据存储**（MongoDB数据库）

## 🚀 5分钟快速开始

### 1️⃣ 安装MongoDB

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Windows:**
下载并安装 https://www.mongodb.com/try/download/community

**或使用云数据库（推荐）:**
免费注册 MongoDB Atlas: https://www.mongodb.com/cloud/atlas

### 2️⃣ 安装后端依赖

```bash
cd server
npm install
```

### 3️⃣ 配置环境

```bash
cp .env.example .env
```

编辑 `.env`:
```env
MONGODB_URI=mongodb://localhost:27017/medical_evaluation
PORT=3001
```

### 4️⃣ 启动服务

```bash
# 在 server/ 目录下
npm start
```

看到以下输出表示成功：
```
✅ MongoDB连接成功
🚀 服务器运行在 http://localhost:3001
```

### 5️⃣ 打开管理面板

新开一个终端，在项目根目录下：
```bash
python -m http.server 8000
```

访问：http://localhost:8000/admin.html

## 📋 使用流程

### 管理员操作

1. **生成完成码**
   - 打开 http://localhost:8000/admin.html
   - 输入生成数量（如 10）
   - 点击"生成完成码"
   - 复制生成的完成码

2. **分发完成码**
   - 将完成码分发给评测人员
   - 例如：a1b2, x7y9, 3k4m

3. **查看收集情况**
   - 管理面板实时显示统计数据
   - 查看哪些码已使用
   - 查看评测数据列表

### 评测人员操作

1. **访问评测页面**
   ```
   http://localhost:8000/model_evaluation_chat.html?id=a1b2
   ```

2. **验证身份**
   - 页面自动验证完成码
   - 右上角显示 ✅ ID: a1b2

3. **填写评测**
   - 选择患者和模型
   - 点击星星评分
   - 填写评论

4. **提交数据**
   - 点击"保存评测"
   - 数据自动提交到服务器
   - 管理员可实时查看

## 📊 系统架构

```
┌─────────────────────────────────┐
│     管理员面板 (admin.html)       │
│  - 生成完成码                     │
│  - 查看统计                       │
│  - 管理数据                       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    后端API (server/server.js)    │
│  - 完成码验证                     │
│  - 数据接收                       │
│  - 统计分析                       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│    MongoDB数据库                  │
│  - codes 集合（完成码）            │
│  - evaluations 集合（评测数据）    │
└─────────────────────────────────┘
             ▲
             │
┌────────────┴────────────────────┐
│  评测前端 (with ?id=xxxx)         │
│  - 验证身份                       │
│  - 填写评分                       │
│  - 提交数据                       │
└─────────────────────────────────┘
```

## 🔑 完成码说明

### 格式
- **长度**：4位
- **字符**：小写字母 a-z 或数字 0-9
- **示例**：a1b2, x7y9, 0000, abcd

### 状态
- **active**：可用（未使用）
- **used**：已使用（可继续编辑）
- **expired**：已过期（不可使用）

### 生成规则
- 随机生成，自动去重
- 最多可生成 36^4 = 1,679,616 个
- 单次最多生成 100 个

## 📁 项目文件结构

```
.
├── server/
│   ├── server.js          # 后端服务主文件
│   ├── package.json       # Node.js依赖配置
│   ├── .env.example       # 环境变量示例
│   └── .gitignore         # Git忽略文件
│
├── admin.html             # 管理面板
├── evaluation-auth.js     # 前端验证脚本
├── model_evaluation_chat.html  # 评测页面（需集成）
│
├── BACKEND_SETUP.md       # 详细部署指南
├── INTEGRATION_GUIDE.md   # 前端集成教程
└── README_BACKEND.md      # 本文件
```

## 🔌 API接口

### 评测人员使用
```http
GET /api/verify-code/:code
POST /api/submit-evaluation
GET /api/evaluations/:code
```

### 管理员使用
```http
POST /api/admin/generate-codes
GET /api/admin/codes
GET /api/admin/stats
GET /api/admin/evaluations
```

详细API文档见：[BACKEND_SETUP.md](BACKEND_SETUP.md#-api文档)

## 🛠 集成到现有HTML

### 方式一：独立验证脚本（推荐）

在 `model_evaluation_chat.html` 底部添加：

```html
<script src="evaluation-auth.js"></script>
```

### 方式二：内联代码

参考 [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) 完整教程

## 📈 数据导出

### 导出为JSON
```bash
mongoexport --db=medical_evaluation --collection=evaluations --out=data.json
```

### 导出为CSV
```bash
mongoexport --db=medical_evaluation --collection=evaluations --type=csv --fields=code,patient,model,total_score,submittedAt --out=data.csv
```

## 🔧 故障排除

### 问题1：无法启动服务器
```bash
# 检查端口占用
lsof -i:3001

# 杀死占用进程
kill -9 <PID>
```

### 问题2：MongoDB连接失败
```bash
# 检查MongoDB状态
brew services list

# 重启MongoDB
brew services restart mongodb-community
```

### 问题3：CORS错误
在 `server/server.js` 中添加：
```javascript
app.use(cors({
    origin: 'http://localhost:8000'
}));
```

### 问题4：完成码已存在
系统会自动重试，如仍失败请减少生成数量

## 🔒 安全建议

### 生产环境必须：
1. ✅ 添加管理员认证（用户名+密码）
2. ✅ 使用HTTPS（SSL证书）
3. ✅ 限制CORS来源
4. ✅ 添加API速率限制
5. ✅ 定期备份数据库

### 示例：添加管理员认证
```javascript
// 在 server.js 中添加
const basicAuth = require('express-basic-auth');

app.use('/api/admin', basicAuth({
    users: { 'admin': 'your-password' },
    challenge: true
}));
```

## 📞 获取帮助

### 文档
- [BACKEND_SETUP.md](BACKEND_SETUP.md) - 完整部署指南
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - 前端集成教程

### 检查日志
```bash
# 服务器日志
# 直接查看终端输出

# MongoDB日志
tail -f /usr/local/var/log/mongodb/mongo.log
```

### 数据库管理
```bash
# 连接数据库
mongosh

# 查看数据
use medical_evaluation
db.codes.find().pretty()
db.evaluations.find().pretty()

# 清空数据
db.codes.deleteMany({})
db.evaluations.deleteMany({})
```

## 🎓 下一步

完成基础设置后，您可以：

1. **自定义评分标准** - 修改评分维度和权重
2. **添加更多功能** - 如邮件通知、批量导出
3. **优化用户体验** - 自定义界面和提示
4. **部署到云端** - 使用Heroku、Vercel等平台

## 📊 示例数据

### 完成码文档
```json
{
  "code": "a1b2",
  "status": "used",
  "createdAt": "2025-11-18T10:00:00Z",
  "usedAt": "2025-11-18T10:30:00Z",
  "batchId": "batch_1731924000",
  "description": "第一批评测人员"
}
```

### 评测数据文档
```json
{
  "code": "a1b2",
  "patient": "患者1",
  "model": "GPT-4",
  "scores": {
    "accuracy": { "score": 5, "max": 5, "comment": "信息准确" },
    "completeness": { "score": 4, "max": 5, "comment": "基本完整" },
    "clinical": { "score": 5, "max": 5, "comment": "实用性强" },
    "structure": { "score": 4, "max": 5, "comment": "结构清晰" },
    "language": { "score": 5, "max": 5, "comment": "语言专业" }
  },
  "total_score": 4.6,
  "overall_comment": "总体表现优秀",
  "submittedAt": "2025-11-18T10:30:00Z"
}
```

---

**版本**: v1.0
**最后更新**: 2025-11-18
**技术栈**: Node.js + Express + MongoDB + Vanilla JS
**作者**: Claude Code

**🌟 如果这个系统对您有帮助，欢迎Star！**
