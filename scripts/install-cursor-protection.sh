#!/bin/bash
# Cursor --no-verify 保护安装脚本

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🛡️ 安装Cursor --no-verify 保护系统"
echo "项目路径: $PROJECT_ROOT"
echo ""

# 方案1: 添加到.bashrc的git alias
echo "📋 方案1: Shell Git Alias (推荐)"
echo "将以下行添加到你的 ~/.bashrc 或 ~/.bash_profile:"
echo ""
echo "# Git --no-verify 保护 (Bravo项目)"
echo "alias git='bash \"$PROJECT_ROOT/scripts/git-guard.sh\"'"
echo ""

# 方案2: 创建当前会话的临时alias
echo "📋 方案2: 当前会话临时保护"
alias git="bash \"$PROJECT_ROOT/scripts/git-guard.sh\""
echo "✅ 临时alias已设置（当前终端会话有效）"
echo ""

# 方案3: 项目级git配置
echo "📋 方案3: Git配置级保护"
cd "$PROJECT_ROOT"
git config alias.commit-safe '!bash scripts/git-guard.sh commit'
echo "✅ 已设置 'git commit-safe' 别名"
echo ""

# 创建测试文件
echo "📋 创建测试保护的脚本"
cat > "$PROJECT_ROOT/test-no-verify-protection.sh" << 'EOF'
#!/bin/bash
echo "🧪 测试 --no-verify 保护是否生效..."
echo ""

echo "测试1: 直接--no-verify (应被拦截)"
git commit --no-verify -m "test protection" 2>&1

echo ""
echo "测试2: -n 简写形式 (应被拦截)" 
git commit -n -m "test protection" 2>&1

echo ""
echo "测试3: 正常commit (应正常工作)"
echo "git commit -m 'normal commit' (不会实际提交)"
EOF

chmod +x "$PROJECT_ROOT/test-no-verify-protection.sh"
echo "✅ 测试脚本已创建: test-no-verify-protection.sh"
echo ""

echo "🎯 快速验证保护是否生效:"
echo "bash test-no-verify-protection.sh"
echo ""

echo "📊 查看拦截日志:"
echo "tail -f logs/git-no-verify-attempts.log"
echo ""

echo "⚠️  重要提醒:"
echo "• Cursor可能需要重启才能识别新的git行为"
echo "• 如果仍然能绕过，尝试在Cursor设置中禁用git.allowNoVerifyCommit"
echo "• 最终方案：使用项目内的 'git commit-safe' 命令"

echo ""
echo "🔧 现在测试一下保护是否生效:"
read -p "按Enter测试当前保护..."

echo ""
echo "测试: git commit --no-verify -m 'test'"
git commit --no-verify -m "test protection test"
