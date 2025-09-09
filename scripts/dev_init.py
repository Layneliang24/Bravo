#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
开发环境初始化脚本
自动设置代码变更追踪基线和开发环境
"""

import json
import os
import subprocess  # nosec
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class DevEnvironmentInitializer:
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or os.getcwd())
        self.baseline_dir = self.project_root / ".code_baselines"
        self.scripts_dir = self.project_root / "scripts"

    def check_git_status(self) -> dict:
        """检查Git状态"""
        try:
            # 检查是否在Git仓库中
            result = subprocess.run(  # nosec
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return {"status": "not_git_repo", "message": "当前目录不是Git仓库"}

            # 检查是否有未提交的更改
            result = subprocess.run(  # nosec
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            uncommitted_files = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # 获取当前分支
            result = subprocess.run(  # nosec
                ["git", "branch", "--show-current"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            current_branch = result.stdout.strip()

            return {
                "status": "ok",
                "branch": current_branch,
                "uncommitted_files": len(uncommitted_files),
                "has_changes": len(uncommitted_files) > 0,
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_baseline_exists(self) -> bool:
        """检查是否已存在基线"""
        baseline_file = self.baseline_dir / "baseline.json"
        return baseline_file.exists()

    def create_baseline_if_needed(self) -> dict:
        """如果需要则创建基线"""
        if self.check_baseline_exists():
            baseline_file = self.baseline_dir / "baseline.json"
            with open(baseline_file, "r", encoding="utf-8") as f:
                baseline = json.load(f)

            return {
                "status": "exists",
                "message": (f"基线已存在，创建时间: " f"{baseline.get('timestamp', 'unknown')}"),
                "baseline": baseline,
            }

        # 创建新基线
        try:
            result = subprocess.run(  # nosec
                [
                    sys.executable,
                    str(self.scripts_dir / "comprehensive_code_manager.py"),
                    "create-baseline",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "status": "created",
                    "message": "基线创建成功",
                    "output": result.stdout,
                }
            else:
                return {
                    "status": "failed",
                    "message": f"基线创建失败: {result.stderr}",
                    "output": result.stdout,
                }

        except Exception as e:
            return {"status": "error", "message": f"创建基线时出错: {str(e)}"}

    def setup_git_hooks(self) -> dict:
        """设置Git钩子"""
        try:
            husky_dir = self.project_root / ".husky"
            if not husky_dir.exists():
                return {
                    "status": "no_husky",
                    "message": "Husky未安装，请先运行: npm install husky",
                }

            pre_commit_file = husky_dir / "pre-commit"
            if pre_commit_file.exists():
                return {"status": "exists", "message": "Git钩子已配置"}

            return {
                "status": "manual_setup",
                "message": (
                    "请手动配置Git钩子或运行: npx husky add .husky/pre-commit "
                    '"python scripts/pre_commit_monitor.py"'
                ),
            }

        except Exception as e:
            return {"status": "error", "message": f"设置Git钩子时出错: {str(e)}"}

    def check_dependencies(self) -> dict:
        """检查依赖"""
        missing_deps = []

        # 检查Python
        if sys.version_info < (3, 7):
            missing_deps.append("Python 3.7+")

        # 检查必要的脚本文件
        required_scripts = [
            "comprehensive_code_manager.py",
            "temp_modification_detector.py",
            "pre_commit_monitor.py",
        ]

        for script in required_scripts:
            script_path = self.scripts_dir / script
            if not script_path.exists():
                missing_deps.append(f"脚本文件: {script}")

        return {
            "status": "ok" if not missing_deps else "missing",
            "missing": missing_deps,
        }

    def run_initial_scan(self) -> dict:
        """运行初始扫描"""
        try:
            result = subprocess.run(  # nosec
                [
                    sys.executable,
                    str(self.scripts_dir / "temp_modification_detector.py"),
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            return {
                "status": "completed",
                "output": result.stdout,
                "exit_code": result.returncode,
            }

        except Exception as e:
            return {"status": "error", "message": f"初始扫描失败: {str(e)}"}

    def initialize(self) -> dict:
        """完整的初始化流程"""
        print("[INFO] 开始初始化开发环境...")

        results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
        }

        # 1. 检查依赖
        print("[INFO] 检查依赖...")
        deps_result = self.check_dependencies()
        results["dependencies"] = deps_result

        if deps_result["status"] == "missing":
            print(f"[ERROR] 缺少依赖: {', '.join(deps_result['missing'])}")
            return results

        # 2. 检查Git状态
        print("[INFO] 检查Git状态...")
        git_result = self.check_git_status()
        results["git"] = git_result

        if git_result["status"] != "ok":
            print(f"[WARNING] Git状态异常: {git_result.get('message', 'unknown')}")
        else:
            print(f"[INFO] 当前分支: {git_result['branch']}")
            if git_result["has_changes"]:
                print(f"[WARNING] 有 {git_result['uncommitted_files']} 个未提交的文件")

        # 3. 创建基线
        print("[INFO] 检查/创建代码基线...")
        baseline_result = self.create_baseline_if_needed()
        results["baseline"] = baseline_result

        if baseline_result["status"] == "created":
            print("[SUCCESS] 基线创建成功")
        elif baseline_result["status"] == "exists":
            print("[INFO] 基线已存在")
        else:
            print(f"[ERROR] 基线处理失败: {baseline_result['message']}")

        # 4. 设置Git钩子
        print("[INFO] 检查Git钩子配置...")
        hooks_result = self.setup_git_hooks()
        results["hooks"] = hooks_result

        if hooks_result["status"] == "exists":
            print("[SUCCESS] Git钩子已配置")
        else:
            print(f"[INFO] {hooks_result['message']}")

        # 5. 运行初始扫描
        print("[INFO] 运行初始代码扫描...")
        scan_result = self.run_initial_scan()
        results["initial_scan"] = scan_result

        if scan_result["status"] == "completed":
            print("[SUCCESS] 初始扫描完成")
        else:
            print(f"[ERROR] 初始扫描失败: {scan_result.get('message', 'unknown')}")

        print("\n[SUCCESS] 开发环境初始化完成！")
        print("\n📋 使用说明:")
        print("  • 每次开始开发前运行: python scripts/dev_init.py")
        print("  • 提交代码时会自动运行检查")
        print("  • 手动检查: python scripts/pre_commit_monitor.py")
        print("  • 查看报告: docs/02_test_report/")

        return results


def main():
    """主函数"""
    project_root = os.getcwd()
    if len(sys.argv) > 1:
        project_root = sys.argv[1]

    initializer = DevEnvironmentInitializer(project_root)
    result = initializer.initialize()

    # 保存初始化结果
    result_file = Path(project_root) / ".code_baselines" / "dev_init_result.json"
    result_file.parent.mkdir(exist_ok=True)

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
