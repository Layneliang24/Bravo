#!/usr/bin/env python3
"""
@deletable: false
@purpose: 扫描工具 - 查找所有标记为deletable的文件并生成报告
@created: 2025-10-20
@author: Claude Sonnet 4.5
@safe_to_delete: no
@dependencies: 文件生命周期管理系统
"""

import argparse
import io
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class DeletableFileScanner:
    """扫描并分析项目中的 deletable 文件"""

    EXCLUDE_PATTERNS = [
        r"node_modules/",
        r"\.git/",
        r"__pycache__/",
        r"\.pytest_cache/",
        r"\.venv/",
        r"venv/",
        r"dist/",
        r"build/",
        r"\.egg-info/",
        r"coverage/",
        r"\.tox/",
        r"\.next/",
        r"\.nuxt/",
    ]

    COMMENT_PATTERNS = {
        "python": [
            r'"""[\s\S]*?@{field}[\s:]+([^\n]+)',
            r"'''[\s\S]*?@{field}[\s:]+([^\n]+)",
            r"#\s*@{field}[\s:]+(.+?)$",
        ],
        "javascript": [
            r"/\*\*[\s\S]*?@{field}\s+([^\n]+)",
            r"//\s*@{field}[\s:]+(.+?)$",
        ],
        "shell": [r"#\s*@{field}[\s:]+(.+?)$"],
        "markdown": [r"<!--[\s\S]*?@{field}[\s:]+([^\n]+)"],
        "yaml": [r"#\s*@{field}[\s:]+(.+?)$"],
    }

    EXTENSION_MAP = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "javascript",
        ".tsx": "javascript",
        ".sh": "shell",
        ".bash": "shell",
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".txt": "shell",
    }

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.deletable_files: List[Dict] = []

    def is_excluded(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path)
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, path_str):
                return True
        return False

    def is_deletable_file(self, file_path: Path) -> bool:
        """判断文件是否标记为可删除"""
        filename = file_path.name
        return ".deletable." in filename.lower() or filename.lower().startswith(
            "deletable_"
        )

    def get_language(self, file_path: Path) -> Optional[str]:
        """根据文件扩展名获取语言类型"""
        ext = file_path.suffix.lower()
        return self.EXTENSION_MAP.get(ext)

    def extract_metadata(
        self, file_path: Path, content: str, field: str
    ) -> Optional[str]:
        """从文件内容中提取指定的元数据字段"""
        language = self.get_language(file_path)
        if not language:
            return None

        patterns = self.COMMENT_PATTERNS.get(language, [])

        for pattern_template in patterns:
            pattern = pattern_template.replace("{field}", re.escape(field))
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)

            for match in matches:
                value = match.group(1).strip()
                return value

        return None

    def analyze_file(self, file_path: Path) -> Dict:
        """分析单个文件的元数据"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            return {
                "path": str(file_path.relative_to(self.root_dir)),
                "error": f"无法读取文件: {e}",
                "size": 0,
            }

        # 提取元数据
        metadata = {
            "path": str(file_path.relative_to(self.root_dir)),
            "size": file_path.stat().st_size,
            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "deletable": self.extract_metadata(file_path, content, "@deletable"),
            "purpose": self.extract_metadata(file_path, content, "@purpose"),
            "safe_to_delete": self.extract_metadata(
                file_path, content, "@safe_to_delete"
            ),
            "dependencies": self.extract_metadata(file_path, content, "@dependencies"),
            "delete_after": self.extract_metadata(file_path, content, "@delete_after"),
            "created": self.extract_metadata(file_path, content, "@created"),
            "author": self.extract_metadata(file_path, content, "@author"),
        }

        # 检查是否有完整的元数据
        has_metadata = bool(
            metadata["deletable"] and metadata["purpose"] and metadata["safe_to_delete"]
        )
        metadata["has_complete_metadata"] = has_metadata

        # 检查是否过期（如果有 delete_after 字段）
        if metadata["delete_after"]:
            try:
                delete_date = datetime.strptime(
                    metadata["delete_after"].strip(), "%Y-%m-%d"
                )
                metadata["is_expired"] = datetime.now() > delete_date
            except ValueError:
                metadata["is_expired"] = False
        else:
            metadata["is_expired"] = False

        return metadata

    def scan(self) -> None:
        """扫描项目中的所有 deletable 文件"""
        print(f"🔍 扫描项目目录: {self.root_dir.absolute()}")
        print("")

        for file_path in self.root_dir.rglob("*"):
            # 跳过目录
            if file_path.is_dir():
                continue

            # 跳过排除的路径
            if self.is_excluded(file_path):
                continue

            # 只处理 deletable 文件
            if self.is_deletable_file(file_path):
                metadata = self.analyze_file(file_path)
                self.deletable_files.append(metadata)

    def print_report(self, format: str = "text") -> None:
        """打印扫描报告"""
        if format == "json":
            self.print_json_report()
        else:
            self.print_text_report()

    def print_text_report(self) -> None:
        """打印文本格式的报告"""
        if not self.deletable_files:
            print("✅ 未发现任何 deletable 文件")
            return

        print("=" * 80)
        print("📊 Deletable 文件扫描报告")
        print("=" * 80)
        print("")
        print(f"📁 扫描目录: {self.root_dir.absolute()}")
        print(f"📝 发现文件: {len(self.deletable_files)} 个")
        print("")

        # 统计信息
        with_metadata = [f for f in self.deletable_files if f["has_complete_metadata"]]
        without_metadata = [
            f for f in self.deletable_files if not f["has_complete_metadata"]
        ]
        expired_files = [f for f in self.deletable_files if f.get("is_expired", False)]
        safe_to_delete = [
            f
            for f in self.deletable_files
            if f.get("safe_to_delete", "").lower() in ["yes", "true"]
        ]

        total_size = sum(f["size"] for f in self.deletable_files)

        print("📈 统计信息：")
        print(f"  ✅ 有完整元数据: {len(with_metadata)} 个")
        print(f"  ❌ 缺少元数据: {len(without_metadata)} 个")
        print(f"  ⏰ 已过期: {len(expired_files)} 个")
        print(f"  🗑️  可安全删除: {len(safe_to_delete)} 个")
        print(f"  💾 总大小: {total_size / 1024:.2f} KB")
        print("")

        # 详细列表
        if without_metadata:
            print("=" * 80)
            print(f"❌ 缺少元数据的文件 ({len(without_metadata)} 个)：")
            print("=" * 80)
            print("")
            for file_info in without_metadata:
                print(f"  📄 {file_info['path']}")
                print(f"     📏 大小: {file_info['size'] / 1024:.2f} KB")
                print(f"     📅 修改: {file_info['modified']}")
                if "error" in file_info:
                    print(f"     ⚠️  错误: {file_info['error']}")
                print("")

        if expired_files:
            print("=" * 80)
            print(f"⏰ 已过期的文件 ({len(expired_files)} 个)：")
            print("=" * 80)
            print("")
            for file_info in expired_files:
                print(f"  📄 {file_info['path']}")
                print(f"     📅 删除日期: {file_info['delete_after']}")
                print(f"     📝 用途: {file_info.get('purpose', 'N/A')}")
                print(f"     🗑️  可删除: {file_info.get('safe_to_delete', 'N/A')}")
                print("")

        if with_metadata:
            print("=" * 80)
            print(f"✅ 有完整元数据的文件 ({len(with_metadata)} 个)：")
            print("=" * 80)
            print("")
            for file_info in with_metadata:
                print(f"  📄 {file_info['path']}")
                print(f"     📝 用途: {file_info.get('purpose', 'N/A')}")
                print(f"     🗑️  可删除: {file_info.get('safe_to_delete', 'N/A')}")
                print(f"     🔗 依赖: {file_info.get('dependencies', 'N/A')}")
                if file_info.get("delete_after"):
                    print(f"     ⏰ 删除日期: {file_info['delete_after']}")
                print(f"     📏 大小: {file_info['size'] / 1024:.2f} KB")
                print(f"     📅 修改: {file_info['modified']}")
                print("")

        print("=" * 80)

    def print_json_report(self) -> None:
        """打印JSON格式的报告"""
        report = {
            "scan_time": datetime.now().isoformat(),
            "root_dir": str(self.root_dir.absolute()),
            "total_files": len(self.deletable_files),
            "statistics": {
                "with_metadata": len(
                    [f for f in self.deletable_files if f["has_complete_metadata"]]
                ),
                "without_metadata": len(
                    [f for f in self.deletable_files if not f["has_complete_metadata"]]
                ),
                "expired": len(
                    [f for f in self.deletable_files if f.get("is_expired", False)]
                ),
                "safe_to_delete": len(
                    [
                        f
                        for f in self.deletable_files
                        if f.get("safe_to_delete", "").lower() in ["yes", "true"]
                    ]
                ),
                "total_size": sum(f["size"] for f in self.deletable_files),
            },
            "files": self.deletable_files,
        }
        print(json.dumps(report, indent=2, ensure_ascii=False))

    def save_report(self, output_file: str, format: str = "json") -> None:
        """保存报告到文件"""
        if format == "json":
            report = {
                "scan_time": datetime.now().isoformat(),
                "root_dir": str(self.root_dir.absolute()),
                "total_files": len(self.deletable_files),
                "files": self.deletable_files,
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ 报告已保存到: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="扫描项目中的 deletable 文件并生成报告")
    parser.add_argument("--dir", "-d", default=".", help="要扫描的目录路径（默认：当前目录）")
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="报告格式（默认：text）",
    )
    parser.add_argument("--output", "-o", help="保存报告到文件")

    args = parser.parse_args()

    # 创建扫描器
    scanner = DeletableFileScanner(args.dir)

    # 执行扫描
    scanner.scan()

    # 打印报告
    scanner.print_report(format=args.format)

    # 保存报告（如果指定）
    if args.output:
        scanner.save_report(args.output, format="json")


if __name__ == "__main__":
    main()
