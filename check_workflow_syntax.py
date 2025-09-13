#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions Workflow 语法检查器
检查常见的语法错误和最佳实践问题
"""

import yaml
import re
import os
from pathlib import Path

def check_workflow_syntax(workflow_file):
    """检查GitHub Actions workflow语法"""
    print(f"🔍 检查workflow文件: {workflow_file}")
    
    errors = []
    warnings = []
    
    try:
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 1. 基本YAML语法检查
        try:
            workflow = yaml.safe_load(content)
            print("✅ YAML语法正确")
        except yaml.YAMLError as e:
            errors.append(f"YAML语法错误: {e}")
            return errors, warnings
            
        # 2. 检查必需的顶级字段
        required_fields = ['name', 'on', 'jobs']
        for field in required_fields:
            if field not in workflow:
                errors.append(f"缺少必需字段: {field}")
                
        # 3. 检查jobs结构
        if 'jobs' in workflow:
            jobs = workflow['jobs']
            if not isinstance(jobs, dict):
                errors.append("jobs必须是字典类型")
            else:
                for job_name, job_config in jobs.items():
                    # 检查job必需字段
                    if 'runs-on' not in job_config:
                        errors.append(f"Job '{job_name}' 缺少 runs-on 字段")
                    
                    # 检查steps结构
                    if 'steps' in job_config:
                        steps = job_config['steps']
                        if not isinstance(steps, list):
                            errors.append(f"Job '{job_name}' 的 steps 必须是列表")
                        else:
                            for i, step in enumerate(steps):
                                if not isinstance(step, dict):
                                    errors.append(f"Job '{job_name}' 的第 {i+1} 个step必须是字典")
                                elif 'name' not in step:
                                    warnings.append(f"Job '{job_name}' 的第 {i+1} 个step建议添加name字段")
                                    
        # 4. 检查action版本
        action_patterns = [
            (r'actions/checkout@v(\d+)', 'actions/checkout', 4),
            (r'actions/setup-node@v(\d+)', 'actions/setup-node', 4),
            (r'actions/setup-python@v(\d+)', 'actions/setup-python', 4),
            (r'actions/cache@v(\d+)', 'actions/cache', 3),
            (r'actions/upload-artifact@v(\d+)', 'actions/upload-artifact', 4)
        ]
        
        for pattern, action_name, recommended_version in action_patterns:
            matches = re.findall(pattern, content)
            for version in matches:
                if int(version) < recommended_version:
                    warnings.append(f"{action_name} 使用了旧版本 v{version}，建议升级到 v{recommended_version}")
                    
        # 5. 检查环境变量引用
        env_refs = re.findall(r'\$\{\{\s*env\.(\w+)\s*\}\}', content)
        if 'env' in workflow:
            defined_envs = set(workflow['env'].keys())
            for env_ref in env_refs:
                if env_ref not in defined_envs:
                    errors.append(f"引用了未定义的环境变量: {env_ref}")
                    
        # 6. 检查secrets引用
        secret_refs = re.findall(r'\$\{\{\s*secrets\.(\w+)\s*\}\}', content)
        if secret_refs:
            warnings.append(f"使用了secrets: {', '.join(set(secret_refs))}，确保在仓库中已配置")
            
        # 7. 检查自定义action引用
        custom_action_refs = re.findall(r'uses:\s*\./\.github/actions/([\w-]+)', content)
        for action_ref in custom_action_refs:
            action_path = Path(workflow_file).parent.parent / 'actions' / action_ref / 'action.yml'
            if not action_path.exists():
                errors.append(f"自定义action不存在: ./.github/actions/{action_ref}")
            else:
                print(f"✅ 自定义action存在: {action_ref}")
                
        # 8. 检查缓存策略
        cache_uses = re.findall(r'uses:\s*actions/cache@v\d+', content)
        if cache_uses:
            # 检查是否有fail-on-cache-miss但没有对应的缓存创建
            fail_on_miss = 'fail-on-cache-miss: true' in content
            if fail_on_miss:
                warnings.append("使用了 fail-on-cache-miss: true，确保有对应的缓存创建步骤")
                
        # 9. 检查并发控制
        if 'concurrency' not in workflow:
            warnings.append("建议添加 concurrency 控制避免重复运行")
            
        # 10. 检查超时设置
        timeout_pattern = r'timeout-minutes:\s*(\d+)'
        timeouts = re.findall(timeout_pattern, content)
        for timeout in timeouts:
            if int(timeout) > 60:
                warnings.append(f"超时时间 {timeout} 分钟较长，考虑优化")
                
    except Exception as e:
        errors.append(f"检查过程中出错: {e}")
        
    return errors, warnings

def main():
    """主函数"""
    workflow_file = '.github/workflows/gate.yml'
    
    if not os.path.exists(workflow_file):
        print(f"❌ 文件不存在: {workflow_file}")
        return
        
    errors, warnings = check_workflow_syntax(workflow_file)
    
    print("\n" + "="*50)
    print("📋 检查结果汇总")
    print("="*50)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
    else:
        print("\n✅ 未发现语法错误")
        
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
    else:
        print("\n✅ 未发现警告")
        
    # 总结
    if not errors and not warnings:
        print("\n🎉 Workflow语法完全正确！")
    elif not errors:
        print("\n✅ Workflow语法正确，但有一些建议优化的地方")
    else:
        print("\n❌ Workflow存在语法错误，需要修复")
        
    return len(errors) == 0

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)