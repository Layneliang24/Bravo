#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钩子合规性监控脚本
检测和报告绕过钩子的行为
"""

import json
import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Tuple


class HookComplianceMonitor:
    """钩子合规性监控器"""

    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.report_file = os.path.join(
            self.project_root, "docs", "02_test_report", "hook_compliance_report.json"
        )

        # 提交信息格式规范
        self.commit_pattern = re.compile(
            r"^(feat|fix|docs|style|refactor|test|chore|ci|build|perf|revert)(\(.+\))?: .{1,50}$"
        )

        # 违规关键词
        self.bypass_keywords = ["--no-verify", "skip hooks", "bypass", "ignore hooks"]

    def check_recent_commits(self, count: int = 20) -> Dict:
        """检查最近的提交"""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"-{count}"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                return {"error": "Failed to get git log"}

            commits = result.stdout.strip().split("\n")
            violations = []

            for commit in commits:
                if not commit:
                    continue

                # 检查提交信息格式
                if not self.commit_pattern.match(commit):
                    violations.append(
                        {
                            "type": "format_violation",
                            "commit": commit,
                            "reason": "不符合提交信息格式规范",
                        }
                    )

                # 检查是否包含绕过关键词
                for keyword in self.bypass_keywords:
                    if keyword.lower() in commit.lower():
                        violations.append(
                            {
                                "type": "bypass_attempt",
                                "commit": commit,
                                "reason": f"可能尝试绕过钩子: {keyword}",
                            }
                        )

            return {
                "total_commits": len(commits),
                "violations": violations,
                "compliance_rate": (len(commits) - len(violations)) / len(commits) * 100
                if commits
                else 100,
            }

        except Exception as e:
            return {"error": str(e)}

    def check_hook_files(self) -> Dict:
        """检查钩子文件状态"""
        hook_files = {
            "pre-commit": ".git/hooks/pre-commit",
            "commit-msg": ".git/hooks/commit-msg",
            "husky-pre-commit": ".husky/pre-commit",
            "husky-commit-msg": ".husky/commit-msg",
            "pre-commit-config": ".pre-commit-config.yaml",
        }

        status = {}
        for name, path in hook_files.items():
            full_path = os.path.join(self.project_root, path)
            status[name] = {
                "exists": os.path.exists(full_path),
                "executable": os.access(full_path, os.X_OK)
                if os.path.exists(full_path)
                else False,
                "size": os.path.getsize(full_path) if os.path.exists(full_path) else 0,
            }

        return status

    def check_git_config(self) -> Dict:
        """检查Git配置"""
        try:
            # 检查hooksPath设置
            result = subprocess.run(
                ["git", "config", "--get", "core.hooksPath"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            hooks_path = result.stdout.strip() if result.returncode == 0 else None

            return {
                "hooks_path": hooks_path,
                "using_husky": hooks_path == ".husky/_" if hooks_path else False,
                "using_pre_commit": hooks_path is None,
            }

        except Exception as e:
            return {"error": str(e)}

    def generate_report(self) -> Dict:
        """生成合规性报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "commit_analysis": self.check_recent_commits(),
            "hook_files_status": self.check_hook_files(),
            "git_config": self.check_git_config(),
        }

        # 保存报告
        os.makedirs(os.path.dirname(self.report_file), exist_ok=True)
        with open(self.report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def print_summary(self, report: Dict):
        """打印报告摘要"""
        print("🔍 钩子合规性检查报告")
        print("=" * 50)

        # 提交分析
        commit_analysis = report.get("commit_analysis", {})
        if "error" in commit_analysis:
            print(f"❌ 提交分析失败: {commit_analysis['error']}")
        else:
            total = commit_analysis.get("total_commits", 0)
            violations = commit_analysis.get("violations", [])
            compliance_rate = commit_analysis.get("compliance_rate", 0)

            print(f"📊 提交统计:")
            print(f"  - 总提交数: {total}")
            print(f"  - 违规数量: {len(violations)}")
            print(f"  - 合规率: {compliance_rate:.1f}%")

            if violations:
                print(f"\n❌ 发现违规:")
                for violation in violations:
                    print(f"  - {violation['type']}: {violation['commit']}")
                    print(f"    原因: {violation['reason']}")
            else:
                print(f"\n✅ 所有提交符合规范")

        # 钩子文件状态
        hook_status = report.get("hook_files_status", {})
        print(f"\n🔧 钩子文件状态:")
        for name, status in hook_status.items():
            if status["exists"]:
                print(f"  ✅ {name}: 存在 ({status['size']} bytes)")
            else:
                print(f"  ❌ {name}: 不存在")

        # Git配置
        git_config = report.get("git_config", {})
        print(f"\n⚙️  Git配置:")
        if git_config.get("using_husky"):
            print(f"  🔧 使用Husky钩子系统")
        elif git_config.get("using_pre_commit"):
            print(f"  🚀 使用Pre-commit框架")
        else:
            print(f"  ⚠️  钩子系统状态未知")


def main():
    """主函数"""
    monitor = HookComplianceMonitor()
    report = monitor.generate_report()
    monitor.print_summary(report)

    # 如果有违规，返回非零退出码
    violations = report.get("commit_analysis", {}).get("violations", [])
    if violations:
        print(f"\n🚨 发现 {len(violations)} 个违规，请及时处理")
        return 1
    else:
        print(f"\n🎉 钩子合规性检查通过")
        return 0


if __name__ == "__main__":
    exit(main())
