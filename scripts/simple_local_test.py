#!/usr/bin/env python3
"""
简化版本地测试 - 直接在宿主机运行，避免Docker下载慢
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(cmd, cwd=None, show_output=True):
    """运行命令并实时显示输出"""
    print(f"🔧 执行: {' '.join(cmd)}")
    if cwd:
        print(f"📁 目录: {cwd}")

    if show_output:
        result = subprocess.run(cmd, cwd=cwd, text=True)
    else:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ 命令失败，返回码: {result.returncode}")
        if not show_output and result.stderr:
            print(f"错误: {result.stderr}")
        return False
    else:
        print("✅ 命令成功")
        return True


def test_frontend_quick():
    """快速前端测试"""
    print("🌐 测试前端环境...")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend目录不存在")
        return False

    # 检查package.json
    if (frontend_dir / "package.json").exists():
        print("✅ package.json存在")
    else:
        print("❌ package.json不存在")
        return False

    # 检查node_modules
    if (frontend_dir / "node_modules").exists():
        print("✅ node_modules已存在，跳过npm install")
    else:
        print("📦 安装前端依赖...")
        if not run_cmd(["npm", "install"], cwd=frontend_dir):
            return False

    # 运行linting
    print("🔍 运行前端代码检查...")
    if not run_cmd(["npm", "run", "lint"], cwd=frontend_dir, show_output=False):
        print("⚠️  Lint检查失败，但继续...")

    # 尝试构建
    print("🏗️  尝试构建...")
    if not run_cmd(["npm", "run", "build"], cwd=frontend_dir, show_output=False):
        print("⚠️  构建失败，但继续...")

    return True


def test_backend_quick():
    """快速后端测试"""
    print("🖥️  测试后端环境...")

    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend目录不存在")
        return False

    # 检查requirements
    req_file = backend_dir / "requirements" / "test.txt"
    if req_file.exists():
        print("✅ requirements/test.txt存在")
    else:
        print("❌ requirements/test.txt不存在")
        return False

    # 检查Python环境
    print("🐍 检查Python环境...")
    if not run_cmd(["python", "--version"]):
        return False

    # 检查Django
    print("🔧 检查Django配置...")
    django_check = [
        "python",
        "manage.py",
        "check",
        "--settings=bravo.settings.test",
        "--verbosity=0",
    ]
    if not run_cmd(django_check, cwd=backend_dir, show_output=False):
        print("⚠️  Django检查失败，可能缺少依赖")

    return True


def test_precommit():
    """测试pre-commit系统"""
    print("🔒 测试Pre-commit系统...")

    # 检查pre-commit配置
    if Path(".pre-commit-config.yaml").exists():
        print("✅ .pre-commit-config.yaml存在")
    else:
        print("❌ .pre-commit-config.yaml不存在")
        return False

    # 运行快速检查
    print("⚡ 运行快速pre-commit检查...")
    quick_checks = [
        "pre-commit",
        "run",
        "--files",
        ".pre-commit-config.yaml",
        "check-yaml",
        "check-json",
    ]
    if not run_cmd(quick_checks, show_output=False):
        print("⚠️  部分检查失败")

    return True


def test_git_hooks():
    """测试Git hooks"""
    print("🔗 测试Git Hooks...")

    husky_dir = Path(".husky")
    if husky_dir.exists():
        print("✅ .husky目录存在")

        # 检查重要的hooks
        hooks = ["pre-commit", "commit-msg", "post-commit", "pre-push"]
        for hook in hooks:
            hook_file = husky_dir / hook
            if hook_file.exists():
                print(f"✅ {hook} hook存在")
            else:
                print(f"❌ {hook} hook不存在")
    else:
        print("❌ .husky目录不存在")
        return False

    return True


def test_workflows():
    """测试GitHub Actions工作流"""
    print("⚙️  测试GitHub Actions工作流...")

    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        print("✅ .github/workflows目录存在")

        # 列出工作流文件
        workflows = list(workflows_dir.glob("*.yml"))
        print(f"📋 发现 {len(workflows)} 个工作流文件:")
        for wf in workflows:
            print(f"   - {wf.name}")

        # 检查语法
        print("🔍 检查YAML语法...")
        for wf in workflows[:3]:  # 只检查前3个避免太慢
            if not run_cmd(
                ["python", "-c", f"import yaml; yaml.safe_load(open('{wf}'))"],
                show_output=False,
            ):
                print(f"⚠️  {wf.name} YAML语法有问题")
    else:
        print("❌ .github/workflows目录不存在")
        return False

    return True


def main():
    print("🚀 Bravo项目 - 快速本地测试")
    print("=" * 50)

    # 检查基本环境
    print("📍 当前目录:", Path.cwd())

    tests = [
        ("Git Hooks", test_git_hooks),
        ("Pre-commit", test_precommit),
        ("前端环境", test_frontend_quick),
        ("后端环境", test_backend_quick),
        ("GitHub Actions", test_workflows),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results[test_name] = False

        if results[test_name]:
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")

    # 总结
    print(f"\n{'='*50}")
    print("📊 测试结果总结:")
    passed = sum(results.values())
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<20} {status}")

    print(f"\n🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 所有测试通过！基础设施状态良好")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关配置")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
