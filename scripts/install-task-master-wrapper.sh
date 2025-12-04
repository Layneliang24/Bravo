#!/bin/bash
# 安装task-master包装脚本到PATH
# 让直接输入 task-master parse-prd 也能自动检查PRD状态

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRAPPER_SCRIPT="$PROJECT_ROOT/scripts/task-master-wrapper.sh"
INSTALL_DIR="$HOME/.local/bin"

# 创建安装目录
mkdir -p "$INSTALL_DIR"

# 创建符号链接或复制脚本
if [ -L "$INSTALL_DIR/task-master" ] || [ -f "$INSTALL_DIR/task-master" ]; then
    echo "⚠️  $INSTALL_DIR/task-master 已存在"
    read -p "是否覆盖? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 安装取消"
        exit 1
    fi
    rm -f "$INSTALL_DIR/task-master"
fi

# 创建包装脚本（使用绝对路径）
cat > "$INSTALL_DIR/task-master" << EOF
#!/bin/bash
# Task-Master包装（自动PRD状态验证）
# 由项目安装脚本生成

exec "$WRAPPER_SCRIPT" "\$@"
EOF

chmod +x "$INSTALL_DIR/task-master"

# 检查PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  $INSTALL_DIR 不在PATH中"
    echo ""
    echo "请将以下内容添加到你的shell配置文件 (~/.bashrc 或 ~/.zshrc):"
    echo ""
    echo "export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    read -p "是否自动添加? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_RC="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_RC="$HOME/.bashrc"
        else
            SHELL_RC="$HOME/.profile"
        fi

        if ! grep -q "$INSTALL_DIR" "$SHELL_RC" 2>/dev/null; then
            echo "" >> "$SHELL_RC"
            echo "# Task-Master包装（自动PRD状态验证）" >> "$SHELL_RC"
            echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$SHELL_RC"
            echo "✅ 已添加到 $SHELL_RC"
            echo "请运行: source $SHELL_RC"
        fi
    fi
else
    echo "✅ PATH已包含 $INSTALL_DIR"
fi

echo ""
echo "✅ 安装完成！"
echo ""
echo "现在可以直接使用: task-master parse-prd <file>"
echo "包装脚本会自动检查PRD状态"
