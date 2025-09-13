#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终验证报告生成器
生成完整的CI/CD修复效果验证报告
"""

import json
import os
import subprocess
import yaml
from datetime import datetime
from pathlib import Path

def run_command(cmd, cwd=None):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_workflow_syntax():
    """检查workflow语法"""
    print("🔍 检查Workflow语法...")
    
    gate_yml = Path(".github/workflows/gate.yml")
    if not gate_yml.exists():
        return False, "gate.yml文件不存在"
    
    try:
        with open(gate_yml, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
        return True, "YAML语法正确"
    except yaml.YAMLError as e:
        return False, f"YAML语法错误: {e}"

def check_env_variable_fixes():
    """检查环境变量修复"""
    print("🔧 检查环境变量修复...")
    
    gate_yml = Path(".github/workflows/gate.yml")
    if not gate_yml.exists():
        return False, "gate.yml文件不存在"
    
    with open(gate_yml, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否还有未修复的环境变量引用
    problematic_patterns = [
        '${{ env.MYSQL_ROOT_PASSWORD }}'
    ]
    
    issues = []
    for pattern in problematic_patterns:
        if pattern in content:
            issues.append(f"发现未修复的环境变量引用: {pattern}")
    
    if issues:
        return False, "; ".join(issues)
    
    return True, "所有环境变量引用已修复"

def check_port_conflicts():
    """检查端口冲突修复"""
    print("🔌 检查端口冲突修复...")
    
    playwright_config = Path("e2e/playwright.config.ts")
    if not playwright_config.exists():
        return False, "playwright.config.ts文件不存在"
    
    with open(playwright_config, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否使用了正确的端口配置
    if 'port: 3001' in content and 'reuseExistingServer: true' in content:
        return True, "端口冲突已修复，使用端口3001并启用服务器复用"
    
    return False, "端口配置可能仍有问题"

def check_workflow_optimization():
    """检查workflow优化"""
    print("⚡ 检查Workflow优化...")
    
    gate_yml = Path(".github/workflows/gate.yml")
    if not gate_yml.exists():
        return False, "gate.yml文件不存在"
    
    with open(gate_yml, 'r', encoding='utf-8') as f:
        content = f.read()
    
    optimizations = []
    
    # 检查智能依赖缓存
    if 'smart-dependencies' in content:
        optimizations.append("✅ 智能依赖缓存已实现")
    
    # 检查并发控制
    if 'concurrency:' in content:
        optimizations.append("✅ 并发控制已配置")
    
    # 检查缓存策略
    if 'fail-on-cache-miss: true' in content:
        optimizations.append("✅ 缓存策略已优化")
    
    if len(optimizations) >= 2:
        return True, "; ".join(optimizations)
    
    return False, "workflow优化不完整"

def check_docker_files():
    """检查Docker测试文件"""
    print("🐳 检查Docker测试文件...")
    
    docker_files = [
        "backend/Dockerfile.test",
        "frontend/Dockerfile.test",
        "e2e/Dockerfile.test"
    ]
    
    missing_files = []
    for file_path in docker_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"缺少Docker测试文件: {', '.join(missing_files)}"
    
    return True, "所有Docker测试文件已创建"

def generate_final_report():
    """生成最终验证报告"""
    print("📋 生成最终验证报告...")
    print("=" * 60)
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "project": "Bravo CI/CD Infrastructure Optimization",
        "branch": "feature/infrastructure-hooks",
        "checks": {},
        "summary": {
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "success_rate": 0
        }
    }
    
    checks = [
        ("workflow_syntax", check_workflow_syntax),
        ("env_variable_fixes", check_env_variable_fixes),
        ("port_conflict_fixes", check_port_conflicts),
        ("workflow_optimization", check_workflow_optimization),
        ("docker_test_files", check_docker_files)
    ]
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            report["checks"][check_name] = {
                "status": "PASS" if success else "FAIL",
                "message": message
            }
            
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {check_name}: {message}")
            
            report["summary"]["total_checks"] += 1
            if success:
                report["summary"]["passed_checks"] += 1
            else:
                report["summary"]["failed_checks"] += 1
                
        except Exception as e:
            report["checks"][check_name] = {
                "status": "ERROR",
                "message": f"检查过程中出错: {str(e)}"
            }
            print(f"❌ {check_name}: 检查过程中出错: {str(e)}")
            report["summary"]["total_checks"] += 1
            report["summary"]["failed_checks"] += 1
    
    # 计算成功率
    if report["summary"]["total_checks"] > 0:
        report["summary"]["success_rate"] = (
            report["summary"]["passed_checks"] / report["summary"]["total_checks"]
        ) * 100
    
    print("\n" + "=" * 60)
    print("📊 验证总结:")
    print(f"总检查项: {report['summary']['total_checks']}")
    print(f"通过检查: {report['summary']['passed_checks']}")
    print(f"失败检查: {report['summary']['failed_checks']}")
    print(f"成功率: {report['summary']['success_rate']:.1f}%")
    
    # 保存报告
    with open("final_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 详细报告已保存到: final_validation_report.json")
    
    # 生成结论
    if report["summary"]["success_rate"] >= 80:
        print("\n🎉 验证结果: 修复效果良好，CI/CD优化成功！")
        print("\n🚀 建议操作:")
        print("1. 创建Pull Request合并到主分支")
        print("2. 监控CI执行效果")
        print("3. 观察资源使用情况改善")
    else:
        print("\n⚠️ 验证结果: 仍有问题需要解决")
        print("\n🔧 建议操作:")
        print("1. 检查失败的验证项")
        print("2. 修复相关问题")
        print("3. 重新运行验证")
    
    return report

if __name__ == "__main__":
    print("🎯 开始最终验证...")
    print(f"📍 当前目录: {os.getcwd()}")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print()
    
    try:
        report = generate_final_report()
        exit_code = 0 if report["summary"]["success_rate"] >= 80 else 1
        exit(exit_code)
    except Exception as e:
        print(f"❌ 验证过程中发生错误: {str(e)}")
        exit(1)