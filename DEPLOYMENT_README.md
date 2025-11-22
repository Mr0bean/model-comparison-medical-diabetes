# 🚀 部署文件总览

本项目已配置完整的生产环境部署方案，支持一键部署到 **ruan.etodo.top**。

## 📁 部署相关文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `deploy.sh` | 自动部署脚本 | ⭐ 主要部署入口 |
| `DEPLOY_QUICK_START.md` | 快速部署指南 | 5分钟快速上手 |
| `DEPLOYMENT.md` | 完整部署文档 | 详细步骤和运维指南 |
| `.deployment-checklist.md` | 部署检查清单 | 确保部署质量 |
| `ecosystem.config.js` | PM2 配置文件 | Node.js 进程管理 |
| `nginx.conf` | Nginx 配置 | Web 服务器配置 |
| `config.js` | 前端环境配置 | API 地址自动切换 |
| `server/.env.production` | 后端生产配置 | 生产环境变量 |

## 🎯 快速开始

### 方式1: 一键部署（推荐）

```bash
# 给脚本执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

### 方式2: 跟随指南部署

查看 [快速部署指南](DEPLOY_QUICK_START.md) - 仅需3步即可完成部署。

### 方式3: 完整手动部署

参考 [完整部署文档](DEPLOYMENT.md) - 包含所有细节和运维命令。

## 📋 部署前准备

### 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **域名**: ruan.etodo.top (需配置 DNS)
- **端口**: 80 (HTTP), 443 (HTTPS), 5001 (API)

### 环境依赖

```bash
Node.js 14+
MongoDB 4.4+
Nginx 1.18+
PM2
```

如未安装，部署脚本会提供安装指引。

## 🔄 部署流程

```
┌─────────────────┐
│  1. 本地准备     │ 配置检查、权限设置
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  2. 打包上传     │ 压缩项目、rsync 传输
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  3. 服务器配置   │ 安装依赖、配置服务
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  4. 启动服务     │ PM2 + Nginx
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. 验证测试     │ 功能测试、日志检查
└─────────────────┘
```

## 🌐 环境配置说明

### 前端配置 (config.js)

系统会自动检测运行环境：

- **开发环境** (localhost): 使用 `http://localhost:5001/api`
- **生产环境** (ruan.etodo.top): 使用 `http://ruan.etodo.top/api`

无需手动修改，自动切换！

### 后端配置 (server/.env.production)

```env
MONGODB_URI=mongodb://localhost:27017/medical_evaluation
PORT=5001
NODE_ENV=production
```

## 📊 部署后访问

部署成功后，可访问：

| 页面 | 地址 |
|------|------|
| 🏠 主页 | http://ruan.etodo.top |
| 📝 评测系统 | http://ruan.etodo.top/model_evaluation_chat.html |
| ⚙️ 管理后台 | http://ruan.etodo.top/admin.html |
| 🔧 API 接口 | http://ruan.etodo.top/api |

## 🛠️ 常用运维命令

### 查看服务状态

```bash
ssh root@ruan.etodo.top 'pm2 status'
```

### 查看日志

```bash
ssh root@ruan.etodo.top 'pm2 logs medical-evaluation-api'
```

### 重启服务

```bash
ssh root@ruan.etodo.top 'pm2 restart medical-evaluation-api'
```

### 更新部署

```bash
./deploy.sh  # 重新运行部署脚本
```

## 🔒 安全建议

1. **配置 HTTPS**
   ```bash
   ssh root@ruan.etodo.top
   certbot --nginx -d ruan.etodo.top
   ```

2. **启用 MongoDB 认证**
3. **配置防火墙规则**
4. **定期备份数据库**

详见 [完整部署文档](DEPLOYMENT.md) 的安全章节。

## ❓ 故障排查

遇到问题？查看：

1. **部署失败**: 查看 deploy.sh 输出信息
2. **API 错误**: 检查 PM2 日志
3. **页面无法访问**: 检查 Nginx 配置和日志
4. **数据库问题**: 验证 MongoDB 状态

详细排查步骤见 [完整部署文档](DEPLOYMENT.md#故障排查)。

## 📚 文档索引

- 📖 [快速部署指南](DEPLOY_QUICK_START.md) - 新手友好，5分钟上手
- 📖 [完整部署文档](DEPLOYMENT.md) - 详细配置和运维
- ✅ [部署检查清单](.deployment-checklist.md) - 质量保证
- 🔧 [后端配置文档](README_BACKEND.md) - API 文档

## 🤝 获取帮助

如果遇到部署问题：

1. 检查部署检查清单
2. 查看故障排查章节
3. 查看服务器日志
4. 联系技术支持

---

**准备好了吗？开始部署吧！** 👉 `./deploy.sh`

