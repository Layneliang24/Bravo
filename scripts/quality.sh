#!/bin/bash

# 代码质量检查脚本
# 该脚本用于统一运行所有代码质量检查工具

set -e

echo "🚀 开始代码质量检查..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python环境
echo "📦 检查Python环境..."
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python未安装${NC}"
    exit 1
fi

# 检查Node.js环境
echo "📦 检查Node.js环境..."
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js未安装${NC}"
    exit 1
fi

# 后端代码质量检查
echo "🔍 运行后端代码质量检查..."
cd backend

echo "  🧹 检查代码格式 (Black)..."
python -m black --check --diff apps/

echo "  📋 检查导入排序 (isort)..."
python -m isort --check-only --diff apps/

echo "  🔍 检查代码风格 (flake8)..."
python -m flake8 apps/

echo "  📝 检查代码质量 (pylint)..."
python -m pylint apps/ --rcfile=.pylintrc --output-format=json > ../reports/pylint-report.json || true

echo "  📊 检查代码复杂度 (radon)..."
python -m radon cc apps/ --config radon.cfg

echo "  📝 检查类型注解 (mypy)..."
python -m mypy apps/ --ignore-missing-imports

echo "  🔒 检查安全问题 (bandit)..."
python -m bandit -r apps/ -f json -o ../reports/security-report.json || true

cd ..

# 前端代码质量检查
echo "🔍 运行前端代码质量检查..."
cd frontend

echo "  🧹 检查代码格式 (Prettier)..."
npm run format:check

echo "  🔍 检查代码风格 (ESLint)..."
npm run lint

cd ..

# 运行预提交钩子检查
echo "🪝 运行预提交钩子检查..."
pre-commit run --all-files

# 生成质量报告
echo "📊 生成代码质量报告..."
mkdir -p reports
cd backend
python -m radon cc apps/ -a -nb --config radon.cfg > ../reports/cyclomatic-complexity.txt
python -m radon mi apps/ --config radon.cfg > ../reports/maintainability-index.txt
python -m radon hal apps/ > ../reports/halstead-metrics.txt
python -m radon raw apps/ > ../reports/raw-metrics.txt
cd ..

echo -e "${GREEN}✅ 代码质量检查完成！${NC}"
echo "📋 报告位置:"
echo "  - Pylint报告: reports/pylint-report.json"
echo "  - 安全报告: reports/security-report.json"
echo "  - 复杂度报告: reports/cyclomatic-complexity.txt"
echo "  - 可维护性报告: reports/maintainability-index.txt"
echo "  - Halstead报告: reports/halstead-metrics.txt"
echo "  - 原始指标报告: reports/raw-metrics.txt"
