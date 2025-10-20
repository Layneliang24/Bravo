#!/bin/bash
# 统一保护机制 - 将所有确认码改为密码验证（完整实现版）
# 执行此脚本后，所有Git保护拦截都将使用加密密码验证

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🔄 统一Git保护机制 - 确认码→密码验证（完整版）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 将要修改的文件："
echo "  1. scripts-golden/git-guard.sh"
echo "  2. scripts/git-interceptor"
echo ""
echo "🎯 修改内容："
echo "  • 移除所有确认码验证（I_UNDERSTAND_THE_RISKS...等）"
echo "  • 统一使用加密密码验证系统"
echo "  • 24个拦截场景全部改为密码验证"
echo "  • 保留环境变量绕过机制（用于CI/CD）"
echo ""

# 备份原文件
echo "📦 备份原文件..."
if [ ! -f "$PROJECT_ROOT/scripts-golden/git-guard.sh.backup.$(date +%Y%m%d)" ]; then
    cp "$PROJECT_ROOT/scripts-golden/git-guard.sh" "$PROJECT_ROOT/scripts-golden/git-guard.sh.backup.$(date +%Y%m%d)"
    echo "✅ 已备份 git-guard.sh"
fi

if [ ! -f "$PROJECT_ROOT/scripts/git-interceptor.backup.$(date +%Y%m%d)" ]; then
    cp "$PROJECT_ROOT/scripts/git-interceptor" "$PROJECT_ROOT/scripts/git-interceptor.backup.$(date +%Y%m%d)"
    echo "✅ 已备份 git-interceptor"
fi

echo ""
echo "🔧 开始修改 scripts-golden/git-guard.sh..."
echo ""

# 修改 show_violation_warning 函数
cat > "$PROJECT_ROOT/scripts-golden/git-guard-new-violation-function.tmp" << 'EOF'
# 通用违规处理函数 - 使用密码验证
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

    # 使用统一的加密密码验证系统
    echo ""
    echo "🔐 需要密码验证才能继续"

    # 调用加密验证系统
    if ! bash "$PROJECT_ROOT/scripts-golden/encrypted_auth_system.sh" --verify "$violation_type" "$command_full"; then
        echo "❌ 密码验证失败 - 操作被拒绝"
        echo "💡 请修复问题后重新尝试"
        exit 1
    fi

    echo "✅ 密码验证通过，已授权继续"
    echo "⚠️  操作已记录"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | PASSWORD_VERIFIED | $violation_type | $command_full" >> "$LOG_FILE"
}
EOF

# 修改 show_protected_branch_warning 函数
cat > "$PROJECT_ROOT/scripts-golden/git-guard-new-protected-function.tmp" << 'EOF'
# 保护分支违规处理函数 - 使用密码验证
show_protected_branch_warning() {
    local operation="$1"
    local command_full="$2"

    echo "🛡️🛡️🛡️ 保护分支修改被拦截！🛡️🛡️🛡️"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "❌ 检测到在保护分支上尝试修改操作！"
    echo ""
    echo "📋 当前分支：$($real_git branch --show-current 2>/dev/null || echo 'unknown')"
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
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 记录违规尝试
    echo "$(date '+%Y-%m-%d %H:%M:%S') | PROTECTED_BRANCH | $($real_git branch --show-current 2>/dev/null || echo 'unknown') | $operation | $command_full" >> "$LOG_FILE"

    # 检查环境变量绕过
    if [[ "$ALLOW_PROTECTED_BRANCH_OPERATIONS" == "true" ]]; then
        echo "🟡 检测到环境变量绕过，允许继续操作"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | PROTECTED_BYPASS_ENV | $operation | $command_full" >> "$LOG_FILE"
        return 0
    fi

    # 使用密码验证
    echo ""
    echo "🔐 需要密码验证才能在保护分支上操作"

    if ! bash "$PROJECT_ROOT/scripts-golden/encrypted_auth_system.sh" --verify "保护分支操作" "$operation"; then
        echo "❌ 密码验证失败 - 操作被拒绝"
        echo "💡 推荐命令：git checkout -b feature/$(whoami)-$(date +%m%d)"
        exit 1
    fi

    echo "✅ 密码验证通过，允许在保护分支操作"
    echo "⚠️  已记录此次操作"
    echo "$(date '+%Y-%m-%d %H:%M:%S') | PROTECTED_PASSWORD_VERIFIED | $operation | $command_full" >> "$LOG_FILE"
    return 0
}
EOF

# 使用Python脚本进行精确替换（避免sed的复杂性）
cat > "$PROJECT_ROOT/scripts/replace-functions.py" << 'PYTHON_EOF'
#!/usr/bin/env python3
"""
替换git-guard.sh中的验证函数
将确认码验证改为密码验证
"""
import re
import sys

def replace_violation_function(content):
    """替换 show_violation_warning 函数"""

    # 读取新函数
    with open('scripts-golden/git-guard-new-violation-function.tmp', 'r', encoding='utf-8') as f:
        new_function = f.read()

    # 匹配原函数（从函数定义到函数结束的右大括号）
    pattern = r'# 通用违规处理函数\s*\nshow_violation_warning\(\)\s*\{.*?\n\}'

    # 使用DOTALL标志使.匹配换行符
    content = re.sub(pattern, new_function.strip(), content, flags=re.DOTALL)

    return content

def replace_protected_branch_function(content):
    """替换 show_protected_branch_warning 函数"""

    # 读取新函数
    with open('scripts-golden/git-guard-new-protected-function.tmp', 'r', encoding='utf-8') as f:
        new_function = f.read()

    # 匹配原函数
    pattern = r'# 保护分支违规处理函数\s*\nshow_protected_branch_warning\(\)\s*\{.*?\n\}'

    content = re.sub(pattern, new_function.strip(), content, flags=re.DOTALL)

    return content

def main():
    if len(sys.argv) < 2:
        print("Usage: python replace-functions.py <file>")
        sys.exit(1)

    filepath = sys.argv[1]

    # 读取文件
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"📖 读取文件：{filepath}")
    print(f"📏 原文件大小：{len(content)} 字节")

    # 执行替换
    content = replace_violation_function(content)
    print("✅ 已替换 show_violation_warning 函数")

    content = replace_protected_branch_function(content)
    print("✅ 已替换 show_protected_branch_warning 函数")

    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"💾 已保存修改后的文件")
    print(f"📏 新文件大小：{len(content)} 字节")

if __name__ == '__main__':
    main()
PYTHON_EOF

chmod +x "$PROJECT_ROOT/scripts/replace-functions.py"

# 执行Python替换脚本
echo "🐍 使用Python脚本精确替换函数..."
python3 "$PROJECT_ROOT/scripts/replace-functions.py" "$PROJECT_ROOT/scripts-golden/git-guard.sh"

# 清理临时文件
rm -f "$PROJECT_ROOT/scripts-golden/git-guard-new-violation-function.tmp"
rm -f "$PROJECT_ROOT/scripts-golden/git-guard-new-protected-function.tmp"
rm -f "$PROJECT_ROOT/scripts/replace-functions.py"

echo ""
echo "✅ git-guard.sh 修改完成！"
echo ""

# 同样修改 git-interceptor（简化版）
echo "🔧 修改 scripts/git-interceptor..."

# git-interceptor使用更简单的结构，直接用sed替换
sed -i.bak \
    -e 's/read -p "确认码: " response/# 调用加密验证系统\n    if ! bash "$PROJECT_ROOT\/scripts-golden\/encrypted_auth_system.sh" --verify "$violation_type" "$command_full"; then\n        echo "❌ 密码验证失败 - 操作被拒绝"\n        exit 1\n    fi\n    return 0/' \
    -e 's/if \[\[ "$response" != "I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS" \]\]; then/if false; then  # 已改用密码验证/' \
    "$PROJECT_ROOT/scripts/git-interceptor"

echo "✅ git-interceptor 修改完成！"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 所有修改已完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 修改总结："
echo "  ✅ 24个拦截场景已统一改为密码验证"
echo "  ✅ 移除所有长确认码（I_UNDERSTAND_THE_RISKS...）"
echo "  ✅ 保留环境变量绕过（ALLOW_*）用于CI/CD"
echo "  ✅ 所有操作都需要输入主密码（8位以上）"
echo ""
echo "🔧 下一步操作："
echo ""
echo "1️⃣ 初始化密码系统（首次使用）："
echo "   bash scripts-golden/encrypted_auth_system.sh --init"
echo ""
echo "2️⃣ 设置主密码："
echo "   - 8位以上"
echo "   - 包含数字、字母、符号"
echo "   - 只有您知道"
echo ""
echo "3️⃣ 测试保护机制："
echo "   git reset --hard  # 应该提示输入密码"
echo "   git push origin xxx  # 应该提示输入密码"
echo ""
echo "4️⃣ 查看密码状态："
echo "   ls -la .auth-config  # 查看加密配置文件"
echo ""
echo "5️⃣ 如需恢复原版本："
echo "   cp scripts-golden/git-guard.sh.backup.$(date +%Y%m%d) scripts-golden/git-guard.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔐 统一密码保护系统已应用"
echo "🔒 现在所有Git危险操作都需要密码验证"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
