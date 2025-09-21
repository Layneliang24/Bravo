#!/bin/bash
echo "��� 执行激进清理回滚..."

# 重置到备份点
git reset --hard MILESTONE-v2.0-before-aggressive-cleanup

# 恢复所有依赖文件
cp package.json.backup package.json 2>/dev/null && echo "✅ 根目录package.json已恢复"
cp frontend/package.json.backup frontend/package.json 2>/dev/null && echo "✅ Frontend package.json已恢复"
cp e2e/package.json.backup e2e/package.json 2>/dev/null && echo "✅ E2E package.json已恢复"
cp backend/requirements/base.txt.backup backend/requirements/base.txt 2>/dev/null && echo "✅ Base requirements已恢复"
cp backend/requirements/test.txt.backup backend/requirements/test.txt 2>/dev/null && echo "✅ Test requirements已恢复"
cp backend/requirements/local.txt.backup backend/requirements/local.txt 2>/dev/null && echo "✅ Local requirements已恢复"

echo "��� 回滚完成！项目已恢复到激进清理前状态"
echo "��� 建议执行：docker-compose down && docker-compose up --build"
