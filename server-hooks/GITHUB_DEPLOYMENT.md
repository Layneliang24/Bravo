# 🚀 GitHub 部署指南

## ⚠️ 重要说明

**GitHub.com（免费版）不支持自定义 pre-receive 钩子！**

本文档提供在 GitHub 上实现类似保护的替代方案。

## 🎯 GitHub 部署方案对比

| 方案                                   | 适用场景 | 保护强度 | 实施难度 |
| -------------------------------------- | -------- | -------- | -------- |
| **GitHub Enterprise Pre-Receive**      | 企业版   | 🔴 最强  | 🟡 中    |
| **GitHub Actions + Branch Protection** | 所有版本 | 🟡 较强  | 🟢 简单  |
| **本地钩子（Husky）**                  | 所有版本 | 🟠 弱    | 🟢 简单  |

## 📋 方案 1：GitHub Actions 模拟（推荐）⭐

### 特点

✅ **优点**:

- 无需服务器配置
- 自动运行所有检查
- 清晰的错误报告
- 集成到 CI/CD 流程

❌ **缺点**:

- 只能在推送**后**检查（无法阻止推送）
- 依赖 GitHub Actions 额度
- 有执行延迟（~30秒）

### 实施步骤

#### 1. 工作流已创建

文件位置：`.github/workflows/server-hooks-simulation.yml`

**包含的检查**:

- ✅ 分支保护
- ✅ 禁止的文件
- ✅ 大文件检查
- ✅ 合并冲突标记
- ✅ 根目录守卫
- ✅ NPM Workspaces 保护
- ✅ Scripts-Golden 保护

#### 2. 配置 Branch Protection Rules（必需）

访问：`Settings` → `Branches` → `Add branch protection rule`

**Main 分支规则**:

```
Branch name pattern: main

✅ Require a pull request before merging
  ✅ Require approvals: 1
  ✅ Dismiss stale pull request approvals when new commits are pushed

✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  必需的状态检查：
    - Pre-Receive Checks Simulation
    - Backend Unit Tests
    - Frontend Unit Tests
    - Integration Tests

✅ Require conversation resolution before merging

✅ Require linear history (optional)

✅ Include administrators (推荐)

❌ Allow force pushes
❌ Allow deletions
```

**Dev 分支规则**:

```
Branch name pattern: dev

✅ Require a pull request before merging
  ✅ Require approvals: 1

✅ Require status checks to pass before merging
  ✅ Require branches to be up to date before merging
  必需的状态检查：
    - Pre-Receive Checks Simulation
    - Backend Unit Tests
    - Frontend Unit Tests

✅ Include administrators (推荐)

❌ Allow force pushes
❌ Allow deletions
```

#### 3. 配置 Rulesets（GitHub 新功能，推荐）

访问：`Settings` → `Rules` → `Rulesets` → `New ruleset`

**创建 Main/Dev 保护规则集**:

```yaml
Ruleset name: Main/Dev Branch Protection

Target branches:
  - main
  - dev

Rules:
  ✅ Restrict creations
  ✅ Restrict updates
  ✅ Restrict deletions
  ✅ Require linear history
  ✅ Require deployments to succeed

  ✅ Require pull request
     - Required approvals: 1
     - Dismiss stale reviews: Yes
     - Require review from Code Owners: Yes

  ✅ Require status checks
     - Require branches to be up to date: Yes
     - Status checks:
       * server-hooks-simulation / Pre-Receive Checks Simulation
       * on-pr / Backend Unit Tests
       * on-pr / Frontend Unit Tests

  ✅ Block force pushes

Bypass list:
  - (留空，包括管理员也要遵守)
```

#### 4. 创建 CODEOWNERS 文件（可选）

创建 `.github/CODEOWNERS`:

```
# 代码所有者文件
# 确保关键目录的变更需要特定人员审查

# 核心安全脚本
/scripts-golden/ @project-lead @security-team

# GitHub 工作流
/.github/workflows/ @devops-team @project-lead

# 服务器钩子
/server-hooks/ @project-lead

# 根目录配置文件
/*.yml @devops-team
/*.json @devops-team
/docker-compose*.yml @devops-team
```

## 📋 方案 2：GitHub Enterprise Pre-Receive

如果你使用 **GitHub Enterprise**，可以部署真正的 pre-receive 钩子：

### 部署步骤

1. **访问管理控制台**

   ```
   https://your-github-enterprise.com/stafftools/pre-receive-hooks
   ```

2. **上传钩子脚本**

   - 上传 `server-hooks/pre-receive`
   - 设置名称: `Bravo Project Pre-Receive`
   - 设置环境: `Default`

3. **启用钩子**

   - 选择仓库: `Bravo`
   - 启用钩子
   - 设置强制模式: `Enabled`

4. **测试**

   ```bash
   # 测试推送到 main（应该被拒绝）
   git push origin main

   # 测试推送到 feature（应该成功）
   git push origin feature/test
   ```

## 📊 保护强度对比

### GitHub.com (Actions + Branch Protection)

| 检查项     | 阻止推送 | 阻止合并 | 提供反馈 |
| ---------- | -------- | -------- | -------- |
| 分支保护   | ❌       | ✅       | ✅       |
| 禁止文件   | ❌       | ✅       | ✅       |
| 大文件     | ❌       | ✅       | ✅       |
| 代码质量   | ❌       | ✅       | ✅       |
| 根目录守卫 | ❌       | ✅       | ✅       |

**总结**: 无法阻止推送，但可以阻止合并到保护分支

### GitHub Enterprise (Pre-Receive)

| 检查项     | 阻止推送 | 阻止合并 | 提供反馈 |
| ---------- | -------- | -------- | -------- |
| 分支保护   | ✅       | ✅       | ✅       |
| 禁止文件   | ✅       | ✅       | ✅       |
| 大文件     | ✅       | ✅       | ✅       |
| 代码质量   | ✅       | ✅       | ✅       |
| 根目录守卫 | ✅       | ✅       | ✅       |

**总结**: 完全阻止，最强保护

## 🧪 测试验证

### 测试 GitHub Actions

1. **提交测试变更**

   ```bash
   git checkout -b test/server-hooks
   echo "test" > test.txt
   git add test.txt
   git commit -m "test: verify server hooks simulation"
   git push origin test/server-hooks
   ```

2. **查看 Actions**

   - 访问: `Actions` 标签
   - 查看 `Server-Side Hooks Simulation` 工作流
   - 验证所有检查是否通过

3. **测试失败场景**
   ```bash
   # 测试大文件（应该失败）
   dd if=/dev/zero of=large.bin bs=1M count=11
   git add large.bin
   git commit -m "test: large file"
   git push origin test/server-hooks
   # 应该看到 Actions 失败
   ```

### 测试 Branch Protection

1. **尝试直接推送到 main**

   ```bash
   git checkout main
   echo "test" >> README.md
   git commit -am "test: direct push"
   git push origin main
   # 应该被 Branch Protection 拒绝
   ```

2. **通过 PR 推送**
   ```bash
   git checkout -b feature/test-pr
   echo "test" >> README.md
   git commit -am "feat: test pr workflow"
   git push origin feature/test-pr
   # 创建 PR 到 main
   # 等待 Actions 通过
   # 通过审查后合并
   ```

## 📚 相关文档

- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets)
- [GitHub Actions](https://docs.github.com/en/actions)
- [GitHub Enterprise Pre-Receive Hooks](https://docs.github.com/en/enterprise-server/admin/policies/enforcing-policy-with-pre-receive-hooks)

## ⚙️ 维护建议

### 定期检查

1. **每月检查 Branch Protection**

   - 确保规则没有被修改
   - 验证必需的状态检查列表

2. **每季度审查 Actions 日志**

   - 查看被拦截的违规尝试
   - 分析常见问题并改进文档

3. **更新钩子脚本**
   - 同步更新 GitHub Actions 工作流
   - 测试新增的检查项

### 故障排查

**问题 1**: Actions 没有运行

- 检查工作流文件语法
- 验证触发条件配置
- 查看 Actions 执行历史

**问题 2**: Branch Protection 不生效

- 确认规则已启用
- 检查 "Include administrators" 选项
- 验证状态检查名称正确

**问题 3**: 误报拦截

- 审查 Actions 日志
- 调整检查规则
- 更新文档

## 🎯 最佳实践

1. **逐步启用规则**

   - 第一周：仅监控模式
   - 第二周：启用部分规则
   - 第三周：启用全部规则

2. **团队培训**

   - 解释 Branch Protection 的重要性
   - 演示正确的 PR 工作流
   - 提供故障排查指南

3. **文档同步**
   - 保持 GitHub 配置与文档一致
   - 记录所有规则变更
   - 定期审查和更新

## ✅ 部署检查清单

- [ ] GitHub Actions 工作流已创建
- [ ] Main 分支 Branch Protection 已配置
- [ ] Dev 分支 Branch Protection 已配置
- [ ] Rulesets 已创建（如果可用）
- [ ] CODEOWNERS 已配置（可选）
- [ ] 测试 Actions 工作流
- [ ] 测试 Branch Protection
- [ ] 团队培训完成
- [ ] 文档更新完成

---

**部署人**: 项目维护团队
**更新时间**: 2025-10-12
**版本**: v1.0.0
**状态**: ✅ 可部署
