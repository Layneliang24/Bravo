#!/usr/bin/env python3
"""
测试CI修复验证脚本
用于验证MySQL连接和Django配置是否正确
"""

import os
import sys
import django
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bravo.settings.test')

# 模拟CI环境变量
os.environ['CI'] = 'true'
# 在Docker环境中使用服务名，在CI环境中使用127.0.0.1
os.environ['DB_HOST'] = os.environ.get('DB_HOST', 'mysql-test')
os.environ['DB_PORT'] = os.environ.get('DB_PORT', '3306')
os.environ['DB_NAME'] = os.environ.get('DB_NAME', 'bravo_test')
os.environ['DB_USER'] = os.environ.get('DB_USER', 'bravo_user')
os.environ['DB_PASSWORD'] = os.environ.get('DB_PASSWORD', 'bravo_password')

print("🧪 开始验证CI修复...")
print(f"📍 当前工作目录: {os.getcwd()}")
print(f"🔧 CI环境: {os.environ.get('CI')}")
print(f"🗄️ 数据库主机: {os.environ.get('DB_HOST')}")

try:
    # 初始化Django
    django.setup()
    print("✅ Django设置成功")
    
    # 首先尝试创建数据库（如果不存在）
    import MySQLdb
    print("🔧 确保测试数据库存在...")
    try:
        conn = MySQLdb.connect(
            host=os.environ.get('DB_HOST', 'mysql-test'),
            port=int(os.environ.get('DB_PORT', '3306')),
            user=os.environ.get('DB_USER', 'bravo_user'),
            passwd=os.environ.get('DB_PASSWORD', 'bravo_password')
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.environ.get('DB_NAME', 'bravo_test')}")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 测试数据库已确保存在")
    except Exception as e:
        print(f"⚠️ 数据库创建警告: {e}")
    
    # 测试数据库连接
    from django.db import connection
    from django.core.management.color import no_style
    
    print("🔍 测试数据库连接...")
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    print(f"✅ 数据库连接成功: {result}")
    
    # 检查数据库配置
    from django.conf import settings
    db_config = settings.DATABASES['default']
    print(f"📋 数据库配置:")
    print(f"   引擎: {db_config['ENGINE']}")
    print(f"   主机: {db_config['HOST']}")
    print(f"   端口: {db_config['PORT']}")
    print(f"   数据库: {db_config['NAME']}")
    print(f"   用户: {db_config['USER']}")
    
    # 测试迁移
    print("🔄 测试数据库迁移...")
    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
    print("✅ 数据库迁移成功")
    
    print("🎉 所有测试通过！CI修复验证成功")
    
except Exception as e:
    print(f"❌ 验证失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)