#!/usr/bin/env python
"""独立测试运行器 - 不依赖pytest-django"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
from django.apps import apps

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 配置Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bravo.settings.test_simple')
django.setup()

def run_tests():
    """运行所有回归测试"""
    from tests.test_regression import (
        UserRegressionTests,
        APIHealthRegressionTests, 
        DatabaseRegressionTests
    )
    
    import unittest
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(UserRegressionTests))
    suite.addTests(loader.loadTestsFromTestCase(APIHealthRegressionTests))
    suite.addTests(loader.loadTestsFromTestCase(DatabaseRegressionTests))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print(f"\n测试结果:")
    print(f"运行测试数: {result.testsRun}")
    print(f"失败数: {len(result.failures)}")
    print(f"错误数: {len(result.errors)}")
    print(f"跳过数: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 返回是否成功
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)