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

        # ⭐ 阶段1：双向关联检查
        self._check_bidirectional_links(file_path, metadata)

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

    def _check_bidirectional_links(self, prd_path: str, metadata: Dict):
        """
        ⭐ 阶段1：双向关联检查
        1. PRD中列出的test_files和implementation_files是否存在
        2. 这些文件中的REQ-ID注释是否匹配PRD的req_id
        3. PRD的req_id是否在tasks.json中存在对应的任务组
        """
        req_id = metadata.get("req_id", "")
        if not req_id:
            return  # 没有req_id无法检查

        # 查找项目根目录
        prd_path_obj = Path(prd_path)
        project_root = None

        # 尝试多个可能的项目根目录
        possible_roots = [
            prd_path_obj,
            *list(prd_path_obj.parents),
            Path("/app"),  # 容器内项目根目录
            Path.cwd(),  # 当前工作目录
        ]

        for parent in possible_roots:
            if (parent / "docs" / "00_product" / "requirements").exists():
                project_root = parent
                break

        if not project_root:
            self.warnings.append("无法定位项目根目录，跳过双向关联检查")
            return

        # 容器内特殊处理：检测Docker挂载结构
        # 如果/app/docs存在但/app/backend不存在，说明：
        # - /app = 宿主机 ./backend 目录
        # - /app/docs = 宿主机 ./docs 目录
        # 所以PRD中声明的 backend/xxx 路径在容器内应该是 /app/xxx
        is_container_env = (
            Path("/app/docs").exists() and not Path("/app/backend").exists()
        )

        # 1. 检查test_files和implementation_files中的文件是否存在，并验证REQ-ID
        test_files = metadata.get("test_files", [])
        implementation_files = metadata.get("implementation_files", [])

        # 检查测试文件
        for test_file in test_files:
            # 容器内特殊处理：如果路径以backend/开头，去掉backend/前缀
            file_path_str = test_file
            if is_container_env and file_path_str.startswith("backend/"):
                file_path_str = file_path_str[8:]  # 去掉"backend/"前缀

            test_file_path = (
                project_root / file_path_str
                if not Path(file_path_str).is_absolute()
                else Path(file_path_str)
            )

            # 容器内特殊处理：如果project_root是/app/docs的父目录，但文件路径是backend/xxx
            # 需要尝试 /app/xxx（因为/app是backend目录）
            if not test_file_path.exists() and is_container_env:
                if test_file.startswith("backend/"):
                    alt_path = Path("/app") / test_file[8:]
                    if alt_path.exists():
                        test_file_path = alt_path
                # e2e和frontend文件不在backend容器内，跳过检查
                elif test_file.startswith("e2e/") or test_file.startswith("frontend/"):
                    continue

            if not test_file_path.exists():
                self.errors.append(f"PRD中声明的测试文件不存在: {test_file}")
                continue

            # 检查文件中的REQ-ID是否匹配
            try:
                content = test_file_path.read_text(encoding="utf-8", errors="ignore")
                # 提取REQ-ID（检查前20行）
                lines = content.split("\n")[:20]
                file_req_id = None
                for line in lines:
                    match = re.search(
                        r"REQ-\d{4}-\d{3}(-[a-z0-9-]+)?", line, re.IGNORECASE
                    )
                    if match:
                        file_req_id = match.group(0)
                        break

                if not file_req_id:
                    self.errors.append(f"测试文件 {test_file} 缺少REQ-ID注释，无法验证关联性")
                elif file_req_id.upper() != req_id.upper():
                    self.errors.append(
                        f"测试文件 {test_file} 中的REQ-ID ({file_req_id}) "
                        f"与PRD的req_id ({req_id}) 不匹配"
                    )
            except Exception as e:
                self.warnings.append(f"无法读取测试文件 {test_file} 以验证REQ-ID: {e}")

        # 检查实现文件
        for impl_file in implementation_files:
            # 容器内特殊处理：如果路径以backend/开头，去掉backend/前缀
            file_path_str = impl_file
            if is_container_env and file_path_str.startswith("backend/"):
                file_path_str = file_path_str[8:]  # 去掉"backend/"前缀

            impl_file_path = (
                project_root / file_path_str
                if not Path(file_path_str).is_absolute()
                else Path(file_path_str)
            )

            # 容器内特殊处理：如果project_root是/app/docs的父目录，但文件路径是backend/xxx
            # 需要尝试 /app/xxx（因为/app是backend目录）
            if not impl_file_path.exists() and is_container_env:
                if impl_file.startswith("backend/"):
                    alt_path = Path("/app") / impl_file[8:]
                    if alt_path.exists():
                        impl_file_path = alt_path
                # e2e和frontend文件不在backend容器内，跳过检查
                elif impl_file.startswith("e2e/") or impl_file.startswith("frontend/"):
                    continue

            if not impl_file_path.exists():
                self.errors.append(f"PRD中声明的实现文件不存在: {impl_file}")
                continue

            # 检查文件中的REQ-ID是否匹配
            try:
                content = impl_file_path.read_text(encoding="utf-8", errors="ignore")
                # 提取REQ-ID（检查前20行）
                lines = content.split("\n")[:20]
                file_req_id = None
                for line in lines:
                    match = re.search(
                        r"REQ-\d{4}-\d{3}(-[a-z0-9-]+)?", line, re.IGNORECASE
                    )
                    if match:
                        file_req_id = match.group(0)
                        break

                if not file_req_id:
                    self.errors.append(f"实现文件 {impl_file} 缺少REQ-ID注释，无法验证关联性")
                elif file_req_id.upper() != req_id.upper():
                    self.errors.append(
                        f"实现文件 {impl_file} 中的REQ-ID ({file_req_id}) "
                        f"与PRD的req_id ({req_id}) 不匹配"
                    )
            except Exception as e:
                self.warnings.append(f"无法读取实现文件 {impl_file} 以验证REQ-ID: {e}")

        # 2. 检查PRD的req_id是否在tasks.json中存在对应的任务组
        tasks_json_path = project_root / ".taskmaster" / "tasks" / "tasks.json"
        if tasks_json_path.exists():
            try:
                import json

                with open(tasks_json_path, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)

                # 检查是否有对应的REQ-ID任务组
                if req_id not in tasks_data:
                    self.warnings.append(
                        f"PRD的req_id ({req_id}) 在tasks.json中不存在对应的任务组。"
                        f"请运行 'task-master parse-prd' 生成任务。"
                    )
                else:
                    # 检查任务组中是否有任务
                    req_tasks = tasks_data.get(req_id, {}).get("tasks", [])
                    if not req_tasks:
                        self.warnings.append(
                            f"PRD的req_id ({req_id}) 在tasks.json中存在，但没有任务。"
                            f"请运行 'task-master parse-prd' 生成任务。"
                        )
            except Exception as e:
                self.warnings.append(f"无法读取tasks.json以验证任务关联: {e}")
        else:
            self.warnings.append(f"tasks.json文件不存在，无法验证PRD与任务的关联: {tasks_json_path}")
