#!/bin/bash
# Git post-merge 钩子：拉取代码后自动检测并部署保护系统
# 实现跨Windows电脑协作的自动生效机制

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# 日志文件
LOG_FILE="logs/auto_deployment.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志函数
log_info() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARN] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" | tee -a "$LOG_FILE"
}

# 检查是否是强制本地测试系统的更新
check_force_local_test_update() {
    log_info "检查是否有强制本地测试系统更新..."

    # 检查最近一次合并是否涉及相关文件
    local changed_files=$(git diff HEAD~1 HEAD --name-only 2>/dev/null || echo "")

    if echo "$changed_files" | grep -qE "(scripts/(git-guard|local_test_passport|one_click_test|setup_cursor_protection)|docs/force_local_test|Makefile.*protection)"; then
        log_info "检测到强制本地测试系统相关文件更新："
        echo "$changed_files" | grep -E "(scripts|docs/force_local_test)" | while read file; do
            log_info "  - $file"
        done
        return 0
    else
        log_info "未检测到强制本地测试系统更新"
        return 1
    fi
}

# 检测Windows环境
detect_windows_environment() {
    local env_type="unknown"

    if [[ -f "/proc/version" ]] && grep -q "Microsoft\|WSL" /proc/version; then
        env_type="WSL"
    elif [[ "$OS" == "Windows_NT" ]]; then
        env_type="Windows"
    elif command -v git.exe &> /dev/null; then
        env_type="Git_Bash"
    fi

    log_info "检测到运行环境: $env_type"
    echo "$env_type"
}

# 检查系统兼容性
check_system_compatibility() {
    log_info "检查系统兼容性..."

    local issues=()

    # 检查Python
    if command -v python3 &> /dev/null; then
        log_info "✅ Python3 可用: $(python3 --version 2>&1)"
    elif command -v python &> /dev/null; then
        log_info "✅ Python 可用: $(python --version 2>&1)"
    else
        issues+=("Python未安装")
    fi

    # 检查Docker
    if command -v docker &> /dev/null; then
        if docker info &> /dev/null; then
            log_info "✅ Docker 服务正常"
        else
            issues+=("Docker服务未启动")
        fi
    else
        issues+=("Docker未安装")
    fi

    # 检查Git
    if command -v git &> /dev/null; then
        log_info "✅ Git 可用: $(git --version)"
    else
        issues+=("Git未安装")
    fi

    if [[ ${#issues[@]} -gt 0 ]]; then
        log_warning "系统兼容性问题："
        for issue in "${issues[@]}"; do
            log_warning "  - $issue"
        done
        return 1
    else
        log_info "✅ 系统兼容性检查通过"
        return 0
    fi
}

# 自动部署保护系统
auto_deploy_protection_system() {
    log_info "开始自动部署保护系统..."

    # 检查安装脚本是否存在
    if [[ ! -f "scripts/setup_cursor_protection.sh" ]]; then
        log_error "安装脚本不存在: scripts/setup_cursor_protection.sh"
        return 1
    fi

    # 检查脚本权限
    if [[ ! -x "scripts/setup_cursor_protection.sh" ]]; then
        log_info "修复安装脚本执行权限..."
        chmod +x scripts/setup_cursor_protection.sh
    fi

    # 运行自动更新
    log_info "执行自动更新..."
    if bash scripts/setup_cursor_protection.sh --auto-update 2>&1 | tee -a "$LOG_FILE"; then
        log_info "✅ 保护系统自动部署成功"

        # 创建部署标记文件
        echo "$(date '+%Y-%m-%d %H:%M:%S'): 自动部署成功" > .force_local_test_auto_deployed

        return 0
    else
        log_error "❌ 保护系统自动部署失败"
        return 1
    fi
}

# 通知用户
notify_user() {
    local deployment_status="$1"

    if [[ "$deployment_status" == "success" ]]; then
        echo ""
        echo "🎉 强制本地测试系统已自动更新完成！"
        echo ""
        echo "📋 新功能现已可用："
        echo "   • make test      - 运行本地测试"
        echo "   • ./test --quick - 快速测试模式"
        echo "   • ./passport     - 检查通行证状态"
        echo ""
        echo "📖 详细说明请查看: docs/CURSOR_PROTECTION_GUIDE.md"
        echo ""
    elif [[ "$deployment_status" == "failed" ]]; then
        echo ""
        echo "⚠️ 强制本地测试系统自动更新失败"
        echo ""
        echo "🔧 手动更新方法："
        echo "   bash scripts/setup_cursor_protection.sh --update"
        echo ""
        echo "📞 如需帮助，请查看:"
        echo "   • docs/force_local_test/FAQ.md"
        echo "   • docs/force_local_test/DEBUG_GUIDE.md"
        echo ""
    elif [[ "$deployment_status" == "manual" ]]; then
        echo ""
        echo "🛡️ 检测到强制本地测试系统更新"
        echo ""
        echo "🚀 建议运行以下命令更新系统："
        echo "   bash scripts/setup_cursor_protection.sh --update"
        echo ""
        echo "⚡ 或者运行快速更新："
        echo "   make setup-protection"
        echo ""
    fi
}

# 主函数
main() {
    log_info "==================== 自动部署检查开始 ===================="
    log_info "项目路径: $PROJECT_ROOT"
    log_info "用户: $(whoami)"
    log_info "主机: $(hostname)"

    # 检测Windows环境
    local windows_env=$(detect_windows_environment)

    # 检查是否有相关更新
    if ! check_force_local_test_update; then
        log_info "无需自动部署，退出"
        return 0
    fi

    # 检查系统兼容性
    if ! check_system_compatibility; then
        log_warning "系统兼容性检查失败，跳过自动部署"
        notify_user "manual"
        return 1
    fi

    # 检查是否已经部署过
    if [[ -f ".force_local_test_auto_deployed" ]]; then
        local last_deploy=$(cat .force_local_test_auto_deployed)
        log_info "系统已自动部署过: $last_deploy"

        # 检查是否需要重新部署（超过1天）
        if [[ $(find .force_local_test_auto_deployed -mtime +1) ]]; then
            log_info "部署时间超过1天，执行重新部署..."
        else
            log_info "最近已部署，跳过自动部署"
            return 0
        fi
    fi

    # 执行自动部署
    if auto_deploy_protection_system; then
        notify_user "success"
        log_info "==================== 自动部署成功 ===================="
        return 0
    else
        notify_user "failed"
        log_error "==================== 自动部署失败 ===================="
        return 1
    fi
}

# 执行主函数
main "$@"
