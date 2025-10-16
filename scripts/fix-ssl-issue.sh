#!/bin/bash
# SSL证书申请问题修复脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "======================================="
echo "   SSL证书问题排查和修复"
echo "======================================="
echo ""

# 检查80端口占用情况
echo -e "${GREEN}[1/5] 检查80端口占用情况...${NC}"
netstat -tlnp | grep ':80 ' || echo "80端口未被占用"

# 检查443端口占用情况
echo -e "${GREEN}[2/5] 检查443端口占用情况...${NC}"
netstat -tlnp | grep ':443 ' || echo "443端口未被占用"

# 检查nginx状态
echo -e "${GREEN}[3/5] 检查nginx状态...${NC}"
systemctl status nginx || echo "nginx未作为系统服务运行"

# 检查Docker容器
echo -e "${GREEN}[4/5] 检查Docker容器...${NC}"
docker ps | grep -E "80|443|nginx|frontend" || echo "无相关容器运行"

# 解决方案
echo ""
echo -e "${GREEN}[5/5] 建议的解决方案:${NC}"
echo ""
echo "选项1：临时停止占用80端口的服务"
echo "  sudo systemctl stop nginx"
echo "  或"
echo "  docker stop \$(docker ps -q)"
echo ""
echo "选项2：使用webroot方式申请证书（推荐）"
echo "  修改setup-ssl.sh使用--webroot模式"
echo ""
echo "选项3：使用DNS验证方式"
echo "  需要API密钥，适合阿里云域名"
