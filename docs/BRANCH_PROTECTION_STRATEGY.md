# Branch Protection Strategy

## 概述

本文档定义了项目的分支保护策略，确保代码质量和稳定性。

## 当前问题分析

### 🚨 紧急问题

**合并后验证而非合并前验证**

- PR #6 在所有关键测试失败的情况下仍然合并到了 `dev` 分支
- 这违反了基本的质量控制原则

## 分支保护配置

### `dev` 分支保护规则

#### 必需的状态检查 (Required Status Checks)

- ✅ `Backend Unit Tests` - 后端单元测试
- ✅ `Frontend Unit Tests` - 前端单元测试
- ✅ `Integration Tests` - 集成测试
- ✅ `E2E Smoke Tests` - E2E烟雾测试（最小集）
- ✅ `Security Scan` - 安全扫描
- ✅ `Coverage Quality Gate` - 代码覆盖率检查
- ✅ `Directory Guard` - 目录保护检查

#### 配置要求

```yaml
required_status_checks:
  strict: true # 要求分支与主分支保持最新
  contexts:
    - "Backend Unit Tests"
    - "Frontend Unit Tests"
    - "Integration Tests"
    - "E2E Smoke Tests"
    - "Security Scan"
    - "Coverage Quality Gate"
    - "Directory Guard"

enforce_admins: true # 管理员也必须遵守规则
allow_force_pushes: false
allow_deletions: false
required_pull_request_reviews:
  required_approving_review_count: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: false
```

### `main` 分支保护规则

```yaml
required_status_checks:
  strict: true
  contexts:
    - "Full Test Suite"
    - "Performance Tests"
    - "Security Audit"
    - "Deployment Smoke Test"

required_pull_request_reviews:
  required_approving_review_count: 2
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
```

## Workflow触发策略

### PR验证 (Pre-merge)

```yaml
name: "PR Validation"
on:
  pull_request:
    branches: [dev, main]
    types: [opened, synchronize, reopened]

jobs:
  # 所有关键检查必须在这里通过
  required-checks:
    runs-on: ubuntu-latest
    steps: [...]
```

### 合并后验证 (Post-merge)

```yaml
name: "Post-merge Validation"
on:
  push:
    branches: [dev]

jobs:
  # 额外的完整测试套件
  extended-validation:
    runs-on: ubuntu-latest
    steps: [...]
```

## 质量门槛标准

### 代码覆盖率

- **后端**: 最低 80%
- **前端**: 最低 85%
- **集成**: 最低 70%

### 测试通过率

- **单元测试**: 100% 通过
- **集成测试**: 100% 通过
- **E2E烟雾测试**: 100% 通过

### 性能要求

- **构建时间**: 不超过 10 分钟
- **测试时间**: 不超过 15 分钟

## 异常处理流程

### 紧急修复 (Hotfix)

1. 创建 `hotfix/*` 分支
2. 通过简化的检查流程
3. 需要两个批准者
4. 自动创建回填PR到 `dev`

### 实验性功能

1. 使用 `experiment/*` 分支
2. 不强制所有检查
3. 明确标记为实验性
4. 定期清理

## 监控和告警

### GitHub Actions监控

- 失败率超过5%时告警
- 平均执行时间增加20%时告警
- 队列积压超过10个时告警

### 代码质量监控

- 覆盖率下降超过2%时告警
- 技术债务增加时告警
- 安全漏洞发现时立即告警

## 改进措施

### 立即行动

1. **修复当前的分支保护配置**
2. **创建合并前验证workflow**
3. **清理dev分支的问题代码**

### 中期改进

1. 建立代码质量仪表板
2. 自动化质量报告
3. 开发者教育培训

### 长期规划

1. 实现预测性质量分析
2. 建立质量文化
3. 持续改进流程

## 参考资料

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests)
- [GitHub Actions Required Status Checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches#require-status-checks-before-merging)
