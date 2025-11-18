/**
 * 医疗AI评测系统 - 身份验证与数据提交模块
 * 在 model_evaluation_chat.html 中引入此文件
 */

const API_BASE = 'http://localhost:3001/api';
let currentUserId = null;
let isVerified = false;

// 页面加载时验证ID
(function initAuth() {
    // 从URL参数获取ID
    const urlParams = new URLSearchParams(window.location.search);
    const id = urlParams.get('id');

    if (!id) {
        showAuthError('缺少身份ID参数', '请使用正确的链接访问此页面（格式: ?id=xxxx）');
        return;
    }

    if (!/^[a-z0-9]{4}$/.test(id)) {
        showAuthError('ID格式错误', 'ID必须是4位小写字母或数字');
        return;
    }

    currentUserId = id;
    verifyCode(id);
})();

// 验证完成码
async function verifyCode(code) {
    try {
        const response = await fetch(`${API_BASE}/verify-code/${code}`);
        const data = await response.json();

        if (data.valid) {
            isVerified = true;
            showAuthSuccess(code, data.status);

            // 如果已使用，加载之前保存的数据
            if (data.status === 'used') {
                loadServerData(code);
            }
        } else {
            showAuthError('验证失败', data.message);
        }
    } catch (error) {
        console.error('验证失败:', error);
        showAuthError('连接失败', '无法连接到服务器，请联系管理员');
    }
}

// 显示验证成功
function showAuthSuccess(code, status) {
    // 创建ID徽章
    const badge = document.createElement('div');
    badge.className = 'id-badge verified';
    badge.innerHTML = `
        <span style="opacity: 0.8;">ID:</span> ${code}
        ${status === 'used' ? '<br><small style="font-size: 12px;">已使用</small>' : ''}
    `;

    document.querySelector('.header').appendChild(badge);

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
