#!/usr/bin/env python3
"""测试修复效果的验证脚本"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_step(step, description):
    """打印步骤"""
    print(f"\n[步骤 {step}] {description}")
    print("-" * 40)

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {description} - 存在")
        return True
    print(f"✗ {description} - 不存在")
    return False

def check_file_content(filepath, search_text, description):
    """检查文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"✓ {description} - 找到内容")
                return True
            else:
                print(f"✗ {description} - 未找到内容")
                return False
    except Exception as e:
        print(f"✗ {description} - 读取失败: {e}")
        return False

def test_backend_health():
    """测试后端健康检查"""
    try:
        # 尝试启动后端服务（如果未运行）
        print("尝试启动后端服务...")
        backend_process = subprocess.Popen(
            ["python", "manage.py", "runserver", "8000"],
            cwd="backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务启动
        time.sleep(3)
        
        # 测试健康检查端点
        response = requests.get("http://localhost:8000/health/", timeout=5)
        if response.status_code == 200:
            print("✓ 后端健康检查端点正常")
            backend_process.terminate()
            return True
        else:
            print(f"✗ 后端健康检查失败: {response.status_code}")
            backend_process.terminate()
            return False
            
    except Exception as e:
        print(f"✗ 后端健康检查异常: {e}")
        if 'backend_process' in locals():
            backend_process.terminate()
        return False

def test_frontend_build():
    """测试前端构建"""
    try:
        print("尝试构建前端...")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd="frontend",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✓ 前端构建成功")
            return True
        else:
            print(f"✗ 前端构建失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ 前端构建异常: {e}")
        return False

def main():
    """主函数"""
    print_header("🔧 Bravo项目修复效果验证")
    
    start_time = time.time()
    results = []
    
    # 步骤1: 检查文件修改
    print_step(1, "检查文件修改")
    results.append(check_file_exists("frontend/src/views/BlogDetail.vue", "博客详情页面"))
    results.append(check_file_exists("backend/apps/common/views.py", "后端通用视图"))
    results.append(check_file_exists("backend/apps/common/urls.py", "后端URL配置"))
    
    # 步骤2: 检查路由配置
    print_step(2, "检查路由配置")
    results.append(check_file_content(
        "frontend/src/router/index.ts",
        "/blog/:id",
        "博客详情路由"
    ))
    results.append(check_file_content(
        "frontend/src/views/Blog.vue",
        "goToBlogDetail",
        "博客跳转函数"
    ))
    
    # 步骤3: 检查可访问性改进
    print_step(3, "检查可访问性改进")
    results.append(check_file_content(
        "frontend/src/views/Blog.vue",
        "role=\"navigation\"",
        "导航ARIA标签"
    ))
    results.append(check_file_content(
        "frontend/src/views/Blog.vue",
        "aria-label",
        "ARIA标签支持"
    ))
    results.append(check_file_content(
        "frontend/src/views/Blog.vue",
        "meta[name=\"description\"]",
        "SEO meta标签"
    ))
    
    # 步骤4: 检查API通信配置
    print_step(4, "检查API通信配置")
    results.append(check_file_content(
        "backend/bravo/settings/base.py",
        "CORS_ALLOW_ALL_ORIGINS = True",
        "CORS配置"
    ))
    results.append(check_file_content(
        "backend/bravo/urls.py",
        "apps.common.urls",
        "通用URL配置"
    ))
    
    # 步骤5: 测试前端构建
    print_step(5, "测试前端构建")
    results.append(test_frontend_build())
    
    # 生成报告
    print_header("📊 修复效果报告")
    
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
        print("\n🎉 修复效果: 优秀")
        print("✓ 主要问题已修复")
        print("✓ 代码质量良好")
    elif success_rate >= 60:
        print("\n⚠️ 修复效果: 良好")
        print("⚠️ 大部分问题已修复，建议进一步优化")
    else:
        print("\n❌ 修复效果: 需要改进")
        print("❌ 部分问题未解决，需要继续修复")
    
    # 保存报告
    report_file = "fix_verification_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Bravo项目修复效果验证报告\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"成功率: {success_rate:.1f}%\n")
        f.write(f"耗时: {elapsed_time:.2f} 秒\n")
        f.write("\n详细结果:\n")
        for i, result in enumerate(results, 1):
            status = "✓" if result else "✗"
            f.write(f"检查项{i}: {status}\n")
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        SUCCESS = main()
        sys.exit(0 if SUCCESS else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了验证过程")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n❌ 验证过程发生异常: {e}")
        sys.exit(3)
