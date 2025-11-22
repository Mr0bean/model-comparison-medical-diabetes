# 邮件通知配置说明

## 功能说明

服务器启动时会自动发送包含详细系统信息的邮件到 `745534891@qq.com`，邮件内容包括：

### 详细系统信息（如果收集成功）
- **服务信息**：服务地址、MongoDB URI、启动时间
- **系统信息**：主机名、操作系统、平台、架构、Node.js版本、运行时间
- **CPU信息**：CPU型号、核心数
- **内存信息**：总内存、已用内存、空闲内存、使用率
- **进程内存**：RSS、Heap Total、Heap Used、External
- **网络接口**：所有网络接口列表

### 简单通知（如果系统信息收集失败）
- 服务地址
- MongoDB URI
- 启动时间
- ⚠️ 系统信息收集失败提示

## 配置步骤

### 1. 获取QQ邮箱授权码

1. 登录 [QQ邮箱网页版](https://mail.qq.com/)
2. 点击右上角的 **设置** -> **账户**
3. 找到 **POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务** 部分
4. 开启 **POP3/SMTP服务** 或 **IMAP/SMTP服务**
5. 点击 **生成授权码**
6. 按照提示发送短信验证
7. 生成的授权码会显示在页面上（**注意保存，只显示一次**）

### 2. 配置 .env 文件

打开项目根目录下的 `.env` 文件，找到邮件配置部分：

```env
# ==============================================
# Email Notification Configuration (邮件通知配置)
# ==============================================
# QQ邮箱账号
EMAIL_USER=745534891@qq.com
# QQ邮箱授权码（需要在QQ邮箱设置中生成）
EMAIL_PASS=your_qq_email_authorization_code_here
```

将 `your_qq_email_authorization_code_here` 替换为你刚才获取的授权码。

**示例：**
```env
EMAIL_USER=745534891@qq.com
EMAIL_PASS=abcdefghijklmnop
```

### 3. 重启服务器

保存 `.env` 文件后，重启服务器：

```bash
# 停止当前服务器（如果正在运行）
# 按 Ctrl+C 或使用：
lsof -ti:3001 | xargs kill -9

# 启动服务器
cd server
node server.js
```

## 错误处理

邮件发送功能已经做了完整的错误处理：

1. ✅ **邮件发送失败不影响服务器启动**
   - 即使邮件配置错误或发送失败，服务器仍会正常启动
   - 只会在控制台显示错误信息

2. ✅ **系统信息收集失败自动降级**
   - 如果无法收集详细系统信息，会自动发送简单版本的通知邮件
   - 确保邮件通知功能的可靠性

3. ✅ **详细的错误日志**
   - 显示错误代码（如：EAUTH）
   - 显示失败的命令（如：AUTH PLAIN）
   - 方便快速定位问题

## 常见问题

### Q1: 收不到邮件？
**A:** 检查以下几点：
1. 确认 `.env` 文件中的授权码配置正确
2. 确认QQ邮箱的SMTP服务已开启
3. 查看控制台是否有错误信息

### Q2: 提示 "Invalid login" 错误？
**A:** 这是授权码配置错误导致的：
1. 检查 `.env` 文件中的 `EMAIL_PASS` 是否为授权码（不是QQ密码）
2. 重新生成授权码并更新配置

### Q3: 提示 "ECONNREFUSED" 错误？
**A:** 这是网络连接问题：
1. 检查网络连接是否正常
2. 确认防火墙没有阻止SMTP端口（587）

### Q4: 想禁用邮件通知？
**A:** 有两种方法：
1. 删除或注释 `.env` 文件中的 `EMAIL_PASS` 配置
2. 在 `server/server.js` 中注释掉邮件发送代码

## 测试邮件发送

启动服务器后，观察控制台输出：

```bash
🚀 服务器运行在 http://localhost:3001
📊 MongoDB URI: mongodb://localhost:27017/medical_evaluation
✅ MongoDB连接成功
✅ 启动通知邮件发送成功: <message-id>
```

或者（如果失败）：

```bash
🚀 服务器运行在 http://localhost:3001
📊 MongoDB URI: mongodb://localhost:27017/medical_evaluation
✅ MongoDB连接成功
❌ 启动通知邮件发送失败: Invalid login
   错误代码: EAUTH
   失败命令: AUTH PLAIN
```

## 技术细节

- **邮件服务**: QQ邮箱 SMTP
- **服务器**: smtp.qq.com
- **端口**: 587
- **安全**: STARTTLS
- **依赖**: nodemailer
- **执行方式**: 异步非阻塞

## 支持

如有问题，请检查：
1. QQ邮箱授权码是否正确
2. 网络连接是否正常
3. 控制台错误日志
