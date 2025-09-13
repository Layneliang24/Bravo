#!/bin/bash
# 分支保护脚本

current_branch=$(git rev-parse --abbrev-ref HEAD)

if [ "$current_branch" = "main" ] || [ "$current_branch" = "dev" ]; then
    echo "⚠️  正在推送到保护分支: $current_branch"
    echo "🔍 确保代码已通过审查和测试"

    if [ -f "test_all.sh" ]; then
        echo "🧪 运行快速测试检查..."
        bash test_all.sh
        if [ $? -ne 0 ]; then
            echo "❌ 测试失败，推送被阻止"
            echo "💡 请修复测试问题后再推送"
            exit 1
        fi
    else
        echo "⚠️  未找到测试脚本，跳过测试检查"
    fi

    echo "✅ 保护分支检查通过"
fi
