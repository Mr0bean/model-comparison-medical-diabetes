/**
 * 医疗AI评测系统 - 身份验证与数据提交模块
 * 在 model_evaluation_chat.html 中引入此文件
 */

const API_BASE = 'http://localhost:3001/api';
let currentUserId = null;
let isVerified = false;

// 页面加载时验证ID
(async function initAuth() {
    // 从URL参数获取ID
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');

    if (id) {
        // 如果URL有id参数，直接验证
        if (!/^[a-z0-9]{4}$/.test(id)) {
            showAuthError('ID格式错误', 'ID必须是4位小写字母或数字');
            return;
        }
        currentUserId = id;
        await verifyCode(id);
        return;
    }

    // 尝试从缓存读取完成码
    const cachedCode = localStorage.getItem('completion_code');
    if (cachedCode && /^[a-z0-9]{4}$/.test(cachedCode)) {
        console.log('检测到缓存的完成码，正在验证...');
        currentUserId = cachedCode;
        const isValid = await verifyCode(cachedCode);
        if (isValid) {
            console.log('缓存的完成码验证成功');
            return;
        } else {
            // 缓存的完成码无效，清除缓存
            console.log('缓存的完成码已失效，清除缓存');
            localStorage.removeItem('completion_code');
        }
    }

    // 没有有效的完成码，显示输入框
    showCodeInput();
})();

// 显示完成码输入框
function showCodeInput() {
    // 检查是否已申请过
    const hasApplied = localStorage.getItem('has_applied_code');
    const appliedCode = localStorage.getItem('applied_code');

    const overlay = document.createElement('div');
    overlay.className = 'auth-overlay';
    overlay.innerHTML = `
        <div class="auth-dialog">
            <h2 style="color: #1890ff; margin-bottom: 20px;">🔐 请输入完成码</h2>
            <p style="color: #666; margin-bottom: 20px;">请输入管理员分配给您的4位完成码，或点击下方申请</p>
            <input type="text" id="codeInput"
                   placeholder="请输入4位完成码"
                   maxlength="4"
                   style="width: 200px; padding: 12px; font-size: 18px; text-align: center;
                          border: 2px solid #d9d9d9; border-radius: 8px;
                          font-family: monospace; letter-spacing: 4px;
                          text-transform: lowercase; margin-bottom: 10px;">
            <div id="codeError" style="color: #f5222d; font-size: 14px; min-height: 20px; margin-bottom: 10px;"></div>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button id="verifyBtn"
                        style="padding: 12px 40px; background: #1890ff; color: white;
                               border: none; border-radius: 8px; font-size: 16px;
                               cursor: pointer; font-weight: 600;">
                    验证
                </button>
                <button id="applyBtn"
                        ${hasApplied ? 'disabled' : ''}
                        style="padding: 12px 40px; background: ${hasApplied ? '#d9d9d9' : '#52c41a'}; color: white;
                               border: none; border-radius: 8px; font-size: 16px;
                               cursor: ${hasApplied ? 'not-allowed' : 'pointer'}; font-weight: 600;">
                    ${hasApplied ? '已申请' : '申请完成码'}
                </button>
            </div>
            ${hasApplied ? `<p style="margin-top: 15px; font-size: 14px; color: #52c41a;">
                您已申请过完成码：<span style="font-family: monospace; font-weight: 600;">${appliedCode || '****'}</span>
            </p>` : ''}
            <p style="margin-top: 20px; font-size: 14px; color: #999;">
                ${hasApplied ? '每台设备只能申请一次完成码' : '如需获取完成码，请联系管理员'}
            </p>
        </div>
    `;

    document.body.appendChild(overlay);

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .auth-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        .auth-dialog {
            background: white;
            padding: 40px;
            border-radius: 12px;
            max-width: 500px;
            text-align: center;
        }
        #codeInput:focus {
            outline: none;
            border-color: #1890ff;
        }
        #verifyBtn:hover {
            background: #40a9ff;
        }
        #verifyBtn:active {
            background: #096dd9;
        }
    `;
    document.head.appendChild(style);

    // 禁用页面交互
    document.body.style.pointerEvents = 'none';
    overlay.style.pointerEvents = 'auto';

    // 自动聚焦输入框
    setTimeout(() => {
        document.getElementById('codeInput').focus();
    }, 100);

    // 绑定验证按钮
    document.getElementById('verifyBtn').addEventListener('click', handleCodeSubmit);

    // 绑定申请按钮
    const applyBtn = document.getElementById('applyBtn');
    if (applyBtn && !hasApplied) {
        applyBtn.addEventListener('click', handleApplyCode);
    }

    // 绑定回车键
    document.getElementById('codeInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleCodeSubmit();
        }
    });

    // 自动转小写
    document.getElementById('codeInput').addEventListener('input', (e) => {
        e.target.value = e.target.value.toLowerCase();
    });
}

// 处理完成码提交
async function handleCodeSubmit() {
    const input = document.getElementById('codeInput');
    const errorDiv = document.getElementById('codeError');
    const code = input.value.trim();

    if (!code) {
        errorDiv.textContent = '请输入完成码';
        return;
    }

    if (!/^[a-z0-9]{4}$/.test(code)) {
        errorDiv.textContent = '完成码必须是4位小写字母或数字';
        return;
    }

    errorDiv.textContent = '验证中...';

    // 验证完成码
    currentUserId = code;
    const result = await verifyCode(code);

    if (!result) {
        errorDiv.textContent = '验证失败，请检查完成码是否正确';
        input.value = '';
        input.focus();
    }
}

// 处理申请完成码
async function handleApplyCode() {
    const errorDiv = document.getElementById('codeError');
    const applyBtn = document.getElementById('applyBtn');

    // 检查是否已申请过
    if (localStorage.getItem('has_applied_code')) {
        errorDiv.textContent = '该设备已申请过完成码，不能重复申请';
        errorDiv.style.color = '#faad14';
        return;
    }

    // 禁用按钮
    applyBtn.disabled = true;
    applyBtn.textContent = '申请中...';
    applyBtn.style.cursor = 'not-allowed';
    errorDiv.textContent = '正在申请完成码...';
    errorDiv.style.color = '#1890ff';

    try {
        const response = await fetch(`${API_BASE}/apply-code`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.success && data.code) {
            // 保存申请标记和完成码
            localStorage.setItem('has_applied_code', 'true');
            localStorage.setItem('applied_code', data.code);

            errorDiv.textContent = `✅ 申请成功！您的完成码是：${data.code}`;
            errorDiv.style.color = '#52c41a';

            // 自动填充完成码
            document.getElementById('codeInput').value = data.code;

            // 3秒后自动验证
            setTimeout(() => {
                handleCodeSubmit();
            }, 2000);
        } else {
            throw new Error(data.message || '申请失败');
        }
    } catch (error) {
        console.error('申请失败:', error);
        errorDiv.textContent = '申请失败：' + error.message;
        errorDiv.style.color = '#f5222d';
        applyBtn.disabled = false;
        applyBtn.textContent = '申请完成码';
        applyBtn.style.cursor = 'pointer';
    }
}

// 验证完成码
async function verifyCode(code) {
    try {
        const response = await fetch(`${API_BASE}/verify-code/${code}`);
        const data = await response.json();

        if (data.valid) {
            isVerified = true;

            // 保存完成码到缓存
            localStorage.setItem('completion_code', code);
            console.log('完成码已缓存到localStorage');

            // 移除输入对话框
            const overlay = document.querySelector('.auth-overlay');
            if (overlay) {
                overlay.remove();
            }
            // 恢复页面交互
            document.body.style.pointerEvents = 'auto';

            showAuthSuccess(code, data.status);

            // 如果已使用，加载之前保存的数据
            if (data.status === 'used') {
                loadServerData(code);
            }

            return true;
        } else {
            return false;
        }
    } catch (error) {
        console.error('验证失败:', error);
        return false;
    }
}

// 显示验证成功
function showAuthSuccess(code, status) {
    // 创建ID徽章
    const badge = document.createElement('div');
    badge.className = 'id-badge verified';
    badge.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <div>
                <span style="opacity: 0.8;">ID:</span> ${code}
                ${status === 'used' ? '<br><small style="font-size: 12px;">已使用</small>' : ''}
            </div>
            <button id="clearCodeBtn" title="清除完成码缓存"
                    style="background: rgba(255,255,255,0.2); border: none; color: white;
                           padding: 4px 8px; border-radius: 4px; cursor: pointer;
                           font-size: 12px;">✕</button>
        </div>
    `;

    document.querySelector('.header').appendChild(badge);

    // 绑定清除按钮事件
    document.getElementById('clearCodeBtn').addEventListener('click', () => {
        if (confirm('确定要清除完成码缓存吗？\n下次访问需要重新输入完成码。')) {
            localStorage.removeItem('completion_code');
            alert('完成码缓存已清除！\n页面将刷新。');
            location.reload();
        }
    });

    // 添加CSS样式
    if (!document.getElementById('auth-styles')) {
        const style = document.createElement('style');
        style.id = 'auth-styles';
        style.textContent = `
            .id-badge {
                position: absolute;
                right: 20px;
                top: 50%;
                transform: translateY(-50%);
                background: rgba(76, 175, 80, 0.3);
                padding: 10px 20px;
                border-radius: 8px;
                font-family: monospace;
                font-size: 16px;
                font-weight: 600;
                color: white;
                text-align: center;
            }
            #clearCodeBtn:hover {
                background: rgba(255,255,255,0.4) !important;
            }
            .auth-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            }
            .auth-dialog {
                background: white;
                padding: 40px;
                border-radius: 12px;
                max-width: 500px;
                text-align: center;
            }
            .auth-dialog h2 {
                color: #f5222d;
                margin-bottom: 15px;
            }
            .auth-dialog p {
                color: #666;
                margin-bottom: 10px;
                line-height: 1.6;
            }
        `;
        document.head.appendChild(style);
    }
}

// 显示验证错误
function showAuthError(title, message) {
    const overlay = document.createElement('div');
    overlay.className = 'auth-overlay';
    overlay.innerHTML = `
        <div class="auth-dialog">
            <h2>❌ ${title}</h2>
            <p>${message}</p>
            <p style="margin-top: 20px; font-size: 14px;">
                如需获取访问码，请联系管理员。
            </p>
        </div>
    `;

    document.body.appendChild(overlay);

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
        .auth-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }
        .auth-dialog {
            background: white;
            padding: 40px;
            border-radius: 12px;
            max-width: 500px;
            text-align: center;
        }
        .auth-dialog h2 {
            color: #f5222d;
            margin-bottom: 15px;
        }
        .auth-dialog p {
            color: #666;
            margin-bottom: 10px;
            line-height: 1.6;
        }
    `;
    document.head.appendChild(style);

    // 禁用页面交互
    document.body.style.pointerEvents = 'none';
    overlay.style.pointerEvents = 'auto';
}

// 从服务器加载已保存的数据
async function loadServerData(code) {
    try {
        const response = await fetch(`${API_BASE}/evaluations/${code}`);
        const data = await response.json();

        if (data.success && data.data.length > 0) {
            console.log(`加载了 ${data.count} 条评测记录`);
            // 这里可以根据需要恢复数据到界面
        }
    } catch (error) {
        console.error('加载服务器数据失败:', error);
    }
}

// 提交评测数据到服务器（覆盖原有的saveEval函数）
window.submitEvaluationToServer = async function(evalData) {
    if (!isVerified || !currentUserId) {
        alert('未验证身份，无法提交数据');
        return false;
    }

    try {
        const response = await fetch(`${API_BASE}/submit-evaluation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code: currentUserId,
                ...evalData
            })
        });

        const data = await response.json();

        if (data.success) {
            return true;
        } else {
            console.error('提交失败:', data.message);
            return false;
        }
    } catch (error) {
        console.error('提交到服务器失败:', error);
        return false;
    }
};

// 导出函数供页面使用
window.getAuthStatus = function() {
    return {
        isVerified,
        userId: currentUserId
    };
};
