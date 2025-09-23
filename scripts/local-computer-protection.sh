#!/bin/bash
# 当前电脑专用的Git --no-verify保护脚本
# 这个脚本只为当前电脑环境优化，不考虑可移植性

PROJECT_ROOT="/s/WorkShop/cursor/Bravo"
LOG_FILE="$PROJECT_ROOT/logs/git-no-verify-attempts.log"

echo "���️ 激活当前电脑的Git --no-verify保护..."

# 1. 设置Shell alias
echo "1. 设置Shell alias..."
alias git="bash \"$PROJECT_ROOT/scripts/git-guard.sh\""

# 2. 检查.vscode设置
echo "2. 检查Cursor IDE设置..."
if grep -q '"git.allowNoVerifyCommit": false' "$PROJECT_ROOT/.vscode/settings.json"; then
    echo "✅ Cursor IDE配置正确"
else
    echo "⚠️ 建议检查.vscode/settings.json配置"
fi

# 3. 检查保护日志
echo "3. 当前保护状态："
if [ -f "$LOG_FILE" ]; then
    echo "��� 最近的拦截记录："
    tail -3 "$LOG_FILE" | while read line; do
        echo "   $line"
    done
else
    echo "��� 暂无拦截记录"
fi

echo ""
echo "��� 当前电脑保护已激活！"
echo "⚡ 虽然不可移植到其他电脑，但在当前环境完全有效"

