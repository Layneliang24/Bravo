#!/bin/bash
# Husky自动同步脚本 - 一劳永逸解决手动同步问题
# 监听.husky/文件变化，自动同步到.git/hooks/

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HUSKY_DIR="$PROJECT_ROOT/.husky"
GIT_HOOKS_DIR="$PROJECT_ROOT/.git/hooks"

sync_hook() {
    local hook_name="$1"
    local husky_file="$HUSKY_DIR/$hook_name"
    local git_file="$GIT_HOOKS_DIR/$hook_name"

    if [ -f "$husky_file" ]; then
        echo "🔄 同步 $hook_name: .husky/ → .git/hooks/"
        cp "$husky_file" "$git_file"
        chmod +x "$git_file"
        echo "✅ $hook_name 同步完成"
    fi
}

# 同步所有常用hooks
sync_hook "pre-commit"
sync_hook "pre-push"
sync_hook "commit-msg"
sync_hook "post-commit"
sync_hook "post-checkout"

echo ""
echo "🎉 Husky hooks自动同步完成！"
echo "📋 修改.husky/文件后运行此脚本即可同步"
echo ""
echo "💡 添加到package.json scripts中："
echo '   "sync-hooks": "bash scripts/auto-sync-hooks.sh"'
echo ""
echo "🚀 使用方式: npm run sync-hooks"
