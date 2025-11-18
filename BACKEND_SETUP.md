# 医疗AI评测系统 - 后端部署指南

## 📋 系统架构

```
┌─────────────────┐
│  管理员面板      │ (admin.html)
│  生成/管理码     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  后端API服务     │◄────►│   MongoDB数据库   │
│  (Node.js)      │      │   - codes集合     │
└────────┬────────┘      │   - evaluations  │
         │               └──────────────────┘
         ▼
┌─────────────────┐
│  评测前端        │ (model_evaluation_chat.html?id=xxxx)
│  验证+提交数据   │
└─────────────────┘
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd server
npm install
```

### 2. 配置MongoDB

方式一：使用本地MongoDB
```bash
# 安装MongoDB（macOS）
brew install mongodb-community

# 启动MongoDB
brew services start mongodb-community
```

方式二：使用MongoDB Atlas（云数据库）
1. 访问 https://www.mongodb.com/cloud/atlas
2. 创建免费集群
3. 获取连接字符串

### 3. 配置环境变量

```bash
cd server
cp .env.example .env
```

编辑 `.env` 文件：
```env
# 本地MongoDB
MONGODB_URI=mongodb://localhost:27017/medical_evaluation

# 或使用MongoDB Atlas
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/medical_evaluation

PORT=3001
```

### 4. 启动后端服务

```bash
# 开发模式（自动重启）
npm run dev

# 或生产模式
npm start
```

看到以下信息表示启动成功：
```
✅ MongoDB连接成功
🚀 服务器运行在 http://localhost:3001
```

### 5. 生成完成码

打开管理面板：
```
http://localhost:8000/admin.html
```

点击"生成完成码"，输入数量（如10），点击生成。

### 6. 分发完成码给评测者

将生成的完成码分发给评测者，他们访问：
```
http://localhost:8000/model_evaluation_chat.html?id=a1b2
```

## 📊 API文档

### 1. 验证完成码
```http
GET /api/verify-code/:code
```

响应：
```json
{
  "valid": true,
  "status": "active",  // active | used | expired
  "message": "完成码验证成功"
}
```

### 2. 提交评测数据
```http
POST /api/submit-evaluation
Content-Type: application/json

{
  "code": "a1b2",
  "patient": "患者1",
  "model": "GPT-4",
  "scores": {
    "accuracy": { "score": 5, "max": 5, "comment": "..." },
    ...
  },
  "total_score": 4.5,
  "overall_comment": "..."
}
```

响应：
```json
{
  "success": true,
  "message": "评测数据提交成功",
  "evaluationId": "..."
}
```

### 3. 获取评测数据
```http
GET /api/evaluations/:code
```

### 4. 生成完成码（管理员）
```http
POST /api/admin/generate-codes
Content-Type: application/json

{
  "count": 10,
  "description": "第一批评测人员"
}
```

### 5. 获取统计数据（管理员）
```http
GET /api/admin/stats
```

### 6. 获取所有评测数据（管理员）
```http
GET /api/admin/evaluations?page=1&limit=50
```

## 🔧 集成到前端

### 方法一：修改现有HTML（推荐）

在 `model_evaluation_chat.html` 的 `</body>` 之前添加：

```html
<!-- 在</body>之前添加 -->
<script src="evaluation-auth.js"></script>
<script>
// 修改原有的saveEval函数
const originalSaveEval = window.saveEval;
window.saveEval = async function(silent = false) {
    // 先保存到localStorage（原有逻辑）
    if (originalSaveEval) {
        originalSaveEval.call(this, silent);
    }

    // 获取评测数据
    const evalData = {
        patient: currentPatient,
        model: availableModels[currentModelIndex],
        scores: {
            accuracy: {
                score: parseInt(document.getElementById('score-accuracy').value) || 0,
                max: 5,
                comment: document.getElementById('comment-accuracy').value
            },
            completeness: {
                score: parseInt(document.getElementById('score-completeness').value) || 0,
                max: 5,
                comment: document.getElementById('comment-completeness').value
            },
            clinical: {
                score: parseInt(document.getElementById('score-clinical').value) || 0,
                max: 5,
                comment: document.getElementById('comment-clinical').value
            },
            structure: {
                score: parseInt(document.getElementById('score-structure').value) || 0,
                max: 5,
                comment: document.getElementById('comment-structure').value
            },
            language: {
                score: parseInt(document.getElementById('score-language').value) || 0,
                max: 5,
                comment: document.getElementById('comment-language').value
            }
        },
        total_score: parseFloat(document.getElementById('totalScore').textContent),
        overall_comment: document.getElementById('overall-comment').value,
        timestamp: new Date().toISOString()
    };

    // 提交到服务器（仅在手动保存时）
    if (!silent && window.submitEvaluationToServer) {
        const success = await window.submitEvaluationToServer(evalData);
        if (success) {
            console.log('✅ 数据已提交到服务器');
        }
    }
};
</script>
```

### 方法二：使用独立的评测页面

创建 `evaluation.html`，基于 `model_evaluation_chat.html` 并集成验证功能。

## 📁 数据结构

### Code Collection
```javascript
{
  code: "a1b2",              // 完成码（4位）
  status: "active",          // active | used | expired
  createdAt: ISODate,
  usedAt: ISODate,
  batchId: "batch_xxx",
  description: "第一批"
}
```

### Evaluation Collection
```javascript
{
  code: "a1b2",              // 关联的完成码
  patient: "患者1",
  model: "GPT-4",
  scores: {
    accuracy: { score: 5, max: 5, comment: "..." },
    completeness: { score: 4, max: 5, comment: "..." },
    clinical: { score: 5, max: 5, comment: "..." },
    structure: { score: 4, max: 5, comment: "..." },
    language: { score: 5, max: 5, comment: "..." }
  },
  total_score: 4.6,
  overall_comment: "...",
  timestamp: ISODate,
  submittedAt: ISODate
}
```

## 🔒 安全建议

1. **生产环境**：
   - 添加管理员认证
   - 使用HTTPS
   - 限制CORS origin
   - 添加速率限制

2. **完成码管理**：
   - 定期清理过期码
   - 设置使用期限
   - 记录访问日志

3. **数据备份**：
   - 定期备份MongoDB
   - 导出评测数据为CSV/JSON

## 📈 监控与维护

### 查看数据库
```bash
# 连接MongoDB
mongosh

# 切换数据库
use medical_evaluation

# 查看完成码
db.codes.find()

# 查看评测数据
db.evaluations.find()

# 统计
db.codes.countDocuments()
db.evaluations.countDocuments()
```

### 导出数据
```bash
# 导出所有评测数据
mongoexport --db=medical_evaluation --collection=evaluations --out=evaluations.json

# 导出完成码
mongoexport --db=medical_evaluation --collection=codes --out=codes.json
```

## 🆘 常见问题

### Q: 无法连接MongoDB
A: 检查MongoDB是否启动：`brew services list`

### Q: CORS错误
A: 确保前端和后端在同一域名，或配置CORS

### Q: 完成码已存在
A: 4位码最多1296个组合，批量生成时可能重复，系统会自动重试

### Q: 如何重置系统
```bash
mongosh
use medical_evaluation
db.codes.deleteMany({})
db.evaluations.deleteMany({})
```

## 📞 技术支持

如有问题，请查看：
- 服务器日志
- 浏览器控制台
- MongoDB日志

---

**版本**: v1.0
**更新日期**: 2025-11-18
**作者**: Claude Code
