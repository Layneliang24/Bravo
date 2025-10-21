#!/usr/bin/env python3
"""
@deletable: false
@purpose: 清理工具 - 自动删除过期或标记为可删除的文件
@created: 2025-10-20
@author: Claude Sonnet 4.5
@safe_to_delete: no
@dependencies: 文件生命周期管理系统
"""

import argparse
import io
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class DeletableFileCleanup:
    """清理标记为可删除的文件"""

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

    def __init__(self, root_dir: str = ".", dry_run: bool = True):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.files_to_delete: List[Dict] = []
        self.deleted_files: List[str] = []
        self.failed_deletions: List[Dict] = []

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

    def should_delete(self, file_path: Path) -> tuple[bool, str]:
        """判断文件是否应该被删除"""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            return False, f"无法读取文件: {e}"

        # 检查 @safe_to_delete
        safe_to_delete = self.extract_metadata(file_path, content, "@safe_to_delete")
        if not safe_to_delete or safe_to_delete.lower() not in ["yes", "true"]:
            return False, f"@safe_to_delete 不是 yes/true (当前: {safe_to_delete})"

        # 检查 @delete_after
        delete_after = self.extract_metadata(file_path, content, "@delete_after")
        if delete_after:
            try:
                delete_date = datetime.strptime(delete_after.strip(), "%Y-%m-%d")
                if datetime.now() > delete_date:
                    return True, f"已过期（删除日期: {delete_after}）"
                else:
                    return False, f"未到删除日期（{delete_after}）"
            except ValueError:
                return False, f"删除日期格式错误: {delete_after}"

        # 没有 delete_after 字段，但 safe_to_delete=yes
        return True, "标记为可安全删除"

    def scan_for_cleanup(self) -> None:
        """扫描需要清理的文件"""
        print(f"🔍 扫描目录: {self.root_dir.absolute()}")
        print("")

        for file_path in self.root_dir.rglob("*"):
            # 跳过目录
            if file_path.is_dir():
                continue

            # 跳过排除的路径
            if self.is_excluded(file_path):
                continue

            # 只处理 deletable 文件
            if not self.is_deletable_file(file_path):
                continue

            # 判断是否应该删除
            should_del, reason = self.should_delete(file_path)

            if should_del:
                self.files_to_delete.append(
                    {
                        "path": str(file_path.relative_to(self.root_dir)),
                        "full_path": str(file_path),
                        "size": file_path.stat().st_size,
                        "reason": reason,
                    }
                )

    def perform_cleanup(self) -> None:
        """执行清理操作"""
        if not self.files_to_delete:
            print("✅ 没有需要清理的文件")
            return

        print("=" * 80)
        if self.dry_run:
            print("🔍 模拟运行 - 以下文件将被删除 ({} 个)：".format(len(self.files_to_delete)))
        else:
            print("🗑️  开始清理 ({} 个文件)：".format(len(self.files_to_delete)))
        print("=" * 80)
        print("")

        total_size = sum(f["size"] for f in self.files_to_delete)

        for file_info in self.files_to_delete:
            print(f"  📄 {file_info['path']}")
            print(f"     📏 大小: {file_info['size'] / 1024:.2f} KB")
            print(f"     💡 原因: {file_info['reason']}")

            if not self.dry_run:
                try:
                    os.remove(file_info["full_path"])
                    self.deleted_files.append(file_info["path"])
                    print("     ✅ 已删除")
                except Exception as e:
                    self.failed_deletions.append(
                        {"path": file_info["path"], "error": str(e)}
                    )
                    print(f"     ❌ 删除失败: {e}")
            else:
                print("     🔍 [模拟] 将会删除")

            print("")

        print("=" * 80)
        print("📊 清理统计：")
        print("=" * 80)
        print(f"  📝 待删除: {len(self.files_to_delete)} 个文件")
        print(f"  💾 总大小: {total_size / 1024:.2f} KB")

        if not self.dry_run:
            print(f"  ✅ 成功删除: {len(self.deleted_files)} 个")
            if self.failed_deletions:
                print(f"  ❌ 删除失败: {len(self.failed_deletions)} 个")
                print("")
                for failed in self.failed_deletions:
                    print(f"     • {failed['path']}: {failed['error']}")
        else:
            print("")
            print("💡 这是模拟运行，文件未被实际删除")
            print("💡 使用 --execute 参数执行实际删除操作")

        print("=" * 80)

    def clean_empty_dirs(self) -> None:
        """清理空目录"""
        if self.dry_run:
            return

        empty_dirs = []
        for dir_path in self.root_dir.rglob("*"):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                if not self.is_excluded(dir_path):
                    empty_dirs.append(dir_path)

        if empty_dirs:
            print("")
            print("=" * 80)
            print("🗂️  发现 {} 个空目录：".format(len(empty_dirs)))
            print("=" * 80)
            for dir_path in empty_dirs:
                try:
                    shutil.rmtree(dir_path)
                    print(f"  ✅ 已删除: {dir_path.relative_to(self.root_dir)}")
                except Exception as e:
                    print(f"  ❌ 删除失败: {dir_path.relative_to(self.root_dir)} - {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="清理标记为可删除的文件")
    parser.add_argument("--dir", "-d", default=".", help="要清理的目录路径（默认：当前目录）")
    parser.add_argument(
        "--execute",
        "-e",
        action="store_true",
        help="实际执行删除操作（默认：模拟运行）",
    )
    parser.add_argument(
        "--clean-empty-dirs",
        action="store_true",
        help="清理空目录",
    )

    args = parser.parse_args()

    # 创建清理工具
    cleanup = DeletableFileCleanup(args.dir, dry_run=not args.execute)

    # 扫描
    cleanup.scan_for_cleanup()

    # 执行清理
    cleanup.perform_cleanup()

    # 清理空目录
    if args.clean_empty_dirs:
        cleanup.clean_empty_dirs()

    # 根据结果返回退出码
    if not args.execute:
        sys.exit(0)  # 模拟运行总是成功
    elif cleanup.failed_deletions:
        sys.exit(1)  # 有删除失败
    else:
        sys.exit(0)  # 全部成功


if __name__ == "__main__":
    main()
