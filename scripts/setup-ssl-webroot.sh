#!/bin/bash
# SSL证书申请脚本 - 使用webroot模式（不需要停止web服务）
# 使用方法：sudo bash setup-ssl-webroot.sh [prod|dev]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   SSL证书配置脚本 (Webroot模式)${NC}"
echo -e "${GREEN}======================================${NC}"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用root权限运行此脚本${NC}"
    echo "使用方法: sudo $0 [环境]"
    exit 1
fi

# 检查参数
ENVIRONMENT=${1:-"prod"}

if [ "$ENVIRONMENT" = "prod" ]; then
    DOMAIN="layneliang.com"
    WWW_DOMAIN="www.layneliang.com"
    EMAIL="2227208441@qq.com"
    WEBROOT="/var/www/html"
    echo -e "${GREEN}配置生产环境SSL证书: ${DOMAIN}${NC}"
elif [ "$ENVIRONMENT" = "dev" ]; then
    DOMAIN="dev.layneliang.com"
    WWW_DOMAIN=""
    EMAIL="2227208441@qq.com"
    WEBROOT="/var/www/html"
    echo -e "${GREEN}配置开发环境SSL证书: ${DOMAIN}${NC}"
else
    echo -e "${RED}错误: 无效的环境参数 '$ENVIRONMENT'${NC}"
    echo "使用方法: $0 [prod|dev]"
    exit 1
fi

# 创建webroot目录
echo -e "${GREEN}创建webroot目录...${NC}"
mkdir -p $WEBROOT/.well-known/acme-challenge
chmod 755 $WEBROOT/.well-known
chmod 755 $WEBROOT/.well-known/acme-challenge

# 检查certbot
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Certbot未安装，正在安装...${NC}"
    yum install -y epel-release
    yum install -y certbot
    echo -e "${GREEN}Certbot安装完成${NC}"
fi

# 创建临时nginx配置（如果需要）
echo -e "${GREEN}准备临时HTTP服务...${NC}"

# 检查nginx是否运行
if systemctl is-active --quiet nginx 2>/dev/null; then
    NGINX_RUNNING=true
    echo -e "${GREEN}Nginx正在运行，将使用现有服务${NC}"
else
    NGINX_RUNNING=false
    # 创建临时nginx配置
    cat > /etc/nginx/conf.d/acme-challenge.conf << 'EOF'
server {
    listen 80;
    server_name layneliang.com www.layneliang.com dev.layneliang.com;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
        allow all;
    }

    location / {
        return 404;
    }
}
EOF
    echo -e "${GREEN}创建临时nginx配置${NC}"
    systemctl start nginx || nginx
fi

# 申请证书
echo -e "${GREEN}开始申请SSL证书...${NC}"
echo -e "${YELLOW}使用webroot模式，不会中断现有服务${NC}"

if [ -z "$WWW_DOMAIN" ]; then
    # 开发环境，只申请单个域名
    certbot certonly \
        --webroot \
        -w $WEBROOT \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --force-renewal \
        -d "$DOMAIN"
else
    # 生产环境，申请主域名和www子域名
    certbot certonly \
        --webroot \
        -w $WEBROOT \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        --force-renewal \
        -d "$DOMAIN" \
        -d "$WWW_DOMAIN"
fi

# 检查证书是否申请成功
if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo -e "${GREEN}✓ SSL证书申请成功！${NC}"
    echo -e "${GREEN}证书位置: /etc/letsencrypt/live/$DOMAIN/${NC}"

    # 显示证书信息
    echo ""
    echo -e "${GREEN}证书详情:${NC}"
    openssl x509 -in "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" -text -noout | grep -E "(Subject:|Issuer:|Not Before|Not After)"

    # 设置自动续期
    echo ""
    echo -e "${GREEN}配置自动续期...${NC}"
    CRON_CMD="0 3 * * * certbot renew --quiet --post-hook 'docker restart \$(docker ps -q -f name=frontend)'"
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo -e "${GREEN}✓ 已添加自动续期cron任务${NC}"
    else
        echo -e "${YELLOW}自动续期cron任务已存在${NC}"
    fi

    # 清理临时配置
    if [ "$NGINX_RUNNING" = false ]; then
        rm -f /etc/nginx/conf.d/acme-challenge.conf
        systemctl stop nginx || true
    fi

    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}   SSL证书配置完成！${NC}"
    echo -e "${GREEN}======================================${NC}"

else
    echo -e "${RED}✗ SSL证书申请失败${NC}"
    echo -e "${YELLOW}请查看日志: /var/log/letsencrypt/letsencrypt.log${NC}"
    exit 1
fi
