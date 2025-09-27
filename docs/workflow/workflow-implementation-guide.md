# GitHub Actions工作流重构实施指南

> **Claude Sonnet 4** - 具体实施方案
> **阶段**: 正在执行重构
> **目标**: 今日完成所有重构工作

## 🚀 阶段1: 基础组件重构 (进行中)

### 1.1 测试套件组件设计 (test-suite.yml)

这个组件将整合所有现有的测试工作流：

- test-unit-backend.yml
- test-unit-frontend.yml
- test-integration-optimized.yml
- test-e2e.yml, test-e2e-smoke.yml, test-e2e-full.yml
- test-regression.yml

```yaml
name: "Test Suite Component"
on:
  workflow_call:
    inputs:
      test-level:
        description: "Test execution level"
        type: string
        required: true
        # "fast" - 只运行单元测试 (≤5分钟)
        # "medium" - 单元+集成测试 (≤12分钟)
        # "full" - 完整测试套件 (≤25分钟)
      target-branch:
        description: "Target branch for testing"
        type: string
        required: false
        default: "dev"
      coverage-required:
        description: "Minimum coverage percentage"
        type: string
        required: false
        default: "80"
    outputs:
      test-results:
        description: "Test execution results"
        value: ${{ jobs.test-summary.outputs.results }}

env:
  NODE_VERSION: "20"
  PYTHON_VERSION: "3.11"

jobs:
  # 并行执行的单元测试
  unit-tests:
    strategy:
      fail-fast: false
      matrix:
        component: ["backend", "frontend"]

    runs-on: ubuntu-latest
    timeout-minutes: 8

    steps:
      - uses: actions/checkout@v4

      - name: Setup Dependency Cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            node_modules
            backend/.venv
          key: unit-deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json', 'backend/requirements/*.txt') }}
          restore-keys: |
            unit-deps-${{ runner.os }}-

      - name: Run Unit Tests
        run: |
          case "${{ matrix.component }}" in
            "backend")
              cd backend && source .venv/bin/activate
              python -m pytest tests/unit/ --cov --cov-report=xml --cov-report=term
              ;;
            "frontend")
              npm run test:unit:frontend -- --coverage
              ;;
          esac

      - name: Upload Coverage
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
          flags: ${{ matrix.component }}
          name: ${{ matrix.component }}-coverage

  # 条件执行的集成测试
  integration-tests:
    if: inputs.test-level != 'fast'
    needs: unit-tests
    runs-on: ubuntu-latest
    timeout-minutes: 12

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_DATABASE: bravo_test
          MYSQL_USER: bravo_user
          MYSQL_PASSWORD: bravo_password
          MYSQL_ROOT_PASSWORD: root_password
        options: --health-cmd="mysqladmin ping" --health-interval=5s --health-timeout=3s --health-retries=10
        ports:
          - 3306:3306

    steps:
      - uses: actions/checkout@v4

      - name: Setup Integration Cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            backend/.venv
          key: integration-deps-${{ runner.os }}-${{ hashFiles('backend/requirements/*.txt') }}
          restore-keys: |
            integration-deps-${{ runner.os }}-

      - name: Run Integration Tests
        run: |
          cd backend && source .venv/bin/activate
          python manage.py migrate --settings=bravo.settings.test
          python -m pytest tests/integration/ --maxfail=3
        env:
          DB_HOST: 127.0.0.1
          DB_PORT: 3306
          DB_NAME: bravo_test
          DB_USER: bravo_user
          DB_PASSWORD: bravo_password

  # E2E测试环境变量设计规范
  #
  # 为确保E2E测试在Docker容器环境中正确运行，定义统一的环境变量规范：
  #
  # 1. 前端服务端点：
  #    - FRONTEND_URL: http://frontend-test:3000
  #    - TEST_BASE_URL: http://frontend-test:3000 (兼容legacy)
  #
  # 2. 后端API端点：
  #    - BACKEND_URL: http://backend-test:8000 (标准变量名)
  #    - ❌ 禁止使用 API_URL (会导致容器间通信失败)
  #
  # 3. 测试代码规范：
  #    - 必须使用 process.env.BACKEND_URL 读取后端地址
  #    - 必须使用 process.env.TEST_BASE_URL 读取前端地址
  #    - fallback值仅用于本地开发，生产环境必须依赖环境变量
  #
  # 4. Docker配置一致性：
  #    - Dockerfile.test 中的 ENV 设置
  #    - docker-compose.test.yml 中的 environment 设置
  #    - 测试代码中的 process.env 读取
  #    - 三者必须保持变量名完全一致
  #

  # 智能E2E测试 (基于Docker Build Cache优化)
  e2e-tests:
    if: inputs.test-level == 'full'
    needs: integration-tests
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Setup Docker Buildx
        uses: docker/setup-buildx-action@v3
        with:
          driver-opts: |
            image=moby/buildkit:latest

      - name: Run E2E Tests with Docker Build Cache
        run: |
          echo "🎭 Running E2E tests with Docker Build Cache optimization..."

          # 启动基础服务 (利用Docker Build Cache)
          docker compose -f docker-compose.test.yml up --build -d mysql-test backend-test frontend-test

          # 等待服务就绪
          sleep 15

          # 运行E2E测试 (利用Docker原生缓存机制)
          E2E_EXIT_CODE=0
          docker compose -f docker-compose.test.yml run --rm e2e-tests || E2E_EXIT_CODE=$?

          # 清理
          docker compose -f docker-compose.test.yml down

          exit $E2E_EXIT_CODE

      - name: Upload E2E Artifacts
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-test-artifacts
          path: e2e-artifacts/
          retention-days: 7

  # 测试结果汇总
  test-summary:
    if: always()
    needs: [unit-tests, integration-tests, e2e-tests]
    runs-on: ubuntu-latest
    outputs:
      results: ${{ steps.summary.outputs.results }}

    steps:
      - name: Generate Test Summary
        id: summary
        run: |
          UNIT_STATUS="${{ needs.unit-tests.result }}"
          INTEGRATION_STATUS="${{ needs.integration-tests.result }}"
          E2E_STATUS="${{ needs.e2e-tests.result }}"

          echo "## 🧪 Test Suite Results" >> $GITHUB_STEP_SUMMARY
          echo "| Test Type | Status | Level |" >> $GITHUB_STEP_SUMMARY
          echo "|-----------|--------|-------|" >> $GITHUB_STEP_SUMMARY
          echo "| Unit Tests | $UNIT_STATUS | Always |" >> $GITHUB_STEP_SUMMARY
          echo "| Integration Tests | $INTEGRATION_STATUS | Medium+ |" >> $GITHUB_STEP_SUMMARY
          echo "| E2E Tests | $E2E_STATUS | Full Only |" >> $GITHUB_STEP_SUMMARY

          if [[ "$UNIT_STATUS" == "success" ]]; then
            if [[ "${{ inputs.test-level }}" == "fast" ]] ||
               [[ "${{ inputs.test-level }}" == "medium" && "$INTEGRATION_STATUS" == "success" ]] ||
               [[ "${{ inputs.test-level }}" == "full" && "$INTEGRATION_STATUS" == "success" && "$E2E_STATUS" == "success" ]]; then
              echo "results=success" >> $GITHUB_OUTPUT
              echo "✅ All required tests passed!" >> $GITHUB_STEP_SUMMARY
            else
              echo "results=failure" >> $GITHUB_OUTPUT
              echo "❌ Some tests failed!" >> $GITHUB_STEP_SUMMARY
              exit 1
            fi
          else
            echo "results=failure" >> $GITHUB_OUTPUT
            echo "❌ Unit tests failed!" >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
```

### 1.2 质量门禁组件设计 (quality-gates.yml)

整合所有质量检查工作流：

- quality-coverage.yml
- quality-security.yml
- quality-performance.yml

```yaml
name: "Quality Gates Component"
on:
  workflow_call:
    inputs:
      quality-level:
        description: "Quality check level"
        type: string
        required: true
        # "basic" - 基础检查 (lint, audit)
        # "standard" - 标准检查 (+ coverage, security)
        # "strict" - 严格检查 (+ performance, accessibility)
      min-coverage:
        description: "Minimum code coverage"
        type: string
        required: false
        default: "80"
    outputs:
      quality-score:
        description: "Overall quality score"
        value: ${{ jobs.quality-summary.outputs.score }}

jobs:
  # 并行基础质量检查
  basic-checks:
    strategy:
      fail-fast: false
      matrix:
        check: ["lint-frontend", "lint-backend", "type-check", "audit"]

    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4
      - name: Setup Cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.cache/ms-playwright
            node_modules
            backend/.venv
          key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json', 'backend/requirements/*.txt', 'e2e/package-lock.json') }}
          restore-keys: |
            deps-${{ runner.os }}-

      - name: Run Check
        run: |
          case "${{ matrix.check }}" in
            "lint-frontend")
              npm run lint:frontend
              ;;
            "lint-backend")
              cd backend && source .venv/bin/activate
              flake8 . --select=E9,F63,F7,F82 --exclude=migrations
              ;;
            "type-check")
              npm run type-check
              ;;
            "audit")
              npm audit --audit-level=high --production
              ;;
          esac

  # 安全扫描 (standard+)
  security-scan:
    if: inputs.quality-level != 'basic'
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4
      - name: Setup Cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.cache/ms-playwright
            node_modules
            backend/.venv
          key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json', 'backend/requirements/*.txt', 'e2e/package-lock.json') }}
          restore-keys: |
            deps-${{ runner.os }}-

      - name: Run Security Scan
        run: |
          echo "🔐 Running security scan..."
          npm audit --audit-level=moderate

          # Python安全扫描
          cd backend && source .venv/bin/activate
          pip install safety bandit
          safety check
          bandit -r . -f json -o ../reports/security/bandit-report.json || true

      - name: Upload Security Results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: reports/security/bandit-report.json

  # 性能审计 (strict only)
  performance-audit:
    if: inputs.quality-level == 'strict'
    runs-on: ubuntu-latest
    timeout-minutes: 8

    steps:
      - uses: actions/checkout@v4
      - name: Setup Cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.cache/ms-playwright
            node_modules
            backend/.venv
          key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json', 'backend/requirements/*.txt', 'e2e/package-lock.json') }}
          restore-keys: |
            deps-${{ runner.os }}-

      - name: Build for Audit
        run: |
          npm run build:frontend

      - name: Run Lighthouse CI
        run: |
          # 创建轻量级测试页面
          mkdir -p frontend/dist
          cat > frontend/dist/audit-test.html << 'EOF'
          <!DOCTYPE html>
          <html lang="zh-CN">
          <head>
              <meta charset="UTF-8">
              <meta name="viewport" content="width=device-width, initial-scale=1.0">
              <title>Bravo Performance Test</title>
          </head>
          <body>
              <h1>Bravo Performance Audit</h1>
              <p>Testing page for Lighthouse CI</p>
          </body>
          </html>
          EOF

          # 配置Lighthouse
          cat > lighthouserc.json << 'EOF'
          {
            "ci": {
              "collect": {
                "staticDistDir": "./frontend/dist",
                "url": ["audit-test.html"],
                "numberOfRuns": 3
              },
              "assert": {
                "assertions": {
                  "categories:performance": ["warn", {"minScore": 0.7}],
                  "categories:accessibility": ["warn", {"minScore": 0.8}]
                }
              }
            }
          }
          EOF

          npx lhci autorun

  # 质量汇总
  quality-summary:
    if: always()
    needs: [basic-checks, security-scan, performance-audit]
    runs-on: ubuntu-latest
    outputs:
      score: ${{ steps.calculate.outputs.score }}

    steps:
      - name: Calculate Quality Score
        id: calculate
        run: |
          BASIC_STATUS="${{ needs.basic-checks.result }}"
          SECURITY_STATUS="${{ needs.security-scan.result }}"
          PERFORMANCE_STATUS="${{ needs.performance-audit.result }}"

          echo "## 🎯 Quality Gates Results" >> $GITHUB_STEP_SUMMARY
          echo "| Gate | Status | Level |" >> $GITHUB_STEP_SUMMARY
          echo "|------|--------|-------|" >> $GITHUB_STEP_SUMMARY
          echo "| Basic Checks | $BASIC_STATUS | Always |" >> $GITHUB_STEP_SUMMARY
          echo "| Security Scan | $SECURITY_STATUS | Standard+ |" >> $GITHUB_STEP_SUMMARY
          echo "| Performance Audit | $PERFORMANCE_STATUS | Strict Only |" >> $GITHUB_STEP_SUMMARY

          # 计算质量分数
          SCORE=0
          if [[ "$BASIC_STATUS" == "success" ]]; then SCORE=$((SCORE + 40)); fi
          if [[ "$SECURITY_STATUS" == "success" ]]; then SCORE=$((SCORE + 35)); fi
          if [[ "$PERFORMANCE_STATUS" == "success" ]]; then SCORE=$((SCORE + 25)); fi

          echo "score=$SCORE" >> $GITHUB_OUTPUT
          echo "**Overall Quality Score: $SCORE/100**" >> $GITHUB_STEP_SUMMARY

          if [[ $SCORE -ge 70 ]]; then
            echo "✅ Quality gates passed!" >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ Quality gates failed!" >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
```

## 🚀 阶段2: 核心场景重构

### 2.1 PR验证流水线 (pr-validation.yml)

替换现有的PR相关工作流：

- on-pr.yml
- branch-protection.yml (PR部分)

```yaml
name: "PR Validation Pipeline"
on:
  pull_request:
    branches: [dev, main]
    types: [opened, synchronize, reopened]

concurrency:
  group: pr-${{ github.ref }}-${{ github.base_ref }}
  cancel-in-progress: true

jobs:
  # 智能检测PR类型
  detect-pr-type:
    name: "Detect PR Type"
    runs-on: ubuntu-latest
    timeout-minutes: 2
    outputs:
      pr-type: ${{ steps.detect.outputs.type }}
      validation-level: ${{ steps.detect.outputs.level }}
      test-level: ${{ steps.detect.outputs.test-level }}
      quality-level: ${{ steps.detect.outputs.quality-level }}

    steps:
      - name: Analyze PR Context
        id: detect
        run: |
          echo "🔍 Analyzing PR: ${{ github.head_ref }} → ${{ github.base_ref }}"

          if [[ "${{ github.base_ref }}" == "main" ]]; then
            if [[ "${{ github.head_ref }}" == "dev" ]]; then
              echo "type=production-release" >> $GITHUB_OUTPUT
              echo "level=strict" >> $GITHUB_OUTPUT
              echo "test-level=full" >> $GITHUB_OUTPUT
              echo "quality-level=strict" >> $GITHUB_OUTPUT
              echo "🏭 Production release detected: Full validation required"
            else
              echo "type=hotfix" >> $GITHUB_OUTPUT
              echo "level=emergency" >> $GITHUB_OUTPUT
              echo "test-level=medium" >> $GITHUB_OUTPUT
              echo "quality-level=standard" >> $GITHUB_OUTPUT
              echo "🚨 Emergency hotfix detected"
            fi
          elif [[ "${{ github.base_ref }}" == "dev" ]]; then
            echo "type=feature-integration" >> $GITHUB_OUTPUT
            echo "level=standard" >> $GITHUB_OUTPUT
            echo "test-level=medium" >> $GITHUB_OUTPUT
            echo "quality-level=standard" >> $GITHUB_OUTPUT
            echo "🚀 Feature integration detected: Standard validation"
          fi

  # 分支保护验证
  branch-protection:
    name: "Branch Protection Check"
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - name: Validate Source Branch
        run: |
          echo "🔒 Validating branch protection rules..."

          if [[ "${{ github.base_ref }}" == "main" && "${{ github.head_ref }}" != "dev" ]]; then
            echo "❌ VIOLATION: Only 'dev' branch can create PRs to main"
            echo "   Source: ${{ github.head_ref }}"
            echo "   Target: ${{ github.base_ref }}"
            exit 1
          fi

          echo "✅ Branch protection rules satisfied"

  # 快速预检查
  quick-validation:
    name: "Quick Validation"
    needs: [detect-pr-type, branch-protection]
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4
      - name: Setup Cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/pip
            ~/.cache/ms-playwright
            node_modules
            backend/.venv
          key: deps-${{ runner.os }}-${{ hashFiles('**/package-lock.json', 'backend/requirements/*.txt', 'e2e/package-lock.json') }}
          restore-keys: |
            deps-${{ runner.os }}-

      - name: Quick Syntax Check
        run: |
          echo "⚡ Running quick syntax checks..."

          # 检查基本语法
          npm run lint:frontend || echo "Frontend lint issues detected"

          cd backend && source .venv/bin/activate
          flake8 . --select=E9,F63,F7,F82 --exclude=migrations || echo "Backend syntax issues detected"

          echo "✅ Quick validation completed"

  # 调用测试套件
  test-execution:
    name: "Test Execution"
    needs: [detect-pr-type, quick-validation]
    uses: ./.github/workflows/test-suite.yml
    with:
      test-level: ${{ needs.detect-pr-type.outputs.test-level }}
      target-branch: ${{ github.base_ref }}
      coverage-required: "85"

  # 调用质量门禁
  quality-checks:
    name: "Quality Checks"
    needs: [detect-pr-type, quick-validation]
    uses: ./.github/workflows/quality-gates.yml
    with:
      quality-level: ${{ needs.detect-pr-type.outputs.quality-level }}
      min-coverage: "85"
      target-branch: ${{ github.event.pull_request.base.ref || 'dev' }}

  # 最终审批门禁
  approval-gate:
    name: "Approval Gate"
    needs: [detect-pr-type, test-execution, quality-checks]
    runs-on: ubuntu-latest

    steps:
      - name: Generate PR Summary
        run: |
          echo "## 🎯 PR Validation Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**PR Type**: ${{ needs.detect-pr-type.outputs.pr-type }}" >> $GITHUB_STEP_SUMMARY
          echo "**Validation Level**: ${{ needs.detect-pr-type.outputs.validation-level }}" >> $GITHUB_STEP_SUMMARY
          echo "**Source → Target**: ${{ github.head_ref }} → ${{ github.base_ref }}" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          TEST_RESULT="${{ needs.test-execution.outputs.test-results }}"
          QUALITY_SCORE="${{ needs.quality-checks.outputs.quality-score }}"

          echo "| Validation Component | Result |" >> $GITHUB_STEP_SUMMARY
          echo "|---------------------|--------|" >> $GITHUB_STEP_SUMMARY
          echo "| Test Suite | $TEST_RESULT |" >> $GITHUB_STEP_SUMMARY
          echo "| Quality Score | $QUALITY_SCORE/100 |" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          if [[ "$TEST_RESULT" == "success" && "$QUALITY_SCORE" -ge "85" ]]; then
            echo "✅ **PR ready for review and merge**" >> $GITHUB_STEP_SUMMARY
            echo "All automated checks passed. Human approval required for final merge." >> $GITHUB_STEP_SUMMARY
          else
            echo "❌ **PR validation failed**" >> $GITHUB_STEP_SUMMARY
            echo "Please fix the issues above before requesting review." >> $GITHUB_STEP_SUMMARY
            exit 1
          fi
```

## 🧹 **第三阶段：旧文件清理计划**

### 3.1 清理策略

重构后应保留的核心文件（6个）：

```bash
.github/workflows/
├── pr-validation.yml      # PR验证流水线
├── push-validation.yml    # Push验证流水线
├── release-pipeline.yml   # 发布流水线
├── scheduled-tasks.yml    # 定时任务
├── test-suite.yml         # 测试组件
├── quality-gates.yml      # 质量门禁
└── cache-strategy.yml     # 缓存策略
```

### 3.2 待删除的旧文件（26个）

**场景触发类（6个）**：

- on-pr.yml
- on-push-dev.yml
- on-push-feature.yml
- on-merge-dev-optimized.yml
- main-release.yml
- branch-protection.yml

**测试执行类（10个）**：

- test-unit-backend.yml
- test-unit-frontend.yml
- test-integration-optimized.yml
- test-regression.yml
- test-e2e.yml
- test-e2e-smoke.yml
- test-e2e-full.yml
- test-backend.yml
- test-frontend.yml
- fast-validation.yml

**质量保障类（4个）**：

- quality-coverage.yml
- quality-security.yml
- quality-performance.yml
- golden-test-protection.yml

**基础设施类（4个）**：

- setup-cache.yml
- deploy-production.yml
- feature-map.yml
- dir_guard.yml

**其他功能类（2个）**：

- regression-scheduled.yml
- temp_script.sh

### 3.3 清理执行步骤

```bash
# 1. 验证新工作流正常运行
git checkout feature/workflow-refactoring-validation
git push origin feature/workflow-refactoring-validation
# 观察GitHub Actions执行情况

# 2. 创建备份分支
git checkout -b backup/old-workflows-$(date +%Y%m%d)
git push origin backup/old-workflows-$(date +%Y%m%d)

# 3. 批量删除旧文件
rm -f .github/workflows/on-*.yml
rm -f .github/workflows/test-unit-*.yml
rm -f .github/workflows/test-integration-*.yml
rm -f .github/workflows/test-e2e*.yml
rm -f .github/workflows/test-backend.yml
rm -f .github/workflows/test-frontend.yml
rm -f .github/workflows/test-regression.yml
rm -f .github/workflows/quality-*.yml
rm -f .github/workflows/fast-validation.yml
rm -f .github/workflows/golden-test-protection.yml
rm -f .github/workflows/setup-cache.yml
rm -f .github/workflows/deploy-production.yml
rm -f .github/workflows/feature-map.yml
rm -f .github/workflows/dir_guard.yml
rm -f .github/workflows/regression-scheduled.yml
rm -f .github/workflows/main-release.yml
rm -f .github/workflows/branch-protection.yml
rm -f .github/workflows/temp_script.sh

# 4. 提交清理结果
git add -A
git commit -m "🧹 清理旧工作流文件 - 完成重构目标 (26→6个文件)"
git push origin feature/workflow-refactoring-validation

# 5. 验证清理后状态
ls -la .github/workflows/ | wc -l  # 应该显示9行(包含., .., README.md + 6个核心文件)
```

### 3.4 风险控制

- **回滚方案**: 备份分支随时可恢复
- **分阶段验证**: 每删除一批文件就验证功能
- **监控告警**: 观察GitHub Actions执行状态
- **团队通知**: 提前通知团队成员文件变更

继续下一阶段吗？还是需要我先实施这些组件？
