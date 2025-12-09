#!/bin/bash
# 安装VSCode/Cursor推荐扩展

set -e

echo "🔌 安装VSCode/Cursor推荐扩展..."

# 检查code命令是否可用
if ! command -v code &> /dev/null; then
    echo "❌ 错误: 'code' 命令不可用"
    echo "请确保已安装VS Code或Cursor，并将code命令添加到PATH"
    echo ""
    echo "Windows上，通常需要："
    echo "1. 打开Cursor"
    echo "2. 按 Ctrl+Shift+P"
    echo "3. 输入 'Shell Command: Install code command in PATH'"
    echo "4. 选择该命令执行"
    exit 1
fi

# 扩展列表
EXTENSIONS=(
    "ms-python.black-formatter"
    "ms-python.isort"
    "esbenp.prettier-vscode"
    "ms-python.python"
    "ms-python.vscode-pylance"
    "Vue.volar"
    "Vue.vscode-typescript-vue-plugin"
)

# 安装扩展
INSTALLED=0
FAILED=0

for ext in "${EXTENSIONS[@]}"; do
    echo ""
    echo "📦 安装: $ext"
    if code --install-extension "$ext" --force 2>&1; then
        echo "✅ 成功安装: $ext"
        ((INSTALLED++))
    else
        echo "❌ 安装失败: $ext"
        ((FAILED++))
    fi
done

echo ""
echo "=========================================="
echo "📊 安装结果汇总"
echo "=========================================="
echo "✅ 成功安装: $INSTALLED 个扩展"
if [ $FAILED -gt 0 ]; then
    echo "❌ 安装失败: $FAILED 个扩展"
    echo ""
    echo "💡 提示: 如果某些扩展安装失败，可以："
    echo "1. 在Cursor中手动安装（Ctrl+Shift+X打开扩展面板）"
    echo "2. 或者稍后重试此脚本"
    exit 1
else
    echo "🎉 所有扩展安装成功！"
    exit 0
fi
