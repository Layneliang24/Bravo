#!/bin/bash
# Git保护监控和自动恢复脚本
# 防止保护机制被意外或恶意破坏

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/protection-monitor.log"
PROTECTION_CONFIG="$PROJECT_ROOT/.git-protection-config"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 记录日志函数
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $1" | tee -a "$LOG_FILE"
}

# 检查当前alias状态
check_alias_status() {
    local current_alias=$(alias git 2>/dev/null || echo "NOT_SET")
    local expected_alias="alias git='bash \"$PROJECT_ROOT/scripts-golden/git-guard.sh\"'"

    if [[ "$current_alias" == *"git-guard.sh"* ]]; then
        echo "PROTECTED"
    elif [[ "$current_alias" == "NOT_SET" ]]; then
        echo "NOT_SET"
    else
        echo "COMPROMISED"
    fi
}

# 检查bashrc配置
check_bashrc_config() {
    local bashrc_path="$HOME/.bashrc"
    if [[ -f "$bashrc_path" ]] && grep -q "git-guard.sh" "$bashrc_path"; then
        echo "CONFIGURED"
    else
        echo "MISSING"
    fi
}

# 检查危险环境变量
check_dangerous_env_vars() {
    local dangerous_vars=(
        "ALLOW_PUSH_WITHOUT_PASSPORT"
        "SKIP_VALIDATION"
        "DISABLE_VALIDATION"
        "PRE_COMMIT_ALLOW_NO_CONFIG"
        "BYPASS_PROTECTION"
        "NO_GUARD"
        "DISABLE_GUARD"
    )

    local found_vars=()
    for var in "${dangerous_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            found_vars+=("$var=${!var}")
        fi
    done

    if [[ ${#found_vars[@]} -gt 0 ]]; then
        echo "COMPROMISED:${found_vars[*]}"
    else
        echo "SAFE"
    fi
}

# 清理危险环境变量
cleanup_dangerous_env_vars() {
    local dangerous_vars=(
        "ALLOW_PUSH_WITHOUT_PASSPORT"
        "SKIP_VALIDATION"
        "DISABLE_VALIDATION"
        "PRE_COMMIT_ALLOW_NO_CONFIG"
        "BYPASS_PROTECTION"
        "NO_GUARD"
        "DISABLE_GUARD"
    )

    local cleaned_vars=()
    for var in "${dangerous_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            unset "$var"
            cleaned_vars+=("$var")
        fi
    done

    if [[ ${#cleaned_vars[@]} -gt 0 ]]; then
        log_message "🧹 CLEANUP | 已清理危险环境变量: ${cleaned_vars[*]}"
        return 0
    else
        return 1
    fi
}

# 自动恢复保护
restore_protection() {
    local reason="$1"
    log_message "🔧 RESTORE | $reason - 正在恢复git保护..."

    # 1. 恢复当前会话alias
    alias git="bash \"$PROJECT_ROOT/scripts-golden/git-guard.sh\""
    log_message "✅ RESTORE | 当前会话alias已恢复"

    # 2. 恢复依赖管理拦截器alias
    alias npm="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" npm"
    alias yarn="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" yarn"
    alias pnpm="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" pnpm"
    alias pip="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" pip"
    alias pip3="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" pip3"
    alias apt="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" apt"
    alias apt-get="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" apt-get"
    alias yum="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" yum"
    alias dnf="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" dnf"
    alias brew="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" brew"
    alias composer="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" composer"
    alias python="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" python"
    alias python3="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" python3"
    alias source="bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" source"
    log_message "✅ RESTORE | 依赖管理拦截器已恢复"

    # 3. 检查并恢复bashrc配置
    local bashrc_path="$HOME/.bashrc"
    local git_alias_line="alias git='bash \"$PROJECT_ROOT/scripts-golden/git-guard.sh\"'"

    if [[ -f "$bashrc_path" ]]; then
        # 恢复git保护alias
        if ! grep -q "git-guard.sh" "$bashrc_path"; then
            echo "# Git --no-verify 保护 (自动恢复)" >> "$bashrc_path"
            echo "$git_alias_line" >> "$bashrc_path"
            log_message "✅ RESTORE | ~/.bashrc Git保护配置已恢复"
        fi

        # 恢复依赖管理拦截器alias
        if ! grep -q "dependency-guard.sh" "$bashrc_path"; then
            echo "# 依赖管理拦截器 (纯Docker环境保护)" >> "$bashrc_path"
            echo "alias npm='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" npm'" >> "$bashrc_path"
            echo "alias yarn='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" yarn'" >> "$bashrc_path"
            echo "alias pnpm='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" pnpm'" >> "$bashrc_path"
            echo "alias pip='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" pip'" >> "$bashrc_path"
            echo "alias pip3='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" pip3'" >> "$bashrc_path"
            echo "alias apt='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" apt'" >> "$bashrc_path"
            echo "alias apt-get='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" apt-get'" >> "$bashrc_path"
            echo "alias brew='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" brew'" >> "$bashrc_path"
            echo "alias composer='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" composer'" >> "$bashrc_path"
            echo "alias python='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" python'" >> "$bashrc_path"
            echo "alias python3='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" python3'" >> "$bashrc_path"
            echo "alias source='bash \"$PROJECT_ROOT/scripts-golden/dependency-guard.sh\" source'" >> "$bashrc_path"
            log_message "✅ RESTORE | ~/.bashrc 依赖管理拦截器配置已恢复"
        fi
    fi

    # 3. 更新保护状态记录（merge操作时跳过，避免冲突）
    # 检查是否是merge操作
    if git rev-parse --verify MERGE_HEAD >/dev/null 2>&1; then
        log_message "⏭️  MERGE | 检测到merge操作，跳过时间戳更新（避免冲突）"
        return 0
    fi

    echo "$(date '+%Y-%m-%d %H:%M:%S') | RESTORED | $reason" > "$PROTECTION_CONFIG"

    # 4. 发出警告
    echo ""
    echo "🚨🚨🚨 GIT保护已自动恢复 🚨🚨🚨"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  检测到git保护被篡改: $reason"
    echo "🔧 已自动恢复保护机制"
    echo "📋 如果这是预期行为，请联系架构负责人"
    echo "📊 详细日志: $LOG_FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# 主检查函数
main_check() {
    local alias_status=$(check_alias_status)
    local bashrc_status=$(check_bashrc_config)
    local env_status=$(check_dangerous_env_vars)
    local protection_compromised=false

    # 检查环境变量安全
    if [[ "$env_status" =~ ^COMPROMISED: ]]; then
        local found_vars="${env_status#COMPROMISED:}"
        log_message "🚨 SECURITY | 检测到危险环境变量: $found_vars"

        # 立即清理危险环境变量
        if cleanup_dangerous_env_vars; then
            log_message "🔒 SECURITY | 环境变量已自动清理"
            # 发送安全警告
            echo ""
            echo "🚨🚨🚨 安全威胁已阻止 🚨🚨🚨"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "⚠️  检测到AI尝试设置绕过环境变量: $found_vars"
            echo "🧹 已自动清理所有危险环境变量"
            echo "🔒 保护机制持续生效"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
        fi
        protection_compromised=true
    fi

    # 检查alias保护
    case "$alias_status" in
        "PROTECTED")
            if [[ "$protection_compromised" == "false" ]]; then
                log_message "✅ CHECK | Git保护正常工作"
            fi
            ;;
        "NOT_SET")
            restore_protection "Alias未设置"
            protection_compromised=true
            ;;
        "COMPROMISED")
            restore_protection "Alias被修改为: $(alias git 2>/dev/null)"
            protection_compromised=true
            ;;
    esac

    # 检查bashrc配置
    if [[ "$bashrc_status" == "MISSING" ]]; then
        restore_protection "Bashrc配置丢失"
        protection_compromised=true
    fi

    if [[ "$protection_compromised" == "true" ]]; then
        return 1
    else
        return 0
    fi
}

# 守护进程模式
daemon_mode() {
    local check_interval=30  # 30秒检查一次
    log_message "🛡️ DAEMON | 启动git保护监控守护进程 (间隔: ${check_interval}s)"

    while true; do
        main_check > /dev/null 2>&1
        sleep $check_interval
    done
}

# 安装系统级保护
install_system_protection() {
    log_message "🔧 INSTALL | 安装系统级保护..."

    # 1. 创建定时检查的crontab任务
    local cron_job="* * * * * cd '$PROJECT_ROOT' && bash scripts/git-protection-monitor.sh check >> /dev/null 2>&1"

    # 检查crontab是否已存在
    if ! crontab -l 2>/dev/null | grep -q "git-protection-monitor"; then
        (crontab -l 2>/dev/null; echo "$cron_job") | crontab -
        log_message "✅ INSTALL | Crontab定时检查已安装"
    else
        log_message "⚠️  INSTALL | Crontab任务已存在"
    fi

    # 2. 创建shell启动时的自动检查
    local shell_check_line="bash '$PROJECT_ROOT/scripts/git-protection-monitor.sh' check 2>/dev/null || true"

    if [[ -f "$HOME/.bashrc" ]]; then
        if ! grep -q "git-protection-monitor" "$HOME/.bashrc"; then
            echo "# Git保护自动检查" >> "$HOME/.bashrc"
            echo "$shell_check_line" >> "$HOME/.bashrc"
            log_message "✅ INSTALL | Shell启动检查已安装"
        fi
    fi

    # 3. 创建git pre-command hook
    cat > "$PROJECT_ROOT/.git/hooks/pre-command" << 'EOF'
#!/bin/bash
# Git命令执行前的保护检查
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -f "$PROJECT_ROOT/scripts/git-protection-monitor.sh" ]]; then
    bash "$PROJECT_ROOT/scripts/git-protection-monitor.sh" check
fi
EOF
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-command" 2>/dev/null || true

    log_message "🎉 INSTALL | 系统级保护安装完成"
}

# 创建不可变的保护脚本备份
create_immutable_backup() {
    local backup_dir="$PROJECT_ROOT/.git-protection-backup"
    mkdir -p "$backup_dir"

    # 备份关键文件
    cp "$PROJECT_ROOT/scripts-golden/git-guard.sh" "$backup_dir/git-guard.sh.backup"
    cp "$0" "$backup_dir/git-protection-monitor.sh.backup"

    # 创建校验和
    sha256sum "$PROJECT_ROOT/scripts-golden/git-guard.sh" > "$backup_dir/checksums.txt"
    sha256sum "$0" >> "$backup_dir/checksums.txt"

    # 设置只读权限
    chmod 444 "$backup_dir"/*.backup 2>/dev/null || true
    chmod 444 "$backup_dir/checksums.txt" 2>/dev/null || true

    log_message "💾 BACKUP | 不可变备份已创建"
}

# 验证文件完整性
verify_integrity() {
    local backup_dir="$PROJECT_ROOT/.git-protection-backup"
    if [[ -f "$backup_dir/checksums.txt" ]]; then
        if sha256sum -c "$backup_dir/checksums.txt" >/dev/null 2>&1; then
            log_message "✅ INTEGRITY | 保护文件完整性验证通过"
            return 0
        else
            log_message "🚨 INTEGRITY | 保护文件被篡改，正在恢复..."
            # 从备份恢复
            cp "$backup_dir/git-guard.sh.backup" "$PROJECT_ROOT/scripts-golden/git-guard.sh"
            cp "$backup_dir/git-protection-monitor.sh.backup" "$0"
            chmod +x "$PROJECT_ROOT/scripts-golden/git-guard.sh"
            chmod +x "$0"
            return 1
        fi
    fi
}

# 教育用户函数
educate_user() {
    cat << EOF

📚 Git保护系统使用须知
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 为什么不能随意修改git alias:

1. 🏗️ 架构保护: 防止破坏npm workspaces和依赖管理
2. 🔍 质量控制: 确保pre-commit检查不被绕过
3. 📊 审计需求: 记录所有git操作用于问题追踪
4. 🛡️ 安全合规: 防止恶意代码注入

🚨 为什么不能在宿主机安装依赖:

1. 🐳 纯Docker环境: 项目严格遵循纯Docker开发原则
2. 🔧 环境一致性: 确保开发、测试、生产环境完全一致
3. 📦 依赖隔离: 防止宿主机环境污染和版本冲突
4. 🚀 CI/CD保证: 保证流水线执行环境的可重现性

✅ 正确的开发流程:

Git操作相关:
• 如需临时禁用检查，使用环境变量:
  export ALLOW_PROTECTED_BRANCH_OPERATIONS=true
• 如需永久调整规则，修改配置文件:
  scripts/git-guard.sh 中的检查逻辑

依赖管理相关:
• 所有依赖操作必须在Docker容器内进行:
  docker-compose exec frontend npm install [package]
  docker-compose exec backend pip install [package]
• 如需临时绕过依赖拦截:
  export ALLOW_HOST_DEPENDENCY_INSTALL=true
• 紧急确认码: DOCKER_NATIVE_BYPASS

⚠️  不要尝试绕过保护系统:
• 不要修改 ~/.bashrc 中的alias
• 不要直接调用 /usr/bin/npm 或系统包管理器
• 不要删除或修改保护脚本
• 不要在宿主机安装依赖，噗你阿母试试！！！

🐳 纯Docker开发原则:
• 宿主机只保留: Git, Docker, 代码编辑器
• 所有开发工具: Node.js, Python, 依赖包都在容器内
• 容器内开发，宿主机编辑

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF
}

# 主程序逻辑
case "${1:-check}" in
    "check")
        main_check
        ;;
    "daemon")
        daemon_mode
        ;;
    "install")
        install_system_protection
        create_immutable_backup
        main_check
        ;;
    "restore")
        restore_protection "手动恢复请求"
        ;;
    "verify")
        verify_integrity
        ;;
    "educate"|"help")
        educate_user
        ;;
    *)
        echo "使用方法: $0 {check|daemon|install|restore|verify|educate}"
        echo ""
        echo "  check    - 检查并自动修复保护状态"
        echo "  daemon   - 启动后台监控守护进程"
        echo "  install  - 安装系统级保护机制"
        echo "  restore  - 强制恢复保护配置"
        echo "  verify   - 验证保护文件完整性"
        echo "  educate  - 显示使用须知"
        ;;
esac
