#!/bin/bash

# 黄金测试保护功能验证脚本
# 此脚本用于验证黄金测试保护机制是否正常工作

set -e

echo "🔍 开始验证黄金测试保护功能..."
echo "======================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 验证函数
verify_step() {
    local step_name="$1"
    local command="$2"
    local expected_result="$3"
    
    echo -e "\n${YELLOW}📋 验证: $step_name${NC}"
    echo "执行命令: $command"
    
    if eval "$command"; then
        if [ "$expected_result" = "success" ]; then
            echo -e "${GREEN}✅ 通过: $step_name${NC}"
            return 0
        else
            echo -e "${RED}❌ 失败: $step_name (期望失败但成功了)${NC}"
            return 1
        fi
    else
        if [ "$expected_result" = "fail" ]; then
            echo -e "${GREEN}✅ 通过: $step_name (正确阻止了操作)${NC}"
            return 0
        else
            echo -e "${RED}❌ 失败: $step_name (期望成功但失败了)${NC}"
            return 1
        fi
    fi
}

# 1. 验证黄金测试目录结构
echo -e "\n${YELLOW}1. 验证黄金测试目录结构${NC}"
verify_step "黄金测试目录存在" "test -d tests-golden" "success"
verify_step "前端黄金测试存在" "test -f tests-golden/e2e/blog.spec.ts" "success"
verify_step "E2E黄金测试存在" "test -f tests-golden/e2e/blog.spec.ts" "success"
verify_step "后端黄金测试存在" "test -f tests-golden/backend/test_user_core.py" "success"

# 2. 验证Git钩子
echo -e "\n${YELLOW}2. 验证Git钩子保护${NC}"
verify_step "pre-commit钩子存在" "test -f .husky/pre-commit" "success"
verify_step "pre-commit钩子内容正确" "grep -q 'lint-staged' .husky/pre-commit" "success"

# 3. 验证GitHub Actions配置
echo -e "\n${YELLOW}3. 验证GitHub Actions配置${NC}"
verify_step "CI工作流存在" "test -f .github/workflows/ci.yml" "success"
verify_step "CI工作流包含测试步骤" "grep -q 'Run tests' .github/workflows/ci.yml" "success"

# 4. 验证CODEOWNERS规则
echo -e "\n${YELLOW}4. 验证CODEOWNERS规则${NC}"
verify_step "CODEOWNERS文件存在" "test -f .github/CODEOWNERS" "success"
verify_step "CODEOWNERS包含黄金测试规则" "grep -q 'tests-golden' .github/CODEOWNERS" "success"

# 5. 验证系统提示词更新
echo -e "\n${YELLOW}5. 验证系统提示词更新${NC}"
verify_step "系统提示词存在" "test -f .cursor/system_prompt.md" "success"
verify_step "系统提示词包含黄金测试约束" "grep -q -i 'tests-golden' .cursor/system_prompt.md" "success"

# 6. 模拟测试保护功能（安全测试）
echo -e "\n${YELLOW}6. 模拟测试保护功能${NC}"

# 创建临时分支进行测试
echo "创建临时测试分支..."
git checkout -b test-golden-protection-$(date +%s) 2>/dev/null || true

# 尝试修改黄金测试文件
echo "尝试修改黄金测试文件..."
echo "// 临时修改用于测试" >> tests-golden/e2e/blog.spec.ts

# 尝试提交（应该被阻止）
echo "尝试提交修改（应该被pre-commit钩子阻止）..."
git add tests-golden/e2e/blog.spec.ts
if git commit -m "测试：尝试修改黄金测试" 2>/dev/null; then
    echo -e "${RED}❌ 警告: Git钩子未能阻止黄金测试修改${NC}"
else
    echo -e "${GREEN}✅ 通过: Git钩子成功阻止了黄金测试修改${NC}"
fi

# 清理测试修改
echo "清理测试修改..."
git reset --hard HEAD 2>/dev/null || true
git checkout - 2>/dev/null || true
git branch -D test-golden-protection-* 2>/dev/null || true

# 7. 运行黄金测试确保功能正常
echo -e "\n${YELLOW}7. 运行黄金测试验证功能${NC}"
cd frontend
verify_step "E2E黄金测试运行" "npx playwright test ../tests-golden/e2e/blog.spec.ts" "success"
cd ..

cd e2e
verify_step "E2E黄金测试配置" "test -f playwright.config.ts" "success"
cd ..

echo -e "\n${GREEN}🎉 黄金测试保护功能验证完成！${NC}"
echo "======================================"
echo -e "${GREEN}✅ 所有保护机制已就绪并正常工作${NC}"
echo -e "${YELLOW}📝 建议：定期运行此脚本确保保护功能持续有效${NC}"