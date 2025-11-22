# 提交状态指示器功能说明

## 🎯 功能概述

为评测系统添加了提交状态指示器，实时显示当前医疗报告的提交状态，让用户清楚知道哪些报告已提交，哪些还未提交。

## ✨ 新增功能

### 1. **提交状态指示器**

位于页面右下角浮动按钮下方的状态指示器，显示当前报告的提交状态：

- **✓ 已提交** (绿色): 当前报告已保存并提交到服务器
- **⚠ 未提交** (橙色): 当前报告尚未提交或仅有自动保存的数据

**特点**：
- 固定显示在页面右下角
- 实时更新，切换报告时自动刷新
- 圆角卡片样式，半透明背景
- 毛玻璃效果（backdrop-filter）
- 带有状态图标和文字说明

## 📋 使用场景

### 场景1: 查看当前报告状态

```
用户切换到某个患者的某个模型报告
↓
系统检查该报告的提交状态
↓
显示状态指示器
- 如果已提交：显示 "✓ 已提交"（绿色）
- 如果未提交：显示 "⚠ 未提交"（橙色）
```

### 场景2: 保存报告后状态更新

```
用户填写评测并点击保存
↓
数据保存到 localStorage 和 eval_history
↓
状态指示器立即更新为 "✓ 已提交"（绿色）
↓
用户可以看到即时反馈
```

### 场景3: 切换报告时查看状态

```
用户切换到下一个报告
↓
updateView() 自动调用 updateSubmitStatus()
↓
检查新报告的提交状态并更新显示
↓
用户可以快速知道新报告是否已提交
```

## 🎨 视觉效果

### 已提交状态
```
┌─────────────┐
│ ✓ 已提交    │  （绿色边框 #52c41a）
└─────────────┘
```

### 未提交状态
```
┌─────────────┐
│ ⚠ 未提交    │  （橙色边框 #faad14）
└─────────────┘
```

**样式特点**：
- 位置：页面右下角，浮动按钮正下方
- 背景：白色半透明 (rgba(255, 255, 255, 0.95))
- 毛玻璃效果：backdrop-filter: blur(10px)
- 圆角：border-radius: 20px
- 阴影：box-shadow: 0 4px 12px rgba(0,0,0,0.15)
- 动画：0.3秒淡入淡出过渡

## 🔧 技术实现

### 1. HTML 结构

```html
<div class="submit-status hidden" id="submitStatus">
    <span class="submit-status-icon" id="submitStatusIcon">✓</span>
    <span id="submitStatusText">已提交</span>
</div>
```

### 2. CSS 样式

```css
.submit-status {
    position: fixed;
    bottom: 20px;
    right: 30px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 8px 16px;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.3s ease;
    z-index: 999;
}

.submit-status.submitted {
    color: #52c41a;
    border: 2px solid #52c41a;
}

.submit-status.not-submitted {
    color: #faad14;
    border: 2px solid #faad14;
}

.submit-status.hidden {
    display: none;
}
```

### 3. JavaScript 核心函数

```javascript
function updateSubmitStatus() {
    const statusDiv = document.getElementById('submitStatus');
    const statusIcon = document.getElementById('submitStatusIcon');
    const statusText = document.getElementById('submitStatusText');

    // 如果没有当前患者或模型，隐藏指示器
    if (!currentPatient || !availableModels[currentModelIndex]) {
        statusDiv.classList.add('hidden');
        return;
    }

    // 检查localStorage中是否有数据
    const storageKey = `eval_${currentPatient}_${availableModels[currentModelIndex]}`;
    const evalData = localStorage.getItem(storageKey);

    if (!evalData) {
        // 没有数据，显示"未提交"
        statusDiv.classList.remove('hidden', 'submitted');
        statusDiv.classList.add('not-submitted');
        statusIcon.textContent = '⚠';
        statusText.textContent = '未提交';
        return;
    }

    // 检查是否在历史记录中（说明已手动保存/提交）
    const history = JSON.parse(localStorage.getItem('eval_history') || '[]');
    const isSubmitted = history.some(h =>
        h.patient === currentPatient &&
        h.model === availableModels[currentModelIndex]
    );

    if (isSubmitted) {
        // 已提交
        statusDiv.classList.remove('hidden', 'not-submitted');
        statusDiv.classList.add('submitted');
        statusIcon.textContent = '✓';
        statusText.textContent = '已提交';
    } else {
        // 有数据但未提交（仅自动保存）
        statusDiv.classList.remove('hidden', 'submitted');
        statusDiv.classList.add('not-submitted');
        statusIcon.textContent = '⚠';
        statusText.textContent = '未提交';
    }
}
```

### 4. 调用位置

#### 在 updateView() 中自动更新

```javascript
function updateView() {
    updateChatView();
    updateReportView();
    updateNavigator();
    loadSavedEval();
    checkCompletionStatus();
    updateSubmitStatus(); // ✨ 新增：更新提交状态显示
}
```

#### 在 saveEval() 保存后立即更新

```javascript
async function saveEval(silent = false) {
    // ... 保存逻辑 ...

    // 更新提交状态显示
    updateSubmitStatus(); // ✨ 新增：保存后立即更新状态

    // 关闭评测弹窗并显示浮动按钮
    closeEvalWindow();

    // 自动切换到下一个任务
    autoSwitchToNext();
}
```

## 📊 状态判断逻辑

系统通过以下条件判断报告是否已提交：

1. **检查 localStorage**: 查找 `eval_${patient}_${model}` 键
2. **检查历史记录**: 查找 `eval_history` 数组中是否包含该患者-模型的记录

```javascript
// 判断逻辑流程图
localStorage中有数据？
├─ 否 → 未提交（橙色）
└─ 是 → eval_history中有记录？
    ├─ 否 → 未提交（橙色，仅自动保存）
    └─ 是 → 已提交（绿色）
```

### 数据存储说明

- **localStorage (`eval_${patient}_${model}`)**:
  - 存储评测数据
  - 由手动保存或自动保存创建

- **localStorage (`eval_history`)**:
  - 存储已提交的评测历史
  - 仅由手动保存（点击保存按钮）时创建
  - 用于判断是否已提交到服务器

## 🎯 用户体验优化

### 对比：添加前 vs 添加后

| 场景 | 添加前 | 添加后 |
|------|--------|--------|
| 查看提交状态 | ❌ 无法知道是否已提交 | ✅ 实时显示提交状态 |
| 切换报告 | ❌ 不知道新报告状态 | ✅ 自动更新显示 |
| 保存后反馈 | ❌ 仅有保存提示 | ✅ 状态立即更新为已提交 |
| 视觉反馈 | ❌ 无视觉指示 | ✅ 绿色/橙色清晰区分 |

### 优势

1. **实时反馈**: 切换报告时立即显示状态，无需猜测
2. **清晰直观**: 绿色已提交、橙色未提交，一目了然
3. **持续可见**: 固定在右下角，始终可见
4. **美观优雅**: 毛玻璃效果，与界面整体风格统一
5. **即时更新**: 保存后立即更新，提供即时反馈

## 🎊 示例效果

```
用户流程：
1. 打开某个患者的某个模型报告
2. 右下角显示 "⚠ 未提交"（橙色）
3. 用户填写评测并保存
4. 状态立即更新为 "✓ 已提交"（绿色）
5. 切换到下一个报告
6. 状态自动刷新，显示新报告的提交状态
```

## 🔄 兼容性

- ✅ 不影响现有功能
- ✅ 向后兼容
- ✅ 所有现代浏览器支持
- ✅ 移动端适配（固定在右下角）
- ✅ 与浮动按钮配合显示

## 📍 位置布局

```
页面右下角：

┌──────────────┐
│              │
│  浮动按钮    │  ← evalFloatBtn（评分按钮）
│              │
└──────────────┘
      ↓
┌─────────────┐
│ ✓ 已提交    │  ← submitStatus（提交状态指示器）
└─────────────┘
```

## 🚀 后续优化建议

1. 可以添加点击状态指示器查看详细信息的功能
2. 可以添加批量查看所有报告提交状态的面板
3. 可以添加未提交报告数量的统计
4. 可以添加一键提交所有未提交报告的功能
5. 可以添加提交失败的错误提示和重试机制

所有功能已完成，开箱即用！🎉
