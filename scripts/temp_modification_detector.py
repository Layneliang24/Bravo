#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时修改标记检测系统
自动检测和追踪代码中的TODO、FIXME等临时标记
"""

import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class TempModification:
    """临时修改记录"""

    file_path: str
    line_number: int
    line_content: str
    marker_type: str
    severity: str
    description: str
    detected_at: str
    context_lines: List[str]


class TempModificationDetector:
    """临时修改检测器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.detection_patterns = {
            "TODO": {
                "pattern": r"(?i)#?\s*TODO[:\s]*(.*)$",
                "severity": "medium",
                "description": "待完成任务",
            },
            "FIXME": {
                "pattern": r"(?i)#?\s*FIXME[:\s]*(.*)$",
                "severity": "high",
                "description": "需要修复的问题",
            },
            "HACK": {
                "pattern": r"(?i)#?\s*HACK[:\s]*(.*)$",
                "severity": "high",
                "description": "临时解决方案",
            },
            "XXX": {
                "pattern": r"(?i)#?\s*XXX[:\s]*(.*)$",
                "severity": "high",
                "description": "需要注意的代码",
            },
            "TEMP": {
                "pattern": r"(?i)#?\s*TEMP[:\s]*(.*)$",
                "severity": "medium",
                "description": "临时代码",
            },
            "DEBUG": {
                "pattern": r"(?i)#?\s*DEBUG[:\s]*(.*)$",
                "severity": "low",
                "description": "调试代码",
            },
            "REMOVE": {
                "pattern": r"(?i)#?\s*REMOVE[:\s]*(.*)$",
                "severity": "high",
                "description": "需要移除的代码",
            },
            "COMMENTED_CODE": {
                "pattern": (
                    r"^\s*#\s*(def |class |import |from |if |for |while |try |"
                    r"except |return |print\()"
                ),
                "severity": "medium",
                "description": "被注释的代码",
            },
            "CONSOLE_LOG": {
                "pattern": r"console\.(log|debug|info|warn|error)\s*\(",
                "severity": "low",
                "description": "控制台输出",
            },
            "PRINT_DEBUG": {
                "pattern": (
                    r"print\s*\([^)]*debug|print\s*\([^)]*test|" r"print\s*\([^)]*temp"
                ),
                "severity": "low",
                "description": "调试打印语句",
            },
        }

        self.file_extensions = {
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
            ".json",
            ".md",
            ".yml",
            ".yaml",
            ".toml",
        }

        self.exclude_dirs = {
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
        }

        self.reports_dir = self.project_root / "docs" / "02_test_report"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def scan_project(self) -> List[TempModification]:
        """扫描整个项目"""
        modifications = []

        for file_path in self._get_scannable_files():
            file_modifications = self._scan_file(file_path)
            modifications.extend(file_modifications)

        return modifications

    def _get_scannable_files(self) -> List[Path]:
        """获取可扫描的文件列表"""
        files = []

        for root, dirs, filenames in os.walk(self.project_root):
            # 排除特定目录
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.suffix.lower() in self.file_extensions:
                    files.append(file_path)

        return files

    def _scan_file(self, file_path: Path) -> List[TempModification]:
        """扫描单个文件"""
        modifications = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                line_modifications = self._check_line(file_path, line_num, line, lines)
                modifications.extend(line_modifications)

        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")

        return modifications

    def _check_line(
        self, file_path: Path, line_num: int, line: str, all_lines: List[str]
    ) -> List[TempModification]:
        """检查单行代码"""
        modifications = []

        for marker_type, config in self.detection_patterns.items():
            pattern = config["pattern"]
            match = re.search(pattern, line)

            if match:
                # 获取上下文行
                context_start = max(0, line_num - 3)
                context_end = min(len(all_lines), line_num + 2)
                context_lines = [
                    f"{i+1:4d}: {all_lines[i].rstrip()}"
                    for i in range(context_start, context_end)
                ]

                # 提取描述信息
                description = (
                    match.group(1) if match.groups() else config["description"]
                )
                if not description.strip():
                    description = config["description"]

                modification = TempModification(
                    file_path=str(file_path.relative_to(self.project_root)),
                    line_number=line_num,
                    line_content=line.strip(),
                    marker_type=marker_type,
                    severity=config["severity"],
                    description=description.strip(),
                    detected_at=datetime.now().isoformat(),
                    context_lines=context_lines,
                )

                modifications.append(modification)

        return modifications

    def generate_report(self, modifications: List[TempModification]) -> Dict:
        """生成检测报告"""
        # 按严重程度分组
        by_severity: Dict[str, List[TempModification]] = {
            "high": [],
            "medium": [],
            "low": [],
        }
        for mod in modifications:
            by_severity[mod.severity].append(mod)

        # 按文件分组
        by_file: Dict[str, List[TempModification]] = {}
        for mod in modifications:
            if mod.file_path not in by_file:
                by_file[mod.file_path] = []
            by_file[mod.file_path].append(mod)

        # 按标记类型分组
        by_type: Dict[str, List[TempModification]] = {}
        for mod in modifications:
            if mod.marker_type not in by_type:
                by_type[mod.marker_type] = []
            by_type[mod.marker_type].append(mod)

        # 统计信息
        stats = {
            "total_modifications": len(modifications),
            "high_severity": len(by_severity["high"]),
            "medium_severity": len(by_severity["medium"]),
            "low_severity": len(by_severity["low"]),
            "affected_files": len(by_file),
            "marker_types": len(by_type),
        }

        # 风险评估
        risk_level = self._assess_risk(stats)

        report = {
            "scan_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "statistics": stats,
            "risk_level": risk_level,
            "modifications_by_severity": {
                k: [asdict(mod) for mod in v] for k, v in by_severity.items()
            },
            "modifications_by_file": {
                k: [asdict(mod) for mod in v] for k, v in by_file.items()
            },
            "modifications_by_type": {
                k: [asdict(mod) for mod in v] for k, v in by_type.items()
            },
        }

        return report

    def _assess_risk(self, stats: Dict) -> str:
        """评估风险等级"""
        high_count = stats["high_severity"]
        medium_count = stats["medium_severity"]
        total_count = stats["total_modifications"]

        if high_count > 10 or total_count > 50:
            return "critical"
        elif high_count > 5 or total_count > 20:
            return "high"
        elif high_count > 0 or medium_count > 10:
            return "medium"
        elif total_count > 0:
            return "low"
        else:
            return "none"

    def generate_markdown_report(self, report: Dict) -> str:
        """生成Markdown格式的报告"""
        lines = []
        lines.append("# 临时修改检测报告")
        lines.append(f"\n**扫描时间**: {report['scan_timestamp']}")
        lines.append(f"**项目路径**: {report['project_root']}")

        # 风险等级图标
        risk_icons = {
            "none": "🟢",
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "critical": "🚨",
        }

        risk_level = report["risk_level"]
        icon = risk_icons.get(risk_level, "❓")
        lines.append(f"\n{icon} **风险等级**: {risk_level.upper()}")

        # 统计概览
        stats = report["statistics"]
        lines.append("\n## 📊 统计概览")
        lines.append(f"- 总计临时修改: **{stats['total_modifications']}** 处")
        lines.append(f"- 高风险: **{stats['high_severity']}** 处")
        lines.append(f"- 中风险: **{stats['medium_severity']}** 处")
        lines.append(f"- 低风险: **{stats['low_severity']}** 处")
        lines.append(f"- 涉及文件: **{stats['affected_files']}** 个")
        lines.append(f"- 标记类型: **{stats['marker_types']}** 种")

        # 按严重程度详细列表
        for severity in ["high", "medium", "low"]:
            modifications = report["modifications_by_severity"][severity]
            if not modifications:
                continue

            severity_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}

            lines.append(f"\n## {severity_icons[severity]} {severity.upper()}风险修改")

            for mod in modifications:
                lines.append(
                    f"\n### {mod['marker_type']} - "
                    f"{mod['file_path']}:{mod['line_number']}"
                )
                lines.append(f"**描述**: {mod['description']}")
                lines.append(f"**代码**: `{mod['line_content']}`")

                # 上下文代码
                if mod["context_lines"]:
                    lines.append("\n**上下文**:")
                    lines.append("```")
                    for context_line in mod["context_lines"]:
                        if str(mod["line_number"]) in context_line.split(":")[0]:
                            lines.append(f">>> {context_line}")
                        else:
                            lines.append(f"    {context_line}")
                    lines.append("```")

        # 按文件汇总
        if report["modifications_by_file"]:
            lines.append("\n## 📁 按文件汇总")

            for file_path, modifications in report["modifications_by_file"].items():
                lines.append(f"\n### {file_path}")
                lines.append(f"发现 **{len(modifications)}** 处临时修改:")

                for mod in modifications:
                    lines.append(
                        f"- 第{mod['line_number']}行: {mod['marker_type']} - "
                        f"{mod['description']}"
                    )

        # 建议行动
        lines.append("\n## 🎯 建议行动")

        if risk_level == "critical":
            lines.append("- 🚨 **立即处理**: 临时修改过多，存在严重风险")
            lines.append("- 🔍 **优先处理**: 所有FIXME、HACK、XXX标记")
            lines.append("- 📋 **制定计划**: 为每个高风险修改制定处理计划")
            lines.append("- 👥 **团队评审**: 组织代码评审会议")
        elif risk_level == "high":
            lines.append("- ⚠️ **尽快处理**: 存在较多高风险临时修改")
            lines.append("- 🎯 **重点关注**: FIXME和HACK标记")
            lines.append("- 📝 **文档记录**: 为复杂修改添加详细说明")
        elif risk_level == "medium":
            lines.append("- 👀 **定期检查**: 关注高风险标记的处理进度")
            lines.append("- 🧹 **代码清理**: 移除不必要的调试代码")
            lines.append("- 📋 **任务规划**: 将TODO转化为正式任务")
        elif risk_level == "low":
            lines.append("- 🟢 **保持现状**: 临时修改数量较少")
            lines.append("- 🔄 **定期扫描**: 建议每周扫描一次")
        else:
            lines.append("- 🎉 **优秀**: 未发现临时修改标记")
            lines.append("- 🔄 **持续监控**: 保持良好的代码习惯")

        # 预防措施
        lines.append("\n## 🛡️ 预防措施")
        lines.append("- 📝 **代码规范**: 建立临时修改标记使用规范")
        lines.append("- 🔍 **自动检查**: 在CI/CD中集成临时修改检测")
        lines.append("- 📋 **任务跟踪**: 将临时修改转化为正式任务")
        lines.append("- 👥 **代码评审**: 在PR中重点关注临时修改")
        lines.append("- 🧹 **定期清理**: 每个迭代结束后清理临时代码")

        return "\n".join(lines)

    def save_report(self, report: Dict, markdown_report: str) -> Tuple[Path, Path]:
        """保存报告文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存JSON报告
        json_file = self.reports_dir / f"temp_modifications_{timestamp}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # 保存Markdown报告
        md_file = self.reports_dir / "temp_modifications_report.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_report)

        # 保存最新的JSON报告
        latest_json = self.reports_dir / "temp_modifications_latest.json"
        with open(latest_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return json_file, md_file


def main():
    """主函数"""

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    detector = TempModificationDetector(project_root)

    print("[INFO] 开始扫描临时修改标记...")
    modifications = detector.scan_project()

    print(f"[SUCCESS] 扫描完成，发现 {len(modifications)} 处临时修改")

    print("[INFO] 生成检测报告...")
    report = detector.generate_report(modifications)
    markdown_report = detector.generate_markdown_report(report)

    print("[INFO] 保存报告文件...")
    json_file, md_file = detector.save_report(report, markdown_report)

    print("[SUCCESS] 报告已生成:")
    print(f"   [INFO] 详细报告: {md_file}")
    print(f"   [INFO] 数据文件: {json_file}")

    # 输出摘要
    stats = report["statistics"]
    risk_level = report["risk_level"]

    print("\n[INFO] 检测摘要:")
    print(f"   总计: {stats['total_modifications']} 处")
    print(f"   高风险: {stats['high_severity']} 处")
    print(f"   中风险: {stats['medium_severity']} 处")
    print(f"   低风险: {stats['low_severity']} 处")
    print(f"   风险等级: {risk_level.upper()}")

    # 根据风险等级返回退出码
    risk_codes = {"none": 0, "low": 0, "medium": 1, "high": 1, "critical": 2}

    return risk_codes.get(risk_level, 1)


if __name__ == "__main__":
    exit(main())
