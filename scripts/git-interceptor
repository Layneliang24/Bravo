#!/bin/bash
# Git --no-verify 终极拦截脚本
# 这个脚本会放在PATH最前面，拦截所有git调用

LOG_FILE="$(pwd)/logs/git-no-verify-attempts.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 检查是否在保护分支上
check_protected_branch() {
    local current_branch=$(git branch --show-current 2>/dev/null)
    [[ "$current_branch" =~ ^(dev|main|master)$ ]]
}

# 保护分支违规处理函数
show_protected_branch_warning() {
    local operation="$1"
    local command_full="$2"

    echo "🛡️🛡️🛡️ 保护分支修改被拦截！🛡️🛡️🛡️"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 检测到在保护分支上尝试修改操作！"
    echo ""
    echo "📋 当前分支：$(git branch --show-current 2>/dev/null)"
    echo "🚫 禁止操作：$operation"
    echo ""
    echo "✅ 正确的开发流程："
    echo "   1. 创建feature分支：git checkout -b feature/your-feature-name"
    echo "   2. 在feature分支上进行开发和提交"
    echo "   3. 推送feature分支：git push origin feature/your-feature-name"
    echo "   4. 创建PR合并到dev分支"
    echo ""
    echo "🔧 快速创建feature分支："
    echo "   git checkout -b feature/quick-fix-$(date +%m%d-%H%M)"
    echo ""
    echo "⚠️  紧急情况绕过（极度不推荐）："
    echo "   export ALLOW_PROTECTED_BRANCH_OPERATIONS=true"
    echo "   或输入紧急确认码：HOTFIX_EMERGENCY_BYPASS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 记录违规尝试
    echo "$(date '+%Y-%m-%d %H:%M:%S') | PROTECTED_BRANCH | $(git branch --show-current) | $operation | $command_full" >> "$LOG_FILE"

    # 检查环境变量绕过
    if [[ "$ALLOW_PROTECTED_BRANCH_OPERATIONS" == "true" ]]; then
        echo "🟡 检测到环境变量绕过，允许继续操作"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | PROTECTED_BYPASS_ENV | $operation | $command_full" >> "$LOG_FILE"
        return 0
    fi

    # 询问紧急确认码
    echo ""
    read -p "紧急确认码: " response
    if [[ "$response" == "HOTFIX_EMERGENCY_BYPASS" ]]; then
        echo "🟡 紧急绕过确认，允许继续操作"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | PROTECTED_BYPASS_EMERGENCY | $operation | $command_full" >> "$LOG_FILE"
        return 0
    else
        echo "❌ 操作被取消 - 请切换到feature分支进行开发！"
        echo "💡 推荐命令：git checkout -b feature/$(whoami)-$(date +%m%d)"
        exit 1
    fi
}

# 通用违规处理函数
show_violation_warning() {
    local violation_type="$1"
    local command_full="$2"

    echo "🚨🚨🚨 检测到严重违规：$violation_type 🚨🚨🚨"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 绝对禁止的Git操作！"
    echo "📋 基于30轮修复血泪教训，这会导致："
    echo "   • npm workspaces依赖漂移"
    echo "   • 代码质量检查被绕过"
    echo "   • 架构违规问题扩散"
    echo "   • 分支保护策略被绕过"
    echo ""
    echo "✅ 正确的解决方案："
    echo "   1. 修复检查发现的问题"
    echo "   2. 如果检查有误报，更新检查规则"
    echo "   3. 使用PR流程合并到保护分支"
    echo "   4. 紧急情况联系架构负责人"
    echo ""
    echo "🔗 详细文档："
    echo "   • docs/architecture/ADR-001-npm-workspaces.md"
    echo "   • docs/architecture/cursor-git-no-verify-fix.md"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 记录违规尝试
    echo "$(date '+%Y-%m-%d %H:%M:%S') | BLOCKED | $violation_type | $command_full" >> "$LOG_FILE"

    # 询问是否强制继续（可选）
    echo ""
    echo "⚠️  如果您确实需要强制继续（极度不推荐）："
    echo "请输入完整确认码: I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS"
    read -p "确认码: " response
    if [[ "$response" != "I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS" ]]; then
        echo "❌ 操作被取消 - 这是明智的选择！"
        echo "💡 请修复问题后重新尝试"
        exit 1
    else
        echo "⚠️  强制继续，但违规行为已记录"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | FORCED | $violation_type | $command_full" >> "$LOG_FILE"
    fi
}

# 保护分支修改检查（在所有其他检查之前）
if check_protected_branch; then
    case "$1" in
        add)
            show_protected_branch_warning "添加文件到暂存区 (git add)" "git $*"
            ;;
        commit)
            # 检查是否是--no-verify，如果是则先处理--no-verify拦截
            if [[ "$*" =~ (^|[[:space:]])--no-verify([[:space:]]|$) || "$*" =~ (^|[[:space:]])-n([[:space:]]|$) ]]; then
                show_violation_warning "commit --no-verify" "git $*"
            else
                show_protected_branch_warning "提交更改 (git commit)" "git $*"
            fi
            ;;
        cherry-pick)
            show_protected_branch_warning "挑选提交 (git cherry-pick)" "git $*"
            ;;
        revert)
            show_protected_branch_warning "撤销提交 (git revert)" "git $*"
            ;;
        apply)
            show_protected_branch_warning "应用补丁 (git apply)" "git $*"
            ;;
        stash)
            if [[ "$*" =~ (^|[[:space:]])(pop|apply)([[:space:]]|$) ]]; then
                show_protected_branch_warning "恢复暂存 (git stash $2)" "git $*"
            fi
            ;;
        merge)
            # merge操作提供更温和的提示，允许PR合并
            echo "⚠️  在保护分支$(git branch --show-current)上执行merge操作"
            echo "如果这是PR合并流程，请确认继续；如果是手动合并，建议切换到feature分支"
            echo ""
            read -p "这是PR合并流程吗？(y/N): " confirm
            if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
                show_protected_branch_warning "手动合并操作 (git merge)" "git $*"
            fi
            ;;
    esac
fi

# 检测commit --no-verify参数
if [[ "$1" == "commit" ]] && [[ "$*" =~ (^|[[:space:]])--no-verify([[:space:]]|$) || "$*" =~ (^|[[:space:]])-n([[:space:]]|$) ]]; then
    show_violation_warning "commit --no-verify" "git $*"
fi

# 检测push --no-verify参数
if [[ "$1" == "push" ]] && [[ "$*" =~ (^|[[:space:]])--no-verify([[:space:]]|$) || "$*" =~ (^|[[:space:]])-n([[:space:]]|$) ]]; then
    show_violation_warning "push --no-verify" "git $*"
fi

# 检测强制推送参数（最高优先级危险操作）
if [[ "$1" == "push" ]] && [[ "$*" =~ (^|[[:space:]])(-f|--force|--force-with-lease|--force-if-includes)([[:space:]]|$) ]]; then
    # 确定具体的强制推送类型
    local force_type=""
    if [[ "$*" =~ (^|[[:space:]])--force-with-lease([[:space:]]|$) ]]; then
        force_type="push --force-with-lease"
    elif [[ "$*" =~ (^|[[:space:]])--force-if-includes([[:space:]]|$) ]]; then
        force_type="push --force-if-includes"
    elif [[ "$*" =~ (^|[[:space:]])--force([[:space:]]|$) ]]; then
        force_type="push --force"
    elif [[ "$*" =~ (^|[[:space:]])-f([[:space:]]|$) ]]; then
        force_type="push -f"
    fi
    show_violation_warning "强制推送 ($force_type)" "git $*"
fi

# 检测数据丢失类操作（高优先级危险操作）
if [[ "$1" == "reset" ]] && [[ "$*" =~ (^|[[:space:]])--hard([[:space:]]|$) ]]; then
    show_violation_warning "数据丢失操作 (reset --hard)" "git $*"
fi

if [[ "$1" == "clean" ]] && [[ "$*" =~ (^|[[:space:]])-[a-zA-Z]*f[a-zA-Z]*d[a-zA-Z]*([[:space:]]|$) || "$*" =~ (^|[[:space:]])-[a-zA-Z]*d[a-zA-Z]*f[a-zA-Z]*([[:space:]]|$) ]]; then
    show_violation_warning "数据丢失操作 (clean -fd)" "git $*"
fi

if [[ "$1" == "checkout" ]] && [[ "$*" =~ (^|[[:space:]])\.([[:space:]]|$) ]]; then
    show_violation_warning "数据丢失操作 (checkout . - 丢弃所有工作区更改)" "git $*"
fi

# 检测分支破坏类操作（中优先级危险操作）
if [[ "$1" == "branch" ]] && [[ "$*" =~ (^|[[:space:]])-D([[:space:]]|$) ]]; then
    show_violation_warning "分支破坏操作 (branch -D - 强制删除分支)" "git $*"
fi

if [[ "$1" == "rebase" ]] && [[ "$*" =~ (^|[[:space:]])-i([[:space:]]|$) ]]; then
    show_violation_warning "分支破坏操作 (rebase -i - 交互式变基)" "git $*"
fi

if [[ "$1" == "tag" ]] && [[ "$*" =~ (^|[[:space:]])-d([[:space:]]|$) ]]; then
    show_violation_warning "分支破坏操作 (tag -d - 删除标签)" "git $*"
fi

# 检测直接推送到保护分支
if [[ "$1" == "push" ]]; then
    # 解析push命令参数
    for arg in "$@"; do
        case $arg in
            origin/dev|dev)
                show_violation_warning "直接推送到dev分支" "git $*"
                ;;
            origin/main|main|origin/master|master)
                show_violation_warning "直接推送到main分支" "git $*"
                ;;
        esac
    done

    # 检查是否尝试推送到保护分支（更全面的检测）
    if echo "$*" | grep -qE "(origin/)?(dev|main|master)( |$)"; then
        # 如果没有指定远程和分支，检查当前分支
        current_branch=$(git branch --show-current 2>/dev/null)
        if [[ "$current_branch" == "dev" ]] || [[ "$current_branch" == "main" ]] || [[ "$current_branch" == "master" ]]; then
            if ! echo "$*" | grep -q ":"; then  # 没有指定目标分支
                show_violation_warning "从保护分支${current_branch}直接推送" "git $*"
            fi
        fi
    fi
fi

# 找到真正的git并执行
if [[ -x "/usr/bin/git" ]]; then
    exec "/usr/bin/git" "$@"
elif [[ -x "/usr/local/bin/git" ]]; then
    exec "/usr/local/bin/git" "$@"
elif [[ -x "/c/Program Files/Git/bin/git.exe" ]]; then
    exec "/c/Program Files/Git/bin/git.exe" "$@"
elif [[ -x "/mingw64/bin/git" ]]; then
    exec "/mingw64/bin/git" "$@"
else
    # 使用command命令找到系统git
    exec "$(command -v git)" "$@"
fi
