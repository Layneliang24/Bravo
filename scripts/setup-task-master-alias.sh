#!/bin/bash
# 设置task-master别名，自动使用包装脚本

WRAPPER_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/task-master-wrapper.sh"

# 检查shell类型并添加别名
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# 添加别名（如果不存在）
if ! grep -q "alias task-master=" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Task-Master包装（自动PRD状态验证）" >> "$SHELL_RC"
    echo "alias task-master='$WRAPPER_PATH'" >> "$SHELL_RC"
    echo "✅ 已添加task-master别名到 $SHELL_RC"
    echo "请运行: source $SHELL_RC"
else
    echo "⚠️  task-master别名已存在"
fi
