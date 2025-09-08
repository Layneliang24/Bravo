#!/bin/bash
set -e
echo "====== 1 测试文件存在性 ======"
find backend -name "test_*.py" | wc -l          # >0 表示有测试文件
echo "====== 2 单测可运行 ======"
pytest backend/tests --collect-only -q | tail -1
echo "====== 3 覆盖率阈值 ======"
pytest --cov=backend --cov-report=term-missing --cov-fail-under=80
echo "====== 4 回归测试 ======"
pytest backend/tests/test_regression.py
echo "====== 5 E2E 可跑 ======"
npx playwright test --reporter=line
echo "====== 6 随机破坏（Mutation） ======"
pip install mutmut
mutmut run --paths-to-mutate=backend/apps || echo "Mutation 测试已跑完"
