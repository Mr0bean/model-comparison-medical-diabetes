# 快速部署指南

## 5分钟快速部署到 ruan.etodo.top

### 前置条件

确保服务器已安装：
- ✅ Node.js 14+
- ✅ MongoDB 4.4+
- ✅ Nginx 1.18+
- ✅ PM2

如未安装，执行：

```bash
# 一键安装脚本
ssh root@ruan.etodo.top << 'EOF'
# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 安装 MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list
apt-get update && apt-get install -y mongodb-org

# 安装 Nginx 和 PM2
apt-get install -y nginx
npm install -g pm2

# 启动服务
systemctl start mongod nginx
systemctl enable mongod nginx

echo "✅ 环境安装完成！"
EOF
```

### 一键部署

```bash
# 1. 确保 deploy.sh 有执行权限
chmod +x deploy.sh

# 2. 运行部署脚本
./deploy.sh
```

脚本会自动：
1. 📦 打包前后端文件
2. 📤 上传到服务器
3. ⚙️  安装依赖
4. 🚀 启动服务
5. 🌐 配置 Nginx

### 手动部署（3步）

如果自动脚本失败，手动执行：

```bash
# 步骤 1: 上传文件
rsync -avz --exclude 'node_modules' --exclude '.git' \
  . root@ruan.etodo.top:/var/www/medical-evaluation/

# 步骤 2: 配置服务器
ssh root@ruan.etodo.top << 'EOF'
cd /var/www/medical-evaluation

# 安装后端依赖
cd server && npm install --production && cd ..

# 启动后端
pm2 start ecosystem.config.js --env production
pm2 save

# 配置 Nginx
cp nginx.conf /etc/nginx/sites-available/medical-evaluation
ln -sf /etc/nginx/sites-available/medical-evaluation /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
EOF

# 步骤 3: 访问网站
# 打开浏览器: http://ruan.etodo.top
```

### 验证部署

```bash
# 检查后端服务
ssh root@ruan.etodo.top 'pm2 status'

# 测试 API
curl http://ruan.etodo.top/api/admin/stats

# 测试前端
curl -I http://ruan.etodo.top
```

### 配置 HTTPS（可选但推荐）

```bash
ssh root@ruan.etodo.top << 'EOF'
# 安装 Certbot
apt-get install -y certbot python3-certbot-nginx

# 获取证书并自动配置
certbot --nginx -d ruan.etodo.top --non-interactive --agree-tos -m your@email.com

echo "✅ HTTPS 配置完成！"
EOF
```

### 常见问题

**Q: 端口 5001 被占用？**
```bash
# 查找占用进程
lsof -i :5001
# 修改端口（server/.env 和 nginx.conf）
```

**Q: MongoDB 连接失败？**
```bash
# 检查 MongoDB 状态
systemctl status mongod
# 查看日志
tail -f /var/log/mongodb/mongod.log
```

**Q: Nginx 403 错误？**
```bash
# 修复权限
chown -R www-data:www-data /var/www/medical-evaluation
chmod -R 755 /var/www/medical-evaluation
```

**Q: 前端无法连接 API？**
- 检查 `config.js` 中的域名配置
- 确保 Nginx 反向代理配置正确
- 查看浏览器控制台 CORS 错误

### 更新部署

```bash
# 快速更新
./deploy.sh

# 或仅更新后端
ssh root@ruan.etodo.top 'cd /var/www/medical-evaluation/server && npm install && pm2 restart medical-evaluation-api'
```

### 访问地址

- 🏠 主页: http://ruan.etodo.top
- 📝 评测系统: http://ruan.etodo.top/model_evaluation_chat.html
- ⚙️ 管理后台: http://ruan.etodo.top/admin.html

### 下一步

- 📖 完整文档: 查看 [DEPLOYMENT.md](DEPLOYMENT.md)
- 🔒 配置 HTTPS 证书
- 📊 设置监控和告警
- 💾 配置数据库备份

---

**部署完成后，记得更新 DNS 记录指向服务器 IP！**
