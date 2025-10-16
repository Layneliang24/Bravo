#!/bin/bash
# SSL证书申请和配置脚本
# 使用Let's Encrypt Certbot自动申请SSL证书

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}   SSL证书配置脚本${NC}"
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
    WWW_DOMAIN=""  # 暂不申请www，因为没有DNS记录
    EMAIL="2227208441@qq.com"  # 请替换为真实邮箱
    HTTP_PORT=80
    HTTPS_PORT=443
    echo -e "${GREEN}配置生产环境SSL证书: ${DOMAIN}${NC}"
elif [ "$ENVIRONMENT" = "dev" ]; then
    DOMAIN="dev.layneliang.com"
    WWW_DOMAIN=""
    EMAIL="2227208441@qq.com"  # 请替换为真实邮箱
    HTTP_PORT=8080
    HTTPS_PORT=8443
    echo -e "${GREEN}配置开发环境SSL证书: ${DOMAIN}${NC}"
else
    echo -e "${RED}错误: 无效的环境参数 '$ENVIRONMENT'${NC}"
    echo "使用方法: $0 [prod|dev]"
    exit 1
fi

# 检查是否安装了certbot
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Certbot未安装，正在安装...${NC}"

    # 检测系统类型
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        OS=$(uname -s)
    fi

    case $OS in
        ubuntu|debian)
            apt-get update
            apt-get install -y certbot
            ;;
        centos|rhel|almalinux)
            yum install -y epel-release
            yum install -y certbot
            ;;
        *)
            echo -e "${RED}不支持的操作系统: $OS${NC}"
            echo "请手动安装certbot: https://certbot.eff.org/"
            exit 1
            ;;
    esac

    echo -e "${GREEN}Certbot安装完成${NC}"
fi

# 创建certbot工作目录
mkdir -p /var/www/certbot
mkdir -p /etc/letsencrypt/live
chmod 755 /var/www/certbot

# 检查80端口是否被占用（生产环境）或8080端口（开发环境）
if [ "$ENVIRONMENT" = "prod" ]; then
    CHECK_PORT=80
else
    CHECK_PORT=8080
fi

if lsof -Pi :$CHECK_PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}警告: 端口 $CHECK_PORT 已被占用${NC}"
    echo -e "${YELLOW}如果这是nginx容器，请先停止容器以完成证书申请${NC}"
    read -p "是否继续? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 申请证书
echo -e "${GREEN}开始申请SSL证书...${NC}"
echo -e "${YELLOW}注意: 确保域名 $DOMAIN 已正确解析到此服务器IP${NC}"
echo -e "${YELLOW}请将 EMAIL 变量替换为您的真实邮箱地址${NC}"

if [ -z "$WWW_DOMAIN" ]; then
    # 开发环境，只申请单个域名
    certbot certonly \
        --standalone \
        --preferred-challenges http \
        --http-01-port $CHECK_PORT \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
else
    # 生产环境，申请主域名和www子域名
    certbot certonly \
        --standalone \
        --preferred-challenges http \
        --http-01-port $CHECK_PORT \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
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

    # 检查是否已有cron任务
    CRON_CMD="0 3 * * * certbot renew --quiet --post-hook 'docker restart \$(docker ps -q -f name=frontend)'"
    if ! crontab -l 2>/dev/null | grep -q "certbot renew"; then
        (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -
        echo -e "${GREEN}✓ 已添加自动续期cron任务（每天凌晨3点检查）${NC}"
    else
        echo -e "${YELLOW}自动续期cron任务已存在${NC}"
    fi

    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}   SSL证书配置完成！${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo "1. 确保Nginx配置文件使用了正确的证书路径"
    echo "2. 重启Docker容器: docker-compose restart frontend"
    echo "3. 访问 https://$DOMAIN 验证"
    echo ""
    echo -e "${YELLOW}证书有效期: 90天${NC}"
    echo -e "${YELLOW}自动续期: 已配置（每天检查）${NC}"

else
    echo -e "${RED}✗ SSL证书申请失败${NC}"
    echo -e "${YELLOW}常见问题排查:${NC}"
    echo "1. 检查域名DNS解析是否正确指向此服务器"
    echo "2. 检查防火墙是否开放了 $CHECK_PORT 端口"
    echo "3. 检查 $CHECK_PORT 端口是否被其他服务占用"
    echo "4. 查看详细错误日志: /var/log/letsencrypt/letsencrypt.log"
    exit 1
fi
