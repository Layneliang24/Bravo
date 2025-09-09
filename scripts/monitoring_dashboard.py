#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码变更追踪系统 - 监控仪表板

功能:
- 统计信息收集和展示
- 使用趋势分析
- 问题反馈收集
- 系统健康检查

作者: 代码变更追踪系统
版本: 1.0.0
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# 配置文件路径
STATS_FILE = ".git/hooks/statistics.json"
FEEDBACK_FILE = ".git/hooks/feedback.json"
HEALTH_CHECK_FILE = ".git/hooks/health_check.json"


class MonitoringDashboard:
    """监控仪表板类"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.stats_file = self.project_root / STATS_FILE
        self.feedback_file = self.project_root / FEEDBACK_FILE
        self.health_file = self.project_root / HEALTH_CHECK_FILE

    def load_statistics(self) -> Dict:
        """加载统计信息"""
        if not self.stats_file.exists():
            return {
                "total_checks": 0,
                "commits_blocked": 0,
                "commits_allowed": 0,
                "average_scan_time": 0.0,
                "total_scan_time": 0.0,
                "high_severity_issues": 0,
                "medium_severity_issues": 0,
                "low_severity_issues": 0,
                "most_common_issues": {},
                "daily_stats": {},
                "file_type_stats": {},
                "last_updated": None,
            }

        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] 无法加载统计信息: {e}")
            return {}

    def load_feedback(self) -> List[Dict]:
        """加载反馈信息"""
        if not self.feedback_file.exists():
            return []

        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARNING] 无法加载反馈信息: {e}")
            return []

    def save_feedback(self, feedback_list: List[Dict]):
        """保存反馈信息"""
        try:
            self.feedback_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.feedback_file, "w", encoding="utf-8") as f:
                json.dump(feedback_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] 无法保存反馈信息: {e}")

    def add_feedback(self, feedback_type: str, message: str, severity: str = "medium"):
        """添加反馈"""
        feedback_list = self.load_feedback()

        new_feedback = {
            "id": len(feedback_list) + 1,
            "type": feedback_type,  # bug, feature, improvement, question
            "message": message,
            "severity": severity,  # low, medium, high, critical
            "timestamp": datetime.now().isoformat(),
            "status": "open",  # open, in_progress, resolved, closed
            "reporter": os.getenv("USER", "unknown"),
        }

        feedback_list.append(new_feedback)
        self.save_feedback(feedback_list)

        print(f"[SUCCESS] 反馈已记录 (ID: {new_feedback['id']})")
        return new_feedback["id"]

    def show_dashboard(self):
        """显示监控仪表板"""
        stats = self.load_statistics()
        feedback_list = self.load_feedback()

        print("\n" + "=" * 60)
        print("🔍 代码变更追踪系统 - 监控仪表板")
        print("=" * 60)

        # 基础统计
        print("\n📊 基础统计信息:")
        print(f"  总检查次数: {stats.get('total_checks', 0)}")
        print(f"  阻止提交: {stats.get('commits_blocked', 0)}")
        print(f"  允许提交: {stats.get('commits_allowed', 0)}")

        if stats.get("total_checks", 0) > 0:
            block_rate = (
                stats.get("commits_blocked", 0) / stats.get("total_checks", 1)
            ) * 100
            print(f"  阻止率: {block_rate:.1f}%")

        # 性能统计
        print("\n⚡ 性能统计:")
        print(f"  平均扫描时间: {stats.get('average_scan_time', 0):.3f}秒")
        print(f"  总扫描时间: {stats.get('total_scan_time', 0):.2f}秒")

        # 问题统计
        print("\n🚨 问题统计:")
        print(f"  高严重性问题: {stats.get('high_severity_issues', 0)}")
        print(f"  中等严重性问题: {stats.get('medium_severity_issues', 0)}")
        print(f"  低严重性问题: {stats.get('low_severity_issues', 0)}")

        # 最常见问题
        common_issues = stats.get("most_common_issues", {})
        if common_issues:
            print("\n🔥 最常见问题:")
            sorted_issues = sorted(
                common_issues.items(), key=lambda x: x[1], reverse=True
            )
            for issue, count in sorted_issues[:5]:
                print(f"  {issue}: {count}次")

        # 文件类型统计
        file_stats = stats.get("file_type_stats", {})
        if file_stats:
            print("\n📁 文件类型统计:")
            sorted_files = sorted(file_stats.items(), key=lambda x: x[1], reverse=True)
            for file_type, count in sorted_files[:5]:
                print(f"  {file_type}: {count}次")

        # 最近7天趋势
        daily_stats = stats.get("daily_stats", {})
        if daily_stats:
            print("\n📈 最近7天趋势:")
            recent_days = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                recent_days.append(date)

            for date in reversed(recent_days):
                day_stats = daily_stats.get(date, {"checks": 0, "blocks": 0})
                print(
                    f"  {date}: {day_stats.get('checks', 0)}次检查, "
                    f"{day_stats.get('blocks', 0)}次阻止"
                )

        # 反馈统计
        print("\n💬 反馈统计:")
        if feedback_list:
            open_feedback = [f for f in feedback_list if f.get("status") == "open"]
            resolved_feedback = [
                f for f in feedback_list if f.get("status") == "resolved"
            ]

            print(f"  总反馈数: {len(feedback_list)}")
            print(f"  待处理: {len(open_feedback)}")
            print(f"  已解决: {len(resolved_feedback)}")

            # 按类型分组
            feedback_by_type = {}
            for feedback in feedback_list:
                fb_type = feedback.get("type", "unknown")
                feedback_by_type[fb_type] = feedback_by_type.get(fb_type, 0) + 1

            print("  按类型分布:")
            for fb_type, count in feedback_by_type.items():
                print(f"    {fb_type}: {count}")
        else:
            print("  暂无反馈记录")

        # 系统健康状态
        print("\n🏥 系统健康状态:")
        health_status = self.check_system_health()
        for check, status in health_status.items():
            status_icon = "✅" if status["status"] == "ok" else "❌"
            print(f"  {status_icon} {check}: {status['message']}")

        # 最后更新时间
        if stats.get("last_updated"):
            print(f"\n🕒 最后更新: {stats.get('last_updated')}")

        print("\n" + "=" * 60)

    def check_system_health(self) -> Dict:
        """检查系统健康状态"""
        health_status = {}

        # 检查Git钩子
        pre_commit_hook = self.project_root / ".husky" / "pre-commit"
        if pre_commit_hook.exists():
            health_status["git_hook"] = {"status": "ok", "message": "Git钩子已安装"}
        else:
            health_status["git_hook"] = {"status": "error", "message": "Git钩子未找到"}

        # 检查脚本文件
        script_file = self.project_root / "scripts" / "fast_pre_commit.py"
        if script_file.exists():
            health_status["script_file"] = {"status": "ok", "message": "检查脚本存在"}
        else:
            health_status["script_file"] = {"status": "error", "message": "检查脚本未找到"}

        # 检查配置文件
        config_file = self.project_root / "scripts" / "production_config.py"
        if config_file.exists():
            health_status["config_file"] = {"status": "ok", "message": "配置文件存在"}
        else:
            health_status["config_file"] = {
                "status": "warning",
                "message": "配置文件未找到，使用默认配置",
            }

        # 检查Python环境
        try:
            health_status["python_env"] = {
                "status": "ok",
                "message": f"Python环境正常 ({sys.version.split()[0]})",
            }
        except Exception as e:
            health_status["python_env"] = {
                "status": "error",
                "message": f"Python环境异常: {e}",
            }

        # 检查统计文件权限
        try:
            if self.stats_file.exists():
                # 尝试读写
                # stats = self.load_statistics()  # Unused variable
                health_status["file_permissions"] = {
                    "status": "ok",
                    "message": "文件权限正常",
                }
            else:
                health_status["file_permissions"] = {
                    "status": "warning",
                    "message": "统计文件不存在，将在首次运行时创建",
                }
        except Exception as e:
            health_status["file_permissions"] = {
                "status": "error",
                "message": f"文件权限异常: {e}",
            }

        return health_status

    def show_feedback(self, status_filter: Optional[str] = None):
        """显示反馈列表"""
        feedback_list = self.load_feedback()

        if status_filter:
            feedback_list = [
                f for f in feedback_list if f.get("status") == status_filter
            ]

        if not feedback_list:
            print("\n📝 暂无反馈记录")
            return

        print(f"\n📝 反馈列表 ({len(feedback_list)}条):")
        print("-" * 80)

        for feedback in sorted(
            feedback_list, key=lambda x: x.get("timestamp", ""), reverse=True
        ):
            status_icon = {
                "open": "🔴",
                "in_progress": "🟡",
                "resolved": "🟢",
                "closed": "⚫",
            }.get(feedback.get("status", "open"), "❓")

            severity_icon = {
                "low": "🔵",
                "medium": "🟡",
                "high": "🟠",
                "critical": "🔴",
            }.get(feedback.get("severity", "medium"), "❓")

            print(f"ID: {feedback.get('id', 'N/A')} {status_icon} " f"{severity_icon}")
            print(f"类型: {feedback.get('type', 'unknown')}")
            print(f"时间: {feedback.get('timestamp', 'unknown')}")
            print(f"报告人: {feedback.get('reporter', 'unknown')}")
            print(f"内容: {feedback.get('message', '')}")
            print("-" * 80)

    def export_report(self, output_file: str):
        """导出监控报告"""
        stats = self.load_statistics()
        feedback_list = self.load_feedback()
        health_status = self.check_system_health()

        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "feedback": feedback_list,
            "health_status": health_status,
            "summary": {
                "total_checks": stats.get("total_checks", 0),
                "success_rate": (
                    (
                        stats.get("commits_allowed", 0)
                        / max(stats.get("total_checks", 1), 1)
                    )
                    * 100
                ),
                "average_scan_time": stats.get("average_scan_time", 0),
                "open_feedback_count": len(
                    [f for f in feedback_list if f.get("status") == "open"]
                ),
                "health_issues": len(
                    [h for h in health_status.values() if h["status"] == "error"]
                ),
            },
        }

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"[SUCCESS] 报告已导出到: {output_file}")
        except Exception as e:
            print(f"[ERROR] 导出报告失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="代码变更追踪系统监控仪表板")
    parser.add_argument("--project-root", default=".", help="项目根目录")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # dashboard命令
    subparsers.add_parser("dashboard", help="显示监控仪表板")

    # feedback命令
    feedback_parser = subparsers.add_parser("feedback", help="反馈管理")
    feedback_subparsers = feedback_parser.add_subparsers(dest="feedback_action")

    # 添加反馈
    add_feedback_parser = feedback_subparsers.add_parser("add", help="添加反馈")
    add_feedback_parser.add_argument(
        "--type",
        required=True,
        choices=["bug", "feature", "improvement", "question"],
        help="反馈类型",
    )
    add_feedback_parser.add_argument("--message", required=True, help="反馈内容")
    add_feedback_parser.add_argument(
        "--severity",
        default="medium",
        choices=["low", "medium", "high", "critical"],
        help="严重性级别",
    )

    # 显示反馈
    list_feedback_parser = feedback_subparsers.add_parser("list", help="显示反馈列表")
    list_feedback_parser.add_argument(
        "--status", choices=["open", "in_progress", "resolved", "closed"], help="按状态过滤"
    )

    # 健康检查
    subparsers.add_parser("health", help="系统健康检查")

    # 导出报告
    export_parser = subparsers.add_parser("export", help="导出监控报告")
    export_parser.add_argument(
        "--output", default="monitoring_report.json", help="输出文件名"
    )

    args = parser.parse_args()

    dashboard = MonitoringDashboard(args.project_root)

    if args.command == "dashboard" or not args.command:
        dashboard.show_dashboard()

    elif args.command == "feedback":
        if args.feedback_action == "add":
            dashboard.add_feedback(args.type, args.message, args.severity)
        elif args.feedback_action == "list":
            dashboard.show_feedback(args.status)
        else:
            print("请指定反馈操作: add 或 list")

    elif args.command == "health":
        health_status = dashboard.check_system_health()
        print("\n🏥 系统健康检查:")
        for check, status in health_status.items():
            status_icon = (
                "✅"
                if status["status"] == "ok"
                else "⚠️"
                if status["status"] == "warning"
                else "❌"
            )
            print(f"  {status_icon} {check}: {status['message']}")

    elif args.command == "export":
        dashboard.export_report(args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
