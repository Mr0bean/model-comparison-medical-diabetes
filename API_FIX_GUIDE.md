# API 修复说明

## 🔧 问题描述

前端访问 `GET /api/admin/evaluation/:id` 接口时返回 404 错误，因为后端缺少这个接口。

## ✅ 已修复的问题

### 1. 新增接口：获取单个评测详情

**接口路径**: `GET /api/admin/evaluation/:id`

**功能**: 根据评测ID获取单个评测的完整详情

**请求参数**:
- `id` (路径参数): 评测的MongoDB ObjectId

**响应示例**:
```json
{
  "success": true,
  "data": {
    "_id": "691dac07e77f1ee6cac7629e",
    "code": "abc1",
    "patient": "患者1",
    "model": "GPT-4",
    "scores": {
      "accuracy": {
        "score": 5,
        "max": 5,
        "comment": "准确性评论"
      },
      "completeness": {
        "score": 4,
        "max": 5,
        "comment": "完整性评论"
      },
      "standard": {
        "score": 5,
        "max": 5,
        "comment": "规范性评论"
      }
    },
    "total_score": 93,
    "overall_comment": "整体评论",
    "submittedAt": "2025-01-19T10:30:00.000Z"
  }
}
```

**错误处理**:
- 400: 无效的评测ID格式
- 404: 未找到该评测记录
- 500: 服务器错误

### 2. 增强接口：统计数据

**接口路径**: `GET /api/admin/stats`

**新增字段**:
```json
{
  "success": true,
  "codes": { ... },
  "evaluations": {
    "total": 100,
    "avgScore": 85.5,        // ✨ 新增：所有评测的平均分
    "todayCount": 12,        // ✨ 新增：今日评测数量
    "activeModels": 8,       // ✨ 新增：有评测记录的模型数量
    "byModel": [...],
    "byPatient": [...]
  }
}
```

**计算逻辑**:
- `avgScore`: 使用MongoDB聚合函数计算所有评测的平均分
- `todayCount`: 统计今天0点之后提交的评测数量
- `activeModels`: 统计有评测记录的不重复模型数量

## 🚀 部署步骤

### 1. 重启后端服务器

```bash
cd server
npm install  # 如果有新依赖（本次无需）
node server.js
```

或使用 pm2:
```bash
pm2 restart server
```

### 2. 验证接口

**测试获取评测详情**:
```bash
curl http://localhost:3001/api/admin/evaluation/691dac07e77f1ee6cac7629e
```

**测试统计数据**:
```bash
curl http://localhost:3001/api/admin/stats
```

## 📋 完整API列表

更新后的完整API列表：

### 用户端API
1. `GET /api/verify-code/:code` - 验证完成码
2. `POST /api/apply-code` - 申请完成码
3. `POST /api/submit-evaluation` - 提交评测数据
4. `GET /api/evaluations/:code` - 根据完成码获取评测列表

### 管理端API
5. `POST /api/admin/generate-codes` - 批量生成完成码
6. `GET /api/admin/codes` - 获取完成码列表（支持筛选）
7. `GET /api/admin/stats` - 获取统计数据（✨ 已增强）
8. `GET /api/admin/evaluations` - 获取评测列表（支持筛选、分页）
9. `GET /api/admin/evaluation/:id` - 获取单个评测详情（✨ 新增）

## 🎯 前端使用示例

### admin.html 中的调用

```javascript
// 查看评测详情
async function viewEvaluation(id) {
    const response = await fetch(`${API_BASE}/admin/evaluation/${id}`);
    const data = await response.json();

    if (data.success) {
        // 显示详情
        console.log(data.data);
    }
}

// 加载统计数据
async function loadStats() {
    const response = await fetch(`${API_BASE}/admin/stats`);
    const data = await response.json();

    if (data.success) {
        // 显示新的统计数据
        document.getElementById('avgScore').textContent =
            data.evaluations.avgScore.toFixed(1);
        document.getElementById('todayEvaluations').textContent =
            data.evaluations.todayCount;
        document.getElementById('activeModels').textContent =
            data.evaluations.activeModels;
    }
}
```

## 🔍 调试技巧

### 查看服务器日志

```bash
# 如果直接运行
node server.js

# 如果使用pm2
pm2 logs server
```

### 测试数据库连接

```bash
# 连接MongoDB
mongo
use medical_evaluation
db.evaluations.find().limit(1)
```

### 验证评测ID格式

MongoDB ObjectId 必须是24个十六进制字符：
- ✅ 正确: `691dac07e77f1ee6cac7629e`
- ❌ 错误: `123` (太短)
- ❌ 错误: `invalid-id` (非十六进制)

## 📊 数据模型

### Evaluation Schema
```javascript
{
  _id: ObjectId,           // MongoDB自动生成
  code: String,            // 完成码
  patient: String,         // 患者名称
  model: String,           // 模型名称
  scores: {
    accuracy: {
      score: Number,       // 1-5星
      max: Number,         // 满分5
      comment: String
    },
    completeness: { ... },
    standard: { ... }
  },
  total_score: Number,     // 百分制总分（0-100）
  overall_comment: String,
  timestamp: Date,
  submittedAt: Date
}
```

## ⚠️ 注意事项

1. **ID验证**: 前端传递的ID必须是有效的MongoDB ObjectId格式
2. **错误处理**: 前端需要处理404错误（记录不存在）
3. **时区问题**: `todayCount` 基于服务器时区计算
4. **性能优化**: 统计数据使用MongoDB聚合，大数据量时可能需要添加索引

## 🎉 修复完成

现在前端的以下功能可以正常工作：
- ✅ 点击评测列表中的"查看详情"按钮
- ✅ 点击完成码的"查看详情"按钮
- ✅ 显示平均分、今日评测数、活跃模型数统计
- ✅ 详情弹窗显示完整的评测信息

重启服务器后即可使用！
