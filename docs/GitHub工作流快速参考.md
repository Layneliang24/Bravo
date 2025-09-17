# GitHub 工作流快速参考手册

## 🔄 工作流触发场景速查

### 开发者日常操作对应的工作流

| 开发者操作          | 触发的工作流          | 预期时长  | 测试级别 |
| ------------------- | --------------------- | --------- | -------- |
| 创建 PR to main/dev | `on-pr.yml`           | 10-15分钟 | 标准验证 |
| Push to feature/xxx | `on-push-feature.yml` | 5-8分钟   | 快速检查 |
| Push to dev         | `on-push-dev.yml`     | 20-30分钟 | 完整测试 |
| Merge PR to dev     | `on-merge-dev.yml`    | 8-12分钟  | 合并验证 |
| Merge PR to main    | `on-merge-main.yml`   | 15-25分钟 | 生产验证 |

## 🛠️ 常用工作流命令

### 手动触发工作流

```bash
# 使用 GitHub CLI 手动触发工作流
gh workflow run "PR Validation - Fast Track"
gh workflow run "Dev Branch - Medium Validation"
gh workflow run "Feature Branch - Development Validation"

# 查看工作流运行状态
gh run list --workflow="on-pr.yml"
gh run view [RUN_ID] --verbose
```

### 本地模拟 GitHub Actions

```bash
# 使用 act 工具在本地运行 GitHub Actions
# 安装: https://github.com/nektos/act

# 模拟 PR 触发
act pull_request -W .github/workflows/on-pr.yml

# 模拟 push 到 feature 分支
act push -W .github/workflows/on-push-feature.yml

# 使用特定事件文件
act -e .github/event.json
```

## 📊 工作流状态速查

### 工作流健康状态检查清单

**✅ 正常状态指标**:

- [ ] 缓存命中率 > 80%
- [ ] 平均运行时间在预期范围内
- [ ] 失败率 < 5%
- [ ] 无超时作业

**⚠️ 需要关注**:

- [ ] 缓存命中率 60-80%
- [ ] 运行时间超出预期20%以上
- [ ] 失败率 5-10%
- [ ] 偶发超时

**🚨 需要立即处理**:

- [ ] 缓存命中率 < 60%
- [ ] 运行时间超出预期50%以上
- [ ] 失败率 > 10%
- [ ] 频繁超时

### 常见问题快速诊断

**问题**: PR 检查一直在"pending"状态

```bash
# 排查步骤
1. 检查工作流是否正确触发
   gh run list --branch=your-branch --limit=5

2. 查看具体失败原因
   gh run view [RUN_ID] --verbose

3. 检查分支保护规则
   gh api repos/:owner/:repo/branches/main/protection
```

**问题**: 缓存未命中导致构建缓慢

```bash
# 排查步骤
1. 检查缓存键是否发生变化
   # 在工作流日志中搜索 "cache hit" 和 "cache miss"

2. 查看依赖文件是否有更新
   git diff HEAD~1 package-lock.json
   git diff HEAD~1 backend/requirements/

3. 手动清理缓存 (通过 GitHub UI)
   Settings > Actions > Caches
```

## 🚀 优化实施快速指南

### 阶段1: 立即可行的优化 (本周内)

**1. 创建统一环境 Action**

```yaml
# 文件: .github/actions/setup-unified-env/action.yml
name: "Unified Environment Setup"
description: "One-stop environment setup with caching"
inputs:
  cache-level:
    description: "Cache level: minimal|standard|full"
    default: "standard"
runs:
  using: "composite"
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: "20"
        cache: "npm"
    - uses: actions/setup-python@v4
      with:
        python-version: "3.11"
        cache: "pip"
    - uses: ./.github/actions/configure-china-mirrors
    - uses: ./.github/actions/setup-cached-env
      if: inputs.cache-level != 'minimal'
```

**使用方式**:

```yaml
# 在现有工作流中替换重复的环境设置
- name: Setup Environment
  uses: ./.github/actions/setup-unified-env
  with:
    cache-level: "full"
```

**2. 优化缓存键**

```yaml
# 当前
key: frontend-deps-v2-${{ runner.os }}-${{ hashFiles('package-lock.json') }}

# 优化后 - 更精确的缓存
key: frontend-deps-v3-${{ runner.os }}-${{ hashFiles('package-lock.json', 'frontend/package.json') }}-${{ env.NODE_VERSION }}
```

### 阶段2: 中期改进 (下周内)

**1. 创建智能测试策略**

```yaml
# .github/workflows/smart-test-selector.yml
name: Smart Test Selector
on:
  workflow_call:
    inputs:
      changed-files:
        required: true
        type: string
    outputs:
      test-strategy:
        value: ${{ jobs.analyze.outputs.strategy }}

jobs:
  analyze:
    runs-on: ubuntu-latest
    outputs:
      strategy: ${{ steps.decide.outputs.strategy }}
    steps:
      - name: Analyze Changes
        id: decide
        run: |
          if echo "${{ inputs.changed-files }}" | grep -q "backend/"; then
            echo "strategy=full-backend" >> $GITHUB_OUTPUT
          elif echo "${{ inputs.changed-files }}" | grep -q "frontend/"; then
            echo "strategy=full-frontend" >> $GITHUB_OUTPUT
          elif echo "${{ inputs.changed-files }}" | grep -q "e2e/"; then
            echo "strategy=e2e-only" >> $GITHUB_OUTPUT
          else
            echo "strategy=minimal" >> $GITHUB_OUTPUT
          fi
```

**2. 实现并行优化**

```yaml
# 优化前: 串行执行
setup → unit-backend → integration → e2e

# 优化后: 最大化并行
setup → (unit-backend + unit-frontend + lint + type-check) → integration → e2e
```

## 📋 监控与告警设置

### GitHub Actions 原生监控

**启用工作流监控**:

1. Repository Settings → Actions → General
2. 启用 "Send notifications for failed workflows"
3. 配置 webhook 到企业微信/钉钉

**设置分支保护规则**:

```bash
# 使用 GitHub CLI 设置分支保护
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["PR Validation Summary"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}'
```

### 第三方监控集成

**Grafana 仪表盘配置** (如果使用):

```yaml
# GitHub Actions 指标收集
metrics:
  - workflow_run_duration_seconds
  - workflow_run_conclusion_total
  - workflow_job_duration_seconds
  - cache_hit_rate_percentage

alerts:
  - name: "Workflow Failure Rate High"
    condition: "failure_rate > 10%"
    duration: "5m"

  - name: "Build Time Increased"
    condition: "avg_duration > 1.2 * baseline"
    duration: "15m"
```

## 🔧 故障排除手册

### 常见故障及解决方案

**故障1: MySQL 服务启动失败**

```yaml
# 症状: "MySQL is unavailable - sleeping"
# 原因: MySQL 服务启动超时

# 解决方案1: 增加等待时间
- name: Wait for MySQL (Extended)
  run: |
    for i in {1..60}; do
      if mysqladmin ping -h 127.0.0.1 -u root -proot_password --silent; then
        echo "MySQL is ready!"
        break
      fi
      echo "MySQL not ready, waiting... ($i/60)"
      sleep 3
    done

# 解决方案2: 优化健康检查
services:
  mysql:
    options: --health-cmd="mysqladmin ping -h localhost" --health-interval=5s --health-timeout=3s --health-retries=20
```

**故障2: 前端构建失败 - vue-tsc 找不到**

```yaml
# 症状: "vue-tsc: command not found"
# 原因: 依赖安装不完整

# 解决方案
- name: Install Frontend Dependencies (Robust)
  run: |
    cd frontend
    # 清理可能损坏的 node_modules
    if [ -d "node_modules" ] && [ ! -f "node_modules/.installed" ]; then
      rm -rf node_modules package-lock.json
    fi

    # 安装依赖
    npm ci --prefer-offline --no-audit

    # 标记安装完成
    touch node_modules/.installed

    # 验证关键工具可用
    npx vue-tsc --version || exit 1
```

**故障3: E2E 测试 Playwright 浏览器下载失败**

```yaml
# 解决方案: 分阶段下载 + 重试机制
- name: Install Playwright Browsers (Robust)
  run: |
    cd e2e

    # 设置国内镜像
    export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/

    # 分阶段安装
    for browser in chromium firefox webkit; do
      echo "Installing $browser..."
      npx playwright install $browser || {
        echo "Retry installing $browser..."
        sleep 10
        npx playwright install $browser
      }
    done

    # 安装系统依赖
    npx playwright install-deps
```

## 📈 性能优化建议

### CPU 密集型任务优化

**并行构建**:

```yaml
# 利用多核 CPU
- name: Build with Parallel Processing
  run: |
    # 前端构建使用多线程
    npm run build -- --parallel

    # Python 测试使用多进程
    python -m pytest --numprocesses=auto
```

**合理分配资源**:

```yaml
# 根据任务类型选择合适的运行器
jobs:
  lint:
    runs-on: ubuntu-latest # 轻量级任务

  build:
    runs-on: ubuntu-latest-4-cores # 构建任务需要更多 CPU

  e2e:
    runs-on: ubuntu-latest-8-cores # E2E 测试需要最多资源
```

### 网络优化

**下载优化**:

```yaml
# 使用国内镜像 + 并行下载
- name: Optimized Downloads
  run: |
    # npm 配置
    npm config set registry https://registry.npmmirror.com
    npm config set maxsockets 20

    # pip 配置
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/

    # 并行安装
    npm ci & pip install -r requirements.txt & wait
```

## 🎯 最佳实践清单

### 工作流设计最佳实践

- [ ] **单一职责**: 每个工作流专注一个场景
- [ ] **fail-fast**: 早期发现问题，快速失败
- [ ] **幂等性**: 多次运行结果一致
- [ ] **可观测性**: 充分的日志和监控
- [ ] **资源效率**: 合理使用 runner 资源

### 缓存使用最佳实践

- [ ] **精确缓存键**: 基于内容哈希，避免过度缓存
- [ ] **分层缓存**: 不同更新频率的内容分开缓存
- [ ] **缓存回退**: 提供合理的 restore-keys
- [ ] **缓存清理**: 定期清理过期缓存
- [ ] **缓存监控**: 监控缓存命中率

### 安全最佳实践

- [ ] **最小权限**: 只授予必要的权限
- [ ] **秘钥管理**: 使用 GitHub Secrets
- [ ] **依赖扫描**: 定期检查依赖漏洞
- [ ] **代码扫描**: 集成 SAST 工具
- [ ] **审计日志**: 保留操作审计记录

---

**更新时间**: 2025-09-17
**维护者**: DevOps Team
**版本**: v1.0
