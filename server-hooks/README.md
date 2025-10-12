# 🛡️ 服务器端 Git 钩子部署指南

## 📋 概述

本目录包含**服务器端 Git 钩子**，用于在 Git 服务器上运行检查，防止绕过本地钩子。

### 🎯 关键区别

#### 本地钩子 vs 服务器端钩子

```
┌─────────────────────────────────────────────────────────┐
│ 本地钩子（由 Husky 管理）                              │
├─────────────────────────────────────────────────────────┤
│ 位置: .husky/ 目录                                     │
│ 触发: 本地 Git 操作（commit, push 等）                │
│ 管理: npm run prepare (Husky)                         │
│ 可绕过: ✗ 是（可用 --no-verify 绕过）                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ 服务器端钩子（本目录）                                 │
├─────────────────────────────────────────────────────────┤
│ 位置: 服务器的仓库 hooks/ 目录                        │
│ 触发: 服务器接收推送时                                │
│ 管理: 手动部署到服务器                                │
│ 可绕过: ✓ 否（无法绕过，服务器强制执行）              │
└─────────────────────────────────────────────────────────┘
```

### 🔒 防御层次

```
第一层: 本地 pre-commit (.husky/pre-commit)
  ↓ 开发者可能绕过 (--no-verify)

第二层: 本地 pre-push (.husky/pre-push)
  ↓ 开发者可能绕过 (--no-verify)

第三层: GitHub Actions (PR/Push 工作流)
  ↓ 可能被分支规则绕过

第四层: 服务器端 pre-receive (本目录) ⭐
  ✓ 无法绕过，最后防线
```

## 📁 钩子列表

### `pre-receive`

**用途**: 服务器接收推送前的最后检查
**检查项目**:

1. ✅ 分支保护（禁止直接推送到 main/dev）
2. ✅ 提交消息格式验证
3. ✅ 禁止的文件检查（密钥、环境变量等）
4. ✅ 大文件检查（>10MB）
5. ✅ 代码质量标记（合并冲突、调试代码）
6. ✅ Docker 依赖管理规范
7. ✅ 本地测试通行证验证（警告）

**特点**:

- 🚀 快速失败：任何检查失败立即终止
- 🔒 无法绕过：服务器强制执行
- 📊 详细日志：提供清晰的错误信息

## 🚀 部署指南

### 前提条件

- 拥有 Git 服务器的访问权限
- 支持自定义钩子的 Git 服务器（Gitea/GitLab/GitHub Enterprise/裸仓库）

### 部署步骤

#### 方案 1: Gitea/Gogs 部署

```bash
# 1. SSH 到服务器
ssh user@your-git-server.com

# 2. 找到仓库位置（通常在 /data/gitea/repositories/）
cd /data/gitea/repositories/your-org/your-repo.git

# 3. 复制钩子文件
cp /path/to/server-hooks/pre-receive hooks/pre-receive

# 4. 设置执行权限
chmod +x hooks/pre-receive

# 5. 测试钩子
./hooks/pre-receive --version  # 如果有版本命令的话
```

#### 方案 2: GitLab 部署

```bash
# 1. SSH 到 GitLab 服务器
ssh user@gitlab-server.com

# 2. 找到仓库位置（通常在 /var/opt/gitlab/git-data/repositories/）
cd /var/opt/gitlab/git-data/repositories/<namespace>/<project>.git

# 3. 复制钩子到 custom_hooks 目录
mkdir -p custom_hooks
cp /path/to/server-hooks/pre-receive custom_hooks/pre-receive

# 4. 设置执行权限
chmod +x custom_hooks/pre-receive

# 5. 重启 GitLab（如需要）
sudo gitlab-ctl restart
```

#### 方案 3: GitHub Enterprise 部署

```bash
# 使用 GitHub Enterprise 管理控制台
# 导航到: Repository Settings > Hooks
# 上传 pre-receive 钩子脚本
```

#### 方案 4: 裸仓库部署

```bash
# 1. 找到裸仓库位置
cd /path/to/bare/repo.git

# 2. 复制钩子
cp /path/to/server-hooks/pre-receive hooks/pre-receive

# 3. 设置执行权限
chmod +x hooks/pre-receive
```

### 🧪 测试部署

```bash
# 在本地测试推送
git push origin feature/test-branch

# 预期结果：
# - 如果推送到 main/dev → 被拒绝
# - 如果包含敏感文件 → 被拒绝
# - 如果包含大文件 → 被拒绝
# - 如果推送到 feature 分支 → 成功
```

## 🔧 配置

### 修改保护的分支

编辑 `pre-receive` 文件的第 12 行：

```bash
# 默认
PROTECTED_BRANCHES="main dev"

# 自定义
PROTECTED_BRANCHES="main develop production"
```

### 修改大文件限制

编辑 `pre-receive` 文件的第 181 行：

```bash
# 默认: 10MB
local max_size=$((10 * 1024 * 1024))

# 自定义: 5MB
local max_size=$((5 * 1024 * 1024))
```

### 禁用特定检查

注释掉不需要的检查函数调用（第 326-331 行）：

```bash
# 执行所有检查（快速失败）
check_branch_protection "$branch"
check_forbidden_files "$oldrev" "$newrev"
# check_large_files "$oldrev" "$newrev"  # 禁用大文件检查
check_code_quality_markers "$oldrev" "$newrev"
check_docker_dependency_rules "$oldrev" "$newrev"
# check_local_test_passport  # 禁用通行证检查
```

## 🛠️ 维护

### 更新钩子

```bash
# 1. 在本地更新 server-hooks/pre-receive
vim server-hooks/pre-receive

# 2. 提交到仓库
git add server-hooks/pre-receive
git commit -m "chore(hooks): update server-side pre-receive hook"
git push

# 3. 重新部署到服务器
# 重复上述部署步骤
```

### 临时禁用钩子（紧急情况）

```bash
# 在服务器上
cd /path/to/repo.git/hooks
mv pre-receive pre-receive.disabled

# 推送完成后重新启用
mv pre-receive.disabled pre-receive
```

### 查看钩子日志

钩子输出会显示在推送的 stderr 中：

```bash
git push origin feature/test
# 输出会显示所有检查步骤和结果
```

## 🔍 故障排查

### 问题 1: 钩子没有执行

**检查**:

```bash
# 确认钩子存在
ls -la /path/to/repo.git/hooks/pre-receive

# 确认执行权限
chmod +x /path/to/repo.git/hooks/pre-receive

# 确认 shebang 正确
head -1 /path/to/repo.git/hooks/pre-receive
# 应该输出: #!/bin/bash
```

### 问题 2: 权限被拒绝

```bash
# 确认钩子所有者
ls -la /path/to/repo.git/hooks/pre-receive

# 修改所有者（如果需要）
sudo chown git:git /path/to/repo.git/hooks/pre-receive
```

### 问题 3: 钩子错误

```bash
# 在服务器上手动测试钩子
cd /path/to/repo.git
echo "old new refs/heads/test" | hooks/pre-receive
```

## 📚 相关文档

- [Git 钩子官方文档](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Gitea 钩子指南](https://docs.gitea.io/en-us/git-hooks/)
- [GitLab 服务器钩子](https://docs.gitlab.com/ee/administration/server_hooks.html)
- [GitHub Enterprise 钩子](https://docs.github.com/en/enterprise-server/admin/policies/enforcing-policy-with-pre-receive-hooks)

## ⚠️ 重要提醒

1. **本地不会触发 pre-receive**：这个钩子只在服务器端运行
2. **Husky 不管理服务器钩子**：需要手动部署到服务器
3. **测试后再部署**：在测试仓库先验证钩子功能
4. **备份原钩子**：部署前备份服务器现有的钩子
5. **文档同步**：更新钩子后同步更新本文档

## 🎯 最佳实践

1. **版本控制**：将钩子脚本提交到仓库，方便追踪变更
2. **测试环境**：先在测试服务器部署验证
3. **渐进式部署**：先启用警告模式，再启用强制模式
4. **监控日志**：定期检查钩子执行日志
5. **团队培训**：确保团队了解服务器端钩子的作用

---

**更新时间**: 2025-10-12
**维护人**: AI Assistant (Claude 3.5 Sonnet)
