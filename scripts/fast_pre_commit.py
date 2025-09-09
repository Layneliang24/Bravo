#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速提交前检查脚本 - 生产版本
仅检查暂存的文件，提高检查速度
集成生产配置和性能优化
"""

import json
import re
import subprocess  # nosec B404
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 导入生产配置
try:
    from production_config import (
        ENABLE_STATISTICS,
        EXCLUDED_FILES,
        EXCLUDED_PATHS,
        HIGH_SEVERITY_PATTERNS,
        LOW_SEVERITY_PATTERNS,
        MAX_FILE_SIZE,
        MEDIUM_SEVERITY_PATTERNS,
        MESSAGE_TEMPLATES,
        SEVERITY_THRESHOLDS,
        STATISTICS_FILE,
        SUPPORTED_EXTENSIONS,
        initialize_config,
    )

    initialize_config()
except ImportError:
    # 回退到基础配置
    HIGH_SEVERITY_PATTERNS = [r"\b(TODO|FIXME|HACK|XXX|BUG|TEMP|DEBUG|REMOVE)\b"]
    MEDIUM_SEVERITY_PATTERNS = [r"\b(NOTE|REVIEW|OPTIMIZE|REFACTOR)\b"]
    LOW_SEVERITY_PATTERNS = []
    SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".vue"}
    EXCLUDED_PATHS = [r"node_modules/", r"\.git/"]
    EXCLUDED_FILES = []
    MAX_FILE_SIZE = 1024 * 1024
    SEVERITY_THRESHOLDS = {
        "high": {"max_issues": 0, "block_commit": True},
        "medium": {"max_issues": 5, "block_commit": False},
        "low": {"max_issues": 20, "block_commit": False},
    }
    MESSAGE_TEMPLATES = {
        "start": "[INFO] 快速提交前检查启动",
        "scanning": "[INFO] 扫描 {file_count} 个暂存文件",
        "completed": "[INFO] 扫描完成，耗时 {duration:.3f} 秒",
        "issues_found": (
            "[RESULT] 发现 {total} 个问题 " "(高: {high}, 中: {medium}, 低: {low})"
        ),
        "commit_blocked": "[FAILED] 提交被阻止 - 发现 {count} 个高严重性问题",
        "commit_allowed": "[SUCCESS] 提交检查通过",
        "bypass_hint": "[TIP] 紧急情况可使用 --no-verify 跳过检查",
    }
    ENABLE_STATISTICS = False
    STATISTICS_FILE = ".git/hooks/statistics.json"


class FastPreCommitChecker:
    """快速提交前检查器 - 生产版本"""

    def __init__(self):
        self.project_root = Path.cwd()

        # 使用生产配置
        self.high_severity_patterns = HIGH_SEVERITY_PATTERNS
        self.medium_severity_patterns = MEDIUM_SEVERITY_PATTERNS
        self.low_severity_patterns = LOW_SEVERITY_PATTERNS
        self.supported_extensions = SUPPORTED_EXTENSIONS
        self.excluded_paths = EXCLUDED_PATHS
        self.excluded_files = EXCLUDED_FILES
        self.max_file_size = MAX_FILE_SIZE
        self.severity_thresholds = SEVERITY_THRESHOLDS
        self.message_templates = MESSAGE_TEMPLATES

        # 临时修改检测规则 - 支持多种注释风格
        self.temp_patterns = {
            "TODO": {"pattern": r"(#|//|/\*)\s*TODO[:\s]", "severity": "medium"},
            "FIXME": {"pattern": r"(#|//|/\*)\s*FIXME[:\s]", "severity": "high"},
            "HACK": {"pattern": r"(#|//|/\*)\s*HACK[:\s]", "severity": "high"},
            "XXX": {"pattern": r"(#|//|/\*)\s*XXX[:\s]", "severity": "high"},
            "DEBUG": {"pattern": r"(#|//|/\*)\s*DEBUG[:\s]", "severity": "medium"},
            "TEMP": {"pattern": r"(#|//|/\*)\s*TEMP[:\s]", "severity": "medium"},
            "console_log": {"pattern": r"console\.log\s*\(", "severity": "medium"},
            "print_debug": {"pattern": r"print\s*\(.*DEBUG", "severity": "medium"},
        }

        # 风险阈值
        self.max_high_severity = 5  # 单次提交最多允许5个高严重性问题
        self.max_total_issues = 20  # 单次提交最多允许20个问题

        # 统计信息
        self.stats = {
            "total_checks": 0,
            "total_files_scanned": 0,
            "total_issues_found": 0,
            "commits_blocked": 0,
            "average_scan_time": 0.0,
            "last_check_time": None,
        }

        # 加载历史统计
        if ENABLE_STATISTICS:
            self.load_statistics()

    def load_statistics(self):
        """加载历史统计数据"""
        try:
            stats_path = Path(STATISTICS_FILE)
            if stats_path.exists():
                with open(stats_path, "r", encoding="utf-8") as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
        except Exception as e:
            print(f"[WARNING] 加载统计数据失败: {e}")

    def save_statistics(self):
        """保存统计数据"""
        if not ENABLE_STATISTICS:
            return

        try:
            stats_path = Path(STATISTICS_FILE)
            stats_path.parent.mkdir(parents=True, exist_ok=True)

            with open(stats_path, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            print(f"[WARNING] 保存统计数据失败: {e}")

    def update_statistics(self, result: Dict):
        """更新统计信息"""
        self.stats["total_checks"] += 1
        self.stats["total_files_scanned"] += result.get("files_checked", 0)
        self.stats["total_issues_found"] += result.get("total_issues", 0)

        if not result.get("is_safe", True):
            self.stats["commits_blocked"] += 1

        # 更新平均扫描时间
        duration = result.get("duration", 0)
        if self.stats["average_scan_time"] == 0:
            self.stats["average_scan_time"] = duration
        else:
            self.stats["average_scan_time"] = (
                self.stats["average_scan_time"] * (self.stats["total_checks"] - 1)
                + duration
            ) / self.stats["total_checks"]

        self.stats["last_check_time"] = datetime.now().isoformat()

        # 保存统计数据
        self.save_statistics()

    def get_staged_files(self) -> List[str]:
        """获取Git暂存区的文件"""
        try:
            result = subprocess.run(  # nosec
                ["git", "diff", "--cached", "--name-only"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
                # 只检查代码文件
                code_extensions = {
                    ".py",
                    ".js",
                    ".ts",
                    ".vue",
                    ".jsx",
                    ".tsx",
                    ".java",
                    ".cpp",
                    ".c",
                    ".h",
                }
                return [
                    f for f in files if any(f.endswith(ext) for ext in code_extensions)
                ]
            return []
        except Exception as e:
            print(f"[ERROR] 获取暂存文件失败: {e}")
            return []

    def check_file_for_temp_modifications(self, file_path: str) -> List[Dict]:
        """检查单个文件的临时修改"""
        issues: List[Dict] = []
        full_path = self.project_root / file_path

        if not full_path.exists():
            return issues

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern_info in self.temp_patterns.items():
                    if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                        issues.append(
                            {
                                "file": file_path,
                                "line": line_num,
                                "type": pattern_name,
                                "severity": pattern_info["severity"],
                                "content": line.strip()[:100],  # 限制长度
                            }
                        )

        except Exception as e:
            print(f"[WARNING] 读取文件失败 {file_path}: {e}")

        return issues

    def run_fast_check(self) -> Tuple[bool, Dict]:
        """运行快速检查"""
        print("[INFO] 开始快速提交前检查...")
        start_time = datetime.now()

        # 获取暂存文件
        staged_files = self.get_staged_files()

        if not staged_files:
            print("[SUCCESS] 没有暂存的代码文件需要检查")
            return True, {"files_checked": 0, "issues": []}

        print(f"[INFO] 检查 {len(staged_files)} 个暂存文件...")

        all_issues = []
        for file_path in staged_files:
            file_issues = self.check_file_for_temp_modifications(file_path)
            all_issues.extend(file_issues)

        # 统计问题
        high_severity_count = sum(
            1 for issue in all_issues if issue["severity"] == "high"
        )
        total_issues = len(all_issues)

        # 评估风险 - 使用生产配置的阈值
        medium_severity_count = sum(
            1 for issue in all_issues if issue["severity"] == "medium"
        )
        low_severity_count = sum(
            1 for issue in all_issues if issue["severity"] == "low"
        )

        is_safe = self._evaluate_safety(
            high_severity_count, medium_severity_count, low_severity_count, total_issues
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            "files_checked": len(staged_files),
            "total_issues": total_issues,
            "high_severity_issues": high_severity_count,
            "medium_severity_issues": sum(
                1 for issue in all_issues if issue["severity"] == "medium"
            ),
            "low_severity_issues": sum(
                1 for issue in all_issues if issue["severity"] == "low"
            ),
            "issues": all_issues,
            "duration": duration,
            "is_safe": is_safe,
        }

        self._print_results(result)

        # 更新统计信息
        self.update_statistics(result)

        return is_safe, result

    def _evaluate_safety(
        self, high_count: int, medium_count: int, low_count: int, total_count: int
    ) -> bool:
        """根据生产配置评估提交安全性"""
        # 检查高严重性问题
        high_threshold = self.severity_thresholds.get("high", {})
        if high_threshold.get("block_commit", True) and high_count > high_threshold.get(
            "max_issues", 0
        ):
            return False

        # 检查中等严重性问题
        medium_threshold = self.severity_thresholds.get("medium", {})
        if medium_threshold.get(
            "block_commit", False
        ) and medium_count > medium_threshold.get("max_issues", 5):
            return False

        # 检查低严重性问题
        low_threshold = self.severity_thresholds.get("low", {})
        if low_threshold.get("block_commit", False) and low_count > low_threshold.get(
            "max_issues", 20
        ):
            return False

        return True

    def _should_block_commit(self, result: Dict) -> bool:
        """判断是否应该阻止提交"""
        return not result["is_safe"]

    def _print_results(self, result: Dict):
        """打印检查结果"""
        high_count = result["high_severity_issues"]
        medium_count = result.get("medium_severity_issues", 0)
        low_count = result.get("low_severity_issues", 0)
        total_issues = result["total_issues"]
        duration = result["duration"]
        files_checked = result["files_checked"]

        # 使用配置的消息模板
        print(self.message_templates["scanning"].format(file_count=files_checked))
        print(self.message_templates["completed"].format(duration=duration))
        print(
            self.message_templates["issues_found"].format(
                total=total_issues, high=high_count, medium=medium_count, low=low_count
            )
        )

        if result["issues"]:
            print("\n详细问题列表:")
            displayed_count = 0
            max_display = 20  # 最多显示20个问题

            for issue in result["issues"]:
                if displayed_count >= max_display:
                    remaining = len(result["issues"]) - displayed_count
                    print(f"  ... 还有 {remaining} 个问题未显示")
                    break

                severity_icon = {
                    "high": "[HIGH]",
                    "medium": "[MED]",
                    "low": "[LOW]",
                }.get(issue["severity"], "[UNKNOWN]")

                content = issue["content"].strip()
                if len(content) > 100:
                    content = content[:97] + "..."

                print(
                    f"  {severity_icon} {issue['file']}:{issue['line']} - " f"{content}"
                )
                displayed_count += 1

        # 根据阈值配置决定是否阻止提交
        should_block = self._should_block_commit(result)

        if should_block:
            message = self.message_templates["commit_blocked"].format(count=high_count)
            print(f"\n{message}")
            print(self.message_templates["bypass_hint"])
        else:
            print(f"\n{self.message_templates['commit_allowed']}")
            if medium_count > 0 or low_count > 0:
                print(f"[INFO] 注意: 发现 {medium_count + low_count} 个非关键问题，" f"建议后续处理")


def main():
    """主函数"""
    try:
        # 使用配置的消息模板
        print(MESSAGE_TEMPLATES.get("start", "[INFO] 快速提交前检查启动"))

        checker = FastPreCommitChecker()
        is_safe, result = checker.run_fast_check()

        # 显示统计信息（如果启用）
        if ENABLE_STATISTICS and hasattr(checker, "stats"):
            stats = checker.stats
            if stats["total_checks"] > 1:  # 不是第一次运行
                print(
                    f"[STATS] 历史统计: 总检查 {stats['total_checks']} 次, "
                    f"平均耗时 {stats['average_scan_time']:.3f}s, "
                    f"阻止提交 {stats['commits_blocked']} 次"
                )

        if is_safe:
            return 0
        else:
            return 1
    except KeyboardInterrupt:
        print("\n[INFO] 检查被用户中断")
        return 1
    except Exception as e:
        print(f"\n[ERROR] 检查过程中出现错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
