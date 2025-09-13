#!/bin/bash

# Docker环境测试验证脚本
# 用于验证CI环境中MySQL连接问题的修复

set -e  # 遇到错误立即退出

echo "🐳 开始Docker环境测试验证..."
echo "📍 当前目录: $(pwd)"
echo "🕐 开始时间: $(date)"

# 清理之前的测试环境
echo "🧹 清理之前的测试环境..."
docker-compose -f docker-compose.test.yml down -v --remove-orphans 2>/dev/null || true
docker system prune -f --volumes 2>/dev/null || true

# 构建测试镜像
echo "🔨 构建测试镜像..."
docker-compose -f docker-compose.test.yml build --no-cache

# 启动MySQL服务并等待就绪
echo "🗄️ 启动MySQL测试服务..."
docker-compose -f docker-compose.test.yml up -d mysql-test

# 等待MySQL服务完全启动
echo "⏳ 等待MySQL服务就绪..."
for i in {1..30}; do
    if docker-compose -f docker-compose.test.yml exec -T mysql-test mysqladmin ping -h localhost --silent; then
        echo "✅ MySQL服务已就绪"
        break
    fi
    echo "等待MySQL启动... ($i/30)"
    sleep 2
done

# 配置数据库权限（模拟CI环境）
echo "🔧 配置数据库权限..."
docker-compose -f docker-compose.test.yml exec -T mysql-test mysql -u root -proot_password -e "
    GRANT ALL PRIVILEGES ON test_%.* TO 'bravo_user'@'%';
    GRANT ALL PRIVILEGES ON bravo_test.* TO 'bravo_user'@'%';
    FLUSH PRIVILEGES;
    SHOW GRANTS FOR 'bravo_user'@'%';
"

echo "✅ 数据库权限配置完成"

# 运行测试验证
echo "🧪 运行测试验证..."
echo "==========================================="
echo "1. 运行CI修复验证脚本"
echo "==========================================="

if docker-compose -f docker-compose.test.yml run --rm test-validator; then
    echo "✅ CI修复验证通过"
else
    echo "❌ CI修复验证失败"
    TEST_FAILED=true
fi

echo "==========================================="
echo "2. 运行后端测试"
echo "==========================================="

if docker-compose -f docker-compose.test.yml run --rm backend-test; then
    echo "✅ 后端测试通过"
else
    echo "❌ 后端测试失败"
    TEST_FAILED=true
fi

# 显示测试结果
echo "==========================================="
echo "📊 测试结果汇总"
echo "==========================================="

if [ "$TEST_FAILED" = true ]; then
    echo "❌ 部分测试失败，请检查上述输出"
    echo "🔍 查看详细日志:"
    echo "   docker-compose -f docker-compose.test.yml logs mysql-test"
    echo "   docker-compose -f docker-compose.test.yml logs backend-test"
    
    # 清理环境
    echo "🧹 清理测试环境..."
    docker-compose -f docker-compose.test.yml down -v
    exit 1
else
    echo "🎉 所有测试通过！CI修复验证成功"
    echo "✅ MySQL连接问题已解决"
    echo "✅ Django测试配置正确"
    echo "✅ 环境变量配置有效"
fi

# 清理环境
echo "🧹 清理测试环境..."
docker-compose -f docker-compose.test.yml down -v

echo "🕐 结束时间: $(date)"
echo "✅ Docker环境测试验证完成"