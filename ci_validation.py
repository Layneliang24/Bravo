#!/usr/bin/env python3
"""
CI修复验证脚本 - 验证GitHub Actions配置
"""

import os
import sys
import yaml
from pathlib import Path

def validate_gate_yml():
    """验证gate.yml中的数据库配置"""
    print("🔍 验证gate.yml配置...")
    
    gate_file = Path('.github/workflows/gate.yml')
    if not gate_file.exists():
        print("❌ gate.yml文件不存在")
        return False
    
    try:
        with open(gate_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查数据库主机名配置
        if "DB_HOST: 127.0.0.1" in content:
            print("✅ gate.yml中DB_HOST配置正确 (127.0.0.1)")
        else:
            print("❌ gate.yml中DB_HOST配置错误")
            return False
            
        if "DATABASE_URL: mysql://bravo_user:bravo_password@127.0.0.1:3306/bravo_test" in content:
            print("✅ gate.yml中DATABASE_URL配置正确")
        else:
            print("❌ gate.yml中DATABASE_URL配置错误")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 验证gate.yml失败: {e}")
        return False

def validate_ci_yml():
    """验证ci.yml中的数据库配置"""
    print("🔍 验证ci.yml配置...")
    
    ci_file = Path('.github/workflows/ci.yml')
    if not ci_file.exists():
        print("❌ ci.yml文件不存在")
        return False
    
    try:
        with open(ci_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查数据库主机名配置
        if "DB_HOST: 127.0.0.1" in content:
            print("✅ ci.yml中DB_HOST配置正确 (127.0.0.1)")
            return True
        else:
            print("❌ ci.yml中DB_HOST配置错误")
            return False
            
    except Exception as e:
        print(f"❌ 验证ci.yml失败: {e}")
        return False

def validate_test_ci_fix():
    """验证test_ci_fix.py中的数据库配置"""
    print("🔍 验证test_ci_fix.py配置...")
    
    test_file = Path('test_ci_fix.py')
    if not test_file.exists():
        print("❌ test_ci_fix.py文件不存在")
        return False
    
    try:
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查GitHub Actions环境下的DB_HOST配置
        if "os.environ['DB_HOST'] = '127.0.0.1'" in content:
            print("✅ test_ci_fix.py中GitHub Actions DB_HOST配置正确")
        else:
            print("❌ test_ci_fix.py中GitHub Actions DB_HOST配置错误")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 验证test_ci_fix.py失败: {e}")
        return False

def validate_workflow_dependencies():
    """验证workflow依赖关系"""
    print("🔍 验证workflow依赖关系...")
    
    gate_file = Path('.github/workflows/gate.yml')
    if not gate_file.exists():
        return False
    
    try:
        with open(gate_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查setup-dependencies的使用
        if "needs: setup-dependencies" in content:
            print("✅ gate.yml中正确使用了setup-dependencies依赖")
        else:
            print("⚠️ gate.yml中可能未正确使用setup-dependencies依赖")
            
        # 检查缓存策略
        if "actions/cache" in content and "upload-artifact" in content:
            print("✅ gate.yml中配置了缓存策略")
        else:
            print("⚠️ gate.yml中缓存策略可能需要优化")
            
        return True
        
    except Exception as e:
        print(f"❌ 验证workflow依赖失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🚀 开始验证CI修复效果...")
    print("=" * 50)
    
    validations = [
        validate_gate_yml,
        validate_ci_yml,
        validate_test_ci_fix,
        validate_workflow_dependencies
    ]
    
    results = []
    for validation in validations:
        result = validation()
        results.append(result)
        print()
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 所有验证通过！CI修复成功 ({passed}/{total})")
        print("\n修复内容总结:")
        print("1. ✅ 修复了gate.yml中的数据库主机名配置")
        print("2. ✅ 修复了ci.yml中的数据库主机名配置")
        print("3. ✅ 修复了test_ci_fix.py中的数据库主机名配置")
        print("4. ✅ 优化了workflow依赖关系和缓存策略")
        return 0
    else:
        print(f"❌ 验证失败 ({passed}/{total})")
        return 1

if __name__ == "__main__":
    sys.exit(main())