#!/usr/bin/env python3
"""
代码文件合规检查器
验证代码文件的关联性和质量
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class CodeChecker:
    """代码文件检查器"""

    def __init__(self, rule_config: Dict):
        self.rule_config = rule_config
        self.errors = []
        self.warnings = []

    def check(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查代码文件

        Args:
            file_path: 代码文件路径

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        path = Path(file_path)

        if not path.exists():
            self.errors.append(f"文件不存在: {file_path}")
            return False, self.errors, self.warnings

        # 检查文件关联性（如果规则要求）
        traceability = self.rule_config.get("traceability", {})
        if traceability.get("require_prd_link", False):
            self._check_prd_link(file_path)

        # 检查代码质量
        self._check_quality(file_path)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_prd_link(self, file_path: str):
        """检查PRD关联（通过文件路径或注释）"""
        # 这里可以检查文件头部注释中是否包含REQ-ID
        # 或者通过文件路径推断
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            # 检查文件头部是否有REQ-ID注释
            lines = content.split("\n")[:20]  # 只检查前20行
            has_req_id = any(re.search(r"REQ-\d{4}-\d{3}-", line) for line in lines)
            if not has_req_id:
                self.warnings.append("建议在文件头部注释中包含REQ-ID关联")
        except Exception:
            pass  # 如果无法读取，跳过此检查

    def _check_quality(self, file_path: str):
        """检查代码质量"""
        quality_rules = self.rule_config.get("quality", {})

        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            self.warnings.append(f"无法读取文件进行质量检查: {e}")
            return

        # 检查文档字符串
        if quality_rules.get("require_docstrings", False):
            if file_path.endswith(".py"):
                # 检查类和函数是否有文档字符串
                if re.search(r"class\s+\w+", content) or re.search(
                    r"def\s+\w+", content
                ):
                    if not re.search(r'""".*"""', content, re.DOTALL):
                        self.warnings.append("建议为类和函数添加文档字符串")

        # 检查类型提示（Python）
        if quality_rules.get("require_type_hints", False) and file_path.endswith(".py"):
            # 检查函数定义是否有类型提示
            func_defs = re.findall(r"def\s+\w+\([^)]*\)", content)
            if func_defs:
                has_type_hints = any("->" in func or ":" in func for func in func_defs)
                if not has_type_hints:
                    self.warnings.append("建议为函数添加类型提示")

        # 检查JSDoc（TypeScript/JavaScript）
        if quality_rules.get("require_jsdoc", False):
            if file_path.endswith((".ts", ".js", ".vue")):
                # 检查函数是否有JSDoc注释
                func_defs = re.findall(
                    r"(function\s+\w+|const\s+\w+\s*=\s*\(|export\s+function)", content
                )
                if func_defs:
                    has_jsdoc = re.search(r"/\*\*.*?\*/", content, re.DOTALL)
                    if not has_jsdoc:
                        self.warnings.append("建议为函数添加JSDoc注释")
