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
    local expected_alias="alias git='bash \"$PROJECT_ROOT/scripts/git-guard.sh\"'"
    
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

# 自动恢复保护
restore_protection() {
    local reason="$1"
    log_message "🔧 RESTORE | $reason - 正在恢复git保护..."
    
    # 1. 恢复当前会话alias
    alias git="bash \"$PROJECT_ROOT/scripts/git-guard.sh\""
    log_message "✅ RESTORE | 当前会话alias已恢复"
    
    # 2. 检查并恢复bashrc配置
    local bashrc_path="$HOME/.bashrc"
    local expected_line="alias git='bash \"$PROJECT_ROOT/scripts/git-guard.sh\"'"
    
    if [[ -f "$bashrc_path" ]]; then
        if ! grep -q "git-guard.sh" "$bashrc_path"; then
            echo "# Git --no-verify 保护 (自动恢复)" >> "$bashrc_path"
            echo "$expected_line" >> "$bashrc_path"
            log_message "✅ RESTORE | ~/.bashrc配置已恢复"
        fi
    fi
    
    # 3. 更新保护状态记录
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
    
    case "$alias_status" in
        "PROTECTED")
            log_message "✅ CHECK | Git保护正常工作"
            return 0
            ;;
        "NOT_SET")
            restore_protection "Alias未设置"
            return 1
            ;;
        "COMPROMISED")
            restore_protection "Alias被修改为: $(alias git 2>/dev/null)"
            return 1
            ;;
    esac
    
    if [[ "$bashrc_status" == "MISSING" ]]; then
        restore_protection "Bashrc配置丢失"
        return 1
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
    cp "$PROJECT_ROOT/scripts/git-guard.sh" "$backup_dir/git-guard.sh.backup"
    cp "$0" "$backup_dir/git-protection-monitor.sh.backup"
    
    # 创建校验和
    sha256sum "$PROJECT_ROOT/scripts/git-guard.sh" > "$backup_dir/checksums.txt"
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
            cp "$backup_dir/git-guard.sh.backup" "$PROJECT_ROOT/scripts/git-guard.sh"
            cp "$backup_dir/git-protection-monitor.sh.backup" "$0"
            chmod +x "$PROJECT_ROOT/scripts/git-guard.sh"
            chmod +x "$0"
            return 1
        fi
    fi
}

# 教育用户函数
educate_user() {
    cat << 'EOF'

📚 Git保护系统使用须知
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 为什么不能随意修改git alias:

1. 🏗️ 架构保护: 防止破坏npm workspaces和依赖管理
2. 🔍 质量控制: 确保pre-commit检查不被绕过  
3. 📊 审计需求: 记录所有git操作用于问题追踪
4. 🛡️ 安全合规: 防止恶意代码注入

✅ 正确的开发流程:

• 如需临时禁用检查，使用环境变量:
  export ALLOW_PROTECTED_BRANCH_OPERATIONS=true

• 如需永久调整规则，修改配置文件:
  scripts/git-guard.sh 中的检查逻辑

• 紧急情况联系架构负责人

⚠️  不要尝试绕过保护系统:
• 不要修改 ~/.bashrc 中的git alias
• 不要直接调用 /usr/bin/git 或 /mingw64/bin/git  
• 不要删除或修改保护脚本

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
