#!/usr/bin/env python3
"""
@deletable: false
@purpose: Pre-commit检查工具 - 验证带deletable标识的文件是否包含必需的元数据
@created: 2025-10-20
@author: Claude Sonnet 4.5
@safe_to_delete: no
@dependencies: Pre-commit系统核心依赖
"""

import io
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class DeletableFileChecker:
    """检查带deletable标识的文件是否符合规范"""

    # 必需的元数据字段
    REQUIRED_METADATA = ["@deletable", "@purpose", "@safe_to_delete"]

    # 可选的元数据字段
    OPTIONAL_METADATA = ["@delete_after", "@dependencies", "@created", "@author"]

    # 支持的注释格式
    COMMENT_PATTERNS = {
        # Python: """ @deletable: true """
        "python": [
            r'"""[\s\S]*?@{field}[\s:]+([^\n]+)',
            r"'''[\s\S]*?@{field}[\s:]+([^\n]+)",
            r"#\s*@{field}[\s:]+(.+?)$",
        ],
        # JavaScript/TypeScript: /** @deletable true */
        "javascript": [
            r"/\*\*[\s\S]*?@{field}\s+([^\n]+)",
            r"//\s*@{field}[\s:]+(.+?)$",
        ],
        # Shell/Bash: # @deletable: true
        "shell": [r"#\s*@{field}[\s:]+(.+?)$"],
        # Markdown: <!-- @deletable: true -->
        "markdown": [r"<!--[\s\S]*?@{field}[\s:]+([^\n]+)"],
        # YAML: # @deletable: true
        "yaml": [r"#\s*@{field}[\s:]+(.+?)$"],
        # JSON (使用 _metadata 字段)
        "json": [r'"@{field}"[\s:]+["\'](.+?)["\']'],
    }

    # 文件扩展名到语言的映射
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
        ".json": "json",
        ".txt": "shell",  # 纯文本文件使用 # 注释
    }

    # 排除的目录和文件模式
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

    def __init__(self):
        self.violations: List[Dict[str, str]] = []
        self.checked_files: Set[str] = set()

    def is_excluded(self, file_path: str) -> bool:
        """检查文件是否应该被排除"""
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, file_path):
                return True
        return False

    def is_deletable_file(self, file_path: str) -> bool:
        """判断文件是否标记为可删除"""
        # 检查文件名是否包含 deletable 标识
        filename = Path(file_path).name
        return ".deletable." in filename.lower() or filename.lower().startswith(
            "deletable_"
        )

    def get_language(self, file_path: str) -> Optional[str]:
        """根据文件扩展名获取语言类型"""
        ext = Path(file_path).suffix.lower()
        return self.EXTENSION_MAP.get(ext)

    def extract_metadata(
        self, file_path: str, content: str, field: str
    ) -> Optional[str]:
        """从文件内容中提取指定的元数据字段"""
        language = self.get_language(file_path)
        if not language:
            return None

        patterns = self.COMMENT_PATTERNS.get(language, [])

        for pattern_template in patterns:
            # 将 {field} 替换为实际的字段名
            pattern = pattern_template.replace("{field}", re.escape(field))
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)

            for match in matches:
                value = match.group(1).strip()
                return value

        return None

    def check_file_metadata(self, file_path: str) -> Tuple[bool, List[str]]:
        """检查文件的元数据完整性"""
        if not os.path.exists(file_path):
            return True, []  # 文件不存在，跳过

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            return False, [f"无法读取文件: {e}"]

        missing_fields = []

        for field in self.REQUIRED_METADATA:
            value = self.extract_metadata(file_path, content, field)
            if not value:
                missing_fields.append(field)

        if missing_fields:
            return False, missing_fields

        # 验证 @deletable 的值
        deletable_value = self.extract_metadata(file_path, content, "@deletable")
        if deletable_value and deletable_value.lower() not in ["true", "yes", "1"]:
            return (
                False,
                [f"@deletable 的值必须是 true/yes/1，当前值: {deletable_value}"],
            )

        # 验证 @safe_to_delete 的值
        safe_value = self.extract_metadata(file_path, content, "@safe_to_delete")
        if safe_value and safe_value.lower() not in ["yes", "no", "true", "false"]:
            return (
                False,
                [f"@safe_to_delete 的值必须是 yes/no，当前值: {safe_value}"],
            )

        return True, []

    def check_files(self, file_paths: List[str]) -> bool:
        """检查一组文件"""
        has_violations = False

        for file_path in file_paths:
            # 跳过已检查的文件
            if file_path in self.checked_files:
                continue

            # 跳过排除的文件
            if self.is_excluded(file_path):
                continue

            # 只检查带 deletable 标识的文件
            if not self.is_deletable_file(file_path):
                continue

            # 检查是否支持该文件类型
            if not self.get_language(file_path):
                self.violations.append(
                    {
                        "file": file_path,
                        "error": "不支持的文件类型，无法验证元数据",
                        "severity": "warning",
                    }
                )
                continue

            # 检查元数据
            is_valid, missing_or_errors = self.check_file_metadata(file_path)

            if not is_valid:
                has_violations = True
                for issue in missing_or_errors:
                    self.violations.append(
                        {"file": file_path, "error": issue, "severity": "error"}
                    )

            self.checked_files.add(file_path)

        return has_violations

    def print_violations(self) -> None:
        """打印所有违规信息"""
        if not self.violations:
            return

        print("")
        print("=" * 70)
        print("❌ Deletable文件元数据检查失败")
        print("=" * 70)
        print("")

        errors = [v for v in self.violations if v["severity"] == "error"]
        warnings = [v for v in self.violations if v["severity"] == "warning"]

        if errors:
            print(f"🚫 发现 {len(errors)} 个错误：")
            print("")
            for violation in errors:
                print(f"  📄 文件: {violation['file']}")
                print(f"     ❌ {violation['error']}")
                print("")

        if warnings:
            print(f"⚠️  发现 {len(warnings)} 个警告：")
            print("")
            for violation in warnings:
                print(f"  📄 文件: {violation['file']}")
                print(f"     ⚠️  {violation['error']}")
                print("")

        print("=" * 70)
        print("💡 修复建议：")
        print("=" * 70)
        print("")
        print("在文件开头添加元数据注释，示例：")
        print("")
        print("Python 文件：")
        print('  """')
        print("  @deletable: true")
        print("  @purpose: 临时测试脚本，验证XXX功能")
        print("  @safe_to_delete: yes")
        print("  @dependencies: none")
        print('  """')
        print("")
        print("JavaScript/TypeScript 文件：")
        print("  /**")
        print("   * @deletable true")
        print("   * @purpose 临时测试，验证API响应")
        print("   * @safe_to_delete yes")
        print("   */")
        print("")
        print("Shell 脚本：")
        print("  # @deletable: true")
        print("  # @purpose: 一次性部署脚本")
        print("  # @safe_to_delete: yes")
        print("")
        print("Markdown 文件：")
        print("  <!--")
        print("  @deletable: true")
        print("  @purpose: 临时调试记录")
        print("  @safe_to_delete: yes")
        print("  -->")
        print("")
        print("=" * 70)
        print("")

    def get_summary(self) -> str:
        """获取检查摘要"""
        if not self.violations:
            return "✅ 所有 deletable 文件的元数据检查通过"

        error_count = len([v for v in self.violations if v["severity"] == "error"])
        warning_count = len([v for v in self.violations if v["severity"] == "warning"])

        return f"❌ 发现 {error_count} 个错误, {warning_count} 个警告"


def main():
    """主函数"""
    # 获取要检查的文件列表
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []

    if not file_paths:
        print("ℹ️  未指定文件，跳过 deletable 文件检查")
        sys.exit(0)

    # 创建检查器
    checker = DeletableFileChecker()

    # 检查文件
    has_violations = checker.check_files(file_paths)

    # 如果没有检查任何文件，静默退出
    if not checker.checked_files:
        sys.exit(0)

    # 打印结果
    if has_violations:
        checker.print_violations()
        print(checker.get_summary())
        sys.exit(1)
    else:
        # 只在有检查文件时才输出成功信息
        if checker.checked_files:
            print(f"✅ Deletable文件元数据检查通过 ({len(checker.checked_files)} 个文件)")
        sys.exit(0)


if __name__ == "__main__":
    main()
