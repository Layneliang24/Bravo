#!/bin/bash
# V4架构安装验证脚本

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  V4架构安装验证${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

FAILED=0

# 1. 检查目录结构
echo -e "${YELLOW}1. 检查目录结构...${NC}"
REQUIRED_DIRS=(
    ".compliance"
    ".compliance/rules"
    ".compliance/checkers"
    ".taskmaster"
    "docs/00_product/requirements"
    "docs/01_guideline/api-contracts"
    "backend/tests/regression"
    "backend/tests/fixtures"
    "e2e/tests/smoke"
    "e2e/tests/regression"
    "e2e/tests/performance"
    "scripts/task-master"
    "scripts/compliance"
    "scripts/setup"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✅${NC} $dir"
    else
        echo -e "  ${RED}❌${NC} $dir (缺失)"
        FAILED=1
    fi
done

# 2. 检查配置文件
echo ""
echo -e "${YELLOW}2. 检查配置文件...${NC}"
REQUIRED_FILES=(
    ".compliance/config.yaml"
    ".compliance/rules/prd.yaml"
    ".compliance/rules/test.yaml"
    ".compliance/rules/code.yaml"
    ".compliance/rules/commit.yaml"
    ".compliance/rules/task.yaml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file (缺失)"
        FAILED=1
    fi
done

# 3. 检查Python代码
echo ""
echo -e "${YELLOW}3. 检查Python代码...${NC}"
REQUIRED_PYTHON_FILES=(
    ".compliance/engine.py"
    ".compliance/runner.py"
    ".compliance/checkers/prd_checker.py"
    ".compliance/checkers/test_checker.py"
    ".compliance/checkers/code_checker.py"
    ".compliance/checkers/commit_checker.py"
    ".compliance/checkers/task_checker.py"
    "scripts/task-master/adapter.py"
    "scripts/task-master/sync_status.py"
)

for file in "${REQUIRED_PYTHON_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✅${NC} $file"
    else
        echo -e "  ${RED}❌${NC} $file (缺失)"
        FAILED=1
    fi
done

# 4. 检查Git Hooks
echo ""
echo -e "${YELLOW}4. 检查Git Hooks...${NC}"
if grep -q "V4合规\|第四层" .husky/pre-commit 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} .husky/pre-commit (已集成)"
else
    echo -e "  ${YELLOW}⚠️${NC} .husky/pre-commit (未集成V4合规检查)"
fi

if grep -q "REQ-\|V4格式" .husky/commit-msg 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} .husky/commit-msg (已支持V4格式)"
else
    echo -e "  ${YELLOW}⚠️${NC} .husky/commit-msg (未支持V4格式)"
fi

if grep -q "V4合规\|REQ-ID" .husky/post-commit 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} .husky/post-commit (已集成)"
else
    echo -e "  ${YELLOW}⚠️${NC} .husky/post-commit (未集成)"
fi

# 5. 检查GitHub Actions工作流
echo ""
echo -e "${YELLOW}5. 检查GitHub Actions工作流...${NC}"
if grep -q "compliance\|V4\|Compliance" .github/workflows/pr-validation.yml 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} pr-validation.yml (已集成)"
else
    echo -e "  ${YELLOW}⚠️${NC} pr-validation.yml (未集成)"
fi

if grep -q "compliance\|V4\|Compliance" .github/workflows/push-validation.yml 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} push-validation.yml (已集成)"
else
    echo -e "  ${YELLOW}⚠️${NC} push-validation.yml (未集成)"
fi

# 6. 检查Python依赖
echo ""
echo -e "${YELLOW}6. 检查Python依赖...${NC}"
if command -v python3 > /dev/null 2>&1; then
    if python3 -c "import yaml" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} pyyaml已安装"
    else
        echo -e "  ${YELLOW}⚠️${NC} pyyaml未安装（需要在容器内安装）"
    fi
else
    echo -e "  ${YELLOW}⚠️${NC} Python3未安装（需要在容器内使用）"
fi

# 7. 检查示例文件
echo ""
echo -e "${YELLOW}7. 检查示例文件...${NC}"
if [ -f "docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md" ]; then
    echo -e "  ${GREEN}✅${NC} 示例PRD文件存在"
else
    echo -e "  ${YELLOW}⚠️${NC} 示例PRD文件不存在（可选）"
fi

if [ -f "docs/01_guideline/api-contracts/REQ-2025-EXAMPLE-demo/api.yaml" ]; then
    echo -e "  ${GREEN}✅${NC} 示例API契约文件存在"
else
    echo -e "  ${YELLOW}⚠️${NC} 示例API契约文件不存在（可选）"
fi

# 总结
echo ""
echo -e "${BLUE}======================================${NC}"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 验证通过！V4架构安装成功${NC}"
    echo ""
    echo -e "${GREEN}📚 下一步：${NC}"
    echo "  1. 阅读使用指南: docs/architecture/V4/V4_USAGE_GUIDE.md"
    echo "  2. 查看示例PRD: docs/00_product/requirements/REQ-2025-EXAMPLE-demo/"
    echo "  3. 开始使用V4架构创建第一个需求"
    exit 0
else
    echo -e "${RED}❌ 验证失败，请检查上述错误${NC}"
    echo ""
    echo -e "${YELLOW}💡 提示：${NC}"
    echo "  - 缺失的目录可以使用 mkdir -p 创建"
    echo "  - 缺失的文件需要重新运行安装脚本"
    exit 1
fi
