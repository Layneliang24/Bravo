#!/usr/bin/env python3
"""
PRD文件合规检查器
验证PRD文件的元数据、结构和内容
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class PRDChecker:
    """PRD文件检查器"""

    def __init__(self, rule_config: Dict):
        self.rule_config = rule_config
        self.errors = []
        self.warnings = []

    def check(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查PRD文件

        Args:
            file_path: PRD文件路径

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        path = Path(file_path)

        if not path.exists():
            self.errors.append(f"文件不存在: {file_path}")
            return False, self.errors, self.warnings

        # 读取文件内容
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(f"无法读取文件: {e}")
            return False, self.errors, self.warnings

        # 检查Frontmatter
        if not self._check_frontmatter(content):
            return False, self.errors, self.warnings

        # 提取元数据
        metadata = self._extract_metadata(content)
        if not metadata:
            return False, self.errors, self.warnings

        # 验证元数据
        self._validate_metadata(metadata)

        # 验证文件结构
        self._validate_structure(content)

        # 验证内容
        self._validate_content(content)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_frontmatter(self, content: str) -> bool:
        """检查Frontmatter格式"""
        if not content.startswith("---"):
            self.errors.append("PRD文件必须以YAML Frontmatter开始（---）")
            return False

        # 检查Frontmatter结束标记
        lines = content.split("\n")
        if len(lines) < 2 or lines[1].strip() != "---":
            self.errors.append("Frontmatter格式错误：缺少结束标记")
            return False

        return True

    def _extract_metadata(self, content: str) -> Optional[Dict]:
        """提取Frontmatter元数据"""
        try:
            # 提取Frontmatter部分
            parts = content.split("---", 2)
            if len(parts) < 3:
                self.errors.append("Frontmatter格式错误")
                return None

            frontmatter_text = parts[1]
            metadata = yaml.safe_load(frontmatter_text)

            if not isinstance(metadata, dict):
                self.errors.append("Frontmatter必须是YAML字典格式")
                return None

            return metadata
        except yaml.YAMLError as e:
            self.errors.append(f"Frontmatter YAML解析错误: {e}")
            return None

    def _validate_metadata(self, metadata: Dict):
        """验证元数据"""
        required_fields = self.rule_config.get("required_metadata_fields", [])
        validation_rules = self.rule_config.get("metadata_validation", {})

        # 检查必需字段
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"缺少必需字段: {field}")

        # 验证字段格式
        for field, rules in validation_rules.items():
            if field not in metadata:
                continue

            value = metadata[field]

            # 检查正则表达式
            if "pattern" in rules:
                pattern = rules["pattern"]
                if not re.match(pattern, str(value)):
                    self.errors.append(f"字段 {field} 格式错误: 必须匹配 {pattern}")

            # 检查枚举值
            if "enum" in rules:
                if value not in rules["enum"]:
                    self.errors.append(
                        f"字段 {field} 值无效: {value}，必须是 {rules['enum']} 之一"
                    )

            # 检查类型
            if "type" in rules:
                expected_type = rules["type"]
                if expected_type == "list" and not isinstance(value, list):
                    self.errors.append(f"字段 {field} 必须是列表类型")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    self.errors.append(f"字段 {field} 必须是布尔类型")

            # 检查列表长度
            if isinstance(value, list) and "min_items" in rules:
                if len(value) < rules["min_items"]:
                    self.errors.append(f"字段 {field} 至少需要 {rules['min_items']} 个项目")

    def _validate_structure(self, content: str):
        """验证文件结构"""
        required_sections = self.rule_config.get("file_structure", {}).get(
            "require_sections", []
        )

        for section in required_sections:
            # 检查是否包含必需的章节标题
            pattern = rf"^#+\s+{re.escape(section)}"
            if not re.search(pattern, content, re.MULTILINE):
                self.errors.append(f"缺少必需章节: {section}")

    def _validate_content(self, content: str):
        """验证内容"""
        content_validation = self.rule_config.get("content_validation", {})

        # 检查最小长度
        if "min_length" in content_validation:
            min_length = content_validation["min_length"]
            # 排除Frontmatter
            parts = content.split("---", 2)
            body_content = parts[2] if len(parts) > 2 else content
            if len(body_content.strip()) < min_length:
                self.warnings.append(
                    f"内容长度不足: 当前 {len(body_content.strip())} 字符，"
                    f"建议至少 {min_length} 字符"
                )

        # 检查测试用例
        if content_validation.get("require_test_cases", False):
            if "测试用例" not in content and "test case" not in content.lower():
                self.warnings.append("建议包含测试用例部分")
