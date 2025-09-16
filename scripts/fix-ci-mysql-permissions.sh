#!/bin/bash
# 修复CI中MySQL权限问题的脚本

set -e

echo "🔧 修复MySQL权限问题..."

# 等待MySQL启动
until mysqladmin ping -h 127.0.0.1 -P 3306 -u root -proot_password --silent; do
  echo "等待MySQL启动..."
  sleep 2
done

# 授予bravo_user完整权限
mysql -h 127.0.0.1 -P 3306 -u root -proot_password -e "
  GRANT ALL PRIVILEGES ON *.* TO 'bravo_user'@'%' WITH GRANT OPTION;
  GRANT CREATE ON *.* TO 'bravo_user'@'%';
  FLUSH PRIVILEGES;
"

echo "✅ 已授予bravo_user完整数据库权限"

# 验证权限
mysql -h 127.0.0.1 -P 3306 -u bravo_user -pbravo_password -e "SHOW GRANTS FOR 'bravo_user'@'%';" || true

echo "🎯 MySQL权限修复完成"
