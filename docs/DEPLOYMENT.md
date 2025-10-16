# 🚀 Bravo项目生产环境部署指南

## 🎯 部署架构概览

### 自动化CI/CD流程（v2.0）

Bravo项目采用**完全自动化的镜像推送架构**，实现零人工干预的持续部署：

```
代码提交 → PR验证 → 合并分支 → 自动构建镜像 → 推送到阿里云 → 自动部署
```

**核心优势**：
- ✅ **服务器零构建**：镜像在GitHub Actions中构建，服务器只需拉取
- ✅ **内存占用低**：无需在服务器上编译代码和构建镜像
- ✅ **部署速度快**：拉取预构建镜像比现场构建快5-10倍
- ✅ **环境完全隔离**：dev和prod使用不同镜像tag，互不影响
- ✅ **支持版本回滚**：每个版本都有独立镜像，可快速回滚

### 镜像仓库架构

**阿里云容器镜像服务（杭州）**：
```
registry.cn-hangzhou.aliyuncs.com/bravo-project/
├── backend:dev           # 开发环境最新版
├── backend:dev-<sha>     # 开发环境特定版本
├── backend:latest        # 生产环境最新版
├── backend:<version>     # 生产环境特定版本（如2025.01.15-a1b2c3d4）
├── frontend:dev
├── frontend:dev-<sha>
├── frontend:latest
└── frontend:<version>
```

### 部署触发条件

| 事件 | 触发工作流 | 结果 |
|------|-----------|------|
| PR合并到dev | ✅ 构建dev镜像 → ✅ 部署到dev环境 | dev.layneliang.com更新 |
| PR合并到main | ✅ 构建latest镜像 → ✅ 部署到prod环境 | layneliang.com更新 |

---

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

### 3. 阿里云镜像仓库配置（首次部署必需）

**⚠️ 重要**：新架构需要先配置阿里云容器镜像服务。

**快速配置步骤**：
1. 登录阿里云控制台：https://cr.console.aliyuncs.com/
2. 创建命名空间：`bravo-project`（私有）
3. 创建仓库：`backend` 和 `frontend`（私有）
4. 设置Registry登录密码
5. 配置GitHub Secrets：
   - `ALIYUN_REGISTRY_USERNAME`：你的阿里云账号
   - `ALIYUN_REGISTRY_PASSWORD`：Registry密码

**详细配置文档**：见 [ALIYUN_REGISTRY_SETUP.md](./ALIYUN_REGISTRY_SETUP.md)

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
docker-compose -f docker-compose.prod.yml up -d

# 等待服务启动（约2-3分钟）
sleep 180

# 执行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 收集静态文件
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# 创建管理员用户
docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
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
docker-compose -f docker-compose.prod.yml ps

# 检查服务日志
docker-compose -f docker-compose.prod.yml logs
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
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 更新代码
git pull origin main
docker-compose -f docker-compose.prod.yml restart

# 备份数据库
docker-compose -f docker-compose.prod.yml exec mysql mysqldump -u root -p bravo_production > backup.sql

# 还原数据库
docker-compose -f docker-compose.prod.yml exec -T mysql mysql -u root -p bravo_production < backup.sql
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
docker-compose -f docker-compose.prod.yml logs mysql

# 重启数据库
docker-compose -f docker-compose.prod.yml restart mysql
```

#### 3. 前端资源404

```bash
# 重新收集静态文件
docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput

# 重启前端容器
docker-compose -f docker-compose.prod.yml restart frontend
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

## 🔐 SSL/HTTPS自动化配置（v2.0+）

### 自动化流程说明

从v2.0版本开始，**SSL配置已完全自动化**，无需手动干预：

#### 1. 部署时自动应用

每次部署时，GitHub Actions会自动：

```bash
# ✅ 自动检测nginx.ssl.conf文件
# ✅ 自动复制到容器内
# ✅ 自动测试Nginx配置
# ✅ 自动重载Nginx
# ✅ 自动验证端口监听
```

#### 2. 配置文件

- **文件位置**：`frontend/nginx.ssl.conf`
- **容器路径**：`/etc/nginx/conf.d/ssl.conf`
- **自动化时机**：每次 `docker-compose up -d` 后

#### 3. 支持的环境

| 环境 | 域名               | 端口 | 自动应用 |
| ---- | ------------------ | ---- | -------- |
| Dev  | dev.layneliang.com | 8443 | ✅       |
| Prod | layneliang.com     | 443  | ✅       |

#### 4. 验证自动化

查看部署日志确认：

```
🔧 配置Nginx SSL...
✅ SSL配置已应用
🔍 验证Nginx端口...
tcp  0.0.0.0:443  LISTEN  nginx
```

#### 5. 如果自动化失败

极少情况下可能需要手动应用：

```bash
# Dev环境
cd /home/layne/project/bravo-dev
docker cp frontend/nginx.ssl.conf bravo-dev-frontend:/etc/nginx/conf.d/ssl.conf
docker exec bravo-dev-frontend nginx -s reload

# Prod环境
cd /home/layne/project/bravo-prod
docker cp frontend/nginx.ssl.conf bravo-prod-frontend:/etc/nginx/conf.d/ssl.conf
docker exec bravo-prod-frontend nginx -s reload
```

### Django域名配置

**ALLOWED_HOSTS**已包含所有域名，无需手动配置：

- ✅ `layneliang.com`（生产）
- ✅ `www.layneliang.com`
- ✅ `dev.layneliang.com`（开发）
- ✅ `8.129.16.190`（IP访问）

---

## 📞 技术支持

如遇到部署问题，请提供以下信息：

1. 服务器系统版本
2. 错误日志
3. 服务状态输出
4. 网络配置情况

---

**祝部署顺利！🎉**
