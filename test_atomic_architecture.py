#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试原子化架构的完整性和依赖关系
"""

import yaml
import os
import sys

def check_workflow_dependencies():
    print("🔍 验证原子化架构依赖关系...")
    
    # 检查 branch-protection.yml 的job依赖
    with open('.github/workflows/branch-protection.yml', 'r', encoding='utf-8') as f:
        bp_workflow = yaml.safe_load(f)
    
    jobs = bp_workflow['jobs']
    print(f"📊 Branch Protection Jobs: {len(jobs)}个")
    
    # 验证关键依赖链
    key_jobs = ['setup-cache', 'unit-tests-backend', 'unit-tests-frontend', 
                'integration-tests', 'e2e-smoke', 'approval-gate']
    
    for job_name in key_jobs:
        if job_name in jobs:
            job = jobs[job_name]
            needs = job.get('needs', [])
            uses = job.get('uses', '')
            
            print(f"✅ {job_name}:")
            if needs:
                print(f"   ↳ 依赖: {needs}")
            if uses:
                print(f"   ↳ 调用: {uses}")
        else:
            print(f"❌ {job_name}: Job不存在")
    
    print("\n🔍 验证原子化组件存在性...")
    
    # 检查原子化组件
    atomic_components = [
        'setup-cache.yml',
        'test-unit-backend.yml', 
        'test-unit-frontend.yml',
        'test-integration.yml',
        'test-e2e-smoke.yml',
        'quality-security.yml'
    ]
    
    for component in atomic_components:
        path = f'.github/workflows/{component}'
        if os.path.exists(path):
            print(f"✅ {component}: 存在")
            # 验证workflow_call
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    if content and 'on' in content and 'workflow_call' in content['on']:
                        print(f"   ↳ 支持workflow_call")
                    else:
                        print(f"   ⚠️ 不支持workflow_call")
            except Exception as e:
                print(f"   ❌ 读取错误: {e}")
        else:
            print(f"❌ {component}: 不存在")

def check_cache_strategy():
    print("\n🔍 验证缓存策略...")
    
    cache_file = '.github/workflows/setup-cache.yml'
    if os.path.exists(cache_file):
        with open(cache_file, 'r', encoding='utf-8') as f:
            content = yaml.safe_load(f)
            
        jobs = content.get('jobs', {})
        setup_job = jobs.get('setup-cache', {})
        steps = setup_job.get('steps', [])
        
        cache_steps = [step for step in steps if 'cache' in step.get('name', '').lower()]
        install_steps = [step for step in steps if 'install' in step.get('name', '').lower()]
        
        print(f"✅ setup-cache.yml: 找到 {len(cache_steps)} 个缓存步骤")
        print(f"✅ setup-cache.yml: 找到 {len(install_steps)} 个安装步骤")
        
        # 检查缓存路径
        for step in cache_steps:
            if 'uses' in step and 'actions/cache' in step['uses']:
                with_config = step.get('with', {})
                key = with_config.get('key', '')
                if 'package-lock.json' in key:
                    print(f"   ↳ 使用正确的workspace缓存键: {key}")
                else:
                    print(f"   ⚠️ 缓存键可能有问题: {key}")

if __name__ == "__main__":
    try:
        check_workflow_dependencies()
        check_cache_strategy()
        print("\n🎉 原子化架构验证完成!")
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        sys.exit(1)
