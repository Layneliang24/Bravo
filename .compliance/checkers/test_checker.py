#!/usr/bin/env python3
"""
测试文件合规检查器
验证测试文件的命名、位置和内容
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml


class TestChecker:
    """测试文件检查器"""

    def __init__(self, rule_config: Dict):
        self.rule_config = rule_config
        self.errors = []
        self.warnings = []

    def check(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查测试文件

        Args:
            file_path: 测试文件路径

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        path = Path(file_path)
        file_from_git = False

        # 如果文件不存在，尝试从git暂存区读取（pre-commit阶段）
        if not path.exists():
            import subprocess

            # 尝试多个可能的git工作目录
            git_dirs = ["/app", str(Path.cwd()), str(Path.cwd().parent)]
            for git_dir in git_dirs:
                git_path = Path(git_dir) / ".git"
                if git_path.exists():
                    try:
                        # 配置git safe.directory（避免权限问题）
                        subprocess.run(
                            [
                                "git",
                                "config",
                                "--global",
                                "--add",
                                "safe.directory",
                                git_dir,
                            ],
                            capture_output=True,
                            check=False,
                            cwd=git_dir,
                        )
                        # 使用git show获取暂存文件内容
                        # 如果是绝对路径，转换为相对路径（相对于git_dir）
                        git_file_path = file_path
                        if Path(file_path).is_absolute():
                            try:
                                git_file_path = str(
                                    Path(file_path).relative_to(Path(git_dir))
                                )
                            except ValueError:
                                # 如果无法转换为相对路径，尝试直接使用文件名
                                git_file_path = Path(file_path).name

                        result = subprocess.run(
                            ["git", "show", f":{git_file_path}"],
                            capture_output=True,
                            text=True,
                            check=False,
                            cwd=git_dir,
                        )
                        if result.returncode == 0:
                            # 文件在git暂存区中，可以继续检查
                            file_from_git = True
                            break
                    except (FileNotFoundError, subprocess.SubprocessError):
                        continue

            if not file_from_git:
                self.errors.append(f"文件不存在: {file_path}")
                return False, self.errors, self.warnings

        # 检查文件位置
        self._check_location(file_path)

        # 检查文件命名
        self._check_naming(file_path)

        # 检查文件内容（如果从git读取，需要特殊处理）
        if file_from_git:
            self._check_content_from_git(file_path)
        else:
            self._check_content(file_path)

        return len(self.errors) == 0, self.errors, self.warnings

    def _find_project_root(self, file_path: str) -> Optional[Path]:
        """
        尝试从当前文件路径向上寻找项目根目录（以 docs/00_product/requirements 为锚点）
        """
        p = Path(file_path).resolve()
        for parent in [p] + list(p.parents):
            if (parent / "docs" / "00_product" / "requirements").exists():
                return parent
        # 兜底：当前工作目录
        cwd = Path.cwd().resolve()
        if (cwd / "docs" / "00_product" / "requirements").exists():
            return cwd
        return None

    def _extract_req_id_from_text(self, text: str) -> Optional[str]:
        m = re.search(r"REQ-\d{4}-\d{3}(?:-[a-z0-9-]+)?", text, re.IGNORECASE)
        return m.group(0) if m else None

    def _enforce_testcase_gate(self, file_path: str, content: str):
        """
        V4.1 强制门禁：
        - 提交测试代码时，必须已经存在对应的测试用例CSV
        - 且 PRD 中 testcase_status.reviewed 必须为 true
        """
        req_id = self._extract_req_id_from_text(
            content
        ) or self._extract_req_id_from_text(str(file_path))
        if not req_id:
            # 没有REQ-ID无法做追溯校验，交给其他规则/警告处理
            return

        project_root = self._find_project_root(file_path)
        if not project_root:
            self.warnings.append(f"无法定位项目根目录，跳过测试用例CSV门禁校验（REQ-ID: {req_id}）")
            return

        prd_path = (
            project_root
            / "docs"
            / "00_product"
            / "requirements"
            / req_id
            / f"{req_id}.md"
        )
        testcase_csv = (
            project_root
            / "docs"
            / "00_product"
            / "requirements"
            / req_id
            / f"{req_id}-test-cases.csv"
        )

        if not testcase_csv.exists():
            self.errors.append(f"缺少测试用例CSV文件（V4.1强制）：{testcase_csv.as_posix()}")
            return

        if not prd_path.exists():
            self.errors.append(f"缺少PRD文件，无法验证测试用例评审状态：{prd_path.as_posix()}")
            return

        try:
            prd_content = prd_path.read_text(encoding="utf-8")
            parts = prd_content.split("---", 2)
            if len(parts) < 3:
                self.errors.append(f"PRD frontmatter格式错误：{prd_path.as_posix()}")
                return
            meta = yaml.safe_load(parts[1]) or {}
            status = str(meta.get("status", "")).lower()
            if status not in ["approved", "implementing", "completed"]:
                self.errors.append(
                    f"PRD状态为 '{status}'，不允许提交测试代码"
                    f"（需 approved/implementing）：{prd_path.as_posix()}"
                )
                return

            tc_status = meta.get("testcase_status") or {}
            reviewed = bool(tc_status.get("reviewed"))
            if not reviewed:
                self.errors.append(
                    "测试用例CSV未评审通过（testcase_status.reviewed != true），不允许提交测试代码"
                )
                return

            # reviewed=true 后进一步强化：测试代码必须引用至少一个TC-xxx-000，并且必须存在于CSV中
            testcase_file_path = meta.get("testcase_file") or testcase_csv.as_posix()
            # 允许PRD里写相对路径
            tc_csv_path = Path(str(testcase_file_path))
            if not tc_csv_path.is_absolute():
                tc_csv_path = project_root / tc_csv_path
            if not tc_csv_path.exists():
                self.errors.append(
                    f"PRD声明的testcase_file不存在，无法校验TestCase-ID引用：{tc_csv_path.as_posix()}"
                )
                return

            # 解析测试文件中的TestCase-ID引用
            # （支持新格式 TC-{MODULE}_{FEATURE}-{序号} 和旧格式 TC-{MODULE}-{序号}）
            # 使用非捕获组或直接匹配整个ID
            referenced_tc_ids = set(
                re.findall(r"TC-[A-Z0-9]+(?:_[A-Z0-9]+)?-\d{3}", content)
            )
            if not referenced_tc_ids:
                self.errors.append(
                    "测试文件缺少TestCase-ID引用"
                    "（示例：TESTCASE-IDS: TC-AUTH_LOGIN-001 或 TC-AUTH-001）。"
                    "当测试用例已评审通过后，测试代码必须显式引用CSV中的用例ID。"
                )
                return

            # 读取CSV中的用例ID集合
            import csv

            csv_ids = set()
            try:
                with open(tc_csv_path, "r", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    if not reader.fieldnames or "用例ID" not in reader.fieldnames:
                        self.errors.append(
                            f"测试用例CSV缺少'用例ID'列，无法校验：{tc_csv_path.as_posix()}"
                        )
                        return
                    for row in reader:
                        tc_id = (row.get("用例ID") or "").strip()
                        if tc_id:
                            csv_ids.add(tc_id)
            except Exception as e:
                self.errors.append(f"读取测试用例CSV失败：{tc_csv_path.as_posix()}，错误：{e}")
                return

            missing = sorted([tc for tc in referenced_tc_ids if tc not in csv_ids])
            if missing:
                self.errors.append(
                    "测试文件引用了不存在的TestCase-ID："
                    + ", ".join(missing[:10])
                    + (f" ... 等{len(missing)}个" if len(missing) > 10 else "")
                )
        except Exception as e:
            self.errors.append(f"读取/解析PRD失败，无法验证测试用例评审状态: {e}")

    def _check_location(self, file_path: str):
        """检查文件位置"""
        location_rules = self.rule_config.get("location", {})

        # 判断文件类型
        if "backend/tests/unit/" in file_path:
            expected_location = location_rules.get("backend_unit", "")
            if expected_location and expected_location not in file_path:
                self.errors.append(f"单元测试文件应位于: {expected_location}")
        elif "backend/tests/integration/" in file_path:
            expected_location = location_rules.get("backend_integration", "")
            if expected_location and expected_location not in file_path:
                self.errors.append(f"集成测试文件应位于: {expected_location}")
        elif "backend/tests/regression/" in file_path:
            expected_location = location_rules.get("backend_regression", "")
            if expected_location and expected_location not in file_path:
                self.errors.append(f"回归测试文件应位于: {expected_location}")
        elif "e2e/tests/smoke/" in file_path:
            expected_location = location_rules.get("e2e_smoke", "")
            if expected_location and expected_location not in file_path:
                self.errors.append(f"冒烟测试文件应位于: {expected_location}")
        elif "e2e/tests/regression/" in file_path:
            expected_location = location_rules.get("e2e_regression", "")
            if expected_location and expected_location not in file_path:
                self.errors.append(f"E2E回归测试文件应位于: {expected_location}")
        elif "e2e/tests/performance/" in file_path:
            expected_location = location_rules.get("e2e_performance", "")
            if expected_location and expected_location not in file_path:
                self.errors.append(f"性能测试文件应位于: {expected_location}")

    def _check_naming(self, file_path: str):
        """检查文件命名"""
        naming_rules = self.rule_config.get("naming", {})
        filename = Path(file_path).name

        # 判断文件类型并检查命名
        if "backend/tests/unit/" in file_path:
            pattern = naming_rules.get("backend_unit", "test_{module}.py")
            if not re.match(r"^test_.+\.py$", filename):
                self.errors.append(f"单元测试文件命名错误: 应匹配 {pattern}")
        elif "backend/tests/integration/" in file_path:
            pattern = naming_rules.get("backend_integration", "test_{feature}.py")
            if not re.match(r"^test_.+\.py$", filename):
                self.errors.append(f"集成测试文件命名错误: 应匹配 {pattern}")
        elif "backend/tests/regression/" in file_path:
            pattern = naming_rules.get("backend_regression", "test_{bug_id}.py")
            if not re.match(r"^test_.+\.py$", filename):
                self.errors.append(f"回归测试文件命名错误: 应匹配 {pattern}")
        elif "e2e/tests/" in file_path:
            pattern = naming_rules.get("e2e", "test-{feature}.spec.ts")
            if not re.match(r"^test-.+\.spec\.ts$", filename):
                self.errors.append(f"E2E测试文件命名错误: 应匹配 {pattern}")

    def _check_content_from_git(self, file_path: str):
        """从git暂存区检查文件内容"""
        import subprocess

        required_content = self.rule_config.get("required_content", [])

        # 尝试从git暂存区读取文件内容
        git_dirs = ["/app", str(Path.cwd()), str(Path.cwd().parent)]
        content = None
        for git_dir in git_dirs:
            git_path = Path(git_dir) / ".git"
            if git_path.exists():
                try:
                    # 如果是绝对路径，转换为相对路径（相对于git_dir）
                    git_file_path = file_path
                    if Path(file_path).is_absolute():
                        try:
                            git_file_path = str(
                                Path(file_path).relative_to(Path(git_dir))
                            )
                        except ValueError:
                            # 如果无法转换为相对路径，尝试直接使用文件名
                            git_file_path = Path(file_path).name

                    result = subprocess.run(
                        ["git", "show", f":{git_file_path}"],
                        capture_output=True,
                        text=True,
                        check=False,
                        cwd=git_dir,
                    )
                    if result.returncode == 0:
                        content = result.stdout
                        break
                except (FileNotFoundError, subprocess.SubprocessError):
                    continue

        if content is None:
            self.errors.append(f"无法从git暂存区读取文件: {file_path}")
            return

        # V4.1：测试用例CSV门禁
        self._enforce_testcase_gate(file_path, content)

        # 检查测试函数定义
        if "test_function_definitions" in required_content:
            if file_path.endswith(".py"):
                # Python测试文件
                if not re.search(r"def\s+test_\w+", content):
                    self.errors.append("缺少测试函数定义（def test_*）")
            elif file_path.endswith(".ts"):
                # TypeScript测试文件
                if not re.search(r"(test|it)\(", content):
                    self.errors.append("缺少测试函数定义（test/it）")

        # 检查断言
        if "assertions" in required_content:
            if file_path.endswith(".py"):
                if not re.search(r"assert\s+", content):
                    self.warnings.append("建议包含断言语句")
            elif file_path.endswith(".ts"):
                if not re.search(r"expect\(", content):
                    self.warnings.append("建议包含expect断言")

        # 检查文档字符串
        if "test_docstrings" in required_content:
            if file_path.endswith(".py"):
                if not re.search(r'""".*"""', content, re.DOTALL):
                    self.warnings.append("建议为测试函数添加文档字符串")

    def _check_content(self, file_path: str):
        """检查文件内容"""
        required_content = self.rule_config.get("required_content", [])

        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(f"无法读取文件: {e}")
            return

        # V4.1：测试用例CSV门禁
        self._enforce_testcase_gate(file_path, content)

        # 检查测试函数定义
        if "test_function_definitions" in required_content:
            if file_path.endswith(".py"):
                # Python测试文件
                if not re.search(r"def\s+test_\w+", content):
                    self.errors.append("缺少测试函数定义（def test_*）")
            elif file_path.endswith(".ts"):
                # TypeScript测试文件
                if not re.search(r"(test|it)\(", content):
                    self.errors.append("缺少测试函数定义（test/it）")

        # 检查断言
        if "assertions" in required_content:
            if file_path.endswith(".py"):
                if not re.search(r"assert\s+", content):
                    self.warnings.append("建议包含断言语句")
            elif file_path.endswith(".ts"):
                if not re.search(r"expect\(", content):
                    self.warnings.append("建议包含expect断言")

        # 检查文档字符串
        if "test_docstrings" in required_content:
            if file_path.endswith(".py"):
                if not re.search(r'""".*"""', content, re.DOTALL):
                    self.warnings.append("建议为测试函数添加文档字符串")
