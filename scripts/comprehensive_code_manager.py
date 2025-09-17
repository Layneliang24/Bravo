#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合代码变更管理系统
整合代码追踪、临时修改检测和还原验证功能
"""

import hashlib
import json
import os
import re
import subprocess  # nosec
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List


@dataclass
class CodeIssue:
    """代码问题记录"""

    file_path: str
    line_number: int
    issue_type: str
    severity: str
    description: str
    code_snippet: str
    context: List[str]
    detected_at: str


class ComprehensiveCodeManager:
    """综合代码管理器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "docs" / "02_test_report"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # 优化的检测规则 - 减少误报
        self.detection_patterns = {
            "TODO": {
                "pattern": (
                    r"(?i)(?:#|//|/\*|<!--)\s*TODO[:\s]+(.+?)" r"(?:\*/|-->|$)"
                ),
                "severity": "medium",
                "description": "待完成任务",
            },
            "FIXME": {
                "pattern": (
                    r"(?i)(?:#|//|/\*|<!--)\s*FIXME[:\s]+(.+?)" r"(?:\*/|-->|$)"
                ),
                "severity": "high",
                "description": "需要修复的问题",
            },
            "HACK": {
                "pattern": (
                    r"(?i)(?:#|//|/\*|<!--)\s*HACK[:\s]+(.+?)" r"(?:\*/|-->|$)"
                ),
                "severity": "high",
                "description": "临时解决方案",
            },
            "TEMP": {
                "pattern": (
                    r"(?i)(?:#|//|/\*|<!--)\s*TEMP[:\s]+(.+?)" r"(?:\*/|-->|$)"
                ),
                "severity": "medium",
                "description": "临时代码",
            },
            "DEBUG_PRINT": {
                "pattern": (
                    r"print\s*\([^)]*" r"(?:debug|test|temp|DEBUG|TEST|TEMP)[^)]*\)"
                ),
                "severity": "low",
                "description": "调试打印语句",
            },
            "CONSOLE_DEBUG": {
                "pattern": (
                    r"console\.(log|debug)\s*\([^)]*"
                    r"(?:debug|test|temp|DEBUG|TEST|TEMP)[^)]*\)"
                ),
                "severity": "low",
                "description": "调试控制台输出",
            },
            "COMMENTED_FUNCTION": {
                "pattern": (r"^\s*#\s*(def\s+\w+|class\s+\w+|async\s+def\s+\w+)\s*\("),
                "severity": "medium",
                "description": "被注释的函数或类定义",
            },
            "COMMENTED_IMPORT": {
                "pattern": r"^\s*#\s*(import\s+\w+|from\s+\w+\s+import)",
                "severity": "low",
                "description": "被注释的导入语句",
            },
        }

        # 文件类型和排除规则
        self.scannable_extensions = {
            ".py",
            ".js",
            ".ts",
            ".vue",
            ".jsx",
            ".tsx",
            ".html",
            ".css",
            ".scss",
            ".sass",
            ".less",
            ".md",
            ".yml",
            ".yaml",
            ".toml",
        }

        self.exclude_patterns = {
            # 目录
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "dist",
            "build",
            ".next",
            ".nuxt",
            "coverage",
            ".vscode",
            ".idea",
            ".code_baselines",
            "htmlcov",
            ".mypy_cache",
            "venv",
            "env",
            # 文件
            "package-lock.json",
            "yarn.lock",
            "poetry.lock",
            ".coverage",
            "coverage.xml",
            # 模式
            r".*\.min\.(js|css)$",
            r".*\.bundle\.(js|css)$",
            r".*\.map$",
        }

    def should_scan_file(self, file_path: Path) -> bool:
        """判断是否应该扫描文件"""
        # 检查文件扩展名
        if file_path.suffix.lower() not in self.scannable_extensions:
            return False

        # 检查排除模式
        relative_path = str(file_path.relative_to(self.project_root))

        for pattern in self.exclude_patterns:
            if pattern.startswith("r"):
                # 正则表达式模式
                regex_pattern = pattern[1:].strip("'\"")
                if re.match(regex_pattern, relative_path):
                    return False
            else:
                # 简单字符串匹配
                if pattern in relative_path:
                    return False

        return True

    def scan_for_issues(self) -> List[CodeIssue]:
        """扫描代码问题"""
        import time

        start_time = time.time()

        issues = []
        scanned_files = 0
        total_files = 0

        # 统计总文件数
        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    pattern in d
                    for pattern in self.exclude_patterns
                    if not pattern.startswith("r")
                )
            ]
            for filename in files:
                file_path = Path(root) / filename
                if self.should_scan_file(file_path):
                    total_files += 1

        print(f"[INFO] 开始扫描 {total_files} 个文件...")

        for root, dirs, files in os.walk(self.project_root):
            # 过滤目录
            dirs[:] = [
                d
                for d in dirs
                if not any(
                    pattern in d
                    for pattern in self.exclude_patterns
                    if not pattern.startswith("r")
                )
            ]

            for filename in files:
                file_path = Path(root) / filename

                if not self.should_scan_file(file_path):
                    continue

                scanned_files += 1
                if scanned_files % 100 == 0:
                    elapsed = time.time() - start_time
                    print(
                        f"[INFO] 已扫描 {scanned_files}/{total_files} 文件 "
                        f"({elapsed:.2f}s)"
                    )

                file_issues = self._scan_file_for_issues(file_path)
                issues.extend(file_issues)

        elapsed_time = time.time() - start_time
        print(
            f"[SUCCESS] 扫描完成: {scanned_files} 文件, {len(issues)} 问题, "
            f"耗时 {elapsed_time:.2f}s"
        )
        print(f"[INFO] 平均速度: {scanned_files / elapsed_time:.1f} 文件/秒")

        return issues

    def _scan_file_for_issues(self, file_path: Path) -> List[CodeIssue]:
        """扫描单个文件的问题"""
        issues = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_issues = self._check_line_for_issues(
                    file_path, line_num, line, lines
                )
                issues.extend(line_issues)

        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")

        return issues

    def _check_line_for_issues(
        self, file_path: Path, line_num: int, line: str, all_lines: List[str]
    ) -> List[CodeIssue]:
        """检查单行代码问题"""
        issues = []

        for issue_type, config in self.detection_patterns.items():
            pattern = config["pattern"]
            match = re.search(pattern, line)

            if match:
                # 获取上下文
                context_start = max(0, line_num - 2)
                context_end = min(len(all_lines), line_num + 1)
                context = [
                    f"{i + 1:4d}: {all_lines[i].rstrip()}"
                    for i in range(context_start, context_end)
                ]

                # 提取描述
                description = (
                    match.group(1) if match.groups() else config["description"]
                )
                if not description or not description.strip():
                    description = config["description"]

                issue = CodeIssue(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    issue_type=issue_type,
                    severity=config["severity"],
                    description=description.strip(),
                    code_snippet=line.strip(),
                    context=context,
                    detected_at=datetime.now().isoformat(),
                )

                issues.append(issue)

        return issues

    def create_baseline(self) -> Dict:
        """创建项目基线"""
        print("[INFO] 创建项目基线...")

        baseline = {
            "timestamp": datetime.now().isoformat(),
            "commit_hash": self._get_git_commit(),
            "features_count": self._count_features(),
            "test_results": self._run_basic_tests(),
            "code_issues": [asdict(issue) for issue in self.scan_for_issues()],
            "file_checksums": self._calculate_key_file_checksums(),
        }

        # 保存基线
        baseline_file = self.reports_dir / "project_baseline.json"
        with open(baseline_file, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)

        return baseline

    def validate_current_state(self) -> Dict:
        """验证当前状态"""
        print("[INFO] 验证当前项目状态...")

        # 加载基线
        baseline_file = self.reports_dir / "project_baseline.json"
        if not baseline_file.exists():
            return {"status": "no_baseline", "message": "未找到基线，请先创建基线"}

        with open(baseline_file, "r", encoding="utf-8") as f:
            baseline: Dict = json.load(f)

        # 获取当前状态
        current_issues = self.scan_for_issues()
        current_state: Dict = {
            "timestamp": datetime.now().isoformat(),
            "commit_hash": self._get_git_commit(),
            "features_count": self._count_features(),
            "test_results": self._run_basic_tests(),
            "code_issues": [asdict(issue) for issue in current_issues],
            "file_checksums": self._calculate_key_file_checksums(),
        }

        # 比较分析
        validation = {
            "baseline_timestamp": baseline["timestamp"],
            "current_timestamp": current_state["timestamp"],
            "commit_changed": (baseline["commit_hash"] != current_state["commit_hash"]),
            "features_analysis": self._analyze_features_change(
                baseline["features_count"], current_state["features_count"]
            ),
            "test_analysis": self._analyze_test_change(
                baseline["test_results"], current_state["test_results"]
            ),
            "issues_analysis": self._analyze_issues_change(
                baseline["code_issues"], current_state["code_issues"]
            ),
            "files_analysis": self._analyze_files_change(
                baseline["file_checksums"], current_state["file_checksums"]
            ),
        }

        # 评估整体风险
        validation["overall_risk"] = self._assess_overall_risk(validation)

        return validation

    def _get_git_commit(self) -> str:
        """获取Git提交哈希"""
        try:
            result = subprocess.run(  # nosec
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"

    def _count_features(self) -> int:
        """统计功能数量"""
        features_file = self.project_root / "features.json"
        if features_file.exists():
            try:
                with open(features_file, "r", encoding="utf-8") as f:
                    features = json.load(f)
                return len(features)
            except Exception:
                return 0
        return 0

    def _run_basic_tests(self) -> Dict:
        """运行基础测试"""
        try:
            # 运行后端简单测试
            result = subprocess.run(  # nosec
                ["python", "simple_test_runner.py"],
                cwd=self.project_root / "backend",
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                # 简单解析测试结果
                output_lines = result.stdout.split("\n")
                passed_count = len([line for line in output_lines if "✅" in line])
                return {
                    "status": "passed",
                    "passed_tests": passed_count,
                    "pass_rate": 100.0 if passed_count > 0 else 0.0,
                }
            else:
                return {
                    "status": "failed",
                    "passed_tests": 0,
                    "pass_rate": 0.0,
                    "error": result.stderr,
                }
        except Exception as e:
            return {
                "status": "error",
                "passed_tests": 0,
                "pass_rate": 0.0,
                "error": str(e),
            }

    def _calculate_key_file_checksums(self) -> Dict[str, str]:
        """计算关键文件校验和"""
        checksums = {}
        key_files = [
            "backend/bravo/settings/base.py",
            "backend/bravo/urls.py",
            "backend/apps/users/models.py",
            "frontend/src/main.ts",
            "frontend/src/App.vue",
            "features.json",
        ]

        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, "rb") as f:
                    content = f.read()
                    checksums[file_path] = hashlib.md5(content).hexdigest()  # nosec

        return checksums

    def _analyze_features_change(self, baseline_count: int, current_count: int) -> Dict:
        """分析功能变更"""
        change = current_count - baseline_count
        return {
            "baseline_count": baseline_count,
            "current_count": current_count,
            "change": change,
            "status": "increased"
            if change > 0
            else "decreased"
            if change < 0
            else "stable",
        }

    def _analyze_test_change(self, baseline_tests: Dict, current_tests: Dict) -> Dict:
        """分析测试变更"""
        baseline_rate = baseline_tests.get("pass_rate", 0)
        current_rate = current_tests.get("pass_rate", 0)

        return {
            "baseline_pass_rate": baseline_rate,
            "current_pass_rate": current_rate,
            "change": current_rate - baseline_rate,
            "status": "improved"
            if current_rate > baseline_rate
            else "degraded"
            if current_rate < baseline_rate
            else "stable",
        }

    def _analyze_issues_change(
        self, baseline_issues: List[Dict], current_issues: List[Dict]
    ) -> Dict:
        """分析代码问题变更"""
        baseline_high = len([i for i in baseline_issues if i["severity"] == "high"])
        current_high = len([i for i in current_issues if i["severity"] == "high"])

        baseline_total = len(baseline_issues)
        current_total = len(current_issues)

        return {
            "baseline_total": baseline_total,
            "current_total": current_total,
            "baseline_high_severity": baseline_high,
            "current_high_severity": current_high,
            "total_change": current_total - baseline_total,
            "high_severity_change": current_high - baseline_high,
            "status": "improved"
            if current_high < baseline_high
            else "degraded"
            if current_high > baseline_high
            else "stable",
        }

    def _analyze_files_change(
        self, baseline_checksums: Dict, current_checksums: Dict
    ) -> Dict:
        """分析文件变更"""
        changed_files = []
        for file_path, baseline_checksum in baseline_checksums.items():
            current_checksum = current_checksums.get(file_path)
            if current_checksum and current_checksum != baseline_checksum:
                changed_files.append(file_path)

        return {
            "changed_files": changed_files,
            "change_count": len(changed_files),
            "status": "stable" if not changed_files else "changed",
        }

    def _assess_overall_risk(self, validation: Dict) -> str:
        """评估整体风险"""
        risk_factors = []

        # 测试通过率下降
        test_analysis = validation["test_analysis"]
        if test_analysis["status"] == "degraded":
            risk_factors.append("test_degradation")

        # 高严重性问题增加
        issues_analysis = validation["issues_analysis"]
        if issues_analysis["high_severity_change"] > 5:
            risk_factors.append("high_severity_issues_increase")

        # 功能数量减少
        features_analysis = validation["features_analysis"]
        if features_analysis["status"] == "decreased":
            risk_factors.append("features_decrease")

        # 关键文件变更
        files_analysis = validation["files_analysis"]
        if files_analysis["change_count"] > 3:
            risk_factors.append("many_file_changes")

        # 评估风险等级
        if len(risk_factors) >= 3:
            return "critical"
        elif len(risk_factors) >= 2:
            return "high"
        elif len(risk_factors) >= 1:
            return "medium"
        else:
            return "low"

    def generate_comprehensive_report(self, validation: Dict) -> str:
        """生成综合报告"""
        lines = []
        lines.append("# 综合代码变更管理报告")
        lines.append(f"\n**生成时间**: {validation['current_timestamp']}")
        lines.append(f"**基线时间**: {validation['baseline_timestamp']}")

        # 风险等级
        risk_icons = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}

        risk = validation["overall_risk"]
        icon = risk_icons.get(risk, "❓")
        lines.append(f"\n{icon} **整体风险等级**: {risk.upper()}")

        # 功能分析
        features = validation["features_analysis"]
        lines.append("\n## 📋 功能变更分析")
        lines.append(f"- 基线功能数: {features['baseline_count']}")
        lines.append(f"- 当前功能数: {features['current_count']}")
        lines.append(f"- 变更数量: {features['change']:+d}")

        if features["status"] == "decreased":
            lines.append("- ⚠️ **警告**: 功能数量减少")
        elif features["status"] == "increased":
            lines.append("- ✅ **良好**: 功能数量增加")

        # 测试分析
        tests = validation["test_analysis"]
        lines.append("\n## 🧪 测试结果分析")
        lines.append(f"- 基线通过率: {tests['baseline_pass_rate']:.1f}%")
        lines.append(f"- 当前通过率: {tests['current_pass_rate']:.1f}%")
        lines.append(f"- 变化幅度: {tests['change']:+.1f}%")

        if tests["status"] == "degraded":
            lines.append("- 🔴 **警告**: 测试通过率下降")
        elif tests["status"] == "improved":
            lines.append("- 🟢 **良好**: 测试通过率提升")

        # 代码问题分析
        issues = validation["issues_analysis"]
        lines.append("\n## 🐛 代码问题分析")
        lines.append(f"- 基线问题总数: {issues['baseline_total']}")
        lines.append(f"- 当前问题总数: {issues['current_total']}")
        lines.append(f"- 基线高严重性: {issues['baseline_high_severity']}")
        lines.append(f"- 当前高严重性: {issues['current_high_severity']}")
        lines.append(f"- 高严重性变化: {issues['high_severity_change']:+d}")

        if issues["status"] == "degraded":
            lines.append("- 🔴 **警告**: 高严重性问题增加")
        elif issues["status"] == "improved":
            lines.append("- 🟢 **良好**: 高严重性问题减少")

        # 文件变更分析
        files = validation["files_analysis"]
        lines.append("\n## 📁 关键文件变更")
        lines.append(f"- 变更文件数: {files['change_count']}")

        if files["changed_files"]:
            lines.append("- 变更的文件:")
            for file_path in files["changed_files"]:
                lines.append(f"  - {file_path}")

        # 建议行动
        lines.append("\n## 🎯 建议行动")

        if risk == "critical":
            lines.append("- 🚨 **立即行动**: 存在严重风险，需要立即处理")
            lines.append("- 🔄 **考虑回滚**: 评估是否需要回滚到基线状态")
            lines.append("- 👥 **团队会议**: 召集团队讨论问题和解决方案")
        elif risk == "high":
            lines.append("- ⚠️ **优先处理**: 存在较高风险，需要优先关注")
            lines.append("- 🔍 **深入分析**: 分析具体的问题原因")
            lines.append("- 📋 **制定计划**: 制定详细的修复计划")
        elif risk == "medium":
            lines.append("- 👀 **持续关注**: 存在一定风险，需要关注")
            lines.append("- 🧪 **增强测试**: 考虑增加相关测试用例")
        else:
            lines.append("- 🟢 **保持现状**: 风险较低，继续正常开发")
            lines.append("- 🔄 **定期检查**: 建议定期运行此检查")

        return "\n".join(lines)


def main():
    """主函数"""
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manager = ComprehensiveCodeManager(project_root)

    if len(sys.argv) > 1 and sys.argv[1] == "create-baseline":
        baseline = manager.create_baseline()
        print("[SUCCESS] 基线已创建")
        print(f"[INFO] 提交哈希: {baseline['commit_hash']}")
        print(f"[INFO] 测试通过率: {baseline['test_results']['pass_rate']:.1f}%")
        print(f"[INFO] 代码问题: {len(baseline['code_issues'])} 处")
        return 0

    # 验证当前状态
    validation = manager.validate_current_state()

    if validation.get("status") == "no_baseline":
        print(
            "[ERROR] 未找到基线，请先运行: "
            "python comprehensive_code_manager.py create-baseline"
        )
        return 1

    # 生成报告
    report = manager.generate_comprehensive_report(validation)

    # 保存报告
    report_file = manager.reports_dir / "comprehensive_code_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[SUCCESS] 综合报告已生成: {report_file}")
    print(f"[INFO] 整体风险等级: {validation['overall_risk'].upper()}")

    # 根据风险等级返回退出码
    risk_codes = {"low": 0, "medium": 0, "high": 1, "critical": 2}

    return risk_codes.get(validation["overall_risk"], 1)


if __name__ == "__main__":
    exit(main())
