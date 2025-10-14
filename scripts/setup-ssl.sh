#!/bin/bash
# SSL证书配置脚本 - 使用Let's Encrypt

set -e

echo "🔐 SSL证书配置向导"
echo "=================="
echo ""

# 检查域名
read -p "请输入你的域名（例如：bravo.example.com）: " DOMAIN
if [ -z "$DOMAIN" ]; then
    echo "❌ 域名不能为空！"
    exit 1
fi

read -p "请输入你的邮箱（用于Let's Encrypt通知）: " EMAIL
if [ -z "$EMAIL" ]; then
    echo "❌ 邮箱不能为空！"
    exit 1
fi

echo ""
echo "📋 配置摘要："
echo "  域名: $DOMAIN"
echo "  邮箱: $EMAIL"
echo ""
read -p "确认继续？(y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

echo ""
echo "📦 步骤1：安装Certbot..."
if ! command -v certbot &> /dev/null; then
    echo "安装Certbot..."
    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y certbot
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y certbot
    else
        echo "❌ 不支持的系统，请手动安装certbot"
        exit 1
    fi
else
    echo "✅ Certbot已安装"
fi

echo ""
echo "📦 步骤2：停止Nginx容器..."
docker-compose -f docker-compose.prod-optimized.yml stop frontend

echo ""
echo "📜 步骤3：申请SSL证书..."
sudo certbot certonly --standalone \
    -d $DOMAIN \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --preferred-challenges http

if [ $? -ne 0 ]; then
    echo "❌ 证书申请失败！请检查："
    echo "  1. 域名DNS是否已正确解析到本服务器"
    echo "  2. 防火墙80端口是否开放"
    echo "  3. 域名拼写是否正确"
    exit 1
fi

echo ""
echo "📁 步骤4：复制证书到项目目录..."
sudo mkdir -p ./ssl
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ./ssl/
sudo chmod 644 ./ssl/fullchain.pem
sudo chmod 600 ./ssl/privkey.pem

echo ""
echo "⚙️  步骤5：更新Nginx配置..."
# 替换nginx配置中的域名占位符
sed -i "s/server_name _;/server_name $DOMAIN;/g" frontend/nginx-ssl.conf

# 更新Docker Compose配置使用SSL版Nginx
cat > docker-compose.prod-optimized.override.yml << EOF
version: "3.8"
services:
  frontend:
    volumes:
      - ./frontend/nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
EOF

echo ""
echo "🚀 步骤6：重启服务..."
docker-compose -f docker-compose.prod-optimized.yml up -d

echo ""
echo "✅ SSL证书配置完成！"
echo ""
echo "📋 访问地址："
echo "  https://$DOMAIN"
echo ""
echo "🔄 证书自动续期："
echo "  Let's Encrypt证书90天有效期"
echo "  添加到crontab自动续期："
echo "  sudo crontab -e"
echo "  添加以下行："
echo "  0 0 1 * * certbot renew --quiet && docker-compose -f $(pwd)/docker-compose.prod-optimized.yml restart frontend"
echo ""
