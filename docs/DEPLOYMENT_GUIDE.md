# Bravo项目部署指南

## 📋 目录

- [服务器要求](#服务器要求)
- [手动部署](#手动部署)
- [自动部署CICD](#自动部署cicd)
- [常见问题](#常见问题)

---

## 服务器要求

### 最低配置

- **CPU**: 2核
- **内存**: 2GB（推荐4GB）
- **磁盘**: 20GB可用空间
- **系统**: Ubuntu 20.04+ / CentOS 7+
- **软件**: Docker 20.10+, Docker Compose 2.0+

### 当前服务器配置

- **IP**: 8.129.16.190
- **系统**: CentOS 7
- **内存**: 1.7GB
- **Docker**: v26.1.4 ✅
- **Docker Compose**: v2.39.2 ✅

---

## 手动部署

### 1. 首次部署

```bash
# SSH连接服务器
ssh root@8.129.16.190

# 进入项目目录
cd /home/layne/project/bravo

# 克隆代码（如果目录为空）
git clone https://github.com/Layneliang24/Bravo.git .

# 或拉取最新代码
git pull origin main

# 运行部署脚本
bash scripts/deploy-server.sh
```

### 2. 更新部署

```bash
# SSH连接服务器
ssh root@8.129.16.190

# 进入项目目录
cd /home/layne/project/bravo

# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build

# 执行数据库迁移
docker exec bravo-backend-prod python manage.py migrate
```

---

## 自动部署（CICD）

### GitHub Actions配置

#### 1. 生成SSH密钥

```bash
# 在本地生成SSH密钥对
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/bravo-deploy

# 将公钥添加到服务器
ssh-copy-id -i ~/.ssh/bravo-deploy.pub root@8.129.16.190

# 复制私钥内容（用于GitHub Secrets）
cat ~/.ssh/bravo-deploy
```

#### 2. 配置GitHub Secrets

在GitHub仓库设置中添加以下Secrets：

| Secret名称       | 值             | 说明      |
| ---------------- | -------------- | --------- |
| `ALIYUN_HOST`    | `8.129.16.190` | 服务器IP  |
| `ALIYUN_USER`    | `root`         | SSH用户名 |
| `ALIYUN_SSH_KEY` | `私钥内容`     | SSH私钥   |

#### 3. 触发自动部署

**方式1：推送代码**

```bash
# 推送到main分支自动部署到生产环境
git push origin main

# 推送到dev分支自动部署到开发环境
git push origin dev
```

**方式2：手动触发**

- 进入GitHub仓库 → Actions → 选择工作流 → Run workflow

---

## 内存优化配置

由于服务器内存为1.7GB，已进行以下优化：

### MySQL优化

```yaml
--max_connections=50           # 限制连接数
--innodb_buffer_pool_size=128M # 减少缓冲池
--performance_schema=OFF       # 关闭性能监控
```

### Redis优化

```yaml
--maxmemory 100mb             # 限制最大内存
--maxmemory-policy allkeys-lru # LRU淘汰策略
```

### Docker资源限制

```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 400M
```

---

## 常用命令

### 服务管理

```bash
# 查看运行状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 重启服务
docker-compose -f docker-compose.prod.yml restart

# 停止服务
docker-compose -f docker-compose.prod.yml stop

# 完全停止并删除
docker-compose -f docker-compose.prod.yml down
```

### Django管理

```bash
# 进入后端容器
docker exec -it bravo-backend-prod bash

# 执行迁移
docker exec bravo-backend-prod python manage.py migrate

# 创建超级用户
docker exec -it bravo-backend-prod python manage.py createsuperuser

# 收集静态文件
docker exec bravo-backend-prod python manage.py collectstatic --noinput
```

### 数据库管理

```bash
# 进入MySQL
docker exec -it bravo-mysql-prod mysql -u bravo -p

# 备份数据库
docker exec bravo-mysql-prod mysqldump -u root -p bravo_production > backup.sql

# 恢复数据库
docker exec -i bravo-mysql-prod mysql -u root -p bravo_production < backup.sql
```

---

## 常见问题

### 1. 内存不足导致容器重启

**症状**：`docker ps` 看到容器不断重启

**解决**：

```bash
# 查看系统内存
free -h

# 停止不需要的服务
docker stop alpha_frontend_prod alpha_backend_prod

# 减少Celery worker并发
# 在docker-compose中设置: --concurrency=1
```

### 2. 端口冲突

**症状**：端口已被占用

**解决**：

```bash
# 查看端口占用
netstat -tuln | grep :80
netstat -tuln | grep :8000

# 停止占用端口的服务
docker stop <container_id>
```

### 3. MySQL启动失败

**症状**：数据库连接错误

**解决**：

```bash
# 查看MySQL日志
docker logs bravo-mysql-prod

# 可能需要清理数据重新初始化
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

### 4. 静态文件404

**解决**：

```bash
# 重新收集静态文件
docker exec bravo-backend-prod python manage.py collectstatic --noinput

# 重启nginx
docker-compose -f docker-compose.prod.yml restart frontend
```

---

## 监控和维护

### 资源监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
df -h

# 清理Docker资源
docker system prune -a
```

### 日志管理

```bash
# 日志文件位置
# Backend: docker logs bravo-backend-prod
# Frontend: docker logs bravo-frontend-prod
# MySQL: docker logs bravo-mysql-prod

# 清理旧日志
docker-compose -f docker-compose.prod.yml logs --tail=100
```

---

## 升级建议

当前内存1.7GB偏小，建议：

1. **短期方案**：使用外部数据库服务

   - 阿里云RDS MySQL（最小规格）
   - 阿里云Redis

2. **长期方案**：升级服务器到4GB内存
   - 可以完整运行所有服务
   - 性能更稳定

---

## 安全建议

1. **修改默认密码**

   ```bash
   # 编辑 .env.production
   vim .env.production
   ```

2. **配置防火墙**

   ```bash
   # 只开放必要端口
   firewall-cmd --permanent --add-port=80/tcp
   firewall-cmd --permanent --add-port=443/tcp
   firewall-cmd --reload
   ```

3. **定期备份数据库**
   ```bash
   # 添加到crontab
   0 2 * * * docker exec bravo-mysql-prod mysqldump -u root -p bravo_production > /backup/bravo_$(date +\%Y\%m\%d).sql
   ```

---

**部署完成后访问**：

- 前端：http://8.129.16.190
- 后端API：http://8.129.16.190:8000
- 健康检查：http://8.129.16.190/health
