#!/bin/bash
# Git保护自动修复和加固脚本
# 在每次git操作前自动检查和修复保护机制

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 快速检查函数（性能优化，避免每次git调用都很慢）
quick_protection_check() {
    # 检查关键alias是否存在
    if ! alias git 2>/dev/null | grep -q "git-guard.sh"; then
        return 1  # 保护被破坏
    fi
    
    # 检查保护脚本是否存在
    if [[ ! -f "$PROJECT_ROOT/scripts/git-guard.sh" ]]; then
        return 1  # 文件丢失
    fi
    
    return 0  # 保护正常
}

# 快速修复函数
quick_fix() {
    # 立即恢复alias
    alias git="bash \"$PROJECT_ROOT/scripts/git-guard.sh\""
    
    # 如果脚本丢失，从备份恢复
    if [[ ! -f "$PROJECT_ROOT/scripts/git-guard.sh" ]] && [[ -f "$PROJECT_ROOT/.git-protection-backup/git-guard.sh.backup" ]]; then
        cp "$PROJECT_ROOT/.git-protection-backup/git-guard.sh.backup" "$PROJECT_ROOT/scripts/git-guard.sh"
        chmod +x "$PROJECT_ROOT/scripts/git-guard.sh"
    fi
}

# 主逻辑：快速检查，必要时修复
if ! quick_protection_check; then
    quick_fix
    echo "⚠️  Git保护已自动修复" >&2
fi
