# 🚀 Bravo项目生产环境部署指南

## 📋 部署前准备

### 1. 服务器要求

- **操作系统**: Ubuntu 20.04+ 或 CentOS 7+
- **内存**: 最低 2GB，推荐 4GB+
- **硬盘**: 最低 20GB，推荐 50GB+
- **CPU**: 最低 1核，推荐 2核+
- **网络**: 公网IP，开放端口 22, 80, 443, 3306, 6379, 8000

### 2. 必需的访问权限

- SSH root 或 sudo 访问权限
- 服务器防火墙配置权限
- 域名解析权限（如果使用域名）

## 🔧 服务器环境设置

### 方法1: 使用自动部署脚本（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/Layneliang24/Bravo.git
cd Bravo

# 2. 配置环境变量
cp .env.production .env
# 编辑 .env 文件，修改密码和配置

# 3. 执行部署
./scripts/deploy.sh
```

### 方法2: 手动部署

#### 步骤1: 连接服务器

```bash
ssh root@8.129.16.190
```

#### 步骤2: 安装Docker和Docker Compose

```bash
# 更新系统
apt-get update
apt-get upgrade -y

# 安装必需工具
apt-get install -y curl wget git

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 启动Docker
systemctl start docker
systemctl enable docker

# 安装Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### 步骤3: 部署项目

```bash
# 创建项目目录
mkdir -p /opt/bravo
cd /opt/bravo

# 克隆代码
git clone -b main https://github.com/Layneliang24/Bravo.git .

# 配置环境变量
cp .env.production .env
nano .env  # 修改配置

# 启动服务
docker-compose -f docker-compose.production.yml up -d

# 等待服务启动（约2-3分钟）
sleep 180

# 执行数据库迁移
docker-compose -f docker-compose.production.yml exec backend python manage.py migrate

# 收集静态文件
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput

# 创建管理员用户
docker-compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```

## ⚙️ 关键配置说明

### 1. 环境变量配置 (.env)

```bash
# 数据库配置
DB_NAME=bravo_production
DB_USER=bravo
DB_PASSWORD=your_secure_password_here
DB_ROOT_PASSWORD=your_root_password_here

# Django配置
DJANGO_SECRET_KEY=your_very_secret_key_here
DEBUG=False

# 服务器配置
ALLOWED_HOSTS=8.129.16.190,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://8.129.16.190,https://yourdomain.com

# 邮件配置（可选）
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

### 2. 防火墙配置

```bash
# Ubuntu/Debian
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw enable

# CentOS/RHEL
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --permanent --add-port=8000/tcp
firewall-cmd --reload
```

### 3. SSL证书配置（推荐）

```bash
# 安装Certbot
apt-get install -y certbot

# 获取SSL证书（需要域名）
certbot certonly --standalone -d yourdomain.com

# 配置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

## 🔍 部署验证

### 1. 服务状态检查

```bash
# 检查所有服务状态
docker-compose -f docker-compose.production.yml ps

# 检查服务日志
docker-compose -f docker-compose.production.yml logs
```

### 2. 功能测试

- **前端**: http://8.129.16.190
- **后端API**: http://8.129.16.190:8000/api/
- **管理后台**: http://8.129.16.190:8000/admin/
- **健康检查**: http://8.129.16.190:8000/health/

### 3. 性能测试

```bash
# 安装测试工具
apt-get install -y apache2-utils

# 并发测试
ab -n 1000 -c 10 http://8.129.16.190/
ab -n 1000 -c 10 http://8.129.16.190:8000/api/
```

## 📊 CI/CD自动部署

### GitHub Secrets配置

在GitHub项目设置中添加以下Secrets:

| Secret名称          | 描述           | 示例值                               |
| ------------------- | -------------- | ------------------------------------ |
| `SSH_PRIVATE_KEY`   | SSH私钥        | `-----BEGIN RSA PRIVATE KEY-----...` |
| `SERVER_IP`         | 服务器IP       | `8.129.16.190`                       |
| `SSH_USER`          | SSH用户        | `root`                               |
| `PROJECT_PATH`      | 项目路径       | `/opt/bravo`                         |
| `DB_PASSWORD`       | 数据库密码     | `secure_password_123`                |
| `DB_ROOT_PASSWORD`  | 数据库root密码 | `root_password_123`                  |
| `DJANGO_SECRET_KEY` | Django密钥     | `your-secret-key-here`               |

### 自动部署触发

- **推送到main分支** → 自动部署
- **手动触发** → GitHub Actions页面手动运行

## 🛠️ 运维管理

### 常用命令

```bash
# 查看服务状态
docker-compose -f docker-compose.production.yml ps

# 查看日志
docker-compose -f docker-compose.production.yml logs -f

# 重启服务
docker-compose -f docker-compose.production.yml restart

# 更新代码
git pull origin main
docker-compose -f docker-compose.production.yml restart

# 备份数据库
docker-compose -f docker-compose.production.yml exec mysql mysqldump -u root -p bravo_production > backup.sql

# 还原数据库
docker-compose -f docker-compose.production.yml exec -T mysql mysql -u root -p bravo_production < backup.sql
```

### 监控和日志

```bash
# 系统资源监控
htop
df -h
free -h

# Docker资源使用
docker stats

# 应用日志位置
/var/lib/docker/volumes/bravo_django_logs/_data/
```

### 定期维护

```bash
# 清理Docker垃圾
docker system prune -f

# 更新系统
apt-get update && apt-get upgrade -y

# 重启服务器（可选）
reboot
```

## ⚠️ 安全建议

1. **定期更新密码**
2. **使用SSH密钥而非密码登录**
3. **启用防火墙**
4. **定期备份数据库**
5. **监控系统日志**
6. **使用HTTPS（SSL证书）**

## 🆘 故障排除

### 常见问题

#### 1. 服务无法启动

```bash
# 检查端口占用
netstat -tlnp | grep :80
netstat -tlnp | grep :8000

# 检查Docker服务
systemctl status docker

# 重启Docker服务
systemctl restart docker
```

#### 2. 数据库连接失败

```bash
# 检查MySQL容器
docker-compose -f docker-compose.production.yml logs mysql

# 重启数据库
docker-compose -f docker-compose.production.yml restart mysql
```

#### 3. 前端资源404

```bash
# 重新收集静态文件
docker-compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput

# 重启前端容器
docker-compose -f docker-compose.production.yml restart frontend
```

#### 4. 内存不足

```bash
# 检查内存使用
free -h
docker stats

# 增加swap空间
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

## 📞 技术支持

如遇到部署问题，请提供以下信息：

1. 服务器系统版本
2. 错误日志
3. 服务状态输出
4. 网络配置情况

---

**祝部署顺利！🎉**
