# 医疗AI评测系统 - 部署文档

## 目标服务器

- **域名**: ruan.etodo.top
- **前端**: Nginx 静态服务
- **后端**: Node.js (PM2 管理)
- **数据库**: MongoDB

## 部署前准备

### 1. 服务器环境要求

```bash
# 系统要求
Ubuntu 20.04+ / CentOS 7+ / Debian 10+

# 需要安装的软件
- Node.js 14+
- MongoDB 4.4+
- Nginx 1.18+
- PM2 (Node.js进程管理器)
```

### 2. 服务器环境安装

```bash
# SSH 登录服务器
ssh root@ruan.etodo.top

# 1. 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 2. 安装 MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org

# 启动 MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 3. 安装 Nginx
sudo apt-get install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# 4. 安装 PM2
sudo npm install -g pm2

# 5. 创建部署目录
sudo mkdir -p /var/www/medical-evaluation
sudo chown -R $USER:$USER /var/www/medical-evaluation
```

## 部署步骤

### 方法1: 使用自动部署脚本（推荐）

```bash
# 在本地项目目录执行
./deploy.sh
```

脚本会自动完成：
1. 打包项目文件
2. 上传到服务器
3. 安装依赖
4. 配置 PM2 和 Nginx
5. 启动服务

### 方法2: 手动部署

#### 1. 上传文件到服务器

```bash
# 方式A: 使用 rsync
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.log' \
  . root@ruan.etodo.top:/var/www/medical-evaluation/

# 方式B: 使用 scp
scp -r . root@ruan.etodo.top:/var/www/medical-evaluation/
```

#### 2. SSH 登录服务器并配置

```bash
ssh root@ruan.etodo.top

cd /var/www/medical-evaluation

# 安装后端依赖
cd server
npm install --production
cd ..

# 启动后端服务
pm2 start ecosystem.config.js --env production
pm2 save
pm2 startup

# 配置 Nginx
sudo cp nginx.conf /etc/nginx/sites-available/medical-evaluation
sudo ln -s /etc/nginx/sites-available/medical-evaluation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 环境配置

### 后端环境变量

编辑 `server/.env` 文件：

```bash
MONGODB_URI=mongodb://localhost:27017/medical_evaluation
PORT=5001
NODE_ENV=production
```

### 前端环境配置

前端会自动检测域名并使用相应的 API 地址：

- 开发环境 (localhost): `http://localhost:5001/api`
- 生产环境 (ruan.etodo.top): `http://ruan.etodo.top/api`

配置文件位于 `config.js`。

## 常用运维命令

### PM2 进程管理

```bash
# 查看进程状态
pm2 status

# 查看日志
pm2 logs medical-evaluation-api

# 重启服务
pm2 restart medical-evaluation-api

# 停止服务
pm2 stop medical-evaluation-api

# 删除进程
pm2 delete medical-evaluation-api

# 监控
pm2 monit
```

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重载配置
sudo systemctl reload nginx

# 重启 Nginx
sudo systemctl restart nginx

# 查看状态
sudo systemctl status nginx

# 查看错误日志
sudo tail -f /var/log/nginx/error.log

# 查看访问日志
sudo tail -f /var/log/nginx/access.log
```

### MongoDB 管理

```bash
# 连接数据库
mongosh medical_evaluation

# 查看集合
show collections

# 查看完成码
db.codes.find().pretty()

# 查看评测数据
db.evaluations.find().pretty()

# 导出数据
mongodump --db medical_evaluation --out /backup/mongodb/

# 导入数据
mongorestore --db medical_evaluation /backup/mongodb/medical_evaluation/
```

## 域名和 SSL 配置

### 配置 SSL 证书（推荐）

```bash
# 安装 certbot
sudo apt-get install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d ruan.etodo.top

# 自动续期
sudo certbot renew --dry-run
```

SSL 配置会自动添加到 Nginx，或者手动取消注释 `nginx.conf` 中的 HTTPS 配置块。

## 监控和日志

### 日志位置

- **后端日志**: `./logs/api-*.log`
- **Nginx 访问日志**: `/var/log/nginx/access.log`
- **Nginx 错误日志**: `/var/log/nginx/error.log`
- **MongoDB 日志**: `/var/log/mongodb/mongod.log`

### 实时监控

```bash
# 监控后端进程
pm2 monit

# 实时查看 API 日志
tail -f logs/api-combined.log

# 实时查看 Nginx 访问
tail -f /var/log/nginx/access.log
```

## 备份策略

### 数据库备份

```bash
# 创建备份脚本
cat > /root/backup-mongodb.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/mongodb"
mkdir -p $BACKUP_DIR
mongodump --db medical_evaluation --out $BACKUP_DIR/backup_$DATE
# 保留最近7天的备份
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
EOF

chmod +x /root/backup-mongodb.sh

# 添加到 crontab (每天凌晨2点备份)
echo "0 2 * * * /root/backup-mongodb.sh" | crontab -
```

## 故障排查

### 后端无法启动

```bash
# 检查端口占用
lsof -i :5001

# 检查 MongoDB 连接
mongosh --eval "db.adminCommand('ping')"

# 查看详细错误
pm2 logs medical-evaluation-api --lines 100
```

### 前端无法访问

```bash
# 检查 Nginx 状态
sudo systemctl status nginx

# 检查配置语法
sudo nginx -t

# 检查文件权限
ls -la /var/www/medical-evaluation/

# 重启 Nginx
sudo systemctl restart nginx
```

### API 请求失败

```bash
# 检查后端是否运行
pm2 status

# 测试 API 连接
curl http://localhost:5001/api/admin/stats

# 检查 CORS 配置
curl -H "Origin: http://ruan.etodo.top" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  http://localhost:5001/api/admin/stats
```

## 性能优化

### Nginx 优化

```nginx
# 在 nginx.conf 中添加
gzip_comp_level 6;
client_max_body_size 10M;
keepalive_timeout 65;
```

### MongoDB 优化

```bash
# 创建索引
mongosh medical_evaluation --eval "
  db.codes.createIndex({ code: 1 }, { unique: true });
  db.evaluations.createIndex({ code: 1, patient: 1, model: 1 });
  db.evaluations.createIndex({ submittedAt: -1 });
"
```

### PM2 集群模式

```javascript
// 修改 ecosystem.config.js
instances: 2  // 改为 2 或 'max'
exec_mode: 'cluster'
```

## 访问地址

部署完成后，可以通过以下地址访问：

- **主页**: http://ruan.etodo.top
- **评测页面**: http://ruan.etodo.top/model_evaluation_chat.html
- **管理后台**: http://ruan.etodo.top/admin.html
- **API 文档**: http://ruan.etodo.top/api/admin/stats

## 更新部署

当有代码更新时：

```bash
# 方式1: 重新运行部署脚本
./deploy.sh

# 方式2: 手动更新
ssh root@ruan.etodo.top "
  cd /var/www/medical-evaluation
  git pull  # 如果使用 git
  cd server && npm install --production
  pm2 restart medical-evaluation-api
"
```

## 安全建议

1. **修改默认端口**: 不要使用 22 端口
2. **配置防火墙**: 只开放 80, 443 端口
3. **MongoDB 认证**: 启用 MongoDB 用户认证
4. **定期备份**: 设置自动备份脚本
5. **监控异常**: 配置告警通知
6. **更新系统**: 定期更新系统和依赖包

## 联系支持

如有问题，请检查：
1. 服务器日志
2. GitHub Issues
3. 部署文档

---

**部署时间**: $(date)
**版本**: v1.0.0
