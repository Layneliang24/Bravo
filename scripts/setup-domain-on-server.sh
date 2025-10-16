#!/bin/bash
# 服务器端域名和SSL配置自动化脚本
# 使用方法：在服务器上执行此脚本

set -e

echo "======================================="
echo "   域名和SSL配置自动化脚本"
echo "======================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查是否为root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用root权限运行${NC}"
    echo "使用方法: sudo bash setup-domain-on-server.sh"
    exit 1
fi

# 项目路径（自动检测或手动指定）
DEV_PROJECT="/home/layne/project/bravo-dev"
PROD_PROJECT="/home/layne/project/bravo-prod"

# 选择一个存在的项目目录来获取脚本
if [ -d "$DEV_PROJECT" ]; then
    PROJECT_DIR="$DEV_PROJECT"
    echo -e "${GREEN}使用开发环境目录: $PROJECT_DIR${NC}"
elif [ -d "$PROD_PROJECT" ]; then
    PROJECT_DIR="$PROD_PROJECT"
    echo -e "${GREEN}使用生产环境目录: $PROJECT_DIR${NC}"
else
    echo -e "${RED}错误: 找不到项目目录${NC}"
    echo "请确保以下目录之一存在："
    echo "  - $DEV_PROJECT"
    echo "  - $PROD_PROJECT"
    exit 1
fi

# 1. 进入项目目录
echo -e "${GREEN}[1/6] 进入项目目录...${NC}"
cd "$PROJECT_DIR" || { echo -e "${RED}错误: 无法进入项目目录${NC}"; exit 1; }
pwd

# 2. 拉取最新代码
echo -e "${GREEN}[2/6] 拉取最新代码...${NC}"
git fetch origin
git pull origin dev 2>/dev/null || git pull origin main 2>/dev/null || echo "代码已是最新"

# 3. 停止容器
echo -e "${GREEN}[3/6] 停止前端容器...${NC}"
docker stop bravo-prod-frontend 2>/dev/null || echo "生产环境前端容器未运行"
docker stop bravo-dev-frontend 2>/dev/null || echo "开发环境前端容器未运行"

# 4. 申请生产环境SSL证书
echo -e "${GREEN}[4/6] 申请生产环境SSL证书 (layneliang.com)...${NC}"
if [ ! -d "/etc/letsencrypt/live/layneliang.com" ]; then
    bash scripts/setup-ssl.sh prod
else
    echo -e "${YELLOW}生产环境证书已存在，跳过申请${NC}"
    ls -la /etc/letsencrypt/live/layneliang.com/
fi

# 5. 申请开发环境SSL证书
echo -e "${GREEN}[5/6] 申请开发环境SSL证书 (dev.layneliang.com)...${NC}"
if [ ! -d "/etc/letsencrypt/live/dev.layneliang.com" ]; then
    bash scripts/setup-ssl.sh dev
else
    echo -e "${YELLOW}开发环境证书已存在，跳过申请${NC}"
    ls -la /etc/letsencrypt/live/dev.layneliang.com/
fi

# 6. 验证证书
echo -e "${GREEN}[6/6] 验证证书状态...${NC}"
echo ""
echo "生产环境证书："
certbot certificates | grep "layneliang.com" -A 5 || echo "未找到证书"
echo ""
echo "开发环境证书："
certbot certificates | grep "dev.layneliang.com" -A 5 || echo "未找到证书"

echo ""
echo -e "${GREEN}=======================================${NC}"
echo -e "${GREEN}   SSL证书配置完成！${NC}"
echo -e "${GREEN}=======================================${NC}"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "1. 在本地推送代码触发自动部署"
echo "2. 访问 https://layneliang.com 验证（生产环境）"
echo "3. 访问 https://dev.layneliang.com:8443 验证（开发环境）"
