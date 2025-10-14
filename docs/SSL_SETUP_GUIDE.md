# 🔐 HTTPS/SSL配置完整指南

## 概述

本指南介绍如何为Bravo项目配置HTTPS，包括使用Let's Encrypt免费证书和自签名证书两种方案。

---

## 📋 前置要求

### 方案A：Let's Encrypt（推荐）

**优点**：

- ✅ 完全免费
- ✅ 自动续期
- ✅ 浏览器信任

**要求**：

1. **域名**（必需）

   - 购买域名（如：`bravo.example.com`）
   - 配置DNS A记录指向服务器IP：`8.129.16.190`

2. **端口开放**

   - 80端口（HTTP，用于证书验证）
   - 443端口（HTTPS）

3. **服务器要求**
   - 公网可访问
   - 能够运行certbot

### 方案B：自签名证书（开发/测试）

**优点**：

- ✅ 无需域名
- ✅ 立即可用

**缺点**：

- ❌ 浏览器会警告"不安全"
- ❌ 需要手动信任证书

---

## 🚀 方案A：Let's Encrypt配置（推荐）

### 步骤1：准备域名

1. **购买域名**

   - 推荐：阿里云、腾讯云、Cloudflare
   - 价格：约50-100元/年

2. **配置DNS解析**

   ```
   类型: A记录
   主机记录: @ 或 www
   记录值: 8.129.16.190
   TTL: 10分钟
   ```

3. **验证DNS生效**

   ```bash
   # Windows
   nslookup bravo.example.com

   # Linux/Mac
   dig bravo.example.com
   ```

### 步骤2：在服务器上运行配置脚本

```bash
# SSH登录到服务器
ssh root@8.129.16.190

# 进入项目目录
cd /home/layne/project/bravo

# 下载最新代码（如果使用了自动化脚本）
git pull origin dev

# 给脚本执行权限
chmod +x scripts/setup-ssl.sh

# 运行SSL配置脚本
./scripts/setup-ssl.sh
```

**按提示输入**：

- 域名：`bravo.example.com`
- 邮箱：`your-email@example.com`

脚本会自动完成：

1. 安装certbot
2. 申请SSL证书
3. 配置Nginx
4. 重启服务

### 步骤3：更新Django配置

编辑 `backend/bravo/settings/production.py`：

```python
# 更新允许的主机
ALLOWED_HOSTS = [
    "bravo.example.com",  # 你的域名
    "www.bravo.example.com",  # 可选
    "8.129.16.190",  # 保留IP访问
]

# 更新CSRF信任源
CSRF_TRUSTED_ORIGINS = [
    "https://bravo.example.com",
    "https://www.bravo.example.com",
]
```

### 步骤4：配置自动续期

Let's Encrypt证书有效期90天，需要自动续期：

```bash
# 编辑crontab
sudo crontab -e

# 添加自动续期任务（每月1号凌晨执行）
0 0 1 * * certbot renew --quiet && docker-compose -f /home/layne/project/bravo/docker-compose.prod-optimized.yml restart frontend
```

### 步骤5：验证HTTPS

```bash
# 测试HTTPS访问
curl -I https://bravo.example.com

# 检查证书有效期
echo | openssl s_client -servername bravo.example.com -connect bravo.example.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 🔧 方案B：自签名证书（开发/测试）

### 步骤1：生成自签名证书

```bash
# SSH登录服务器
ssh root@8.129.16.190
cd /home/layne/project/bravo

# 创建SSL目录
mkdir -p ssl

# 生成私钥和证书（有效期365天）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/privkey.pem \
  -out ssl/fullchain.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Bravo/CN=8.129.16.190"

# 设置权限
chmod 600 ssl/privkey.pem
chmod 644 ssl/fullchain.pem
```

### 步骤2：更新Docker Compose

创建 `docker-compose.prod-optimized.override.yml`：

```yaml
version: "3.8"
services:
  frontend:
    volumes:
      - ./frontend/nginx-ssl.conf:/etc/nginx/conf.d/default.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
```

### 步骤3：更新Nginx配置

```bash
# 复制SSL配置
cp frontend/nginx-ssl.conf frontend/nginx.conf

# 重启服务
docker-compose -f docker-compose.prod-optimized.yml restart frontend
```

### 步骤4：信任自签名证书

**浏览器访问时**：

1. 访问 `https://8.129.16.190`
2. 点击"高级" → "继续访问"
3. 或在Chrome中输入：`thisisunsafe`

**永久信任**：

- Windows：双击证书 → 安装到"受信任的根证书颁发机构"
- Mac：钥匙串访问 → 导入证书 → 设置为"始终信任"

---

## 🔍 故障排查

### 问题1：证书申请失败

**可能原因**：

1. DNS未生效（等待10-30分钟）
2. 80端口未开放
3. 域名拼写错误

**解决方案**：

```bash
# 检查80端口
sudo netstat -tlnp | grep :80

# 检查DNS
nslookup your-domain.com

# 手动申请（查看详细错误）
sudo certbot certonly --standalone -d your-domain.com --email your-email@example.com
```

### 问题2：HTTPS重定向循环

**原因**：Nginx未正确传递X-Forwarded-Proto头

**解决方案**：
检查 `frontend/nginx-ssl.conf` 中：

```nginx
proxy_set_header X-Forwarded-Proto https;  # 必须是https而非$scheme
```

### 问题3：混合内容警告

**原因**：HTTPS页面加载HTTP资源

**解决方案**：
确保所有资源使用相对路径或HTTPS绝对路径。

---

## 📊 性能优化

### 启用HTTP/2

Nginx配置已包含：

```nginx
listen 443 ssl http2;
```

### 启用OCSP Stapling

添加到 `frontend/nginx-ssl.conf`：

```nginx
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/nginx/ssl/fullchain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
```

### 配置SSL会话复用

已包含：

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

---

## 🔄 证书更新流程

### 自动更新（推荐）

已配置crontab自动更新。

### 手动更新

```bash
# 更新证书
sudo certbot renew

# 重启Nginx
docker-compose -f docker-compose.prod-optimized.yml restart frontend

# 验证新证书
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 📚 相关资源

- [Let's Encrypt官网](https://letsencrypt.org/)
- [Certbot文档](https://certbot.eff.org/)
- [Mozilla SSL配置生成器](https://ssl-config.mozilla.org/)
- [SSL Labs测试工具](https://www.ssllabs.com/ssltest/)

---

## ⚠️ 临时方案：禁用HTTPS重定向

如果暂时不配置SSL，可以禁用HTTPS重定向：

在 `docker-compose.prod-optimized.yml` 的backend服务中添加：

```yaml
environment:
  - DISABLE_SSL_REDIRECT=True
```

**注意**：生产环境强烈建议配置HTTPS！
