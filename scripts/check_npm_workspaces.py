#!/usr/bin/env python3
"""
NPM Workspaces 架构保护脚本

目的：检查和预防npm workspaces架构违规，避免30轮修复的恶性循环

检查项目：
1. 子目录中的npm ci/install调用
2. working-directory + npm组合
3. npm install -g全局安装
4. 危险的cd && npm模式

基于30轮修复血泪教训，这些违规会导致依赖漂移灾难。
"""

import sys
import re
import os
from pathlib import Path


class NPMWorkspacesChecker:
    def __init__(self):
        self.violations = []
        self.warning_patterns = [
            # 最危险的模式
            (r'cd\s+(?:frontend|e2e|[^&\s]+)\s*&&\s*npm\s+(?:ci|install)', 
             "❌ 严重违规：子目录npm ci/install会破坏workspace依赖树"),
            
            # 工作流违规
            (r'working-directory:\s*\.\/(?:frontend|e2e)', 
             "⚠️  工作流违规：working-directory应该使用npm run xxx:frontend"),
             
            # 全局安装违规
            (r'npm\s+install\s+-g', 
             "⚠️  全局安装违规：应使用项目依赖+npx执行"),
             
            # package.json scripts违规
            (r'"[^"]*":\s*"[^"]*cd\s+(?:frontend|e2e)[^"]*npm\s+(?:ci|install)', 
             "⚠️  Scripts违规：package.json中不应有子目录npm命令"),
        ]

    def check_file(self, file_path: str) -> bool:
        """检查单个文件，返回是否有违规"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return False  # 跳过二进制文件或无权限文件

        file_violations = []
        
        for line_num, line in enumerate(content.splitlines(), 1):
            for pattern, message in self.warning_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    file_violations.append({
                        'file': file_path,
                        'line': line_num,
                        'content': line.strip(),
                        'message': message,
                        'pattern': pattern
                    })

        if file_violations:
            self.violations.extend(file_violations)
            return True
        return False

    def print_violations(self):
        """打印所有违规信息"""
        if not self.violations:
            print("✅ NPM Workspaces架构检查通过 - 无违规发现")
            return

        print("🚨 发现NPM Workspaces架构违规！")
        print("=" * 60)
        print("基于30轮修复血泪教训，以下模式会导致依赖漂移灾难：")
        print()

        for violation in self.violations:
            print(f"📁 文件: {violation['file']}")
            print(f"📍 行号: {violation['line']}")
            print(f"💭 内容: {violation['content']}")
            print(f"⚠️  问题: {violation['message']}")
            print()

        print("🔧 修复指南：")
        print("• cd frontend && npm ci  → npm run build:frontend")
        print("• npm install -g tool   → npx tool (项目依赖)")
        print("• working-directory     → 根目录npm run")
        print()
        print("📚 详细说明: docs/architecture/ADR-001-npm-workspaces.md")
        print("=" * 60)

    def check_files(self, file_paths: list) -> bool:
        """检查多个文件，返回是否有任何违规"""
        has_violations = False
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                if self.check_file(file_path):
                    has_violations = True

        return has_violations


def main():
    """主函数：pre-commit hook入口"""
    if len(sys.argv) < 2:
        print("用法: check_npm_workspaces.py <file1> [file2] ...")
        return 0

    checker = NPMWorkspacesChecker()
    file_paths = sys.argv[1:]
    
    has_violations = checker.check_files(file_paths)
    checker.print_violations()
    
    if has_violations:
        print("\n💡 提示：这个检查基于30轮修复的惨痛教训。")
        print("   npm workspaces依赖管理违规会导致难以调试的依赖漂移问题。")
        print("   修复这些问题比忽略它们更节省时间！")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
