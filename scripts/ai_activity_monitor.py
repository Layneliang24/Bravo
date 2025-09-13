#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI活动监控脚本
检测和记录AI可能绕过钩子的行为
"""

import json
import os
import re
import subprocess
from datetime import datetime
from typing import Dict


class AIActivityMonitor:
    """AI活动监控器"""

    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_file = os.path.join(
            self.project_root, "docs", "02_test_report", "ai_activity_log.json"
        )

        # AI相关的可疑行为模式
        self.suspicious_patterns = [
            r"--no-verify",
            r'git commit -m ".*" --no-verify',
            r"git push --force",
            r"git reset --hard",
            r"rm -rf \.git/hooks",
            r"chmod -x \.git/hooks",
            r"bypass.*hook",
            r"skip.*check",
            r"ignore.*validation",
        ]

    def check_recent_activity(self) -> Dict:
        """检查最近的活动"""
        try:
            # 检查最近的提交
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--grep=--no-verify"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            bypass_commits = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            # 检查是否有强制推送
            result = subprocess.run(
                ["git", "log", "--oneline", "-10", "--grep=force"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            force_commits = (
                result.stdout.strip().split("\n") if result.stdout.strip() else []
            )

            return {
                "bypass_attempts": len(bypass_commits),
                "force_pushes": len(force_commits),
                "suspicious_activity": bypass_commits + force_commits,
            }

        except Exception as e:
            return {"error": str(e)}

    def check_hook_integrity(self) -> Dict:
        """检查钩子完整性"""
        hook_files = [
            ".git/hooks/pre-commit",
            ".git/hooks/commit-msg",
            ".pre-commit-config.yaml",
        ]

        integrity_status = {}
        for hook_file in hook_files:
            full_path = os.path.join(self.project_root, hook_file)
            if os.path.exists(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 检查是否包含可疑内容
                    suspicious = False
                    for pattern in self.suspicious_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            suspicious = True
                            break

                    integrity_status[hook_file] = {
                        "exists": True,
                        "size": os.path.getsize(full_path),
                        "suspicious_content": suspicious,
                        "last_modified": datetime.fromtimestamp(
                            os.path.getmtime(full_path)
                        ).isoformat(),
                    }
                except Exception as e:
                    integrity_status[hook_file] = {"exists": True, "error": str(e)}
            else:
                integrity_status[hook_file] = {"exists": False}

        return integrity_status

    def log_ai_activity(self, activity_type: str, details: Dict):
        """记录AI活动"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity_type": activity_type,
            "details": details,
            "user_agent": "AI Assistant",
        }

        # 读取现有日志
        logs = []
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        # 添加新日志
        logs.append(log_entry)

        # 保存日志
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

    def generate_alert(self, severity: str, message: str):
        """生成警报"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "severity": severity,
            "message": message,
            "action_required": True,
        }

        alert_file = os.path.join(
            self.project_root, "docs", "02_test_report", "security_alert.json"
        )
        with open(alert_file, "w", encoding="utf-8") as f:
            json.dump(alert, f, indent=2, ensure_ascii=False)

        print(f"🚨 安全警报 [{severity.upper()}]: {message}")
        print(f"📄 警报详情已保存到: {alert_file}")


def main():
    """主函数"""
    monitor = AIActivityMonitor()

    # 检查最近活动
    activity = monitor.check_recent_activity()
    if "error" not in activity:
        if activity["bypass_attempts"] > 0:
            monitor.generate_alert(
                "HIGH", f"检测到 {activity['bypass_attempts']} 次可能的钩子绕过尝试"
            )

        if activity["force_pushes"] > 0:
            monitor.generate_alert("MEDIUM", f"检测到 {activity['force_pushes']} 次强制推送")

    # 检查钩子完整性
    integrity = monitor.check_hook_integrity()
    for hook_file, status in integrity.items():
        if status.get("suspicious_content"):
            monitor.generate_alert("HIGH", f"钩子文件 {hook_file} 包含可疑内容")

    # 记录检查活动
    monitor.log_ai_activity(
        "compliance_check", {"activity_check": activity, "integrity_check": integrity}
    )

    print("🔍 AI活动监控完成")
    return 0


if __name__ == "__main__":
    exit(main())
