# 集成指南 - 如何为评测系统添加身份验证

## 快速集成步骤

### 步骤1：在HTML中引入验证脚本

在 `model_evaluation_chat.html` 的 `</head>` 之前添加：

```html
<!-- 身份验证脚本 -->
<script>
    const API_BASE = 'http://localhost:3001/api';
    let currentUserId = null;
    let isVerified = false;
</script>
```

### 步骤2：添加验证逻辑

在 `<script>` 标签中（在所有其他JavaScript之前）添加：

```javascript
// ==================== 身份验证模块 ====================
(async function initAuth() {
    // 从URL获取ID
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');

    if (!id) {
        showAuthError('缺少身份ID', '请使用正确的链接访问（格式: ?id=xxxx）');
        return;
    }

    if (!/^[a-z0-9]{4}$/.test(id)) {
        showAuthError('ID格式错误', 'ID必须是4位小写字母或数字');
        return;
    }

    currentUserId = id;

    // 验证ID
    try {
        const response = await fetch(`${API_BASE}/verify-code/${id}`);
        const data = await response.json();

        if (data.valid) {
            isVerified = true;
            showAuthBadge(id, data.status);
        } else {
            showAuthError('验证失败', data.message);
        }
    } catch (error) {
        showAuthError('连接失败', '无法连接到服务器');
    }
})();

function showAuthBadge(code, status) {
    // 添加ID显示徽章
    const style = document.createElement('style');
    style.textContent = `
        .id-badge {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.9);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 14px;
            font-weight: 600;
            z-index: 1000;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
    `;
    document.head.appendChild(style);

    const badge = document.createElement('div');
    badge.className = 'id-badge';
    badge.innerHTML = `
        ✅ ID: ${code}
        ${status === 'used' ? '<br><small>已使用</small>' : ''}
    `;
    document.body.appendChild(badge);
}

function showAuthError(title, message) {
    document.body.innerHTML = `
        <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #f5f5f5;">
            <div style="background: white; padding: 40px; border-radius: 12px; text-align: center; max-width: 500px;">
                <h2 style="color: #f5222d; margin-bottom: 15px;">❌ ${title}</h2>
                <p style="color: #666; margin-bottom: 10px;">${message}</p>
                <p style="margin-top: 20px; font-size: 14px;">如需获取访问码，请联系管理员。</p>
            </div>
        </div>
    `;
}

async function submitToServer(evalData) {
    if (!isVerified || !currentUserId) return false;

    try {
        const response = await fetch(`${API_BASE}/submit-evaluation`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code: currentUserId,
                ...evalData
            })
        });

        const data = await response.json();
        return data.success;
    } catch (error) {
        console.error('提交失败:', error);
        return false;
    }
}
// ==================== 验证模块结束 ====================
```

### 步骤3：修改保存函数

找到原有的 `saveEval` 函数，修改为：

```javascript
// 原有的saveEval函数
async function saveEval(silent = false) {
    if (!currentPatient || !availableModels[currentModelIndex]) return;

    const evalData = {
        timestamp: new Date().toISOString(),
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
        overall_comment: document.getElementById('overall-comment').value
    };

    // 保存到localStorage（原有逻辑）
    const storageKey = `eval_${currentPatient}_${availableModels[currentModelIndex]}`;
    localStorage.setItem(storageKey, JSON.stringify(evalData));

    // 提交到服务器（新增）
    if (!silent) {
        const success = await submitToServer(evalData);
        if (success) {
            alert('✅ 评测已保存并提交到服务器！\n\n患者: ' + currentPatient + '\n模型: ' + availableModels[currentModelIndex] + '\n总分: ' + evalData.total_score);
        } else {
            alert('⚠️ 评测已保存到本地，但提交到服务器失败');
        }
    }
}
```

## 完整示例

如果你不想修改现有文件，可以使用以下完整的示例代码创建新文件：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>医疗模型评测 - 带身份验证</title>
    <script>
        const API_BASE = 'http://localhost:3001/api';
        let currentUserId = null;
        let isVerified = false;

        // 验证逻辑（见上文）
        // ...
    </script>
</head>
<body>
    <!-- 原有的HTML内容 -->
    <!-- ... -->

    <script>
        // 原有的JavaScript代码
        // ...

        // 修改后的saveEval函数
        // ...
    </script>
</body>
</html>
```

## 测试步骤

1. **启动后端**：
   ```bash
   cd server
   npm start
   ```

2. **启动前端**：
   ```bash
   python -m http.server 8000
   ```

3. **生成完成码**：
   访问 http://localhost:8000/admin.html
   点击"生成完成码"，获得如 `a1b2` 的码

4. **测试访问**：
   访问 http://localhost:8000/model_evaluation_chat.html?id=a1b2

5. **验证功能**：
   - 右上角应显示 "✅ ID: a1b2"
   - 填写评测并保存
   - 查看管理面板确认数据已提交

## 调试技巧

### 检查验证状态
在浏览器控制台输入：
```javascript
console.log('Verified:', isVerified);
console.log('User ID:', currentUserId);
```

### 查看网络请求
1. 打开开发者工具 (F12)
2. 切换到 Network 标签
3. 筛选 XHR 请求
4. 查看 verify-code 和 submit-evaluation 请求

### 常见错误

#### 错误1: "无法连接到服务器"
- 检查后端是否启动
- 检查API_BASE地址是否正确
- 检查CORS配置

#### 错误2: "ID格式错误"
- 确保ID是4位小写字母或数字
- 例如: a1b2, x7y9, 0000, abcd

#### 错误3: "完成码不存在"
- 确认已在管理面板生成该码
- 检查数据库中是否存在

## 下一步

完成集成后，您可以：
1. 自定义验证错误页面样式
2. 添加更多安全检查
3. 实现数据加密传输
4. 添加批量导出功能
5. 集成邮件通知

---

**需要帮助？** 查看 BACKEND_SETUP.md 或联系技术支持
