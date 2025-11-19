#!/bin/bash

# 医疗AI评测系统部署脚本
# 目标服务器: ruan.etodo.top

set -e

echo "🚀 开始部署医疗AI评测系统..."

# 配置变量
SERVER="ruan.etodo.top"
REMOTE_USER="root"  # 根据实际情况修改
REMOTE_PATH="/var/www/medical-evaluation"
PROJECT_NAME="medical-evaluation"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}📦 步骤 1: 打包项目文件${NC}"

# 创建临时部署目录
DEPLOY_DIR="deploy_temp"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# 复制前端文件
echo "  - 复制前端文件..."
cp *.html $DEPLOY_DIR/ 2>/dev/null || true
cp *.js $DEPLOY_DIR/ 2>/dev/null || true
cp -r output $DEPLOY_DIR/ 2>/dev/null || true

# 复制后端文件
echo "  - 复制后端文件..."
mkdir -p $DEPLOY_DIR/server
cp server/package*.json $DEPLOY_DIR/server/
cp server/server.js $DEPLOY_DIR/server/
cp server/.env.production $DEPLOY_DIR/server/.env

# 复制部署配置
cp ecosystem.config.js $DEPLOY_DIR/
cp nginx.conf $DEPLOY_DIR/

echo -e "${GREEN}✅ 文件打包完成${NC}"

echo -e "${YELLOW}📤 步骤 2: 上传文件到服务器${NC}"

# 创建远程目录
ssh $REMOTE_USER@$SERVER "mkdir -p $REMOTE_PATH"

# 上传文件
rsync -avz --progress \
  --exclude 'node_modules' \
  --exclude '.git' \
  --exclude '__pycache__' \
  --exclude '*.log' \
  --exclude '.DS_Store' \
  $DEPLOY_DIR/ $REMOTE_USER@$SERVER:$REMOTE_PATH/

echo -e "${GREEN}✅ 文件上传完成${NC}"

echo -e "${YELLOW}⚙️  步骤 3: 配置服务器环境${NC}"

ssh $REMOTE_USER@$SERVER << 'ENDSSH'
set -e

cd /var/www/medical-evaluation

echo "  - 安装后端依赖..."
cd server
npm install --production
cd ..

echo "  - 配置 PM2..."
# 停止旧进程
pm2 stop medical-evaluation-api 2>/dev/null || true
pm2 delete medical-evaluation-api 2>/dev/null || true

# 启动新进程
pm2 start ecosystem.config.js --env production
pm2 save
pm2 startup

echo "  - 配置 Nginx..."
# 备份旧配置
if [ -f /etc/nginx/sites-available/medical-evaluation ]; then
    cp /etc/nginx/sites-available/medical-evaluation /etc/nginx/sites-available/medical-evaluation.backup.$(date +%Y%m%d_%H%M%S)
fi

# 复制新配置
cp nginx.conf /etc/nginx/sites-available/medical-evaluation

# 启用站点
ln -sf /etc/nginx/sites-available/medical-evaluation /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重载 Nginx
systemctl reload nginx

echo "  - 修复文件权限..."
# 设置正确的所有者和权限
chown -R www-data:www-data /var/www/medical-evaluation
chmod -R 755 /var/www/medical-evaluation
find /var/www/medical-evaluation -type f -name "*.html" -exec chmod 644 {} \;
find /var/www/medical-evaluation -type f -name "*.js" -exec chmod 644 {} \;
find /var/www/medical-evaluation -type f -name "*.css" -exec chmod 644 {} \;

echo "  - 检查 MongoDB..."
systemctl status mongod --no-pager || echo "⚠️  MongoDB 未运行，请手动启动"

ENDSSH

echo -e "${GREEN}✅ 服务器配置完成${NC}"

echo -e "${YELLOW}🧹 步骤 4: 清理临时文件${NC}"
rm -rf $DEPLOY_DIR
echo -e "${GREEN}✅ 清理完成${NC}"

echo ""
echo -e "${GREEN}🎉 部署完成！${NC}"
echo ""
echo "访问地址: http://ruan.etodo.top"
echo "API 地址: http://ruan.etodo.top/api"
echo ""
echo "常用命令:"
echo "  查看后端日志: ssh $REMOTE_USER@$SERVER 'pm2 logs medical-evaluation-api'"
echo "  重启后端: ssh $REMOTE_USER@$SERVER 'pm2 restart medical-evaluation-api'"
echo "  查看状态: ssh $REMOTE_USER@$SERVER 'pm2 status'"
echo ""
