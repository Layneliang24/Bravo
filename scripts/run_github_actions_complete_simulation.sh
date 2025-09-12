#!/bin/bash
# GitHub Actions 完整模拟脚本 - 与gate.yml一对一对应
# 完全在Docker容器内运行，解决所有环境差异问题

set -e

echo "🚀 GitHub Actions 完整本地模拟开始"
echo "================================================"
echo "⏰ 开始时间: $(date)"
echo "📍 模拟分支: feature/infrastructure-hooks"
echo "📋 模拟触发: push到feature分支 (会触发gate.yml)"
echo "🎯 目标: 完全模拟GitHub Actions环境，解决所有差异"
echo "================================================"

# 记录开始时间
START_TIME=$(date +%s)

# 设置环境变量（完全模拟GitHub Actions环境）
export CI=true
export GITHUB_ACTIONS=true
export PYTHONUNBUFFERED=1
export DB_HOST=127.0.0.1  # 模拟GitHub Actions的localhost
export DB_PORT=3306
export DB_NAME=bravo_test
export DB_USER=bravo_user
export DB_PASSWORD=bravo_password
export DJANGO_SETTINGS_MODULE=bravo.settings.test

echo ""
echo "🔧 第一步: 启动基础服务（模拟GitHub Actions services）"
echo "----------------------------------------"
echo "启动MySQL服务..."
docker-compose up -d mysql

echo "等待MySQL就绪..."
for i in {1..30}; do
    if docker-compose exec -T mysql mysqladmin ping -h localhost -u root -proot_password --silent; then
        echo "✅ MySQL已就绪"
        break
    fi
    echo "等待MySQL启动... (attempt $i/30)"
    sleep 2
done

echo ""
echo "🗄️ 第二步: 数据库初始化（完全模拟GitHub Actions的Setup Test Database步骤）"
echo "----------------------------------------"

# 配置MySQL用户权限（模拟GitHub Actions）
echo "🔧 配置MySQL用户权限..."
docker-compose exec -T mysql mysql -h localhost -u root -proot_password -e "
    CREATE DATABASE IF NOT EXISTS bravo_test;
    CREATE USER IF NOT EXISTS 'bravo_user'@'%' IDENTIFIED BY 'bravo_password';
    GRANT ALL PRIVILEGES ON bravo_test.* TO 'bravo_user'@'%';
    GRANT ALL PRIVILEGES ON \`test_%\`.* TO 'bravo_user'@'%';
    FLUSH PRIVILEGES;
"
echo "✅ MySQL用户权限配置完成"

# 启动后端容器进行数据库初始化
echo "🗄️ 设置测试数据库（完全模拟GitHub Actions）..."
docker-compose run --rm backend python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bravo.settings.test')
django.setup()
from django.db import connection
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from apps.users.models import User

print('📋 创建数据库表...')
models_to_create = [ContentType, Group, Permission, User, Session, LogEntry]

with connection.schema_editor() as schema_editor:
    for model in models_to_create:
        if not model._meta.db_table in connection.introspection.table_names():
            schema_editor.create_model(model)
            print(f'✅ Created table: {model._meta.db_table}')
        else:
            print(f'⏭️  Table already exists: {model._meta.db_table}')

print('✅ 数据库表创建完成')
" -e DB_HOST=mysql -e DB_PORT=3306 -e DB_NAME=bravo_test -e DB_USER=bravo_user -e DB_PASSWORD=bravo_password

echo "✅ 测试数据库设置完成"

echo ""
echo "📦 第三步: 依赖安装（完全模拟GitHub Actions的依赖安装步骤）"
echo "----------------------------------------"

# 构建所有服务（确保依赖正确安装）
echo "🏗️ 构建所有服务..."
docker-compose build frontend backend

# 安装前端依赖（模拟GitHub Actions）
echo "📦 安装前端依赖..."
docker-compose run --rm frontend bash -c "
    echo '📦 配置npm国内源...'
    npm config set registry https://registry.npmmirror.com
    npm config set maxsockets 20
    npm config set fetch-retries 3
    echo '📦 安装前端依赖...'
    npm ci --prefer-offline --no-audit
    echo '✅ 前端依赖安装完成'
"

# 安装E2E依赖（模拟GitHub Actions）
echo "🧪 安装E2E测试依赖..."
docker-compose run --rm e2e bash -c "
    echo '📦 配置npm国内源...'
    npm config set registry https://registry.npmmirror.com
    npm config set maxsockets 20
    echo '🎭 安装E2E依赖...'
    npm ci --prefer-offline --no-audit
    echo '🎭 安装Playwright浏览器...'
    npx playwright install --with-deps
    echo '✅ E2E依赖安装完成'
"

# 安装后端依赖（模拟GitHub Actions）
echo "🐍 安装后端依赖..."
docker-compose run --rm backend bash -c "
    echo '🐍 配置pip国内源...'
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
    echo '🐍 安装后端依赖...'
    pip install -r requirements/test.txt
    echo '✅ 后端依赖安装完成'
"

echo ""
echo "🧪 第四步: 并行测试执行（完全模拟GitHub Actions的并行作业）"
echo "----------------------------------------"

# 启动后端和前端服务
echo "🚀 启动应用服务..."
docker-compose up -d backend frontend

# 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# Job 1: backend-tests（模拟GitHub Actions）
echo "🐍 启动 Job: backend-tests（后台运行）"
docker-compose exec -T backend bash -c "
    echo '🐍 Job: backend-tests 开始'
    echo '设置环境变量...'
    export DB_HOST=mysql
    export DB_PORT=3306
    export DB_NAME=bravo_test
    export DB_USER=bravo_user
    export DB_PASSWORD=bravo_password
    export DJANGO_SETTINGS_MODULE=bravo.settings.test
    echo '运行后端测试...'
    python -m pytest tests/ -v --maxfail=0 --tb=short --junitxml=test-results/backend-unit-results.xml
    echo '✅ backend-tests 完成'
" > /tmp/backend_test.log 2>&1 &
BACKEND_PID=$!

# Job 2: frontend-tests（模拟GitHub Actions）
echo "📦 启动 Job: frontend-tests（后台运行）"
docker-compose exec -T frontend bash -c "
    echo '📦 Job: frontend-tests 开始'
    echo '运行前端单元测试...'
    npm run test
    echo '✅ frontend-tests 完成'
" > /tmp/frontend_test.log 2>&1 &
FRONTEND_PID=$!

# Job 3: e2e-tests（模拟GitHub Actions）
echo "🎭 启动 Job: e2e-tests（后台运行）"
docker-compose run --rm e2e bash -c "
    echo '🎭 Job: e2e-tests 开始'
    echo '构建前端用于E2E测试...'
    cd ../frontend && npm run build:skip-check
    echo '运行E2E测试...'
    cd ../e2e && npx playwright test --workers=2 --max-failures=5 --trace=retain-on-failure --reporter=html --reporter=junit
    echo '✅ e2e-tests 完成'
" > /tmp/e2e_test.log 2>&1 &
E2E_PID=$!

echo ""
echo "⏳ 等待所有并行作业完成..."
echo "----------------------------------------"

# 等待所有作业完成
wait $BACKEND_PID
BACKEND_RESULT=$?
echo "🐍 backend-tests 完成，退出码: $BACKEND_RESULT"

wait $FRONTEND_PID
FRONTEND_RESULT=$?
echo "📦 frontend-tests 完成，退出码: $FRONTEND_RESULT"

wait $E2E_PID
E2E_RESULT=$?
echo "🎭 e2e-tests 完成，退出码: $E2E_RESULT"

# 计算总耗时
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "📊 测试结果汇总"
echo "================================================"
echo "⏰ 总耗时: ${DURATION}秒"
echo "🐍 后端测试: $([ $BACKEND_RESULT -eq 0 ] && echo '✅ 通过' || echo '❌ 失败')"
echo "📦 前端测试: $([ $FRONTEND_RESULT -eq 0 ] && echo '✅ 通过' || echo '❌ 失败')"
echo "🎭 E2E测试: $([ $E2E_RESULT -eq 0 ] && echo '✅ 通过' || echo '❌ 失败')"

# 显示详细日志
echo ""
echo "📋 详细测试日志"
echo "----------------------------------------"
echo "🐍 后端测试日志:"
cat /tmp/backend_test.log

echo ""
echo "📦 前端测试日志:"
cat /tmp/frontend_test.log

echo ""
echo "🎭 E2E测试日志:"
cat /tmp/e2e_test.log

# 计算最终结果
TOTAL_RESULT=$((BACKEND_RESULT + FRONTEND_RESULT + E2E_RESULT))

echo ""
echo "🎯 最终结果"
echo "================================================"
if [ $TOTAL_RESULT -eq 0 ]; then
    echo "✅ 所有测试通过！GitHub Actions模拟成功！"
    echo "🚀 可以安全推送到远程仓库"
else
    echo "❌ 部分测试失败，需要修复后再推送"
    echo "🔧 失败的作业数: $TOTAL_RESULT"
fi

# 清理临时文件
rm -f /tmp/backend_test.log /tmp/frontend_test.log /tmp/e2e_test.log

# 停止服务
echo "🛑 停止服务..."
docker-compose down

echo "✅ GitHub Actions完整模拟完成！"
exit $TOTAL_RESULT

