#!/usr/bin/env python3
"""
测试用例CSV文件合规检查器
验证测试用例设计文件的完整性和格式
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Tuple


class TestCaseChecker:
    """测试用例CSV文件检查器"""

    # 必填字段
    REQUIRED_FIELDS = [
        "用例ID",
        "用例名称",
        "测试类型",
        "优先级",
        "关联REQ-ID",
        "关联功能点",
        "测试场景",
        "前置条件",
        "测试步骤",
        "预期结果",
    ]

    # 有效的测试类型
    VALID_TEST_TYPES = ["UNIT", "INTEGRATION", "E2E", "REGRESSION"]

    # 有效的优先级
    VALID_PRIORITIES = ["P0", "P1", "P2", "P3"]

    # 用例ID格式（新格式：TC-{MODULE}_{FEATURE}-{序号}，兼容旧格式：TC-{MODULE}-{序号}）
    TESTCASE_ID_PATTERN = r"^TC-[A-Z]+(_[A-Z]+)?-\d{3}$"

    # REQ-ID格式
    REQ_ID_PATTERN = r"^REQ-\d{4}-\d{3}(-[a-z0-9-]+)?$"

    def __init__(self, rule_config: Dict):
        self.rule_config = rule_config
        self.errors = []
        self.warnings = []

    def check(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查测试用例CSV文件

        Args:
            file_path: CSV文件路径

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        path = Path(file_path)

        # 检查文件是否存在
        if not path.exists():
            self.errors.append(f"文件不存在: {file_path}")
            return False, self.errors, self.warnings

        # 检查文件扩展名
        if path.suffix.lower() != ".csv":
            self.errors.append(f"文件必须是CSV格式: {file_path}")
            return False, self.errors, self.warnings

        # 检查文件命名
        self._check_naming(file_path)

        # 检查文件内容
        self._check_content(file_path)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_naming(self, file_path: str):
        """检查文件命名"""
        filename = Path(file_path).name
        # 强制统一命名：{REQ-ID}-test-cases.csv
        if not re.match(
            r"^REQ-\d{4}-\d{3}(-[a-z0-9-]+)?-test-cases\.csv$",
            filename,
            re.IGNORECASE,
        ):
            self.errors.append(
                "测试用例文件命名不符合规范：必须为 {REQ-ID}-test-cases.csv "
                "(示例：REQ-2025-003-user-login-test-cases.csv)"
            )

    def _check_content(self, file_path: str):
        """检查CSV文件内容"""
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)

                # 检查表头
                if reader.fieldnames is None:
                    self.errors.append("CSV文件为空或格式错误")
                    return

                # 检查必填字段
                missing_fields = []
                for field in self.REQUIRED_FIELDS:
                    if field not in reader.fieldnames:
                        missing_fields.append(field)

                if missing_fields:
                    self.errors.append(f"缺少必填字段: {', '.join(missing_fields)}")

                # 检查每行数据
                row_count = 0
                p0_count = 0
                testcase_ids = set()

                # 从文件名推导REQ-ID，强制每行一致
                filename = Path(file_path).name
                req_id_match = re.match(
                    r"^(REQ-\d{4}-\d{3}(?:-[a-z0-9-]+)?)-test-cases\.csv$",
                    filename,
                    re.IGNORECASE,
                )
                expected_req_id = req_id_match.group(1) if req_id_match else None
                for row_num, row in enumerate(reader, start=2):  # 从第2行开始（第1行是表头）
                    row_count += 1
                    self._check_row(row, row_num)

                    # 统计P0用例数量
                    if row.get("优先级") == "P0":
                        p0_count += 1

                    # 用例ID唯一性检查
                    tc_id = (row.get("用例ID") or "").strip()
                    if tc_id:
                        if tc_id in testcase_ids:
                            self.errors.append(f"第{row_num}行: 用例ID重复: {tc_id}")
                        testcase_ids.add(tc_id)

                    # 关联REQ-ID一致性检查
                    if expected_req_id:
                        row_req = (row.get("关联REQ-ID") or "").strip()
                        if row_req and row_req.lower() != expected_req_id.lower():
                            self.errors.append(
                                f"第{row_num}行: 关联REQ-ID与文件REQ-ID不一致 "
                                f"(期望 {expected_req_id}, 实际 {row_req})"
                            )

                # 检查用例数量
                if row_count == 0:
                    self.errors.append("CSV文件没有测试用例数据")
                else:
                    min_cfg = self.rule_config.get("min_testcases", {})
                    min_total = int(min_cfg.get("total", 5))
                    if row_count < min_total:
                        self.errors.append(f"测试用例数量不足：当前 {row_count}，最低要求 {min_total}")

                # 检查P0用例数量
                min_cfg = self.rule_config.get("min_testcases", {})
                min_p0 = int(min_cfg.get("p0", 1))
                if p0_count < min_p0:
                    self.errors.append(f"P0用例数量不足：当前 {p0_count}，最低要求 {min_p0}")

        except UnicodeDecodeError:
            self.errors.append("CSV文件编码错误，请使用UTF-8编码")
        except csv.Error as e:
            self.errors.append(f"CSV解析错误: {e}")
        except Exception as e:
            self.errors.append(f"读取文件失败: {e}")

    def _check_row(self, row: Dict, row_num: int):
        """检查单行数据"""
        # 检查用例ID格式
        testcase_id = row.get("用例ID", "").strip()
        if testcase_id:
            if not re.match(self.TESTCASE_ID_PATTERN, testcase_id):
                self.warnings.append(
                    f"第{row_num}行: 用例ID格式建议使用 TC-{{MODULE}}_{{FEATURE}}-{{序号}} "
                    f"(如 TC-AUTH_LOGIN-001) 或 TC-{{MODULE}}-{{序号}} (如 TC-AUTH-001)"
                )
            # 检查是否使用旧格式（建议迁移到新格式）
            elif re.match(r"^TC-[A-Z]+-\d{3}$", testcase_id) and "_" not in testcase_id:
                self.warnings.append(
                    f"第{row_num}行: 用例ID使用旧格式，建议升级为 TC-{{MODULE}}_{{FEATURE}}-{{序号}} "
                    f"(当前: {testcase_id})"
                )

        # 检查测试类型
        test_type = row.get("测试类型", "").strip().upper()
        if test_type and test_type not in self.VALID_TEST_TYPES:
            self.errors.append(
                f"第{row_num}行: 无效的测试类型 '{test_type}'，应为 {self.VALID_TEST_TYPES}"
            )

        # 检查优先级
        priority = row.get("优先级", "").strip().upper()
        if priority and priority not in self.VALID_PRIORITIES:
            self.errors.append(
                f"第{row_num}行: 无效的优先级 '{priority}'，应为 {self.VALID_PRIORITIES}"
            )

        # 检查关联REQ-ID格式
        req_id = row.get("关联REQ-ID", "").strip()
        if req_id and not re.match(self.REQ_ID_PATTERN, req_id):
            self.warnings.append(f"第{row_num}行: REQ-ID格式建议使用 REQ-YYYY-NNN[-slug]")

        # 检查必填字段是否为空
        for field in self.REQUIRED_FIELDS:
            value = row.get(field, "").strip()
            if not value:
                self.warnings.append(f"第{row_num}行: 必填字段 '{field}' 为空")

        # 检查测试步骤格式
        test_steps = row.get("测试步骤", "").strip()
        if test_steps and not re.search(r"\d+\.", test_steps):
            self.warnings.append(f"第{row_num}行: 测试步骤建议使用编号格式 (如 1.xxx 2.xxx)")


def check_testcase_file_exists(prd_path: str) -> Tuple[bool, List[str], List[str]]:
    """
    检查PRD对应的测试用例文件是否存在

    Args:
        prd_path: PRD文件路径

    Returns:
        (是否存在, 错误列表, 警告列表)
    """
    errors = []
    warnings = []

    prd_dir = Path(prd_path).parent
    prd_name = Path(prd_path).stem  # 不含扩展名

    # 提取REQ-ID
    req_id_match = re.match(r"(REQ-\d{4}-\d{3}(-[a-z0-9-]+)?)", prd_name, re.IGNORECASE)
    if not req_id_match:
        warnings.append(f"无法从PRD文件名中提取REQ-ID: {prd_name}")
        return True, errors, warnings

    req_id = req_id_match.group(1)

    # 检查测试用例文件是否存在
    possible_names = [
        f"{req_id}-test-cases.csv",
        f"{req_id}-testcases.csv",
        f"{prd_name}-test-cases.csv",
        f"{prd_name}-testcases.csv",
    ]

    testcase_file_exists = False
    for name in possible_names:
        testcase_path = prd_dir / name
        if testcase_path.exists():
            testcase_file_exists = True
            break

    if not testcase_file_exists:
        warnings.append(f"建议创建测试用例文件: {prd_dir}/{req_id}-test-cases.csv")

    return True, errors, warnings
