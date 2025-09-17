#!/bin/bash
# 修复E2E测试前端依赖问题的脚本

set -e

cd frontend

echo "🔧 修复前端依赖问题..."
echo "Node version: $(node --version)"
echo "npm version: $(npm --version)"

# 检查关键依赖
check_deps() {
    echo "检查关键前端依赖..."

    # 检查vue-tsc
    if ! npx vue-tsc --version > /dev/null 2>&1; then
        echo "❌ vue-tsc 不可用"
        return 1
    fi

    # 检查vite
    if ! npx vite --version > /dev/null 2>&1; then
        echo "❌ vite 不可用"
        return 1
    fi

    echo "✅ 关键依赖检查通过"
    return 0
}

# 强制重装依赖
force_reinstall() {
    echo "🔄 强制重装前端依赖..."
    rm -rf node_modules package-lock.json
    npm cache clean --force
    npm install
}

# 主逻辑
if [ ! -d "node_modules" ]; then
    echo "node_modules不存在，安装依赖..."
    npm ci --prefer-offline --no-audit
elif ! check_deps; then
    echo "依赖检查失败，重新安装..."
    force_reinstall
else
    echo "✅ 前端依赖正常"
fi

echo "🎯 前端依赖修复完成"
