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
        """验证元数据（增强版）"""
        # 保存metadata供其他方法使用
        self.metadata = metadata

        required_fields = self.rule_config.get("required_metadata_fields", [])
        validation_rules = self.rule_config.get("metadata_validation", {})

        # 检查必需字段
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"缺少必需字段: {field}")

        # 验证PRD状态（T09: PRD状态为draft时不允许开发）
        status = metadata.get("status", "").lower()
        if status == "draft":
            self.errors.append(
                "PRD状态为 'draft'，必须先审核通过（状态改为 'approved'）才能开始开发。\n"
                "PRD审核流程：draft（草稿）→ review（审核中）→ approved（已批准）"
            )
        elif status not in ["approved", "review", "draft", "archived"]:
            self.warnings.append(
                f"PRD状态 '{status}' 不在标准状态列表中：draft, review, approved, archived"
            )

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
        """验证内容（增强版）"""
        content_validation = self.rule_config.get("content_validation", {})

        # 1. 原有检查：最小长度
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

        # 2. 新增：推荐章节检查
        recommended_sections = content_validation.get("recommended_sections", [])
        for section_config in recommended_sections:
            section_name = section_config["name"]
            level = section_config.get("level", "warning")
            applicable = self._is_section_applicable(section_config)

            if not applicable:
                continue

            # 检查章节是否存在
            pattern = rf"^#+\s+{re.escape(section_name)}"
            if not re.search(pattern, content, re.MULTILINE):
                message = (
                    f"建议添加章节：{section_name}\n" f"说明：{section_config['description']}"
                )
                if level == "error":
                    self.errors.append(message)
                else:
                    self.warnings.append(message)

        # 3. 新增：章节详细度检查
        section_requirements = content_validation.get("section_detail_requirements", {})
        for section_name, requirements in section_requirements.items():
            # 检查章节是否适用
            if "applicable_when" in requirements:
                if not self._is_section_applicable(requirements):
                    continue
            self._check_section_detail(content, section_name, requirements)

        # 4. 原有检查：测试用例
        if content_validation.get("require_test_cases", False):
            if "测试用例" not in content and "test case" not in content.lower():
                self.warnings.append("建议包含测试用例部分")

    def _is_section_applicable(self, section_config: dict) -> bool:
        """
        判断章节是否适用于当前PRD

        Args:
            section_config: 章节配置

        Returns:
            是否适用
        """
        applicable_when = section_config.get("applicable_when", [])

        if not applicable_when:
            return True  # 没有条件限制，总是适用

        # 检查条件（从metadata中获取）
        if not hasattr(self, "metadata"):
            return True  # 如果没有metadata，默认适用

        for condition in applicable_when:
            pattern = condition["pattern"]
            field = condition["in_field"]

            if field in self.metadata:
                field_value = str(self.metadata[field])
                if re.search(pattern, field_value, re.IGNORECASE):
                    return True

        return False

    def _check_section_detail(
        self, content: str, section_name: str, requirements: dict
    ):
        """
        检查章节内容详细度

        Args:
            content: PRD文件内容
            section_name: 章节名称
            requirements: 详细度要求
        """
        # 提取章节内容
        section_pattern = rf"^#+\s+{re.escape(section_name)}\s*$(.*?)(?=^#+\s+|\Z)"
        match = re.search(section_pattern, content, re.MULTILINE | re.DOTALL)

        if not match:
            return  # 章节不存在，由其他检查处理

        section_content = match.group(1)

        # 检查关键词
        if "require_keywords" in requirements:
            keywords = requirements["require_keywords"]
            missing_keywords = []

            for keyword in keywords:
                if keyword not in section_content:
                    missing_keywords.append(keyword)

            if missing_keywords:
                self.warnings.append(
                    f"章节 '{section_name}' 建议包含关键内容：{', '.join(missing_keywords)}\n"
                    f"格式建议：{requirements.get('format', '描述性文本')}"
                )

        # 检查最小项目数（用于列表类章节）
        if "min_items" in requirements:
            min_items = requirements["min_items"]
            # 统计列表项（- 或 1. 开头）
            list_items = re.findall(r"^\s*[-\d]+\.", section_content, re.MULTILINE)

            if len(list_items) < min_items:
                self.warnings.append(
                    f"章节 '{section_name}' 建议至少包含 {min_items} 条内容，"
                    f"当前只有 {len(list_items)} 条\n"
                    f"说明：{requirements.get('description', '')}"
                )
