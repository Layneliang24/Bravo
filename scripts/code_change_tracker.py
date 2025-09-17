#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码变更追踪系统
用于检测和管理临时修改，防止功能缺失
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class CodeChangeTracker:
    """代码变更追踪器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.tracking_file = self.project_root / ".code_changes_tracking.json"
        self.temp_markers = {
            "TODO": r"#\s*TODO[:\s](.+)",
            "FIXME": r"#\s*FIXME[:\s](.+)",
            "HACK": r"#\s*HACK[:\s](.+)",
            "TEMP": r"#\s*TEMP[:\s](.+)",
            "TEMPORARY": r"#\s*TEMPORARY[:\s](.+)",
            "DEBUG": r"#\s*DEBUG[:\s](.+)",
            "COMMENTED_CODE": r"^\s*#\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[=\(]",
            "DISABLED_TEST": (r"@pytest\.mark\.skip|@unittest\.skip|def\s+_test_"),
        }
        self.risk_patterns = {
            "DELETED_IMPORT": (r"^\s*#\s*from\s+\w+\s+import|^\s*#\s*import\s+\w+"),
            "DELETED_FUNCTION": r"^\s*#\s*def\s+\w+\s*\(",
            "DELETED_CLASS": r"^\s*#\s*class\s+\w+\s*[\(:]",
            "SIMPLIFIED_LOGIC": r"#\s*(if|for|while|try)\s+.*:",
            "BYPASSED_VALIDATION": r"#\s*(assert|raise|validate|check)",
        }

    def scan_temporary_changes(self) -> Dict:
        """扫描临时修改"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "temporary_markers": [],
            "high_risk_changes": [],
            "commented_code": [],
            "disabled_tests": [],
            "summary": {},
        }

        # 扫描所有代码文件
        for file_path in self._get_code_files():
            self._scan_file(file_path, results)

        # 生成摘要
        results["summary"] = self._generate_summary(results)

        return results

    def _get_code_files(self) -> List[Path]:
        """获取所有代码文件"""
        code_files = []
        extensions = {".py", ".js", ".ts", ".vue", ".jsx", ".tsx"}

        for root, dirs, files in os.walk(self.project_root):
            # 跳过特定目录
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d
                not in {"node_modules", "__pycache__", "venv", "env", "dist", "build"}
            ]

            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    code_files.append(Path(root) / file)

        return code_files

    def _scan_file(self, file_path: Path, results: Dict):
        """扫描单个文件"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            rel_path = file_path.relative_to(self.project_root)

            for line_num, line in enumerate(lines, 1):
                # 检查临时标记
                for marker_type, pattern in self.temp_markers.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        results["temporary_markers"].append(
                            {
                                "file": str(rel_path),
                                "line": line_num,
                                "type": marker_type,
                                "content": line.strip(),
                                "severity": self._get_severity(marker_type),
                            }
                        )

                # 检查高风险变更
                for risk_type, pattern in self.risk_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        results["high_risk_changes"].append(
                            {
                                "file": str(rel_path),
                                "line": line_num,
                                "type": risk_type,
                                "content": line.strip(),
                                "severity": "HIGH",
                            }
                        )

                # 检查注释掉的代码
                if re.search(self.temp_markers["COMMENTED_CODE"], line):
                    results["commented_code"].append(
                        {
                            "file": str(rel_path),
                            "line": line_num,
                            "content": line.strip(),
                        }
                    )

                # 检查禁用的测试
                if re.search(self.temp_markers["DISABLED_TEST"], line):
                    results["disabled_tests"].append(
                        {
                            "file": str(rel_path),
                            "line": line_num,
                            "content": line.strip(),
                        }
                    )

        except Exception as e:
            print(f"扫描文件 {file_path} 时出错: {e}")

    def _get_severity(self, marker_type: str) -> str:
        """获取标记严重程度"""
        high_severity = {"FIXME", "HACK", "TEMP", "TEMPORARY"}
        medium_severity = {"TODO", "DEBUG"}

        if marker_type in high_severity:
            return "HIGH"
        elif marker_type in medium_severity:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_summary(self, results: Dict) -> Dict:
        """生成扫描摘要"""
        summary: Dict = {
            "total_issues": len(results["temporary_markers"])
            + len(results["high_risk_changes"]),
            "high_severity_count": len(
                [x for x in results["temporary_markers"] if x["severity"] == "HIGH"]
            ),
            "commented_code_count": len(results["commented_code"]),
            "disabled_tests_count": len(results["disabled_tests"]),
            "files_affected": len(
                set(
                    [x["file"] for x in results["temporary_markers"]]
                    + [x["file"] for x in results["high_risk_changes"]]
                )
            ),
            "risk_assessment": "LOW",
        }

        # 风险评估
        if summary["high_severity_count"] > 10 or summary["disabled_tests_count"] > 5:
            summary["risk_assessment"] = "HIGH"
        elif summary["high_severity_count"] > 5 or summary["disabled_tests_count"] > 2:
            summary["risk_assessment"] = "MEDIUM"

        return summary

    def save_tracking_data(self, data: Dict):
        """保存追踪数据"""
        with open(self.tracking_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_tracking_data(self) -> Dict:
        """加载追踪数据"""
        if self.tracking_file.exists():
            with open(self.tracking_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def compare_with_previous(self, current_data: Dict) -> Dict:
        """与上次扫描结果比较"""
        previous_data = self.load_tracking_data()

        if not previous_data:
            return {"status": "first_scan", "changes": []}

        changes = []

        # 比较临时标记数量
        prev_count = len(previous_data.get("temporary_markers", []))
        curr_count = len(current_data.get("temporary_markers", []))

        if curr_count > prev_count:
            changes.append(
                {
                    "type": "INCREASE",
                    "category": "temporary_markers",
                    "message": f"临时标记增加了 {curr_count - prev_count} 个",
                }
            )
        elif curr_count < prev_count:
            changes.append(
                {
                    "type": "DECREASE",
                    "category": "temporary_markers",
                    "message": f"临时标记减少了 {prev_count - curr_count} 个",
                }
            )

        # 比较高风险变更
        prev_risk_count = len(previous_data.get("high_risk_changes", []))
        curr_risk_count = len(current_data.get("high_risk_changes", []))

        if curr_risk_count > prev_risk_count:
            changes.append(
                {
                    "type": "INCREASE",
                    "category": "high_risk_changes",
                    "message": (f"高风险变更增加了 " f"{curr_risk_count - prev_risk_count} 个"),
                    "severity": "HIGH",
                }
            )

        return {
            "status": "compared",
            "changes": changes,
            "trend": "improving"
            if (len(changes) == 0 or all(c["type"] == "DECREASE" for c in changes))
            else "degrading",
        }

    def generate_report(self, data: Dict, comparison: Dict) -> str:
        """生成报告"""
        report = []
        report.append("# 代码变更追踪报告")
        report.append(f"\n生成时间: {data['timestamp']}")
        report.append(f"扫描结果: {data['summary']['total_issues']} 个问题")
        report.append(f"风险评估: {data['summary']['risk_assessment']}")

        # 摘要统计
        report.append("\n## 摘要统计")
        summary = data["summary"]
        report.append(f"- 总问题数: {summary['total_issues']}")
        report.append(f"- 高严重性问题: {summary['high_severity_count']}")
        report.append(f"- 注释代码行数: {summary['commented_code_count']}")
        report.append(f"- 禁用测试数: {summary['disabled_tests_count']}")
        report.append(f"- 受影响文件数: {summary['files_affected']}")

        # 变化趋势
        if comparison["status"] == "compared":
            report.append("\n## 变化趋势")
            report.append(f"趋势: {comparison['trend']}")
            for change in comparison["changes"]:
                report.append(f"- {change['message']}")

        # 高风险变更详情
        if data["high_risk_changes"]:
            report.append("\n## 🚨 高风险变更")
            for change in data["high_risk_changes"][:10]:  # 只显示前10个
                report.append(
                    f"- **{change['file']}:{change['line']}** - " f"{change['type']}"
                )
                report.append(f"  ```{change['content']}```")

        # 临时标记详情
        if data["temporary_markers"]:
            report.append("\n## 临时标记")
            high_severity = [
                x for x in data["temporary_markers"] if x["severity"] == "HIGH"
            ]
            for marker in high_severity[:10]:  # 只显示前10个高严重性
                report.append(
                    f"- **{marker['file']}:{marker['line']}** - " f"{marker['type']}"
                )
                report.append(f"  ```{marker['content']}```")

        # 禁用测试
        if data["disabled_tests"]:
            report.append("\n## 禁用测试")
            for test in data["disabled_tests"]:
                report.append(f"- **{test['file']}:{test['line']}**")
                report.append(f"  ```{test['content']}```")

        # 建议行动
        report.append("\n## 建议行动")
        if summary["risk_assessment"] == "HIGH":
            report.append("- **立即处理**: 存在大量高风险变更，需要立即审查")
            report.append("- **代码审查**: 检查所有注释掉的代码是否需要恢复")
            report.append("- **测试恢复**: 重新启用被禁用的测试")
        elif summary["risk_assessment"] == "MEDIUM":
            report.append("- 🟡 **定期检查**: 安排时间处理临时标记")
            report.append("- **文档记录**: 为临时修改添加详细说明")
        else:
            report.append("- 🟢 **保持现状**: 代码质量良好，继续监控")

        report.append("\n## 🔄 下次扫描")
        report.append("建议每周运行一次代码变更追踪，确保临时修改得到及时处理。")

        return "\n".join(report)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="代码变更追踪工具")
    parser.add_argument("--validate-commit", action="store_true", help="验证提交前的代码质量")
    parser.add_argument("--commit", action="store_true", help="提交时记录变更")

    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tracker = CodeChangeTracker(project_root)

    if args.validate_commit:
        # 提交前验证
        print("[INFO] 执行提交前代码质量验证...")

        # 检查暂存文件
        import subprocess

        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=True,
            )
            staged_files = [f.strip() for f in result.stdout.split("\n") if f.strip()]

            if not staged_files:
                print("[INFO] 没有暂存文件，跳过验证")
                return 0

            print(f"[INFO] 检查 {len(staged_files)} 个暂存文件...")

            # 执行扫描
            current_data = tracker.scan_temporary_changes()

            issues_count = current_data["summary"]["total_issues"]
            risk_level = current_data["summary"]["risk_assessment"]

            if risk_level == "HIGH":
                print(f"\n[ERROR] 发现 {issues_count} 个高风险问题")
                print("[ERROR] 严格模式: 请修复高风险问题后重新提交")
                return 1
            else:
                print(f"[SUCCESS] 代码质量验证通过 (发现{issues_count}个低风险问题，可接受)")
                return 0

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Git命令执行失败: {e}")
            return 1
    elif args.commit:
        # 提交后记录 - 只记录日志，不修改文件
        print("[INFO] 记录提交信息到日志...")

        # 获取最新提交信息
        import subprocess

        try:
            commit_hash = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%h"], text=True, encoding="utf-8"
            ).strip()
            commit_msg = subprocess.check_output(
                ["git", "log", "-1", "--pretty=%B"], text=True, encoding="utf-8"
            ).strip()

            print(f"[INFO] 提交 {commit_hash}: {commit_msg[:50]}...")
            print("[INFO] 提交记录完成，未修改任何文件")
            return 0

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] 获取提交信息失败: {e}")
            return 1
    else:
        # 默认扫描和报告
        print("开始扫描代码变更...")
        current_data = tracker.scan_temporary_changes()

        print("比较历史数据...")
        comparison = tracker.compare_with_previous(current_data)

        print("保存追踪数据...")
        tracker.save_tracking_data(current_data)

        print("生成报告...")
        report = tracker.generate_report(current_data, comparison)

        # 保存报告
        report_file = (
            Path(project_root)
            / "docs"
            / "02_test_report"
            / "code_change_tracking_report.md"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"报告已生成: {report_file}")
        print(f"\n扫描结果: {current_data['summary']['total_issues']} 个问题")
        print(f"风险评估: {current_data['summary']['risk_assessment']}")

        # 如果有高风险问题，返回非零退出码
        if current_data["summary"]["risk_assessment"] == "HIGH":
            print("\n检测到高风险问题，建议立即处理！")
            return 1

        return 0


if __name__ == "__main__":
    exit(main())
