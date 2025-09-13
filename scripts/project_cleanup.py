#!/usr/bin/env python3
"""
Bravo 项目瘦身脚本
功能：
- 清理无用的脚本文件、报告文件
- 删除.keep、.backup、.old等占位文件
- 整理重复或过时的配置文件
- 保留必要的文件，删除冗余内容
"""

import json
import logging
import os
import shutil
from pathlib import Path
from typing import Dict, List, Set

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ProjectCleaner:
    """项目清理器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.cleaned_files = []
        self.kept_files = []

        # 定义清理规则
        self.cleanup_patterns = {
            # 占位文件
            "placeholder_files": [
                "**/*.keep",
                "**/*.backup",
                "**/*.old",
                "**/*.tmp",
                "**/*.temp",
            ],
            # 过时的测试和开发文件
            "obsolete_files": [
                # 根目录过时文件
                "test_*.py",
                "fix_*.py",
                "validate_*.py",
                "verify_*.py",
                "check_*.py",
                "ci_validation.py",
                "final_validation_report.*",
                "fix_verification_report.*",
                "gate_optimized.yml",
                "lighthouserc-simple.json",
                "playwright.config.optimized.ts",
                "simulate_ci.sh",
                # 重复的Docker配置
                "docker-compose.github-actions-simulator.yml",
                "Dockerfile.github-actions-simulator",
                # 过时的报告和构建文件
                "build.log",
                "bandit-report.json",
                "bandit-report-fixed.json",
                # 后端过时文件
                "backend/health_check_complete.py",
                "backend/health_check_report.txt",
                "backend/run_tests_standalone.py",
                "backend/simple_test_runner.py",
                "backend/test_coverage.py",
                "backend/pytest_simple.ini",
                "backend/celerybeat-schedule",
                "backend/test.db",
                "backend/db.sqlite3",
                # E2E过时文件
                "e2e/test-results.xml",
                "e2e/test-results.zip",
                # 文档中的测试文件
                "docs/test_*.txt",
                "docs/test_*.md",
            ],
            # 空目录或只有.keep的目录
            "empty_directories": [
                "tests/data",
                "tests/integration",
                "tests/load",
                "tests/security",
                "tests/system",
                "k8s/base",
                "k8s/helm-bravo",
                "k8s/monitoring",
                "k8s/overlays",
            ],
        }

        # 需要保留的重要文件（即使匹配清理模式）
        self.protected_files = {
            ".github/workflows/gate.yml.backup",  # 重要备份
            "docs/02_test_report/",  # 测试报告保留
            "tests-golden/",  # 黄金测试保留
            "frontend/tests/",  # 前端测试保留
            "backend/tests/",  # 后端测试保留
            "e2e/tests/",  # E2E测试保留
        }

    def is_protected(self, file_path: Path) -> bool:
        """检查文件是否受保护"""
        str_path = str(file_path.relative_to(self.project_root))
        for protected in self.protected_files:
            if protected in str_path:
                return True
        return False

    def cleanup_placeholder_files(self) -> List[Path]:
        """清理占位文件"""
        logger.info("🧹 清理占位文件(.keep, .backup, .old等)...")

        removed_files = []
        for pattern in self.cleanup_patterns["placeholder_files"]:
            for file_path in self.project_root.rglob(pattern):
                if file_path.is_file() and not self.is_protected(file_path):
                    try:
                        file_path.unlink()
                        removed_files.append(file_path)
                        logger.info(
                            f"删除占位文件: {file_path.relative_to(self.project_root)}"
                        )
                    except Exception as e:
                        logger.error(f"删除失败 {file_path}: {e}")

        return removed_files

    def cleanup_obsolete_files(self) -> List[Path]:
        """清理过时文件"""
        logger.info("🗑️  清理过时和冗余文件...")

        removed_files = []
        for pattern in self.cleanup_patterns["obsolete_files"]:
            # 如果是相对路径，从项目根目录搜索
            if "/" in pattern:
                full_pattern = self.project_root / pattern
                if full_pattern.exists():
                    try:
                        if full_pattern.is_file():
                            full_pattern.unlink()
                        elif full_pattern.is_dir():
                            shutil.rmtree(full_pattern)
                        removed_files.append(full_pattern)
                        logger.info(f"删除过时文件: {pattern}")
                    except Exception as e:
                        logger.error(f"删除失败 {pattern}: {e}")
            else:
                # glob模式搜索
                for file_path in self.project_root.rglob(pattern):
                    if not self.is_protected(file_path):
                        try:
                            if file_path.is_file():
                                file_path.unlink()
                            elif file_path.is_dir():
                                shutil.rmtree(file_path)
                            removed_files.append(file_path)
                            logger.info(
                                f"删除过时文件: {file_path.relative_to(self.project_root)}"
                            )
                        except Exception as e:
                            logger.error(f"删除失败 {file_path}: {e}")

        return removed_files

    def cleanup_empty_directories(self) -> List[Path]:
        """清理空目录"""
        logger.info("📁 清理空目录...")

        removed_dirs = []
        for dir_pattern in self.cleanup_patterns["empty_directories"]:
            dir_path = self.project_root / dir_pattern
            if dir_path.exists() and dir_path.is_dir():
                try:
                    # 检查目录是否为空或只有.keep文件
                    contents = list(dir_path.iterdir())
                    if not contents or all(f.name.endswith(".keep") for f in contents):
                        shutil.rmtree(dir_path)
                        removed_dirs.append(dir_path)
                        logger.info(f"删除空目录: {dir_pattern}")
                except Exception as e:
                    logger.error(f"删除目录失败 {dir_pattern}: {e}")

        return removed_dirs

    def cleanup_duplicate_configs(self) -> List[Path]:
        """清理重复配置文件"""
        logger.info("⚙️  清理重复配置文件...")

        removed_files = []

        # 清理重复的Docker配置
        docker_configs = [
            "docker-compose.prod.yml.keep",
            "docker-compose.test.yml.keep",
            "docker-compose.yml.keep",
            "backend/Dockerfile.keep",
            "backend/Dockerfile.dev.backup",
            "backend/Dockerfile.dev.fixed",
            "frontend/Dockerfile.dev.backup",
            "frontend/Dockerfile.dev.fixed",
        ]

        for config in docker_configs:
            config_path = self.project_root / config
            if config_path.exists():
                try:
                    config_path.unlink()
                    removed_files.append(config_path)
                    logger.info(f"删除重复配置: {config}")
                except Exception as e:
                    logger.error(f"删除失败 {config}: {e}")

        # 清理重复的工作流文件
        workflow_configs = [
            "e2e/playwright.config.ts.backup",
            "e2e/playwright.config.ts.keep",
            "e2e/package.json.keep",
            "e2e/selenium.config.js.keep",
        ]

        for config in workflow_configs:
            config_path = self.project_root / config
            if config_path.exists():
                try:
                    config_path.unlink()
                    removed_files.append(config_path)
                    logger.info(f"删除重复工作流配置: {config}")
                except Exception as e:
                    logger.error(f"删除失败 {config}: {e}")

        return removed_files

    def cleanup_old_reports(self) -> List[Path]:
        """清理旧报告文件"""
        logger.info("📊 清理旧报告文件...")

        removed_files = []

        # 清理根目录的报告文件
        report_files = [
            "features.json",  # 已被新的feature-test-map.json替代
        ]

        for report in report_files:
            report_path = self.project_root / report
            if report_path.exists():
                try:
                    report_path.unlink()
                    removed_files.append(report_path)
                    logger.info(f"删除旧报告: {report}")
                except Exception as e:
                    logger.error(f"删除失败 {report}: {e}")

        # 清理backend/reports中的旧报告
        backend_reports_dir = self.project_root / "backend" / "reports"
        if backend_reports_dir.exists():
            for report_file in backend_reports_dir.glob("*.json"):
                # 保留最新的几个报告，删除较老的
                try:
                    # 这里可以添加基于时间的逻辑
                    pass
                except Exception as e:
                    logger.error(f"处理报告文件失败 {report_file}: {e}")

        return removed_files

    def optimize_gitignore(self):
        """优化.gitignore文件"""
        logger.info("📝 优化.gitignore...")

        gitignore_path = self.project_root / ".gitignore"
        if not gitignore_path.exists():
            return

        # 读取现有内容
        with open(gitignore_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 添加新的忽略规则
        new_rules = [
            "\n# 清理后新增的忽略规则\n",
            "*.backup\n",
            "*.old\n",
            "*.tmp\n",
            "*.temp\n",
            "build.log\n",
            "test_*.py\n",
            "fix_*.py\n",
            "validate_*.py\n",
            "verify_*.py\n",
        ]

        # 检查规则是否已存在
        existing_content = "".join(lines)
        rules_to_add = []

        for rule in new_rules:
            if rule.strip() and rule.strip() not in existing_content:
                rules_to_add.append(rule)

        if rules_to_add:
            with open(gitignore_path, "a", encoding="utf-8") as f:
                f.writelines(rules_to_add)
            logger.info("已更新.gitignore文件")

    def generate_cleanup_report(self, removed_files: List[Path]) -> str:
        """生成清理报告"""
        report_path = self.project_root / "reports" / "project_cleanup_report.json"
        report_path.parent.mkdir(exist_ok=True)

        report = {
            "timestamp": "2025-01-13",
            "total_files_removed": len(removed_files),
            "files_by_category": {
                "placeholder_files": [],
                "obsolete_files": [],
                "duplicate_configs": [],
                "empty_directories": [],
                "old_reports": [],
            },
            "space_saved_estimate": "计算中...",
            "recommendations": [
                "定期运行项目清理脚本",
                "避免提交临时文件和备份文件",
                "使用.gitignore防止无用文件进入版本控制",
            ],
        }

        # 按类别分类文件
        for file_path in removed_files:
            file_str = str(file_path.relative_to(self.project_root))
            if any(pattern in file_str for pattern in [".keep", ".backup", ".old"]):
                report["files_by_category"]["placeholder_files"].append(file_str)
            elif any(pattern in file_str for pattern in ["test_", "fix_", "validate_"]):
                report["files_by_category"]["obsolete_files"].append(file_str)
            elif "docker-compose" in file_str or "Dockerfile" in file_str:
                report["files_by_category"]["duplicate_configs"].append(file_str)
            elif file_path.is_dir():
                report["files_by_category"]["empty_directories"].append(file_str)
            else:
                report["files_by_category"]["old_reports"].append(file_str)

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"清理报告已保存: {report_path}")
            return str(report_path)
        except Exception as e:
            logger.error(f"保存清理报告失败: {e}")
            return ""

    def run_full_cleanup(self) -> Dict:
        """运行完整清理"""
        logger.info("🚀 开始项目瘦身...")

        all_removed_files = []

        # 1. 清理占位文件
        all_removed_files.extend(self.cleanup_placeholder_files())

        # 2. 清理过时文件
        all_removed_files.extend(self.cleanup_obsolete_files())

        # 3. 清理空目录
        all_removed_files.extend(self.cleanup_empty_directories())

        # 4. 清理重复配置
        all_removed_files.extend(self.cleanup_duplicate_configs())

        # 5. 清理旧报告
        all_removed_files.extend(self.cleanup_old_reports())

        # 6. 优化.gitignore
        self.optimize_gitignore()

        # 7. 生成清理报告
        report_path = self.generate_cleanup_report(all_removed_files)

        result = {
            "total_files_removed": len(all_removed_files),
            "removed_files": [
                str(f.relative_to(self.project_root)) for f in all_removed_files
            ],
            "report_path": report_path,
        }

        logger.info(f"✅ 项目瘦身完成！共清理 {len(all_removed_files)} 个文件")
        return result


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Bravo 项目瘦身工具")
    parser.add_argument("--project-root", default=".", help="项目根目录")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际删除文件")

    args = parser.parse_args()

    if args.dry_run:
        logger.info("🔍 预览模式 - 不会实际删除文件")
        # TODO: 实现预览模式
        return

    cleaner = ProjectCleaner(args.project_root)
    result = cleaner.run_full_cleanup()

    print("\n📊 清理结果:")
    print(f"总计清理文件: {result['total_files_removed']}")
    if result["report_path"]:
        print(f"详细报告: {result['report_path']}")


if __name__ == "__main__":
    main()
