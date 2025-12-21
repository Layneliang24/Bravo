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

    # 类变量：记录已执行反向检查的REQ-ID，避免重复检查
    _reverse_checked_req_ids = set()

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
            # 使用统一的提取方法
            referenced_tc_ids = self._extract_testcase_ids_from_content(content)

            # 检查是否提取到用例ID
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

            # 正向检查：测试文件引用的ID是否在CSV中存在
            missing = sorted([tc for tc in referenced_tc_ids if tc not in csv_ids])
            if missing:
                self.errors.append(
                    "测试文件引用了不存在的TestCase-ID："
                    + ", ".join(missing[:10])
                    + (f" ... 等{len(missing)}个" if len(missing) > 10 else "")
                )

            # ⭐ 新增：反向检查 - CSV中的用例是否都在测试代码中实现
            # 需要检查PRD中声明的所有test_files，提取所有用例ID
            # ⚠️ 重要：反向检查应该只执行一次（针对每个REQ-ID），避免重复报错
            # 使用类变量记录已检查的REQ-ID，确保每个REQ-ID只检查一次
            test_files = meta.get("test_files", [])
            if test_files:
                # 检查是否已经为这个REQ-ID执行过反向检查
                if req_id in TestChecker._reverse_checked_req_ids:
                    # 已经检查过，跳过反向检查（避免重复报错）
                    # 但仍然执行阶段2的检查（文件是否在PRD列表中、REQ-ID是否在tasks.json中）
                    self._check_file_in_prd_test_files(
                        file_path, req_id, project_root, meta
                    )
                    self._check_req_id_in_tasks_json(file_path, req_id, project_root)
                    return

                # 标记这个REQ-ID已经执行过反向检查
                TestChecker._reverse_checked_req_ids.add(req_id)

                # 获取当前文件的绝对路径（用于比较）
                try:
                    current_file_abs = Path(file_path).resolve()
                except Exception:
                    # 如果无法解析，使用原始路径
                    current_file_abs = Path(file_path)

                # 容器内特殊处理：检测Docker挂载结构
                is_container_env = (
                    Path("/app/docs").exists() and not Path("/app/backend").exists()
                )

                all_code_case_ids = set(referenced_tc_ids)  # 当前文件的用例ID

                # 从PRD声明的其他测试文件中提取用例ID
                for test_file in test_files:
                    # 容器内特殊处理：根据文件路径前缀确定实际路径
                    file_path_str = test_file
                    if is_container_env:
                        if file_path_str.startswith("backend/"):
                            # backend文件：去掉backend/前缀，在/app下
                            file_path_str = file_path_str[8:]  # 去掉"backend/"前缀
                        elif file_path_str.startswith("e2e/"):
                            # e2e文件：保持e2e/前缀，在/app/e2e下
                            # 不需要修改，直接使用
                            pass
                        elif file_path_str.startswith("frontend/"):
                            # frontend文件：保持frontend/前缀，在/app/frontend下
                            # 不需要修改，直接使用
                            pass

                    # 处理相对路径和绝对路径
                    if Path(file_path_str).is_absolute():
                        test_file_path = Path(file_path_str)
                    else:
                        # 容器内特殊处理：根据文件类型选择正确的根目录
                        if is_container_env:
                            if test_file.startswith("backend/"):
                                # backend文件：相对于/app
                                test_file_path = Path("/app") / file_path_str
                            elif test_file.startswith("e2e/"):
                                # e2e文件：相对于/app/e2e
                                test_file_path = Path("/app") / test_file
                            elif test_file.startswith("frontend/"):
                                # frontend文件：相对于/app/frontend
                                test_file_path = Path("/app") / test_file
                            else:
                                # 其他文件：使用project_root
                                test_file_path = project_root / file_path_str
                        else:
                            # 非容器环境：使用project_root
                            test_file_path = project_root / file_path_str

                    # 容器内特殊处理：如果project_root是/app，但文件路径是backend/xxx
                    # 需要尝试 /app/xxx（因为/app是backend目录）
                    if not test_file_path.exists() and is_container_env:
                        if test_file.startswith("backend/"):
                            alt_path = Path("/app") / test_file[8:]
                            if alt_path.exists():
                                test_file_path = alt_path

                    # 检查是否是当前文件（需要处理相对路径和绝对路径）
                    try:
                        test_file_resolved = test_file_path.resolve()
                        if test_file_resolved == current_file_abs:
                            # 是当前文件，跳过（已经在referenced_tc_ids中）
                            continue
                    except Exception:
                        # 如果无法解析路径，继续尝试读取
                        pass

                    if test_file_path.exists():
                        try:
                            other_content = test_file_path.read_text(encoding="utf-8")
                            # 使用统一的提取方法
                            other_ids = self._extract_testcase_ids_from_content(
                                other_content
                            )
                            all_code_case_ids.update(other_ids)
                        except Exception:
                            # 如果无法读取其他文件，跳过（可能是权限问题）
                            pass

                # 检查CSV中是否有用例未在代码中实现
                missing_in_code = sorted(
                    [tc for tc in csv_ids if tc not in all_code_case_ids]
                )
                if missing_in_code:
                    # 只显示前10个，避免输出过长
                    missing_display = missing_in_code[:10]
                    missing_msg = ", ".join(missing_display)
                    if len(missing_in_code) > 10:
                        missing_msg += f" ... 等{len(missing_in_code)}个"

                    # ⭐ 如果测试用例已评审通过（reviewed=true），反向检查应该更严格
                    # 因为评审通过意味着所有用例都应该实现，缺失用例是严重问题
                    if reviewed:
                        self.errors.append(
                            f"测试用例已评审通过，但CSV中有{len(missing_in_code)}个用例"
                            f"未在测试代码中实现：{missing_msg}。"
                            f"评审通过的用例必须全部实现，请补充缺失的测试代码。"
                        )
                    else:
                        # 如果还未评审通过，只发出警告
                        self.warnings.append(
                            f"CSV中有{len(missing_in_code)}个用例未在测试代码中实现：{missing_msg}。"
                            f"请确保所有用例都有对应的测试代码实现。"
                        )

                # ⭐ 阶段2：检查文件是否在PRD的test_files中
                self._check_file_in_prd_test_files(
                    file_path, req_id, project_root, meta
                )

                # ⭐ 阶段2：检查REQ-ID是否在tasks.json中
                self._check_req_id_in_tasks_json(file_path, req_id, project_root)
        except Exception as e:
            self.errors.append(f"读取/解析PRD失败，无法验证测试用例评审状态: {e}")

    def _extract_testcase_ids_from_content(self, content: str) -> set:
        """
        从文件内容中提取所有用例ID
        统一的提取逻辑，避免代码重复

        Args:
            content: 文件内容

        Returns:
            用例ID集合
        """
        case_ids = set()

        # 1. 匹配 TESTCASE-IDS 注释
        # 例如：TESTCASE-IDS: TC-AUTH_LOGIN-001, TC-AUTH_LOGIN-002
        pattern1 = r"TESTCASE-IDS:\s*([A-Z0-9_-]+(?:\s*,\s*[A-Z0-9_-]+)*)"
        matches1 = re.findall(pattern1, content, re.IGNORECASE)
        for match in matches1:
            ids = [id.strip() for id in match.split(",")]
            case_ids.update(ids)

        # 2. 匹配 test() 函数中的用例ID
        # 例如：test("TC-AUTH_LOGIN-001: 测试登录功能")
        pattern2 = r"test\(['\"]TC-([A-Z0-9_-]+):"
        matches2 = re.findall(pattern2, content)
        for match in matches2:
            case_ids.add(f"TC-{match}")

        # 3. 匹配 test() 函数中的用例ID（不带描述）
        # 例如：test("TC-AUTH_LOGIN-001")
        pattern3 = r"test\(['\"]TC-([A-Z0-9_-]+)['\"]"
        matches3 = re.findall(pattern3, content)
        for match in matches3:
            case_ids.add(f"TC-{match}")

        # 4. 匹配所有TC-XXX-001格式（兜底，匹配所有用例ID）
        pattern4 = r"TC-[A-Z0-9]+(?:_[A-Z0-9]+)?-\d{3}"
        matches4 = re.findall(pattern4, content)
        case_ids.update(matches4)

        return case_ids

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

    def _check_file_in_prd_test_files(
        self, file_path: str, req_id: str, project_root: Path, metadata: Dict
    ):
        """
        ⭐ 阶段2：检查文件是否在PRD的test_files中
        """
        test_files = metadata.get("test_files", [])

        # 容器内特殊处理：检测Docker挂载结构
        is_container_env = (
            Path("/app/docs").exists() and not Path("/app/backend").exists()
        )

        # 将文件路径转换为相对路径（相对于项目根目录）
        try:
            file_path_obj = Path(file_path)
            file_path_resolved = file_path_obj.resolve()
            project_root_resolved = project_root.resolve()

            # 容器内特殊处理：如果文件在/app下，需要转换为相对于项目根目录的路径
            if is_container_env and str(file_path_resolved).startswith("/app/"):
                # 尝试转换为backend/xxx格式（因为/app是backend目录）
                try:
                    # 检查是否是backend目录下的文件
                    if Path("/app/tests").exists() or Path("/app/apps").exists():
                        # /app是backend目录，需要转换为backend/xxx格式
                        relative_file_path = "backend/" + str(
                            file_path_resolved.relative_to(Path("/app"))
                        )
                    else:
                        relative_file_path = str(
                            file_path_resolved.relative_to(project_root_resolved)
                        )
                except ValueError:
                    relative_file_path = str(file_path_resolved)
            else:
                relative_file_path = str(
                    file_path_resolved.relative_to(project_root_resolved)
                )
        except (ValueError, AttributeError):
            # 如果无法转换为相对路径，使用原始路径
            relative_file_path = file_path

        # 检查文件是否在test_files中
        # 支持相对路径和绝对路径匹配
        file_found = False
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

            # 容器内特殊处理：如果project_root是/app，但文件路径是backend/xxx
            # 需要尝试 /app/xxx（因为/app是backend目录）
            if not test_file_path.exists() and is_container_env:
                if test_file.startswith("backend/"):
                    alt_path = Path("/app") / test_file[8:]
                    if alt_path.exists():
                        test_file_path = alt_path

            try:
                if test_file_path.resolve() == file_path_resolved:
                    file_found = True
                    break
            except Exception:
                # 如果路径解析失败，尝试字符串匹配
                # 支持多种格式匹配
                match_patterns = [
                    relative_file_path == test_file,
                    file_path == test_file,
                    str(file_path_resolved) == str(test_file_path),
                ]
                # 容器内特殊处理：backend/xxx 格式匹配
                if is_container_env:
                    if file_path_str.startswith("backend/"):
                        backend_relative = "backend/" + relative_file_path
                        match_patterns.append(backend_relative == test_file)
                    elif relative_file_path.startswith("backend/"):
                        without_backend = relative_file_path[8:]
                        match_patterns.append(without_backend == file_path_str)

                if any(match_patterns):
                    file_found = True
                    break

        if not file_found:
            self.warnings.append(
                f"测试文件 {file_path} 不在PRD ({req_id}) 的test_files列表中。"
                f"请确保PRD的test_files字段包含此文件。"
            )

    def _check_req_id_in_tasks_json(
        self, file_path: str, req_id: str, project_root: Path
    ):
        """
        ⭐ 阶段2：检查REQ-ID是否在tasks.json中存在
        """
        # 检查tasks.json
        tasks_json_path = project_root / ".taskmaster" / "tasks" / "tasks.json"
        if not tasks_json_path.exists():
            self.warnings.append(f"tasks.json文件不存在，无法验证任务关联: {tasks_json_path}")
            return

        try:
            import json

            with open(tasks_json_path, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)

            # 检查REQ-ID是否在tasks.json中
            if req_id not in tasks_data:
                self.warnings.append(
                    f"测试文件的REQ-ID ({req_id}) 在tasks.json中不存在对应的任务组。"
                    f"请运行 'task-master parse-prd' 生成任务。"
                )
            else:
                # 检查任务组中是否有任务
                req_tasks = tasks_data.get(req_id, {}).get("tasks", [])
                if not req_tasks:
                    self.warnings.append(
                        f"测试文件的REQ-ID ({req_id}) 在tasks.json中存在，但没有任务。"
                        f"请运行 'task-master parse-prd' 生成任务。"
                    )
        except Exception as e:
            self.warnings.append(f"无法读取tasks.json以验证任务关联: {e}")
