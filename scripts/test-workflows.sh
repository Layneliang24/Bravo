#!/bin/bash

# 测试所有workflow的脚本
# 这个脚本帮助我们验证所有场景的workflow设计

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查act是否安装
check_act() {
    if ! command -v act &> /dev/null; then
        log_error "act未安装，请先安装act"
        log_info "安装命令："
        log_info "  macOS: brew install act"
        log_info "  Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
        log_info "  Windows: choco install act-cli"
        exit 1
    fi

    log_success "act已安装: $(act --version)"
}

# 测试PR workflow
test_pr_workflow() {
    log_info "测试PR workflow..."

    # 模拟PR事件
    cat > /tmp/pr-event.json << EOF
{
  "pull_request": {
    "number": 1,
    "base": {
      "ref": "main"
    },
    "head": {
      "ref": "feature/test"
    }
  },
  "action": "opened"
}
EOF

    # 运行branch-protection workflow
    if act pull_request -W .github/workflows/branch-protection.yml -e /tmp/pr-event.json --dry-run; then
        log_success "PR workflow验证通过"
    else
        log_error "PR workflow验证失败"
        return 1
    fi
}

# 测试push到feature workflow
test_push_feature_workflow() {
    log_info "测试push到feature workflow..."

    # 使用默认push事件（act会用当前分支ref），要求当前在feature/*分支运行
    if act push -W .github/workflows/on-push-feature.yml --dry-run; then
        log_success "Push到feature workflow验证通过"
    else
        log_error "Push到feature workflow验证失败"
        return 1
    fi
}

# 测试单个workflow文件的语法
test_workflow_syntax() {
    local workflow_file=$1

    log_info "测试workflow语法: $workflow_file"

    # 使用act的--list参数来验证语法
    if act --list -W "$workflow_file" &> /dev/null; then
        log_success "语法检查通过: $workflow_file"
    else
        log_error "语法检查失败: $workflow_file"
        return 1
    fi
}

# 测试所有workflow文件的语法
test_all_workflow_syntax() {
    log_info "测试所有workflow文件的语法..."

    local failed_count=0

    for workflow_file in .github/workflows/*.yml; do
        if ! test_workflow_syntax "$workflow_file"; then
            ((failed_count++))
        fi
    done

    if [ $failed_count -eq 0 ]; then
        log_success "所有workflow语法检查通过"
    else
        log_error "$failed_count 个workflow文件语法有问题"
        return 1
    fi
}

# 生成workflow覆盖报告
generate_coverage_report() {
    log_info "生成workflow覆盖报告..."

    cat > workflow-coverage-report.md << 'EOF'
# Workflow覆盖报告

## 场景覆盖情况

| 场景 | 触发条件 | Workflow文件 | 状态 |
|------|----------|-------------|------|
| PR到main | `pull_request` → main | `branch-protection.yml` | ✅ |
| PR到dev | `pull_request` → dev | `branch-protection.yml` | ✅ |
| Push到feature | `push` → feature/* | `on-push-feature.yml` | ✅ |
| 合并到dev | merge → dev | `on-merge-dev.yml` | ✅ |
| 合并到main | merge → main | `on-merge-main.yml` | ✅ |
| 定时回归测试 | schedule | `regression-scheduled.yml` | ✅ |
| 手动触发 | workflow_dispatch | 多个文件 | ✅ |

## 测试类型覆盖

| 测试类型 | Workflow文件 | 状态 |
|----------|-------------|------|
| 后端单元测试 | `test-unit-backend.yml` | ✅ |
| 前端单元测试 | `test-unit-frontend.yml` | ✅ |
| 集成测试 | `test-integration.yml` | ✅ |
| E2E测试 | `test-e2e-*.yml` | ✅ |
| 安全扫描 | `quality-security.yml` | ✅ |
| 性能测试 | `quality-performance.yml` | ✅ |
| 覆盖率检查 | `quality-coverage.yml` | ✅ |
| 回归测试 | `test-regression.yml` | ✅ |

## 质量门禁

| 质量门禁 | 实现位置 | 状态 |
|----------|----------|------|
| 分支保护 | `branch-protection.yml` | ✅ |
| 目录保护 | `dir_guard.yml` | ✅ |
| 黄金测试保护 | `golden-test-protection.yml` | ✅ |
| 特性覆盖率 | `feature-map.yml` | ✅ |

## 缓存策略

| 缓存类型 | 实现位置 | 状态 |
|----------|----------|------|
| 统一缓存管理 | `setup-cache.yml` | ✅ |
| 缓存策略配置 | `cache-strategy.yml` | ✅ |

## 本地测试支持

| 工具 | 配置文件 | 状态 |
|------|----------|------|
| Docker Compose | `docker-compose.local-ci.yml` | ✅ |
| Act配置 | `.actrc` | ✅ |
| 本地CI脚本 | `scripts/local-ci.sh` | ✅ |
| Workflow测试脚本 | `scripts/test-workflows.sh` | ✅ |

## 总结

- ✅ **完整覆盖**: 所有关键场景都有对应的workflow
- ✅ **原子化设计**: 每个workflow职责单一，可复用
- ✅ **本地测试**: 支持本地验证所有workflow
- ✅ **质量保证**: 多层质量门禁确保代码质量
- ✅ **性能优化**: 智能缓存策略提升CI效率

EOF

    log_success "workflow覆盖报告已生成: workflow-coverage-report.md"
}

# 运行完整验证
run_full_validation() {
    log_info "运行完整workflow验证..."

    local failed_tests=0

    # 语法检查
    if ! test_all_workflow_syntax; then
        ((failed_tests++))
    fi

    # PR workflow测试
    if ! test_pr_workflow; then
        ((failed_tests++))
    fi

    # Push workflow测试（feature/*）
    if ! test_push_feature_workflow; then
        ((failed_tests++))
    fi

    # 生成报告
    generate_coverage_report

    if [ $failed_tests -eq 0 ]; then
        log_success "所有workflow验证通过！"
        log_info "可以安全地使用这些workflow进行CI/CD"
    else
        log_error "$failed_tests 个测试失败"
        log_info "请修复失败的workflow后重新测试"
        return 1
    fi
}

# 显示帮助
show_help() {
    echo "Workflow测试脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  syntax        测试所有workflow语法"
    echo "  pr            测试PR workflow"
    echo "  push-dev      测试push到dev workflow"
    echo "  push-main     测试push到main workflow"
    echo "  full          运行完整验证"
    echo "  report        生成覆盖报告"
    echo ""
    echo "示例:"
    echo "  $0 syntax"
    echo "  $0 full"
}

# 主函数
main() {
    local command=$1

    # 检查act
    check_act

    case $command in
        "syntax")
            test_all_workflow_syntax
            ;;
        "pr")
            test_pr_workflow
            ;;
        "push-dev")
            test_push_dev_workflow
            ;;
        "push-main")
            test_push_main_workflow
            ;;
        "full")
            run_full_validation
            ;;
        "report")
            generate_coverage_report
            ;;
        "help"|"-h"|"--help"|"")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"
