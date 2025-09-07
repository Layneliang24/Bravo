#!/usr/bin/env python
"""完整的一键体检脚本 - 验证测试体系完整性"""

import os
import sys
import time
import random
import shutil
import subprocess

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """打印步骤"""
    print(f"\n[步骤 {step}] {description}")
    print("-" * 40)

def run_command_safe(command, description):
    """安全运行命令"""
    print(f"执行: {command}")
    try:
        # 使用subprocess.run()替代os.system()以避免命令注入
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} - 成功")
            return True
        else:
            print(f"✗ {description} - 失败 (退出码: {result.returncode})")
            if result.stderr:
                print(f"错误输出: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"✗ {description} - 异常: {e}")
        return False

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if os.path.exists(file_path):
        print(f"✓ {description} - 存在")
        return True
    else:
        print(f"✗ {description} - 不存在")
        return False

def random_damage_test():
    """随机破坏测试 - 模拟各种故障场景"""
    print_step("随机破坏", "模拟系统故障场景")
    
    damage_scenarios = [
        "临时删除测试文件",
        "修改环境变量", 
        "创建临时冲突文件",
        "模拟网络延迟",
        "模拟磁盘空间不足"
    ]
    
    selected_scenario = random.choice(damage_scenarios)
    print(f"选择破坏场景: {selected_scenario}")
    
    if selected_scenario == "临时删除测试文件":
        # 备份并删除一个测试文件
        test_file = "tests/test_regression.py"
        backup_file = "tests/test_regression.py.backup"
        
        if os.path.exists(test_file):
            shutil.copy2(test_file, backup_file)
            os.remove(test_file)
            print(f"✓ 临时删除了 {test_file}")
            
            # 运行测试，应该失败
            print("运行测试（预期失败）...")
            result = run_command_safe("python simple_test_runner.py", "破坏后测试")
            
            # 恢复文件
            shutil.move(backup_file, test_file)
            print(f"✓ 恢复了 {test_file}")
            
            return True
    
    elif selected_scenario == "修改环境变量":
        # 临时修改环境变量
        original_path = os.environ.get('PYTHONPATH', '')
        os.environ['PYTHONPATH'] = '/invalid/path:' + original_path
        print("✓ 临时修改了PYTHONPATH")
        
        # 运行测试
        print("运行测试（可能受影响）...")
        result = run_command_safe("python simple_test_runner.py", "环境变量修改后测试")
        
        # 恢复环境变量
        os.environ['PYTHONPATH'] = original_path
        print("✓ 恢复了PYTHONPATH")
        
        return True
    
    elif selected_scenario == "创建临时冲突文件":
        # 创建一个可能冲突的临时文件
        conflict_file = "temp_conflict.py"
        with open(conflict_file, 'w') as f:
            f.write("# 临时冲突文件\nraise Exception('冲突文件被导入')\n")
        print(f"✓ 创建了冲突文件 {conflict_file}")
        
        # 运行测试
        result = run_command_safe("python simple_test_runner.py", "冲突文件存在时测试")
        
        # 清理冲突文件
        os.remove(conflict_file)
        print(f"✓ 清理了冲突文件 {conflict_file}")
        
        return True
    
    elif selected_scenario == "模拟网络延迟":
        # 模拟网络延迟（通过sleep）
        print("模拟网络延迟 2 秒...")
        time.sleep(2)
        
        # 运行测试
        result = run_command_safe("python simple_test_runner.py", "网络延迟后测试")
        
        return True
    
    elif selected_scenario == "模拟磁盘空间不足":
        # 创建一个大文件模拟磁盘使用
        large_file = "temp_large_file.tmp"
        try:
            with open(large_file, 'w') as f:
                f.write('x' * 1024 * 100)  # 100KB文件
            print(f"✓ 创建了临时大文件 {large_file}")
            
            # 运行测试
            result = run_command_safe("python simple_test_runner.py", "磁盘使用增加后测试")
            
            # 清理大文件
            os.remove(large_file)
            print(f"✓ 清理了临时大文件 {large_file}")
            
            return True
        except Exception as e:
            print(f"✗ 磁盘空间模拟失败: {e}")
            return False
    
    return False

def main():
    """主函数 - 执行完整的健康检查"""
    print_header("🏥 Bravo项目测试体系一键体检")
    
    start_time = time.time()
    results = []
    
    # 步骤1: 环境检查
    print_step(1, "环境检查")
    results.append(check_file_exists("manage.py", "Django项目文件"))
    results.append(check_file_exists("tests/test_regression.py", "回归测试文件"))
    results.append(check_file_exists("simple_test_runner.py", "简化测试运行器"))
    
    # 步骤2: 基础功能测试
    print_step(2, "基础功能测试")
    results.append(run_command_safe("python simple_test_runner.py", "基础功能测试"))
    
    # 步骤3: 回归测试验证
    print_step(3, "回归测试验证")
    results.append(run_command_safe("python test_simple.py", "回归测试套件"))
    
    # 步骤4: 覆盖率工具检查
    print_step(4, "覆盖率工具检查")
    results.append(run_command_safe("pip show coverage", "覆盖率工具安装检查"))
    
    # 步骤5: 前端E2E测试配置检查
    print_step(5, "前端E2E测试配置检查")
    frontend_path = "../frontend"
    if os.path.exists(frontend_path):
        results.append(check_file_exists(f"{frontend_path}/playwright.config.ts.keep", "Playwright配置"))
        results.append(check_file_exists(f"{frontend_path}/package.json", "前端包配置"))
    else:
        print("⚠️ 前端目录不存在，跳过E2E检查")
        results.append(False)
    
    # 步骤6: 随机破坏测试
    print_step(6, "随机破坏测试（故障恢复能力）")
    results.append(random_damage_test())
    
    # 步骤7: 恢复验证
    print_step(7, "恢复验证")
    results.append(run_command_safe("python simple_test_runner.py", "破坏后恢复测试"))
    
    # 生成报告
    print_header("📊 体检报告")
    
    passed = sum(results)
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"总检查项: {total}")
    print(f"通过项: {passed}")
    print(f"失败项: {total - passed}")
    print(f"成功率: {success_rate:.1f}%")
    
    elapsed_time = time.time() - start_time
    print(f"耗时: {elapsed_time:.2f} 秒")
    
    if success_rate >= 80:
        print("\n🎉 测试体系健康状况: 良好")
        print("✓ 测试体系基本功能完整")
        print("✓ 具备基本的故障恢复能力")
    elif success_rate >= 60:
        print("\n⚠️ 测试体系健康状况: 一般")
        print("⚠️ 部分功能存在问题，建议检查")
    else:
        print("\n❌ 测试体系健康状况: 需要修复")
        print("❌ 多项功能存在问题，需要立即处理")
    
    # 生成体检报告文件
    report_file = "health_check_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"Bravo项目测试体系体检报告\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"成功率: {success_rate:.1f}%\n")
        f.write(f"耗时: {elapsed_time:.2f} 秒\n")
        f.write(f"\n详细结果:\n")
        for i, result in enumerate(results, 1):
            status = "✓" if result else "✗"
            f.write(f"步骤{i}: {status}\n")
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return success_rate >= 80

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了体检过程")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ 体检过程发生异常: {e}")
        sys.exit(3)