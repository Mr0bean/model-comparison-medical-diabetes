# Toast 提示功能说明

## 🎯 功能概述

为评测系统添加了优雅的 Toast 非阻塞提示功能，优化了切换患者时的用户体验。

## ✨ 新增功能

### 1. **Toast 提示组件**

美观的非阻塞提示框，支持多种类型：
- 🔵 **info**: 普通信息（默认，紫色渐变）
- ✅ **success**: 成功提示（绿色渐变）
- ⚠️ **warning**: 警告提示（橙色渐变）
- ❌ **error**: 错误提示（红色渐变）

**特点**：
- 自动滑入/滑出动画
- 固定显示在页面顶部中央
- 不阻塞用户操作
- 自动隐藏（可自定义时长）

### 2. **切换患者检查逻辑**

#### 手动切换（点击患者标签）
- **未完成检查**: 点击其他患者标签时，检查当前患者的所有报告是否已评测完成
- **阻止切换**: 如果未完成，显示 alert 提示，不允许切换
- **允许切换**: 如果已完成，直接切换，无提示

#### 自动切换（保存后自动）
- **静默切换**: 保存当前报告后，自动切换到下一个报告或患者
- **Toast 提示**: 切换到新患者时，显示绿色成功提示
- **完成提示**: 所有任务完成时，显示庆祝提示

## 📋 使用场景

### 场景1: 用户手动切换患者（未完成）
```
用户点击"患者2"标签
↓
系统检测：患者1 还有报告未评测
↓
显示 alert: "⚠️ 请先完成当前患者的所有报告评测！"
↓
停留在患者1，不允许切换
```

### 场景2: 用户手动切换患者（已完成）
```
用户点击"患者2"标签
↓
系统检测：患者1 所有报告已完成
↓
直接切换到患者2
↓
无任何提示（避免打扰）
```

### 场景3: 保存后自动切换患者
```
用户保存患者1的最后一个报告
↓
系统检测：患者1 所有报告已完成
↓
自动切换到患者2
↓
显示 Toast: "✅ 当前患者已完成，已自动切换到 患者2"
↓
Toast 4秒后自动消失
```

### 场景4: 所有任务完成
```
用户保存最后一个患者的最后一个报告
↓
系统检测：所有患者都已完成
↓
显示 Toast: "🎉 恭喜！所有评测任务已完成！"
↓
Toast 5秒后自动消失
```

## 🎨 视觉效果

### Toast 提示框样式
```
┌─────────────────────────────────────────┐
│  ✅ 当前患者已完成，已自动切换到 患者2  │
└─────────────────────────────────────────┘
```

- 位置：页面顶部中央
- 动画：从上方滑入，延迟后滑出
- 渐变背景，白色文字
- 圆角，阴影效果

## 🔧 技术实现

### 1. CSS 动画
```css
@keyframes slideDown {
    from { transform: translate(-50%, -100%); opacity: 0; }
    to { transform: translate(-50%, 0); opacity: 1; }
}

@keyframes slideUp {
    from { transform: translate(-50%, 0); opacity: 1; }
    to { transform: translate(-50%, -100%); opacity: 0; }
}
```

### 2. JavaScript 函数
```javascript
// 显示 Toast
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show ' + type;

    // 自动隐藏
    setTimeout(() => {
        toast.classList.add('hiding');
        setTimeout(() => {
            toast.classList.remove('show', 'hiding', type);
        }, 300);
    }, duration);
}
```

### 3. 患者切换逻辑
```javascript
function selectPatient(patient, fromAuto = false) {
    // 手动切换时检查完成度
    if (!fromAuto && currentPatient !== patient) {
        if (!allCompleted) {
            alert('⚠️ 请先完成当前患者的所有报告评测！');
            return;
        }
    }

    // 执行切换
    currentPatient = patient;
    updateView();

    // 自动切换时显示提示
    if (fromAuto) {
        showToast(`✅ 当前患者已完成，已自动切换到 ${patient}`, 'success', 4000);
    }
}
```

## 📊 完成度检查

系统会检查以下条件来判断患者是否完成：

1. **所有模型都已评测**: 检查每个模型的 localStorage 记录
2. **所有评分都已填写**: 检查3个维度（准确性、完整性、规范性）的分数都大于0

```javascript
// 检查逻辑
for (let model of availableModels) {
    const saved = localStorage.getItem(`eval_${patient}_${model}`);
    const evalData = JSON.parse(saved);

    if (!evalData ||
        evalData.scores.accuracy.score === 0 ||
        evalData.scores.completeness.score === 0 ||
        evalData.scores.standard.score === 0) {
        return false; // 未完成
    }
}
return true; // 已完成
```

## 🎯 用户体验优化

### 对比：修改前 vs 修改后

| 场景 | 修改前 | 修改后 |
|------|--------|--------|
| 手动切换（未完成） | ❌ 可以切换，丢失数据 | ✅ 阻止切换，提示完成 |
| 手动切换（已完成） | ✅ 直接切换 | ✅ 直接切换（保持） |
| 自动切换患者 | ✅ 静默切换 | ✅ Toast 提示（更友好） |
| 所有完成 | ❌ 无提示 | ✅ 庆祝提示 |

### 优势

1. **防止误操作**: 手动切换时检查完成度，避免未完成就切换
2. **友好提示**: 自动切换时显示非阻塞提示，用户清楚发生了什么
3. **不打扰**: 手动切换已完成的患者时，不显示提示（避免冗余）
4. **反馈及时**: Toast 提示立即出现，4秒后自动消失
5. **视觉美观**: 渐变色、动画效果，提升用户体验

## 🎊 示例效果

```
用户流程：
1. 评测患者1的所有报告 → 保存最后一个
2. Toast 出现："✅ 当前患者已完成，已自动切换到 患者2"（绿色）
3. 页面自动切换到患者2，第一个报告
4. Toast 4秒后滑出消失
5. 用户继续评测患者2
```

## 🔄 兼容性

- ✅ 不影响现有功能
- ✅ 向后兼容
- ✅ 所有浏览器支持（CSS3 动画）
- ✅ 移动端适配

## 🚀 后续优化建议

1. 可以添加 Toast 队列，支持多个提示依次显示
2. 可以添加关闭按钮，允许用户手动关闭
3. 可以添加声音提示（可选）
4. 可以记录提示历史，允许用户查看

所有功能已完成，开箱即用！🎉
