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

        # 使用split检查是否有完整的frontmatter结构
        parts = content.split("---", 2)
        if len(parts) < 3:
            self.errors.append("Frontmatter格式错误：缺少结束标记")
            return False

        # 检查frontmatter内容不为空
        if not parts[1].strip():
            self.errors.append("Frontmatter内容为空")
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

        # 验证PRD状态（状态机管理）
        status = metadata.get("status", "").lower()

        # 从配置中读取有效状态列表
        status_validation = self.rule_config.get("metadata_validation", {}).get(
            "status", {}
        )
        valid_states = status_validation.get(
            "enum",
            ["draft", "review", "approved", "implementing", "completed", "archived"],
        )

        # 检查1：状态必须是有效值
        if status not in valid_states:
            self.errors.append(
                f"❌ PRD状态 '{status}' 无效\n"
                f"有效状态：{', '.join(valid_states)}\n\n"
                f"📋 PRD状态机流程：\n"
                f"  draft → review → approved → implementing → completed → archived"
            )
            return

        # V4.1：测试用例设计与评审元数据校验
        # - draft/review：允许不完整，但会给出警告，便于迁移
        # - approved/implementing/completed：必须完整（否则阻止进入实现阶段）
        must_have_testcase_meta = status in ["approved", "implementing", "completed"]

        if "testcase_file" not in metadata or not metadata.get("testcase_file"):
            msg = "缺少测试用例清单字段 testcase_file（应指向 {REQ-ID}-test-cases.csv）"
            if must_have_testcase_meta:
                self.errors.append(msg)
            else:
                self.warnings.append(msg)
        else:
            testcase_file = metadata.get("testcase_file")
            if testcase_file and not str(testcase_file).endswith(".csv"):
                self.warnings.append("testcase_file 应该是一个 .csv 文件")

        if "testcase_status" not in metadata or metadata.get("testcase_status") is None:
            msg = "缺少测试用例状态字段 testcase_status（需包含 reviewed/reviewed_by/reviewed_at 等）"
            if must_have_testcase_meta:
                self.errors.append(msg)
            else:
                self.warnings.append(msg)
        else:
            tc_status = metadata.get("testcase_status")
            if not isinstance(tc_status, dict):
                self.errors.append("testcase_status 必须是字典格式")
            else:
                # 强化：implementing/completed 状态必须评审通过
                if (
                    status in ["implementing", "completed"]
                    and tc_status.get("reviewed") is not True
                ):
                    self.errors.append(
                        "PRD状态为 implementing/completed 时，测试用例必须评审通过 "
                        "(testcase_status.reviewed=true)"
                    )
                if tc_status.get("reviewed") is True:
                    if not tc_status.get("reviewed_by"):
                        self.warnings.append("测试用例已评审通过，但未记录评审人 (reviewed_by)")
                    if not tc_status.get("reviewed_at"):
                        self.warnings.append("测试用例已评审通过，但未记录评审时间 (reviewed_at)")

        # 检查2：draft状态不允许开发
        if status == "draft":
            self.errors.append(
                "❌ PRD状态为 'draft'（草稿），不允许开始开发\n\n"
                "📋 开发前必须完成以下步骤：\n"
                "  1. 完善PRD内容\n"
                "  2. 提交审核：将status改为 'review'\n"
                "  3. 审核通过：将status改为 'approved'\n"
                "  4. 解析任务：运行 task-master parse-prd\n"
                "  5. 开始开发：status自动变为 'implementing'\n\n"
                "⚠️  状态转换只能人工修改，不能自动修改（除了approved→implementing）"
            )

        # 检查3：review状态警告（允许修改PRD，但不允许提交实现代码）
        elif status == "review":
            self.warnings.append(
                "⚠️ PRD状态为 'review'（审核中）\n\n"
                "📋 当前可以做的：\n"
                "  ✅ 修改PRD文件本身（完善需求）\n"
                "  ❌ 提交implementation_files中的代码\n\n"
                "🔄 审核通过后，将status改为 'approved'，然后运行 task-master parse-prd"
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
                elif expected_type == "dict" and not isinstance(value, dict):
                    self.errors.append(f"字段 {field} 必须是字典类型")
                elif expected_type == "string" and not isinstance(value, str):
                    self.errors.append(f"字段 {field} 必须是字符串类型")

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
