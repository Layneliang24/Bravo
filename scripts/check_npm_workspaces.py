#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NPM Workspaces架构守护脚本

基于30轮CI修复血泪教训的深层洞察：
- npm workspaces设计原理：只应在根目录运行依赖管理命令
- 子目录npm ci的破坏性：会重新评估整个workspace依赖树
- deduped机制冲突：导致共享依赖被错误移除或重新定位
- 这是固有行为特性：不是配置问题，而是npm workspaces的内在机制

严格规范（基于架构级理解）：
[OK] CI环境：必须使用`npm ci`，确保版本严格一致
[OK] workspace原则：**绝对只在根目录**运行npm ci
[OK] 工具管理：所有工具添加到devDependencies，使用npx执行
[X] 绝对禁止：CI中使用`npm install`（包括`npm install -g`）
[X] 严重禁止：子目录的任何npm ci调用（会破坏整个workspace结构）
"""

import io
import os
import re
import sys

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


class NPMWorkspacesChecker:
    def __init__(self):
        self.violations = []
        self.patterns = [
            (
                re.compile(r"npm (ci|install).*", re.IGNORECASE),
                "working-directory:",
                "[X] 严重违规：子目录npm ci/install会破坏workspace依赖树",
            ),
            (
                re.compile(r"working-directory:.*frontend.*", re.IGNORECASE),
                "npm",
                "[!] 工作流违规：working-directory应该使用npm run xxx:frontend",
            ),
            (
                re.compile(r"npm install -g", re.IGNORECASE),
                "",
                "[!] 全局安装违规：应使用项目依赖+npx执行",
            ),
            (
                re.compile(r'"[^"]*npm (ci|install)[^"]*"', re.IGNORECASE),
                "scripts",
                "[!] Scripts违规：package.json中不应有子目录npm命令",
            ),
        ]

    def check_file(self, file_path):
        """检查单个文件是否违反npm workspaces架构规则"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                for pattern, context_hint, message in self.patterns:
                    if pattern.search(line) and (
                        not context_hint or context_hint in line
                    ):
                        self.violations.append(
                            {
                                "file": file_path,
                                "line": line_num,
                                "content": line.strip(),
                                "message": message,
                            }
                        )

        except (UnicodeDecodeError, FileNotFoundError):
            # 忽略二进制文件和不存在的文件
            pass

        return len(self.violations) == 0

    def should_check_file(self, file_path):
        """判断是否应该检查此文件"""
        if not os.path.exists(file_path):
            return False

        # 跳过自己
        if "check_npm_workspaces" in file_path:
            return False

        # 检查文件扩展名
        _, ext = os.path.splitext(file_path)
        if ext not in [".yml", ".yaml", ".py", ".js", ".json", ".sh", "Makefile"]:
            return False

        # 跳过某些路径
        skip_paths = [
            "node_modules",
            ".git",
            "__pycache__",
            ".cache",
            ".backup/",
            "docs/02_test_report/temp_modifications",
        ]
        return not any(skip_path in file_path for skip_path in skip_paths)

    def print_violations(self):
        """打印所有违规信息"""
        if not self.violations:
            # 静默模式：没有违规时不输出，避免重复信息
            return False

        print("[ERROR] 发现NPM Workspaces架构违规！")
        print("=" * 60)
        print("基于30轮修复血泪教训，以下模式会导致依赖漂移灾难：")
        print()

        for violation in self.violations:
            print(f"文件: {violation['file']}")
            print(f"行号: {violation['line']}")
            print(f"内容: {violation['content']}")
            print(f"问题: {violation['message']}")
            print()

        print("修复指南：")
        print("- cd frontend && npm ci  => npm run build:frontend")
        print("- npm install -g tool   => npx tool (项目依赖)")
        print("- 在GitHub Actions中只在根目录调用npm ci")
        print("- 删除所有working-directory + npm 组合")
        print()
        print("正确做法：")
        print("+ npm ci --prefer-offline --no-audit (仅根目录)")
        print("+ npm run build:frontend/test:backend")
        print("+ npx tool执行工具(不要-g全局安装)")

        return len(self.violations) > 0


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: check_npm_workspaces.py <file1> [file2] ...")
        return 0

    checker = NPMWorkspacesChecker()

    for file_path in sys.argv[1:]:
        if checker.should_check_file(file_path):
            checker.check_file(file_path)

    if checker.print_violations():
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
