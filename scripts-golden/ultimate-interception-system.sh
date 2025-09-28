#!/bin/bash
# 终极拦截系统 - 多层防护阻止AI绕过命令拦截
# 结合PATH劫持 + Shell函数 + Alias三重防护

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🛡️  启动终极拦截系统 - 三重防护"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 第一层：PATH劫持拦截
echo "🔧 [第一层] 启动PATH劫持拦截..."
source "$SCRIPT_DIR/path-hijacker.sh" setup

# 第二层：Shell函数拦截
echo "🔧 [第二层] 启动Shell函数拦截..."
source "$SCRIPT_DIR/shell-function-interceptors.sh"

# 第三层：Alias拦截（现有机制）
echo "🔧 [第三层] 启动Alias拦截..."
source "$PROJECT_ROOT/scripts/git-protection-monitor.sh" check

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 终极拦截系统启动完成"
echo ""
echo "🔒 防护层级："
echo "   1️⃣ PATH劫持 - 拦截绝对路径调用"
echo "   2️⃣ Shell函数 - 拦截直接命令调用"
echo "   3️⃣ Alias别名 - 拦截简单命令"
echo ""
echo "🎯 拦截范围："
echo "   • Node.js: npm, yarn, pnpm"
echo "   • Python: python, python3, pip, pip3"
echo "   • Go: go"
echo "   • Rust: cargo"
echo "   • Ruby: gem"
echo "   • Java: mvn, gradle"
echo "   • Conda: conda, mamba"
echo "   • 虚拟环境: source"
echo ""
echo "🧪 测试拦截:"
echo "   bash $SCRIPT_DIR/ultimate-interception-system.sh test"

# 测试模式
if [[ "$1" == "test" ]]; then
    echo ""
    echo "🧪 拦截系统测试："
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo "📋 PATH优先级测试:"
    echo "PATH前5个目录:"
    echo "$PATH" | tr ':' '\n' | head -5 | nl

    echo ""
    echo "🔍 命令定位测试:"
    for cmd in npm pip python go cargo; do
        cmd_path=$(which "$cmd" 2>/dev/null || echo "未找到")
        if [[ "$cmd_path" == *"/scripts-golden/path-interceptors/"* ]]; then
            echo "  ✅ $cmd -> $cmd_path [被拦截]"
        else
            echo "  ⚠️  $cmd -> $cmd_path [可能绕过]"
        fi
    done

    echo ""
    echo "🔧 函数定义测试:"
    for func in npm pip python; do
        if declare -f "$func" >/dev/null 2>&1; then
            echo "  ✅ 函数 $func() 已定义"
        else
            echo "  ❌ 函数 $func() 未定义"
        fi
    done

    echo ""
    echo "🎭 Alias状态测试:"
    alias | grep -E "(npm|pip|python)" | head -3

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
fi

echo ""
echo "⚠️  重要：AI现在无法通过以下方式绕过："
echo "   ❌ 直接命令调用: npm install"
echo "   ❌ 绝对路径调用: /usr/bin/npm install"
echo "   ❌ which查找调用: \$(which npm) install"
echo "   ❌ PATH变量调用: PATH=/usr/bin npm install"
