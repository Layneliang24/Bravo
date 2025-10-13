# Docker Compose 配置指南

## 📁 文件结构

Bravo项目的Docker配置经过优化，提供清晰、模块化的容器编排方案。

### 核心配置文件（4个）

| 文件                                | 用途               | 使用场景       |
| ----------------------------------- | ------------------ | -------------- |
| `docker-compose.yml`                | 基础开发环境       | 日常开发       |
| `docker-compose.test.yml`           | 测试环境           | CI/CD测试      |
| `docker-compose.production.yml`     | 生产环境           | 生产部署       |
| `docker-compose.github-actions.yml` | GitHub Actions仿真 | 本地工作流调试 |

### 可选增强配置（2个）

| 文件                            | 用途       | 包含服务                                   |
| ------------------------------- | ---------- | ------------------------------------------ |
| `docker-compose.monitoring.yml` | 监控和日志 | Prometheus, Grafana, Elasticsearch, Kibana |
| `docker-compose.tools.yml`      | 开发工具   | Mailhog, MinIO, Nginx                      |

### 环境配置文件

| 文件                                | 用途                 |
| ----------------------------------- | -------------------- |
| `docker/env/env.production.example` | 生产环境配置示例     |
| `docker/env/env.local-prod.example` | 本地生产测试配置示例 |

---

## 🚀 使用方式

### 1. 基础开发环境

最简单的开发环境，包含核心服务：MySQL, Redis, Backend, Frontend, Celery。

```bash
# 启动
docker-compose up

# 后台运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

**包含服务**：

- MySQL (端口 3307)
- Redis (端口 6379)
- Backend (端口 8000)
- Frontend (端口 3000)
- Celery Worker
- Celery Beat
- E2E测试
- Validator（本地测试通行证）

---

### 2. 开发 + 监控

需要性能监控和日志分析时使用。

```bash
# 启动开发环境 + 监控工具
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# 访问监控面板
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3003 (admin/admin123)
# Kibana: http://localhost:5601
```

**额外服务**：

- Prometheus - 指标收集
- Grafana - 可视化面板
- Elasticsearch - 日志存储
- Kibana - 日志分析

---

### 3. 开发 + 工具

需要邮件测试、对象存储等辅助工具时使用。

```bash
# 启动开发环境 + 开发工具
docker-compose -f docker-compose.yml -f docker-compose.tools.yml up -d

# 访问工具面板
# Mailhog: http://localhost:8025
# MinIO Console: http://localhost:9001 (minioadmin/minioadmin123)
```

**额外服务**：

- Mailhog - 邮件测试
- MinIO - 对象存储（S3兼容）
- Nginx - 反向代理

---

### 4. 完整开发环境

启动所有服务（开发 + 监控 + 工具）。

```bash
docker-compose \
  -f docker-compose.yml \
  -f docker-compose.monitoring.yml \
  -f docker-compose.tools.yml \
  up -d
```

⚠️ **注意**：完整环境需要较多资源，建议至少8GB内存。

---

### 5. 测试环境

用于运行自动化测试，优化了性能和启动速度。

```bash
# 启动测试环境
docker-compose -f docker-compose.test.yml up

# 运行后端测试
docker-compose -f docker-compose.test.yml run backend-test

# 运行前端测试
docker-compose -f docker-compose.test.yml run frontend-test

# 清理测试环境
docker-compose -f docker-compose.test.yml down -v
```

**特点**：

- MySQL使用tmpfs（内存存储）加速测试
- 独立的测试数据库
- 优化的healthcheck配置

---

### 6. 生产环境

用于生产部署或本地生产环境测试。

#### 生产部署

```bash
# 1. 创建环境配置
cp docker/env/env.production.example .env.production
# 编辑 .env.production，填入实际配置

# 2. 启动生产环境
docker-compose --env-file .env.production -f docker-compose.production.yml up -d

# 3. 查看状态
docker-compose -f docker-compose.production.yml ps

# 4. 查看日志
docker-compose -f docker-compose.production.yml logs -f
```

#### 本地生产测试

```bash
# 1. 创建本地测试配置
cp docker/env/env.local-prod.example .env.local-prod

# 2. 启动本地生产测试
docker-compose --env-file .env.local-prod -f docker-compose.production.yml up -d
```

---

### 7. GitHub Actions本地仿真

使用act工具本地运行GitHub Actions工作流。

```bash
# 启动GitHub Actions仿真环境
docker-compose -f docker-compose.github-actions.yml up -d

# 进入runner容器
docker-compose -f docker-compose.github-actions.yml exec github-actions-runner bash

# 运行act命令
act pull_request
```

---

## 🔧 常用命令

### 服务管理

```bash
# 启动特定服务
docker-compose up mysql redis

# 重启服务
docker-compose restart backend

# 停止服务（保留数据）
docker-compose stop

# 停止并删除容器（保留数据卷）
docker-compose down

# 停止并删除所有（包括数据卷）
docker-compose down -v
```

### 日志和调试

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend

# 实时跟踪日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash
docker-compose exec mysql mysql -u root -p
```

### 数据管理

```bash
# 备份MySQL数据
docker-compose exec mysql mysqldump -u root -p bravo_local > backup.sql

# 恢复MySQL数据
docker-compose exec -T mysql mysql -u root -p bravo_local < backup.sql

# 清理未使用的数据卷
docker volume prune
```

---

## 📊 端口映射

### 开发环境端口

| 服务     | 端口 | 说明                          |
| -------- | ---- | ----------------------------- |
| MySQL    | 3307 | 数据库（避免与本地MySQL冲突） |
| Redis    | 6379 | 缓存                          |
| Backend  | 8000 | Django API                    |
| Frontend | 3000 | Vue应用                       |
| E2E      | 9323 | Playwright UI                 |

### 监控工具端口

| 服务          | 端口 | 说明       |
| ------------- | ---- | ---------- |
| Prometheus    | 9090 | 指标收集   |
| Grafana       | 3003 | 可视化面板 |
| Elasticsearch | 9200 | 日志存储   |
| Kibana        | 5601 | 日志分析   |

### 开发工具端口

| 服务          | 端口   | 说明        |
| ------------- | ------ | ----------- |
| Mailhog SMTP  | 1025   | 邮件发送    |
| Mailhog Web   | 8025   | 邮件查看    |
| MinIO API     | 9000   | 对象存储API |
| MinIO Console | 9001   | 管理控制台  |
| Nginx         | 80/443 | 反向代理    |

---

## 🎯 最佳实践

### 1. 日常开发

```bash
# 大多数情况下，只需要基础环境
docker-compose up -d

# 需要监控时
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

### 2. 性能优化

```bash
# 只启动需要的服务
docker-compose up mysql redis backend

# 清理未使用的资源
docker system prune -a
```

### 3. 问题排查

```bash
# 1. 查看服务状态
docker-compose ps

# 2. 查看日志
docker-compose logs -f [service_name]

# 3. 进入容器调试
docker-compose exec [service_name] bash

# 4. 重建服务
docker-compose up -d --build [service_name]
```

### 4. 数据持久化

所有重要数据都存储在Docker volumes中，即使删除容器也不会丢失：

```bash
# 列出所有volumes
docker volume ls

# 查看volume详情
docker volume inspect bravo_mysql_data
```

---

## 🆘 故障排除

### 问题1: 端口冲突

```bash
# 修改端口映射
# 编辑 docker-compose.yml
ports:
  - "3308:3306"  # 将3307改为其他端口
```

### 问题2: 内存不足

```bash
# 减少服务数量
docker-compose up mysql redis backend frontend

# 或限制容器内存
# 在 docker-compose.yml 中添加
deploy:
  resources:
    limits:
      memory: 512M
```

### 问题3: 数据库连接失败

```bash
# 1. 确认MySQL健康状态
docker-compose ps mysql

# 2. 查看MySQL日志
docker-compose logs mysql

# 3. 手动连接测试
docker-compose exec mysql mysql -u bravo_user -p
```

---

## 📚 相关文档

- [Docker官方文档](https://docs.docker.com/)
- [Docker Compose文档](https://docs.docker.com/compose/)
- [Bravo项目开发规范](../README.md)

---

## 🔄 版本历史

### v2.0 (2025-10-13)

- ✅ 优化文件结构（7个→4个核心+2个可选）
- ✅ 提取监控工具到独立配置
- ✅ 提取开发工具到独立配置
- ✅ 添加环境变量配置示例
- ✅ 改进文档说明

### v1.0

- 初始版本，包含7个配置文件
