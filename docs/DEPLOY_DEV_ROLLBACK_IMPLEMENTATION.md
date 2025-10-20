# Dev环境自动回滚机制实现

## 📋 问题背景

### 修复前的问题

`deploy-dev.yml`工作流中包含一个名为"Test Rollback Mechanism with Intentional Failure"的步骤，但这**不是真正的回滚机制**，只是一个模拟测试：

**假的回滚测试做了什么**：

1. 检查一个不存在的URL（模拟失败）
2. 重启服务（不是真正的回滚）
3. 验证服务是否恢复

**问题**：

- ❌ 没有保存备份镜像
- ❌ 没有真正的健康检查
- ❌ 部署失败时不会自动回滚
- ❌ 只是重启服务，不是恢复到上一个版本

### 生产环境的对比

`deploy-production.yml`拥有完整的自动回滚机制：

- ✅ 部署前备份当前镜像
- ✅ 完整的健康检查函数
- ✅ 失败时自动使用备份镜像回滚
- ✅ 回滚后再次验证健康状态
- ✅ 记录部署历史

---

## 🎯 实现的回滚机制

### 1. 部署前备份（Deploy Step）

```bash
# 在部署新版本前备份当前镜像
echo "📦 备份当前镜像作为回滚点..."
if docker images | grep -q bravo-dev-backend; then
  docker tag bravo-dev-backend:latest bravo-dev-backend-backup:latest
fi
if docker images | grep -q bravo-dev-frontend; then
  docker tag bravo-dev-frontend:latest bravo-dev-frontend-backup:latest
fi

# 记录部署信息
echo "DEPLOYED_AT=$(date '+%Y-%m-%d %H:%M:%S')" > .deployment-current
echo "GITHUB_SHA=${{ github.sha }}" >> .deployment-current
echo "GITHUB_RUN_ID=${{ github.run_id }}" >> .deployment-current
```

### 2. 健康检查函数（Health Check Step）

```bash
check_health() {
  local retry=0
  local max_retry=3

  while [ $retry -lt $max_retry ]; do
    # 检查容器状态
    if ! docker ps | grep -q bravo-dev-backend; then
      echo "❌ Backend容器未运行"
      retry=$((retry+1))
      sleep 10
      continue
    fi

    if ! docker ps | grep -q bravo-dev-frontend; then
      echo "❌ Frontend容器未运行"
      retry=$((retry+1))
      sleep 10
      continue
    fi

    # 检查前端（dev环境使用端口8080）
    FRONTEND_STATUS=$(curl -L -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
    if [ "$FRONTEND_STATUS" != "200" ]; then
      retry=$((retry+1))
      sleep 10
      continue
    fi

    # 检查后端API（dev环境使用端口8001）
    BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/)
    if [ "$BACKEND_STATUS" != "200" ]; then
      retry=$((retry+1))
      sleep 10
      continue
    fi

    # 所有检查通过
    echo "✅ 健康检查通过"
    return 0
  done

  echo "❌ 健康检查失败（重试${max_retry}次）"
  return 1
}
```

### 3. 自动回滚流程

```bash
if check_health; then
  echo "🎉 Dev环境部署成功！"

  # 更新dev-stable标签
  docker tag backend:dev backend:dev-stable
  docker tag frontend:dev frontend:dev-stable
  docker push backend:dev-stable
  docker push frontend:dev-stable

  # 记录成功部署
  echo "[$(date)] Dev部署成功" >> .deployment-history
  exit 0
else
  echo "🚨 健康检查失败，开始自动回滚..."

  # 检查是否有备份
  if ! docker images | grep -q bravo-dev-backend-backup; then
    echo "❌ 没有可回滚的备份镜像"
    exit 1
  fi

  # 停止失败的容器
  COMPOSE_PROJECT_NAME=bravo-dev docker-compose -f docker-compose.prod.yml down

  # 使用备份镜像回滚
  docker tag bravo-dev-backend-backup:latest backend:dev
  docker tag bravo-dev-frontend-backup:latest frontend:dev

  # 重新启动服务（使用备份版本）
  COMPOSE_PROJECT_NAME=bravo-dev docker-compose -f docker-compose.prod.yml up -d

  # 等待服务就绪
  sleep 15

  # 重新配置Nginx SSL
  docker cp frontend/nginx.domain-dev.conf bravo-dev-frontend:/etc/nginx/conf.d/default.conf
  docker exec bravo-dev-frontend nginx -t && nginx -s reload

  # 验证回滚后的服务
  if check_health; then
    echo "✅ 回滚成功！服务已恢复到上一个稳定版本"
    echo "[$(date)] Dev部署失败 - 已自动回滚成功" >> .deployment-history
    exit 1  # 返回失败状态
  else
    echo "❌ 回滚后健康检查仍然失败"
    exit 1
  fi
fi
```

---

## 📊 回滚机制对比

| 特性       | 修复前                       | 修复后                           |
| ---------- | ---------------------------- | -------------------------------- |
| 备份机制   | ❌ 无                        | ✅ 部署前自动备份                |
| 健康检查   | ❌ 假检查（检查不存在的URL） | ✅ 真实检查（容器+前端+后端API） |
| 自动回滚   | ❌ 只是重启服务              | ✅ 使用备份镜像回滚              |
| 重试机制   | ❌ 无                        | ✅ 3次重试机会                   |
| 回滚验证   | ❌ 无                        | ✅ 回滚后再次健康检查            |
| 部署历史   | ❌ 无                        | ✅ 记录到.deployment-history     |
| Stable标签 | ❌ 无                        | ✅ 成功后更新dev-stable标签      |
| 端口适配   | ❌ 硬编码                    | ✅ 使用Dev环境端口(8080/8001)    |

---

## 🔄 工作流程

### 正常部署流程

```
1. 备份当前镜像 → backup标签
2. 部署新版本 → 拉取镜像 → 启动容器
3. 健康检查 → 3次重试
4. ✅ 成功 → 更新dev-stable标签 → 推送到镜像仓库
5. 记录部署历史
```

### 失败回滚流程

```
1. 备份当前镜像 → backup标签
2. 部署新版本 → 拉取镜像 → 启动容器
3. 健康检查 → 3次重试 → ❌ 失败
4. 停止失败的容器
5. 使用backup镜像回滚
6. 重新启动服务（旧版本）
7. 重新健康检查
8. ✅ 回滚成功 → 服务恢复
9. 记录回滚历史
```

---

## 🎯 与生产环境的一致性

现在Dev环境和Production环境的回滚机制保持一致，区别仅在于：

| 项目       | Dev环境            | Production环境 |
| ---------- | ------------------ | -------------- |
| 端口       | 8080/8001/8443     | 80/8000/443    |
| 域名       | dev.layneliang.com | layneliang.com |
| 重试次数   | 3次                | 5次            |
| Stable标签 | dev-stable         | prod-stable    |
| 项目名     | bravo-dev          | bravo-prod     |

---

## ✅ 修复验证

### 验证步骤

1. ✅ 删除假的"Test Rollback Mechanism"步骤
2. ✅ 添加真正的"Health Check with Auto Rollback"步骤
3. ✅ 实现部署前备份机制
4. ✅ 实现健康检查函数（容器+前端+后端）
5. ✅ 实现自动回滚逻辑
6. ✅ 实现回滚后验证
7. ✅ 添加部署历史记录
8. ✅ 添加dev-stable标签管理

### 预期行为

- **部署成功**：健康检查通过 → 更新stable标签 → 记录历史
- **部署失败**：健康检查失败 → 自动回滚 → 验证恢复 → 记录历史
- **首次部署失败**：没有备份 → 记录失败 → 需要手动介入

---

## 📝 文档更新

- [x] 创建 `DEPLOY_DEV_ROLLBACK_IMPLEMENTATION.md`
- [ ] 更新 `README.md` 中的部署说明
- [ ] 更新 `DEPLOYMENT_ROLLBACK_IMPLEMENTATION.md`（如果需要）

---

## 🔍 后续建议

1. **监控告警**：集成Slack/钉钉告警，部署失败时立即通知
2. **版本管理**：使用Git commit SHA作为镜像标签，更精确的版本控制
3. **回滚测试**：定期测试回滚机制是否正常工作
4. **多版本保留**：保留最近3个stable版本，支持回滚到更早版本

---

## 📅 修复时间

- **发现时间**: 2025-10-20
- **修复分支**: `fix/deploy-dev-rollback-mechanism`
- **负责人**: Claude Sonnet 4.5
