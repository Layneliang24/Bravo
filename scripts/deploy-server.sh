#!/bin/bash
# Bravo项目服务器部署脚本
# 使用方式: bash scripts/deploy-server.sh

set -e

echo "🚀 开始部署Bravo项目到生产环境..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查是否在项目根目录
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ 错误: 请在项目根目录执行此脚本${NC}"
    exit 1
fi

# 1. 停止并清理旧容器
echo -e "${YELLOW}📦 停止旧容器...${NC}"
docker-compose -f docker-compose.prod.yml down || true

# 2. 清理alpha项目容器（如果存在）
echo -e "${YELLOW}🧹 清理alpha项目...${NC}"
docker stop alpha_frontend_prod alpha_backend_prod alpha_mysql_prod 2>/dev/null || true
docker rm alpha_frontend_prod alpha_backend_prod alpha_mysql_prod 2>/dev/null || true

# 3. 创建环境变量文件（如果不存在）
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}📝 创建环境变量文件...${NC}"
    cat > .env.production << 'EOF'
# 数据库配置
DB_ROOT_PASSWORD=bravo_root_2024_change_me
DB_NAME=bravo_production
DB_USER=bravo
DB_PASSWORD=bravo_pass_2024_change_me

# Django配置
DJANGO_SECRET_KEY=your-secret-key-here-change-me
ALLOWED_HOSTS=*

# 其他配置
TZ=Asia/Shanghai
EOF
    echo -e "${GREEN}✅ 已创建 .env.production，请修改其中的密码！${NC}"
fi

# 4. 构建镜像
echo -e "${YELLOW}🔨 构建Docker镜像...${NC}"
docker-compose -f docker-compose.prod.yml build --no-cache

# 5. 启动服务
echo -e "${YELLOW}🚀 启动服务...${NC}"
docker-compose -f docker-compose.prod.yml up -d

# 6. 等待服务就绪
echo -e "${YELLOW}⏳ 等待服务启动...${NC}"
sleep 15

# 7. 检查服务状态
echo -e "${YELLOW}🔍 检查服务状态...${NC}"
docker-compose -f docker-compose.prod.yml ps

# 8. 执行数据库迁移
echo -e "${YELLOW}📊 执行数据库迁移...${NC}"
docker exec bravo-backend-prod python manage.py migrate --noinput || echo "迁移可能已执行"

# 9. 创建超级用户（交互式）
echo -e "${YELLOW}👤 是否创建Django超级用户？(y/n)${NC}"
read -r create_superuser
if [ "$create_superuser" = "y" ]; then
    docker exec -it bravo-backend-prod python manage.py createsuperuser
fi

# 10. 清理无用镜像
echo -e "${YELLOW}🧹 清理无用镜像...${NC}"
docker image prune -f

# 11. 显示访问信息
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "📍 访问地址："
echo -e "   前端: ${GREEN}http://$(hostname -I | awk '{print $1}')${NC}"
echo -e "   后端API: ${GREEN}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo ""
echo -e "📊 查看日志："
echo -e "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "🔧 管理命令："
echo -e "   停止: docker-compose -f docker-compose.prod.yml stop"
echo -e "   启动: docker-compose -f docker-compose.prod.yml start"
echo -e "   重启: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo -e "${YELLOW}⚠️  记得修改 .env.production 中的密码！${NC}"
