#!/usr/bin/env python3
"""
验证CI修复效果的脚本
测试数据库连接配置是否正确
"""

import os
import sys
import subprocess
from pathlib import Path

def test_database_config():
    """测试数据库配置是否正确"""
    print("🔍 验证数据库配置...")
    
    # 测试环境变量
    test_env = os.environ.copy()
    test_env['GITHUB_ACTIONS'] = 'true'
    test_env['DJANGO_SETTINGS_MODULE'] = 'bravo.settings.test'
    
    # 运行Django配置检查
    backend_dir = Path(__file__).parent / 'backend'
    if not backend_dir.exists():
        print("❌ 后端目录不存在")
        return False
    
    try:
        # 检查Django数据库配置
        result = subprocess.run([
            sys.executable, '-c', 
            '''
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "bravo.settings.test"
import django
django.setup()
from django.conf import settings
db = settings.DATABASES["default"]
print(f"HOST: {db['HOST']}")
print(f"PORT: {db['PORT']}")
print(f"NAME: {db['NAME']}")
print(f"USER: {db['USER']}")
print("配置检查完成")
'''
        ], 
        cwd=str(backend_dir),
        capture_output=True, text=True, env=test_env)
        
        if result.returncode == 0:
            print("✅ Django配置检查通过")
            print(result.stdout.encode('utf-8').decode('utf-8', 'ignore'))
            
            # 检查HOST是否为127.0.0.1
            if "HOST: 127.0.0.1" in result.stdout:
                print("✅ 数据库主机名配置正确")
                return True
            else:
                print("❌ 数据库主机名配置错误")
                return False
        else:
            print("❌ Django配置检查失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_ci_fix_script():
    """测试CI修复脚本"""
    print("\n🔍 验证CI修复脚本...")
    
    test_env = os.environ.copy()
    test_env['GITHUB_ACTIONS'] = 'true'
    
    try:
        result = subprocess.run([
            sys.executable, 'test_ci_fix.py'
        ], 
        capture_output=True, text=True, env=test_env)
        
        if result.returncode == 0:
            print("✅ CI修复脚本运行成功")
            return True
        else:
            print("❌ CI修复脚本运行失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 脚本测试失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🚀 开始验证CI修复效果...")
    print("=" * 50)
    
    # 测试数据库配置
    db_ok = test_database_config()
    
    # 测试CI修复脚本
    script_ok = test_ci_fix_script()
    
    print("\n" + "=" * 50)
    if db_ok and script_ok:
        print("🎉 所有验证通过！CI修复成功")
        return 0
    else:
        print("❌ 验证失败，需要进一步修复")
        return 1

if __name__ == "__main__":
    sys.exit(main())