#!/bin/bash

# 模拟GitHub Actions CI环境 - 前端测试流程
# 基于 .github/workflows/gate.yml 的配置

set -e

echo "🚀 开始模拟GitHub Actions CI环境..."
echo "📋 基于 .github/workflows/gate.yml 配置"

# 环境变量设置（模拟GitHub Actions环境）
export NODE_VERSION=20
export CI=true
export GITHUB_ACTIONS=true

echo "\n=== 步骤1: 检出代码 ==="
echo "✅ 代码已在本地 (模拟 actions/checkout@v4)"

echo "\n=== 步骤2: 设置Node.js环境 ==="
echo "📦 当前Node.js版本: $(node --version)"
echo "📦 当前npm版本: $(npm --version)"

echo "\n=== 步骤3: 模拟smart-dependencies job ==="
echo "🔧 smart-dependencies job负责安装所有依赖并缓存"

# 清除现有依赖来模拟CI环境
echo "🧹 清除现有依赖 (模拟CI全新环境)..."
rm -rf frontend/node_modules e2e/node_modules
rm -f package-lock.json

echo "📦 smart-dependencies: 使用npm workspace安装所有依赖..."
echo "🔧 执行命令: npm install --ignore-scripts"
npm install --ignore-scripts
echo "✅ smart-dependencies: 所有依赖安装完成"

cd frontend

echo "\n=== 步骤4: 模拟frontend-tests job缓存恢复 ==="
echo "🔍 frontend-tests job: 尝试恢复缓存..."
# 模拟缓存键检查
CACHE_KEY="frontend-deps-Linux-$(sha256sum package-lock.json | cut -d' ' -f1)"
echo "🔑 缓存键: $CACHE_KEY"

# 在CI中，frontend-tests job会尝试恢复smart-dependencies创建的缓存
if [ -d "node_modules" ]; then
    echo "✅ 缓存恢复成功 (从smart-dependencies继承)"
    CACHE_HIT=true
else
    echo "❌ 缓存恢复失败"
    CACHE_HIT=false
fi

echo "\n=== 步骤5: frontend-tests job fallback安装 ==="
if [ "$CACHE_HIT" != "true" ]; then
    echo "📦 frontend-tests: 缓存未命中，执行fallback安装..."
    echo "🔧 执行命令: npm ci --prefer-offline --no-audit"
    npm ci --prefer-offline --no-audit
    echo "✅ frontend-tests: fallback安装完成"
else
    echo "⏭️  frontend-tests: 跳过安装 (使用缓存)"
fi

echo "\n=== 步骤6: 运行前端测试 ==="
echo "🧪 运行前端测试..."
echo "🔧 执行命令: npm run test:coverage"
npm run test:coverage
echo "✅ 前端测试完成"

echo "\n=== 步骤7: 上传覆盖率报告 ==="
if [ -d "coverage" ]; then
    echo "📊 发现覆盖率报告目录: coverage/"
    echo "✅ 覆盖率报告准备就绪 (模拟 actions/upload-artifact@v4)"
else
    echo "❌ 未发现覆盖率报告"
fi

echo "\n🎉 CI模拟完成！"
echo "📝 总结:"
echo "   - Node.js版本: $(node --version)"
echo "   - npm版本: $(npm --version)"
echo "   - 依赖安装: $([ "$CACHE_HIT" = "true" ] && echo "缓存命中" || echo "fallback安装")"
echo "   - 测试状态: 已执行"
echo "   - 覆盖率: $([ -d "coverage" ] && echo "已生成" || echo "未生成")"