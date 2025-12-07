#!/bin/bash
# PRD状态拦截测试脚本
# 用于测试pre-commit钩子是否正确拦截draft/review状态的PRD

set -e

echo "=== PRD状态拦截测试 ==="
echo ""

# 检查backend容器是否运行
if ! docker-compose ps backend | grep -q "Up"; then
    echo "⚠️ 警告：backend容器未运行，测试可能失败"
    echo "   请先运行: docker-compose up -d backend"
    echo ""
fi

# 步骤1：查看当前metadata
echo "📋 步骤1：查看tasks.json的metadata"
cat .taskmaster/tasks/tasks.json | docker-compose exec -T backend python -c "
import json, sys
data = json.load(sys.stdin)
master_meta = data.get('master', {}).get('metadata', {})
print('source_prd_path:', master_meta.get('source_prd_path'))
print('source_prd_paths:', master_meta.get('source_prd_paths', []))
" 2>&1 | grep -v "WARNING" || echo "⚠️ 无法读取metadata"
echo ""

# 步骤2：修改PRD为draft
PRD_FILE="docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md"
if [ ! -f "$PRD_FILE" ]; then
    echo "❌ PRD文件不存在: $PRD_FILE"
    echo "   请使用其他PRD文件，或先创建测试PRD"
    exit 1
fi

echo "📋 步骤2：修改PRD状态为draft"
echo "修改前："
grep "^status:" "$PRD_FILE" || echo "未找到status字段"
sed -i 's/status: approved/status: draft/' "$PRD_FILE"
echo "修改后："
grep "^status:" "$PRD_FILE"
echo ""

# 步骤3：修改tasks.json
echo "📋 步骤3：修改tasks.json"
cat .taskmaster/tasks/tasks.json | docker-compose exec -T backend python -c "
import json, sys
data = json.load(sys.stdin)
data['master']['metadata']['test_note'] = 'pre-commit拦截测试 - $(date)'
print(json.dumps(data, indent=2, ensure_ascii=False))
" > .taskmaster/tasks/tasks.json.tmp && mv .taskmaster/tasks/tasks.json.tmp .taskmaster/tasks/tasks.json
echo "✅ tasks.json已修改"
echo ""

# 步骤4：暂存文件
echo "📋 步骤4：暂存文件"
git add .taskmaster/tasks/tasks.json
echo "✅ 文件已暂存"
echo ""

# 步骤5：尝试提交（应该被拦截）
echo "📋 步骤5：尝试提交（应该被拦截）"
echo "执行: git commit -m 'test: PRD状态拦截测试'"
echo ""
echo "--- 开始提交 ---"
if git commit -m 'test: PRD状态拦截测试' 2>&1; then
    echo ""
    echo "❌ 测试失败：提交没有被拦截！"
    echo "   预期：提交应该被pre-commit钩子拦截"
    echo "   实际：提交成功"
    exit 1
else
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 1 ]; then
        echo ""
        echo "✅ 测试成功：提交被拦截！"
        echo "   退出码: $EXIT_CODE (符合预期)"
    else
        echo ""
        echo "⚠️ 提交失败，但退出码不是1 (退出码: $EXIT_CODE)"
        echo "   可能有问题，请检查错误信息"
    fi
fi
echo ""

# 步骤6：恢复PRD状态
echo "📋 步骤6：恢复PRD状态为approved"
sed -i 's/status: draft/status: approved/' "$PRD_FILE"
git add "$PRD_FILE"
echo "✅ PRD状态已恢复"
echo ""

# 步骤7：再次提交（应该成功）
echo "📋 步骤7：再次提交（应该成功）"
echo "执行: git commit -m 'test: PRD状态拦截测试（approved状态）'"
echo ""
echo "--- 开始提交 ---"
if git commit -m 'test: PRD状态拦截测试（approved状态）' 2>&1; then
    echo ""
    echo "✅ 测试成功：approved状态下提交成功！"
else
    EXIT_CODE=$?
    echo ""
    echo "❌ 测试失败：approved状态下提交被拦截！"
    echo "   退出码: $EXIT_CODE"
    echo "   这不应该发生，请检查错误信息"
    exit 1
fi
echo ""

echo "=== 测试完成 ==="
echo "✅ 所有测试通过"
echo ""
echo "📝 测试总结："
echo "  1. ✅ draft状态PRD + 修改tasks.json → 提交被拦截"
echo "  2. ✅ approved状态PRD + 修改tasks.json → 提交成功"
echo ""
echo "💡 提示：如果不想保留测试提交，可以运行："
echo "  git reset HEAD~1  # 撤销最后一次提交"
echo "  git restore .taskmaster/tasks/tasks.json  # 恢复tasks.json"
