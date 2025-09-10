#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Post-checkout 钩子处理器
在切换分支后执行必要的检查和同步操作
"""

import os
import subprocess
import sys
from pathlib import Path


class PostCheckoutHandler:
    """Post-checkout 处理器"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.old_head = os.environ.get('GIT_PARAMS', '').split()[0] if os.environ.get('GIT_PARAMS') else None
        self.new_head = os.environ.get('GIT_PARAMS', '').split()[1] if os.environ.get('GIT_PARAMS') else None
        self.branch_checkout = os.environ.get('GIT_PARAMS', '').split()[2] if os.environ.get('GIT_PARAMS') else None

    def run_post_checkout_checks(self):
        """运行 post-checkout 检查"""
        print("Post-checkout 检查开始...")
        
        # 检查是否是分支切换（而不是文件检出）
        if self.branch_checkout != "1":
            print("📁 文件检出，跳过分支切换检查")
            return True

        # 获取当前分支
        current_branch = self.get_current_branch()
        print(f"切换到分支: {current_branch}")

        # 执行分支特定的检查
        success = True
        
        # 1. 检查依赖同步
        if not self.check_dependencies():
            success = False

        # 2. 检查环境配置
        if not self.check_environment():
            success = False

        # 3. 检查分支特定配置
        if not self.check_branch_config(current_branch):
            success = False

        # 4. 清理临时文件
        self.cleanup_temp_files()

        if success:
            print("Post-checkout 检查完成")
        else:
            print("Post-checkout 检查发现问题，请手动处理")

        return success

    def get_current_branch(self):
        """获取当前分支名"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def check_dependencies(self):
        """检查依赖同步"""
        print("检查依赖同步...")
        
        # 检查前端依赖
        if (self.project_root / "frontend" / "package.json").exists():
            if not (self.project_root / "frontend" / "node_modules").exists():
                print("前端依赖未安装，建议运行: cd frontend && npm install")
                return False

        # 检查后端依赖
        if (self.project_root / "backend" / "requirements").exists():
            if not (self.project_root / "backend" / ".venv").exists():
                print("后端虚拟环境未创建，建议运行: cd backend && python -m venv .venv")
                return False

        print("依赖检查通过")
        return True

    def check_environment(self):
        """检查环境配置"""
        print("🔧 检查环境配置...")
        
        # 检查环境变量文件
        env_files = [".env", ".env.local", ".env.development"]
        missing_env = []
        
        for env_file in env_files:
            if not (self.project_root / env_file).exists():
                missing_env.append(env_file)

        if missing_env:
            print(f"缺少环境配置文件: {', '.join(missing_env)}")
            return False

        print("环境配置检查通过")
        return True

    def check_branch_config(self, branch_name):
        """检查分支特定配置"""
        print(f"检查分支 {branch_name} 特定配置...")
        
        # 检查是否是保护分支
        if branch_name in ["main", "dev"]:
            print("切换到保护分支，确保代码已通过审查")
            
            # 检查是否有未提交的更改
            try:
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    print("工作区有未提交的更改")
                    return False
            except Exception:
                pass

        # 检查分支特定的配置文件
        branch_config = self.project_root / f".config.{branch_name}.json"
        if branch_config.exists():
            print(f"📋 发现分支特定配置: {branch_config.name}")

        print("分支配置检查通过")
        return True

    def cleanup_temp_files(self):
        """清理临时文件"""
        print("🧹 清理临时文件...")
        
        temp_patterns = [
            "**/__pycache__",
            "**/*.pyc",
            "**/node_modules/.cache",
            "**/.pytest_cache",
            "**/coverage",
            "**/dist",
            "**/build"
        ]
        
        cleaned_count = 0
        for pattern in temp_patterns:
            for temp_file in self.project_root.glob(pattern):
                if temp_file.is_dir():
                    try:
                        import shutil
                        shutil.rmtree(temp_file)
                        cleaned_count += 1
                    except Exception:
                        pass
                elif temp_file.is_file():
                    try:
                        temp_file.unlink()
                        cleaned_count += 1
                    except Exception:
                        pass

        if cleaned_count > 0:
            print(f"清理了 {cleaned_count} 个临时文件/目录")
        else:
            print("✨ 无需清理临时文件")


def main():
    """主函数"""
    try:
        handler = PostCheckoutHandler()
        success = handler.run_post_checkout_checks()
        return 0 if success else 1
    except Exception as e:
        print(f"Post-checkout 检查失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
