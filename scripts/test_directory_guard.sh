#!/bin/bash

# 目录守卫测试脚本
# 用于验证目录守卫功能是否正常工作

echo "🔍 开始测试目录守卫功能..."

# 测试1：检查规则文件是否存在
if [ -f ".cursor/rules/directory_guard.mdc" ]; then
    echo "✅ Cursor规则文件存在"
else
    echo "❌ Cursor规则文件不存在"
    exit 1
fi

# 测试2：检查CI工作流是否存在
if [ -f ".github/workflows/dir_guard.yml" ]; then
    echo "✅ CI工作流文件存在"
else
    echo "❌ CI工作流文件不存在"
    exit 1
fi

# 测试3：检查pre-commit钩子是否配置
if grep -q "Root Clutter Guard" .pre-commit-config.yaml; then
    echo "✅ pre-commit钩子已配置"
else
    echo "❌ pre-commit钩子未配置"
    exit 1
fi

# 测试4：检查Makefile目标是否存在
if grep -q "move-clutter" Makefile; then
    echo "✅ Makefile补救目标已配置"
else
    echo "❌ Makefile补救目标未配置"
    exit 1
fi

# 测试5：模拟违规文件检测
echo "🧪 模拟违规文件检测..."
touch test_temp.md
if git add test_temp.md 2>/dev/null && git commit -m "test" 2>/dev/null; then
    echo "❌ 目录守卫未生效 - 违规文件被提交"
    rm -f test_temp.md
    git reset HEAD test_temp.md 2>/dev/null
    exit 1
else
    echo "✅ 目录守卫生效 - 违规文件被拦截"
    rm -f test_temp.md
    git reset HEAD test_temp.md 2>/dev/null
fi

echo "🎉 所有测试通过！目录守卫功能正常"
