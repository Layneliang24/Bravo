#!/bin/bash
# 工作流持续验证脚本
# 用途：每次修改工作流文件时自动验证其正确性

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATION_REPORT="$PROJECT_ROOT/.workflow-validation-report.json"
VALIDATION_LOG="$PROJECT_ROOT/.workflow-validation.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$VALIDATION_LOG"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$VALIDATION_LOG"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$VALIDATION_LOG"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$VALIDATION_LOG"
}

# 初始化
init_validation() {
    log_info "初始化工作流验证环境..."
    > "$VALIDATION_LOG"

    # 检查必要工具
    local missing_tools=()

    if ! command -v act &> /dev/null; then
        missing_tools+=("act")
    fi

    if ! command -v gh &> /dev/null; then
        missing_tools+=("gh")
    fi

    if [ ${#missing_tools[@]} -gt 0 ]; then
        log_warning "缺少工具: ${missing_tools[*]}"
        log_info "建议安装: choco install act-cli github-cli"
    fi
}

# 检测工作流文件变更
detect_workflow_changes() {
    log_info "检测工作流文件变更..."

    # 获取变更的工作流文件
    local changed_workflows=""

    if git rev-parse --verify HEAD &> /dev/null; then
        # 检查staged的变更
        changed_workflows=$(git diff --cached --name-only --diff-filter=AM | grep "^.github/workflows/" || true)

        # 如果没有staged变更，检查未staged的变更
        if [ -z "$changed_workflows" ]; then
            changed_workflows=$(git diff --name-only --diff-filter=AM | grep "^.github/workflows/" || true)
        fi
    fi

    if [ -z "$changed_workflows" ]; then
        log_info "未检测到工作流文件变更"
        return 1
    fi

    log_info "检测到变更的工作流:"
    echo "$changed_workflows" | while read -r file; do
        log_info "  - $file"
    done

    echo "$changed_workflows"
    return 0
}

# act语法验证
validate_with_act() {
    local workflow_file="$1"
    log_info "使用act验证工作流语法: $workflow_file"

    local workflow_name=$(basename "$workflow_file")
    local validation_result=0

    # 1. 列出jobs
    log_info "  └─ 列出jobs..."
    if act -l -W "$workflow_file" > /tmp/act-list.txt 2>&1; then
        local job_count=$(grep -c "^[0-9]" /tmp/act-list.txt || echo "0")
        log_success "    ✓ 发现 $job_count 个jobs"
    else
        log_error "    ✗ 无法列出jobs"
        validation_result=1
    fi

    # 2. 语法检查（dry-run）
    log_info "  └─ Dry-run检查..."
    if timeout 30 act push -W "$workflow_file" -n --job detect-branch-context > /tmp/act-dryrun.txt 2>&1; then
        log_success "    ✓ 语法检查通过"
    else
        # 检查是否是超时或其他错误
        if grep -q "workflow is not configured for push" /tmp/act-dryrun.txt; then
            log_warning "    ⚠ 工作流未配置push触发器"
        else
            log_error "    ✗ 语法检查失败"
            cat /tmp/act-dryrun.txt | tail -10 | tee -a "$VALIDATION_LOG"
            validation_result=1
        fi
    fi

    return $validation_result
}

# 验证工作流结构完整性
validate_workflow_structure() {
    local workflow_file="$1"
    log_info "验证工作流结构: $workflow_file"

    local validation_result=0

    # 检查必要的字段
    if ! grep -q "^name:" "$workflow_file"; then
        log_error "  ✗ 缺少 'name' 字段"
        validation_result=1
    fi

    if ! grep -q "^on:" "$workflow_file" && ! grep -q "^\"on\":" "$workflow_file"; then
        log_error "  ✗ 缺少 'on' 触发器"
        validation_result=1
    fi

    if ! grep -q "^jobs:" "$workflow_file"; then
        log_error "  ✗ 缺少 'jobs' 定义"
        validation_result=1
    fi

    if [ $validation_result -eq 0 ]; then
        log_success "  ✓ 工作流结构完整"
    fi

    return $validation_result
}

# 生成验证报告
generate_validation_report() {
    log_info "生成验证报告..."

    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local total_workflows=$(find "$PROJECT_ROOT/.github/workflows" -name "*.yml" -type f | wc -l)

    cat > "$VALIDATION_REPORT" << EOF
{
  "timestamp": "$timestamp",
  "validation_run": "continuous",
  "total_workflows": $total_workflows,
  "validation_method": "act + structure_check",
  "results": {
    "syntax_valid": true,
    "structure_valid": true,
    "act_compatible": true
  },
  "recommendations": [
    "定期运行完整GitHub Actions验证",
    "监控实际运行的覆盖率和性能指标",
    "每次修改后使用act快速验证"
  ]
}
EOF

    log_success "验证报告已生成: $VALIDATION_REPORT"
}

# 主验证流程
main_validation() {
    log_info "================================"
    log_info "工作流持续验证开始"
    log_info "================================"

    init_validation

    # 检测变更
    local changed_workflows
    if changed_workflows=$(detect_workflow_changes); then
        local validation_failed=0

        echo "$changed_workflows" | while read -r workflow; do
            if [ -n "$workflow" ]; then
                log_info ""
                log_info "验证: $workflow"
                log_info "---"

                # 结构验证
                if ! validate_workflow_structure "$workflow"; then
                    validation_failed=1
                fi

                # act验证
                if command -v act &> /dev/null; then
                    if ! validate_with_act "$workflow"; then
                        validation_failed=1
                    fi
                else
                    log_warning "  ⚠ act未安装，跳过语法验证"
                fi
            fi
        done

        if [ $validation_failed -eq 0 ]; then
            log_success ""
            log_success "================================"
            log_success "✅ 所有工作流验证通过"
            log_success "================================"
            generate_validation_report
            return 0
        else
            log_error ""
            log_error "================================"
            log_error "❌ 工作流验证失败"
            log_error "================================"
            return 1
        fi
    else
        log_info "跳过验证（无工作流变更）"
        return 0
    fi
}

# 快速验证模式（仅语法）
quick_validation() {
    log_info "快速验证模式"

    local workflow_files=$(find "$PROJECT_ROOT/.github/workflows" -name "*.yml" -type f)
    local failed=0

    for workflow in $workflow_files; do
        if ! validate_workflow_structure "$workflow"; then
            failed=1
        fi
    done

    if [ $failed -eq 0 ]; then
        log_success "✅ 快速验证通过"
    else
        log_error "❌ 快速验证失败"
    fi

    return $failed
}

# 完整验证模式
full_validation() {
    log_info "完整验证模式"

    local workflow_files=$(find "$PROJECT_ROOT/.github/workflows" -name "*.yml" -type f)
    local failed=0

    for workflow in $workflow_files; do
        log_info ""
        log_info "验证: $workflow"

        if ! validate_workflow_structure "$workflow"; then
            failed=1
        fi

        if command -v act &> /dev/null; then
            if ! validate_with_act "$workflow"; then
                failed=1
            fi
        fi
    done

    if [ $failed -eq 0 ]; then
        log_success ""
        log_success "✅ 完整验证通过"
        generate_validation_report
    else
        log_error ""
        log_error "❌ 完整验证失败"
    fi

    return $failed
}

# 命令行参数处理
case "${1:-auto}" in
    "auto")
        main_validation
        ;;
    "quick")
        quick_validation
        ;;
    "full")
        full_validation
        ;;
    "help")
        echo "用法: $0 [auto|quick|full|help]"
        echo ""
        echo "模式:"
        echo "  auto  - 自动检测变更并验证（默认）"
        echo "  quick - 快速验证所有工作流结构"
        echo "  full  - 完整验证所有工作流"
        echo "  help  - 显示帮助"
        ;;
    *)
        log_error "未知命令: $1"
        exit 1
        ;;
esac
