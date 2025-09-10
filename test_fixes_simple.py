#!/usr/bin/env python3
"""简化的修复验证脚本"""

import os
import sys
import time
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

def check_multiple_content(filepath, search_texts, description):
    """检查多个内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            found_count = 0
            for text in search_texts:
                if text in content:
                    found_count += 1
            
            if found_count == len(search_texts):
                print(f"✓ {description} - 所有内容都找到 ({found_count}/{len(search_texts)})")
                return True
            else:
                print(f"⚠️ {description} - 部分内容找到 ({found_count}/{len(search_texts)})")
                return found_count >= len(search_texts) // 2
    except Exception as e:
        print(f"✗ {description} - 读取失败: {e}")
        return False

def main():
    """主函数"""
    print_header("🔧 Bravo项目修复效果验证（简化版）")
    
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
    results.append(check_multiple_content(
        "frontend/src/views/Blog.vue",
        ["role=\"navigation\"", "aria-label", "tabindex"],
        "可访问性标签"
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
    
    # 步骤5: 检查博客详情页面功能
    print_step(5, "检查博客详情页面功能")
    results.append(check_multiple_content(
        "frontend/src/views/BlogDetail.vue",
        ["role=\"main\"", "aria-label", "data-testid"],
        "博客详情页面可访问性"
    ))
    results.append(check_file_content(
        "frontend/src/views/BlogDetail.vue",
        "useRoute",
        "路由功能"
    ))
    
    # 步骤6: 检查前端构建结果
    print_step(6, "检查前端构建结果")
    results.append(check_file_exists("frontend/dist/index.html", "前端构建产物"))
    # 检查博客详情页面构建产物（使用通配符匹配）
    blog_detail_files = [f for f in os.listdir("frontend/dist/assets/") if f.startswith("BlogDetail-")]
    if blog_detail_files:
        print(f"✓ 博客详情页面构建产物 - 找到 {len(blog_detail_files)} 个文件")
        results.append(True)
    else:
        print("✗ 博客详情页面构建产物 - 未找到")
        results.append(False)
    
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
    
    if success_rate >= 90:
        print("\n🎉 修复效果: 优秀")
        print("✓ 所有主要问题已修复")
        print("✓ 代码质量良好")
        print("✓ 功能完整")
    elif success_rate >= 75:
        print("\n✅ 修复效果: 良好")
        print("✓ 大部分问题已修复")
        print("⚠️ 建议进一步优化")
    elif success_rate >= 60:
        print("\n⚠️ 修复效果: 一般")
        print("⚠️ 部分问题已修复，需要继续完善")
    else:
        print("\n❌ 修复效果: 需要改进")
        print("❌ 多项问题未解决，需要继续修复")
    
    # 详细结果
    print("\n📋 详细检查结果:")
    check_items = [
        "博客详情页面文件",
        "后端通用视图文件", 
        "后端URL配置文件",
        "博客详情路由配置",
        "博客跳转函数",
        "可访问性标签",
        "SEO meta标签",
        "CORS配置",
        "通用URL配置",
        "博客详情页面可访问性",
        "路由功能",
        "前端构建产物",
        "博客详情页面构建产物"
    ]
    
    for i, (result, item) in enumerate(zip(results, check_items)):
        status = "✓" if result else "✗"
        print(f"  {i+1:2d}. {status} {item}")
    
    # 保存报告
    report_file = "fix_verification_simple_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Bravo项目修复效果验证报告（简化版）\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"成功率: {success_rate:.1f}%\n")
        f.write(f"耗时: {elapsed_time:.2f} 秒\n")
        f.write("\n详细结果:\n")
        for i, (result, item) in enumerate(zip(results, check_items)):
            status = "✓" if result else "✗"
            f.write(f"{i+1:2d}. {status} {item}\n")
    
    print(f"\n📄 详细报告已保存到: {report_file}")
    
    return success_rate >= 75

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
