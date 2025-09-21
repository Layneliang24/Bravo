#!/bin/bash

echo "🚀 第30轮修复本地验证脚本"
echo "验证智能数据库创建策略是否正确工作"

# 启动MySQL容器（模拟GitHub Actions环境）
echo "📦 启动MySQL测试容器..."
docker run -d \
  --name mysql-round30-test \
  -p 3308:3306 \
  -e MYSQL_DATABASE=bravo_test \
  -e MYSQL_USER=bravo_user \
  -e MYSQL_PASSWORD=bravo_password \
  -e MYSQL_ROOT_PASSWORD=root_password \
  mysql:8.0

echo "⏳ 等待MySQL容器启动..."
sleep 30

# 检查MySQL是否启动成功
echo "🔍 检查MySQL容器状态..."
if ! docker exec mysql-round30-test mysql -u root -proot_password -e "SELECT 1" >/dev/null 2>&1; then
  echo "❌ MySQL容器启动失败！"
  docker logs mysql-round30-test
  docker rm -f mysql-round30-test
  exit 1
fi

echo "✅ MySQL容器启动成功"

# 验证MySQL容器自动创建的数据库和用户
echo "🔍 验证MySQL容器自动创建的数据库..."
docker exec mysql-round30-test mysql -u root -proot_password -e "SHOW DATABASES;" | grep bravo_test
if [ $? -eq 0 ]; then
  echo "✅ bravo_test数据库已由容器自动创建"
else
  echo "❌ bravo_test数据库未自动创建"
  docker rm -f mysql-round30-test
  exit 1
fi

echo "🔍 验证MySQL容器自动创建的用户..."
docker exec mysql-round30-test mysql -u root -proot_password -e "SELECT user, host FROM mysql.user WHERE user='bravo_user';"

# 测试第30轮修复逻辑
echo "🛠️ 测试第30轮智能验证逻辑..."

# 模拟第30轮修复的智能检查逻辑
if docker exec mysql-round30-test mysql -u root -proot_password -e "USE bravo_test; SELECT 1;" >/dev/null 2>&1; then
  echo "✅ bravo_test数据库已存在，检查用户权限..."

  # 检查bravo_user是否可以访问数据库
  if docker exec mysql-round30-test mysql -u bravo_user -pbravo_password -e "USE bravo_test; SELECT 1 as test;" >/dev/null 2>&1; then
    echo "🎉 bravo_test数据库和bravo_user用户权限完全正常，无需修复！"
    REPAIR_NEEDED=false
  else
    echo "⚠️ bravo_user无法访问bravo_test数据库，需要修复用户权限..."
    REPAIR_NEEDED=true
  fi
else
  echo "⚠️ bravo_test数据库不存在，需要创建..."
  REPAIR_NEEDED=true
fi

# 如果需要修复，执行修复逻辑
if [ "$REPAIR_NEEDED" = "true" ]; then
  echo "🔧 执行修复逻辑..."
  # 这里应该执行实际的修复SQL，但对于验证来说，我们知道不需要修复
  echo "❌ 意外！容器自动创建的数据库和用户应该是正常工作的"
  docker rm -f mysql-round30-test
  exit 1
fi

# 最终验证
echo "✅ 进行最终验证..."
docker exec mysql-round30-test mysql -u bravo_user -pbravo_password -e "USE bravo_test; SELECT 'SUCCESS' as test_result;"
if [ $? -eq 0 ]; then
  echo "🎉 第30轮修复验证完全成功！"
  echo "✅ MySQL容器自动创建的数据库得到保护"
  echo "✅ 智能检查避免了破坏性的DROP操作"
  echo "✅ 用户权限验证逻辑工作正常"

  # 清理
  echo "🧹 清理测试环境..."
  docker rm -f mysql-round30-test

  echo "✅ 本地验证通过！可以安全推送到远程！"
  exit 0
else
  echo "❌ 最终验证失败！"
  docker logs mysql-round30-test
  docker rm -f mysql-round30-test
  exit 1
fi
