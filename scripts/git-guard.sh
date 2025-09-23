#!/bin/bash
# Git --no-verify 守卫脚本
# 用法：在.bashrc中添加alias git='bash /path/to/scripts/git-guard.sh'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_ROOT/logs/git-no-verify-attempts.log"
mkdir -p "$(dirname "$LOG_FILE")"

# 检测--no-verify参数 (更精确的匹配)
if [[ "$1" == "commit" ]] && [[ "$*" =~ (^|[[:space:]])--no-verify([[:space:]]|$) || "$*" =~ (^|[[:space:]])-n([[:space:]]|$) ]]; then
    echo ""
    echo "🚨🚨🚨 Cursor的--no-verify被拦截！🚨🚨🚨"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 检测到严重违规：禁止使用 --no-verify"
    echo ""
    echo "📋 基于30轮修复血泪教训，--no-verify会导致："
    echo "   • 跳过npm workspaces架构检查"
    echo "   • 绕过代码质量和安全检查"
    echo "   • 导致依赖漂移和构建失败"
    echo ""
    echo "✅ 正确的解决方案："
    echo "   1. 让pre-commit hooks运行并修复发现的问题"
    echo "   2. 如果检查有误报，更新.pre-commit-config.yaml"
    echo "   3. 紧急情况联系架构负责人"
    echo ""
    echo "🔗 详细文档："
    echo "   • docs/architecture/ADR-001-npm-workspaces.md"
    echo "   • docs/architecture/cursor-git-no-verify-fix.md"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # 记录违规尝试
    echo "$(date '+%Y-%m-%d %H:%M:%S') | BLOCKED_BY_GUARD | $*" >> "$LOG_FILE"
    
    echo ""
    echo "⚠️  如果您确实需要跳过检查（极度不推荐）："
    echo "请输入完整确认码: I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS"
    read -p "确认码: " response
    
    if [[ "$response" == "I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS" ]]; then
        echo "⚠️  强制继续，违规行为已记录到日志"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | FORCED_BYPASS | $*" >> "$LOG_FILE"
        # 移除--no-verify参数，让检查正常运行
        args=("$@")
        filtered_args=()
        for arg in "${args[@]}"; do
            if [[ "$arg" != "--no-verify" && "$arg" != "-n" ]]; then
                filtered_args+=("$arg")
            fi
        done
        exec git "${filtered_args[@]}"
    else
        echo "❌ 提交被取消 - 这是明智的选择！"
        echo "💡 请修复检查问题后重新提交"
        exit 1
    fi
fi

# 正常的git命令，直接执行
exec git "$@"
