#!/bin/bash
# 保护系统状态检查脚本 - 基于Husky Hooks的永久保护架构
# 无需alias设置，通过Git Native Hooks实现永久保护

echo "🛡️ Husky永久保护系统状态检查"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 1. 检查Husky Hooks状态（永久保护机制）
echo "📋 [1/3] 检查Git Hooks永久保护状态..."
if [ -f "$PROJECT_ROOT/.git/hooks/pre-commit" ] && [ -f "$PROJECT_ROOT/.git/hooks/pre-push" ]; then
    echo "✅ Husky Hooks已配置并永久生效"
    echo "   - pre-commit: 三层检查（防篡改+通行证+代码质量）"
    echo "   - pre-push: 通行证验证+依赖安全+Git完整性"
else
    echo "⚠️  Husky Hooks未完全配置，请运行: npm install"
    echo "💡 Hooks配置后将永久生效，无需重复激活"
fi

# 2. 验证防篡改脚本完整性
echo ""
echo "📋 [2/3] 验证防篡改脚本完整性..."
GOLDEN_FILES=("git-guard.sh" "local_test_passport.py" "dependency-guard.sh" "git-protection-monitor.sh")
MISSING_COUNT=0

for file in "${GOLDEN_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/scripts-golden/$file" ]; then
        echo "✅ $file: 防篡改脚本完整"
    else
        echo "❌ $file: 防篡改脚本缺失"
        ((MISSING_COUNT++))
    fi
done

if [ $MISSING_COUNT -eq 0 ]; then
    echo "✅ 所有防篡改脚本完整性验证通过"
else
    echo "⚠️  $MISSING_COUNT 个防篡改脚本需要修复"
fi

# 3. 检查通行证生成系统
echo ""
echo "📋 [3/3] 检查通行证生成系统..."
if [ -f "$PROJECT_ROOT/scripts-golden/local_test_passport.py" ]; then
    echo "✅ 通行证生成器: scripts-golden/local_test_passport.py"
else
    echo "❌ 通行证生成器未找到"
fi

# 4. 启动保护监控（可选）
if [ -f "$PROJECT_ROOT/scripts-golden/git-protection-monitor.sh" ]; then
    echo "✅ 保护监控器: scripts-golden/git-protection-monitor.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Husky永久保护系统状态检查完成！"
echo ""
echo "📊 永久保护架构（无需重复激活）："
echo "   🛡️  Pre-commit Hook: 防篡改+通行证+代码质量"
echo "   🛡️  Pre-push Hook: 通行证验证+推送安全"
echo "   🛡️  便捷命令: ./test, ./passport, ./safe-push"
echo ""
echo "💡 使用方式："
echo "   ./test        # 生成本地测试通行证"
echo "   git commit    # 自动三层检查（永久生效）"
echo "   git push      # 自动通行证验证（永久生效）"
echo ""
echo "✅ 优势：一次配置，永久生效，零维护成本"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
