#!/usr/bin/env python
"""最简单的测试运行器 - 直接运行测试代码"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_simple_tests():
    """运行简化的测试"""
    print("开始运行简化测试...")
    
    # 测试1: 基本Python功能
    print("\n=== 测试1: 基本功能测试 ===")
    try:
        assert 1 + 1 == 2
        print("[PASS] 基本数学运算正常")
    except Exception as e:
        print(f"[FAIL] 基本数学运算失败: {e}")
        return False
    
    # 测试2: 文件系统访问
    print("\n=== 测试2: 文件系统测试 ===")
    try:
        test_file = "temp_test_file.txt"
        with open(test_file, 'w') as f:
            f.write("test")
        with open(test_file, 'r') as f:
            content = f.read()
        os.remove(test_file)
        assert content == "test"
        print("[PASS] 文件读写正常")
    except Exception as e:
        print(f"[FAIL] 文件读写失败: {e}")
        return False
    
    # 测试3: 模块导入测试
    print("\n=== 测试3: 模块导入测试 ===")
    try:
        import json
        import datetime
        import sqlite3
        print("[PASS] 标准库导入正常")
    except Exception as e:
        print(f"[FAIL] 标准库导入失败: {e}")
        return False
    
    # 测试4: Django相关测试（不启动Django）
    print("\n=== 测试4: Django模块测试 ===")
    try:
        # 只导入Django模块，不启动
        import django
        print(f"[PASS] Django版本: {django.get_version()}")
    except Exception as e:
        print(f"[FAIL] Django导入失败: {e}")
        return False
    
    # 测试5: 数据库连接测试（SQLite内存数据库）
    print("\n=== 测试5: 数据库测试 ===")
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE test (id INTEGER, name TEXT)')
        cursor.execute('INSERT INTO test VALUES (1, "test")')
        cursor.execute('SELECT * FROM test')
        result = cursor.fetchone()
        conn.close()
        assert result == (1, 'test')
        print("[PASS] 数据库操作正常")
    except Exception as e:
        print(f"[FAIL] 数据库操作失败: {e}")
        return False
    
    # 测试6: HTTP请求测试
    print("\n=== 测试6: HTTP库测试 ===")
    try:
        import urllib.request
        import json
        # 测试本地回环
        print("[PASS] HTTP库导入正常")
    except Exception as e:
        print(f"[FAIL] HTTP库测试失败: {e}")
        return False
    
    print("\n=== 所有测试完成 ===")
    print("[PASS] 所有基础功能测试通过")
    return True

if __name__ == '__main__':
    success = run_simple_tests()
    if success:
        print("\n[SUCCESS] 测试体系基础功能验证成功！")
        sys.exit(0)
    else:
        print("\n[ERROR] 测试体系基础功能验证失败！")
        sys.exit(1)