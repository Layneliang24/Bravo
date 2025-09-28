#!/bin/bash
# 🐍 代码质量检查包装脚本
# 用途：避免pre-commit命名混乱，提供清晰的代码质量检查入口
#
# 这个脚本替代原来的 "pre-commit run" 命令
# 使用重命名的配置文件 .code-quality-config.yaml

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="$PROJECT_ROOT/.code-quality-config.yaml"

echo "🐍 [Code Quality] 代码质量检查启动"
echo "📋 [Config] 使用配置文件: .code-quality-config.yaml"
echo "🔍 [Tool] 基于Python pre-commit工具，但避免命名混乱"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ [Error] 代码质量配置文件不存在: $CONFIG_FILE"
    echo "💡 [Help] 请确保 .code-quality-config.yaml 文件存在"
    exit 1
fi

# 检查pre-commit工具是否安装
if ! command -v pre-commit &> /dev/null; then
    echo "❌ [Error] Python pre-commit工具未安装"
    echo "💡 [Help] 请安装: pip install pre-commit"
    exit 1
fi

echo ""
echo "🚀 [Execution] 开始执行代码质量检查..."
echo "───────────────────────────────────────────"

# 执行代码质量检查，使用重命名的配置文件
pre-commit run --config "$CONFIG_FILE" "$@"

RESULT=$?

echo "───────────────────────────────────────────"
if [ $RESULT -eq 0 ]; then
    echo "✅ [Success] 代码质量检查通过"
else
    echo "❌ [Failed] 代码质量检查失败"
    echo "💡 [Help] 请根据上述错误信息修复问题后重试"
fi

echo "🏁 [Complete] 代码质量检查完成"
exit $RESULT
