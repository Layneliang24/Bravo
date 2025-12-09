# 🚀 服务器初始化指南

本指南帮助你在Ubuntu 22.04服务器上初始化Bravo项目的运行环境。

## 📋 前置条件

- ✅ Ubuntu 22.04 LTS 服务器
- ✅ Root权限访问
- ✅ 网络连接（用于下载依赖）

## 🎯 快速开始

### 方法1: 使用初始化脚本（推荐）

```bash
# 1. 下载或克隆项目到服务器
cd /home/layne/project
git clone <your-repo-url> bravo
cd bravo

# 2. 运行初始化脚本（需要root权限）
sudo bash scripts/init-server.sh
```

脚本会自动完成以下操作：

- ✅ 更新系统包
- ✅ 安装基础工具（curl, git, vim等）
- ✅ 安装Docker和Docker Compose
- ✅ 配置Docker镜像加速（国内服务器）
- ✅ 配置时区为Asia/Shanghai
- ✅ 配置防火墙规则
- ✅ 创建项目目录结构
- ✅ 优化系统配置

### 方法2: 手动初始化

如果脚本执行失败，可以手动执行以下步骤：

#### 步骤1: 更新系统

```bash
apt-get update
apt-get upgrade -y
```

#### 步骤2: 安装基础工具

```bash
apt-get install -y curl wget git vim htop net-tools ufw
```

#### 步骤3: 安装Docker

```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 启动Docker服务
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
```

#### 步骤4: 安装Docker Compose

```bash
# Docker Compose Plugin（推荐）
apt-get install -y docker-compose-plugin

# 或安装独立版本
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
    -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 验证安装
docker compose version
```

#### 步骤5: 配置Docker镜像加速

```bash
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com",
    "https://registry.docker-cn.com"
  ]
}
EOF

systemctl daemon-reload
systemctl restart docker
```

#### 步骤6: 配置时区

```bash
timedatectl set-timezone Asia/Shanghai
```

#### 步骤7: 配置防火墙

```bash
# 启用UFW
ufw --force enable

# 允许必要端口
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # Django Backend

# 查看状态
ufw status
```

#### 步骤8: 创建项目目录

```bash
# 创建目录
mkdir -p /home/layne/project/bravo

# 设置权限
chown -R layne:layne /home/layne/project

# 将用户添加到docker组
usermod -aG docker layne
```

## ✅ 验证安装

执行以下命令验证所有组件是否正确安装：

```bash
# 检查Docker
docker --version
docker compose version

# 检查Docker服务状态
systemctl status docker

# 测试Docker
docker run --rm hello-world

# 检查时区
timedatectl

# 检查防火墙
ufw status
```

## 📦 后续步骤

初始化完成后，按照以下步骤部署项目：

### 1. 切换到项目用户

```bash
su - layne
cd /home/layne/project/bravo
```

### 2. 克隆项目代码（如果尚未克隆）

```bash
git clone <your-repo-url> .
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp docker/env/env.production.example .env.production

# 编辑环境变量（修改密码和配置）
nano .env.production
```

**重要配置项：**

- `DB_ROOT_PASSWORD`: MySQL root密码
- `DB_PASSWORD`: MySQL用户密码
- `DJANGO_SECRET_KEY`: Django密钥（必须修改！）
- `ALLOWED_HOSTS`: 允许访问的域名/IP

### 4. 启动服务

```bash
# 使用生产环境配置启动
docker compose -f docker-compose.prod.yml up -d
```

### 5. 查看服务状态

```bash
# 查看所有服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f backend
```

### 6. 执行数据库迁移

```bash
# 等待MySQL启动（约30秒）
sleep 30

# 执行迁移
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# 创建超级用户
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

### 7. 收集静态文件

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

## 🔧 常见问题

### Q1: Docker命令需要sudo权限

**解决方案：**

```bash
# 将用户添加到docker组
usermod -aG docker layne

# 重新登录或执行
newgrp docker
```

### Q2: Docker镜像下载慢

**解决方案：**

- 脚本已自动配置国内镜像加速
- 如果仍然慢，检查 `/etc/docker/daemon.json` 配置
- 重启Docker服务：`systemctl restart docker`

### Q3: 防火墙阻止访问

**解决方案：**

```bash
# 检查防火墙状态
ufw status

# 开放端口
ufw allow <port>/tcp

# 如果使用云服务器，还需要在云控制台配置安全组
```

### Q4: 时区不正确

**解决方案：**

```bash
# 设置时区
timedatectl set-timezone Asia/Shanghai

# 验证
timedatectl
```

### Q5: 磁盘空间不足

**解决方案：**

```bash
# 清理Docker未使用的资源
docker system prune -a

# 查看磁盘使用
df -h
```

## 📊 系统要求

### 最低配置

- CPU: 2核
- 内存: 4GB
- 磁盘: 20GB

### 推荐配置

- CPU: 4核
- 内存: 8GB
- 磁盘: 50GB（用于Docker镜像和数据卷）

## 🔒 安全建议

1. **修改默认密码**

   - 修改数据库密码
   - 修改Django SECRET_KEY
   - 使用强密码

2. **防火墙配置**

   - 只开放必要端口
   - 生产环境建议关闭MySQL和Redis外部访问

3. **定期更新**

   ```bash
   apt-get update && apt-get upgrade -y
   ```

4. **备份数据**
   - 定期备份数据库
   - 备份重要配置文件

## 📝 相关文档

- [部署指南](./DEPLOYMENT.md)
- [Docker Compose指南](./DOCKER_COMPOSE_GUIDE.md)
- [环境变量配置](./ENV_CONFIG.md)

## 🆘 获取帮助

如果遇到问题：

1. 查看日志：`docker compose -f docker-compose.prod.yml logs`
2. 检查服务状态：`docker compose -f docker-compose.prod.yml ps`
3. 查看项目文档：`docs/` 目录
4. 提交Issue到项目仓库
