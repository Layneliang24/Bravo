#!/usr/bin/env python
"""
独立覆盖率测试脚本
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner
import coverage

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bravo.settings.test')
django.setup()

def run_coverage_test():
    """运行带覆盖率的测试"""
    # 初始化覆盖率
    cov = coverage.Coverage()
    cov.start()
    
    try:
        # 导入并运行测试
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
        
        # 停止覆盖率收集
        cov.stop()
        cov.save()
        
        # 生成覆盖率报告
        print("\n" + "="*50)
        print("覆盖率报告")
        print("="*50)
        cov.report(show_missing=True)
        
        # 计算覆盖率百分比
        total_coverage = cov.report(show_missing=False)
        print(f"\n总覆盖率: {total_coverage:.1f}%")
        
        if total_coverage >= 50:
            print("✅ 覆盖率测试通过 (≥50%)")
            return True
        else:
            print("❌ 覆盖率测试失败 (<50%)")
            return False
            
    except Exception as e:
        print(f"覆盖率测试出错: {e}")
        return False
    finally:
        cov.stop()

if __name__ == '__main__':
    success = run_coverage_test()
    sys.exit(0 if success else 1)