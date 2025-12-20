#!/usr/bin/env python3
"""
代码文件合规检查器
验证代码文件的关联性和质量
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import yaml
except ImportError:
    yaml = None


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

        # 解析文件路径（支持相对路径和绝对路径）
        path = Path(file_path)
        if not path.is_absolute():
            # 尝试多个可能的路径
            possible_paths = [
                Path.cwd() / path,
                Path("/app") / path,  # 容器内项目根目录
            ]
            for p in possible_paths:
                if p.exists():
                    path = p
                    break
            else:
                # 如果都找不到，使用第一个可能的路径
                path = possible_paths[0]
        path = path.resolve()

        # 如果文件不存在，尝试从git获取内容（暂存文件）
        file_content = None
        file_from_git = False
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
                        if result.returncode == 0 and result.stdout:
                            file_content = result.stdout
                            file_from_git = True
                            break
                    except (FileNotFoundError, subprocess.SubprocessError):
                        continue

            # 如果无法从git获取，记录警告但不阻止（可能是新文件，让其他检查继续）
            if not file_content:
                self.warnings.append(f"无法从文件系统或git获取文件内容: {file_path}，将跳过内容检查")
                # 不直接返回False，让其他检查（如路径检查）继续

        # 检查文件关联性（如果规则要求）
        traceability = self.rule_config.get("traceability", {})
        if traceability.get("require_prd_link", False):
            self._check_prd_link(
                file_path, file_content if file_content else None, file_from_git
            )
        if traceability.get("require_test_link", False):
            self._check_test_link(file_path, file_from_git)
        if traceability.get("require_task_link", False):
            self._check_task_link(file_path, file_from_git)

        # 检查删除功能授权（如果规则要求）
        modification_validation = self.rule_config.get("modification_validation", {})
        if modification_validation.get("require_prd_approval_for_deletion", False):
            self._check_deletion_authorization(file_path)

        # ⭐ 检查API契约一致性（如果规则要求）
        if modification_validation.get("require_api_contract_consistency", False):
            # 检查是否是后端API代码文件
            if "backend/apps/" in file_path and (
                "views.py" in file_path or "serializers.py" in file_path
            ):
                # 提取REQ-ID
                content = file_content
                if not content:
                    try:
                        path = Path(file_path)
                        if path.exists():
                            content = path.read_text(encoding="utf-8", errors="ignore")
                    except Exception:
                        pass

                if content:
                    lines = content.split("\n")[:20]
                    req_id = None
                    for line in lines:
                        match = re.search(
                            r"REQ-\d{4}-\d{3}(-[a-z0-9-]+)?", line, re.IGNORECASE
                        )
                        if match:
                            req_id = match.group(0)
                            break

                    if req_id:
                        self._check_api_contract_consistency(file_path, req_id)

        # 检查代码质量
        self._check_quality(file_path)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_prd_link(
        self, file_path: str, file_content: str = None, file_from_git: bool = False
    ):
        """检查PRD关联（通过文件路径或注释）"""
        # 获取文件内容
        content = file_content
        if not content:
            # 解析文件路径
            path = Path(file_path)
            if not path.is_absolute():
                possible_paths = [
                    Path.cwd() / path,
                    Path("/app") / path,
                ]
                for p in possible_paths:
                    if p.exists():
                        path = p
                        break

            try:
                if path.exists():
                    content = path.read_text(encoding="utf-8", errors="ignore")
                else:
                    # 文件不存在，尝试从git获取（暂存文件）
                    import subprocess

                    git_dirs = ["/app", str(Path.cwd()), str(Path.cwd().parent)]
                    for git_dir in git_dirs:
                        git_path = Path(git_dir) / ".git"
                        if git_path.exists():
                            try:
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
                                if result.returncode == 0 and result.stdout:
                                    content = result.stdout
                                    break
                            except (FileNotFoundError, subprocess.SubprocessError):
                                continue

                    if not content:
                        # 无法获取文件内容，但继续检查（可能是新文件）
                        self.warnings.append(f"无法读取文件以检查PRD关联: {file_path}，将跳过REQ-ID检查")
                        return
            except Exception as e:
                self.errors.append(f"无法读取文件以检查PRD关联: {str(e)}")
                return

        if content:
            # 检查文件头部是否有REQ-ID注释
            lines = content.split("\n")[:20]  # 只检查前20行
            req_id = None
            for line in lines:
                match = re.search(r"REQ-\d{4}-\d{3}(-[a-z0-9-]+)?", line, re.IGNORECASE)
                if match:
                    req_id = match.group(0)
                    break

            if not req_id:
                # 在strict_mode下，这是错误而非警告
                self.errors.append(
                    "❌ 代码文件必须包含REQ-ID关联（在文件头部注释中）\n"
                    "   提示: 请在文件头部添加注释，例如: # REQ-2025-001-feature-name"
                )
                return

            # ⭐ 阶段2：检查文件是否在PRD的implementation_files中
            self._check_file_in_prd_implementation_files(file_path, req_id)

            # 注意：API契约一致性检查已移至modification_validation部分，避免重复检查

    def _check_test_link(self, file_path: str, file_from_git: bool = False):
        """检查测试文件是否存在"""
        # 推断对应的测试文件路径
        path = Path(file_path)

        # 如果是backend代码文件，查找对应的测试文件
        if "backend/apps/" in file_path or "backend/bravo/" in file_path:
            # 提取模块名
            module_name = path.stem

            # 如果文件在apps/下，提取app名称
            app_name = None
            if "backend/apps/" in file_path:
                parts = file_path.split("backend/apps/")[1].split("/")
                if len(parts) > 0:
                    app_name = parts[0]

            # 可能的测试文件位置（包括带app前缀的命名）
            test_locations = [
                f"backend/tests/unit/test_{module_name}.py",
                f"backend/tests/integration/test_{module_name}.py",
            ]

            # 如果有app名称，也接受 test_{app}_{module}.py 的命名
            if app_name:
                test_locations.extend(
                    [
                        f"backend/tests/unit/test_{app_name}_{module_name}.py",
                        f"backend/tests/integration/test_{app_name}_{module_name}.py",
                    ]
                )

            # 检查是否存在测试文件（包括从git检查）
            has_test = False
            for test_loc in test_locations:
                test_path = Path(test_loc)
                if not test_path.is_absolute():
                    possible_paths = [
                        Path.cwd() / test_path,
                        Path("/app") / test_path,
                    ]
                    for p in possible_paths:
                        if p.exists():
                            has_test = True
                            break
                else:
                    if test_path.exists():
                        has_test = True
                        break

                # 如果文件不存在，尝试从git检查（暂存文件）
                if not has_test and file_from_git:
                    import subprocess

                    git_dirs = ["/app", str(Path.cwd()), str(Path.cwd().parent)]
                    for git_dir in git_dirs:
                        git_path = Path(git_dir) / ".git"
                        if git_path.exists():
                            try:
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
                                result = subprocess.run(
                                    ["git", "show", f":{test_loc}"],
                                    capture_output=True,
                                    text=True,
                                    check=False,
                                    cwd=git_dir,
                                )
                                if result.returncode == 0:
                                    has_test = True
                                    break
                            except (FileNotFoundError, subprocess.SubprocessError):
                                continue

                if has_test:
                    break

            if not has_test:
                # 构建更准确的错误信息
                if app_name:
                    self.errors.append(
                        f"代码文件 {file_path} 缺少对应的测试文件。"
                        f"请创建: backend/tests/unit/test_{app_name}_{module_name}.py 或 "
                        f"backend/tests/integration/test_{app_name}_{module_name}.py 或 "
                        f"backend/tests/unit/test_{module_name}.py"
                    )
                else:
                    self.errors.append(
                        f"代码文件 {file_path} 缺少对应的测试文件。"
                        f"请创建: backend/tests/unit/test_{module_name}.py 或 "
                        f"backend/tests/integration/test_{module_name}.py"
                    )

        # 如果是frontend代码文件，查找对应的E2E测试
        elif "frontend/src/" in file_path:
            # 提取功能名
            feature_name = path.stem
            test_location = f"e2e/tests/smoke/test-{feature_name}.spec.ts"

            if not Path(test_location).exists():
                self.warnings.append(f"建议为前端文件创建E2E测试: {test_location}")

    def _check_task_link(self, file_path: str, file_from_git: bool = False):
        """检查Task-Master任务是否存在"""
        # 从文件路径或注释中提取REQ-ID
        req_id = None
        content = None

        # 尝试读取文件内容
        try:
            path = Path(file_path)
            if not path.is_absolute():
                possible_paths = [
                    Path.cwd() / path,
                    Path("/app") / path,
                ]
                for p in possible_paths:
                    if p.exists():
                        path = p
                        break

            if path.exists():
                content = path.read_text(encoding="utf-8", errors="ignore")
            elif file_from_git:
                # 尝试从git获取
                import subprocess

                git_dirs = ["/app", str(Path.cwd()), str(Path.cwd().parent)]
                for git_dir in git_dirs:
                    git_path = Path(git_dir) / ".git"
                    if git_path.exists():
                        try:
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
                            if result.returncode == 0 and result.stdout:
                                content = result.stdout
                                break
                        except (FileNotFoundError, subprocess.SubprocessError):
                            continue
        except Exception:
            pass

        # 从内容中提取REQ-ID
        if content:
            lines = content.split("\n")[:20]
            for line in lines:
                match = re.search(
                    r"REQ-(\d{4})(-\d{3})?-[a-zA-Z0-9-]+", line, re.IGNORECASE
                )
                if match:
                    req_id = match.group(0)
                    break

        # 如果找不到REQ-ID，尝试从文件路径推断
        if not req_id:
            # 从路径中查找REQ-ID模式
            match = re.search(
                r"REQ-\d{4}(-\d{3})?-[a-zA-Z0-9-]+", file_path, re.IGNORECASE
            )
            if match:
                req_id = match.group(0)

        if req_id:
            # ⭐ 阶段2：检查REQ-ID是否在tasks.json中存在
            self._check_req_id_in_tasks_json(file_path, req_id)
        else:
            # 如果没有REQ-ID，无法检查任务关联
            # 在strict_mode下，这也是错误
            self.errors.append(
                "无法从代码文件中提取REQ-ID，无法验证Task-Master任务关联。" "请在文件头部注释中包含REQ-ID"
            )

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

    def _check_deletion_authorization(self, file_path: str):
        """检查删除功能是否获得PRD授权"""
        # 获取git diff中的删除操作
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--unified=0", file_path],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                # 文件不在暂存区或不是删除操作，跳过
                return

            diff_output = result.stdout

            # 检查是否有删除的行（以-开头，但不是---）
            deleted_lines = [
                line[1:]  # 去掉-前缀
                for line in diff_output.split("\n")
                if line.startswith("-") and not line.startswith("---")
            ]

            if deleted_lines:
                # 检查删除的内容是否是功能代码（函数、类等）
                is_feature_code = False
                feature_patterns = [
                    r"def\s+\w+\(",  # Python函数
                    r"class\s+\w+",  # Python类
                    r"async\s+function",  # JS async函数
                    r"export\s+function",  # JS export函数
                    r"export\s+class",  # JS export类
                ]

                for line in deleted_lines:
                    for pattern in feature_patterns:
                        if re.search(pattern, line):
                            is_feature_code = True
                            break
                    if is_feature_code:
                        break

                if is_feature_code:
                    # 检查PRD授权
                    # 1. 从文件路径或注释中提取REQ-ID
                    req_id = None
                    try:
                        # 尝试从当前文件读取REQ-ID
                        if Path(file_path).exists():
                            content = Path(file_path).read_text(
                                encoding="utf-8", errors="ignore"
                            )
                            lines = content.split("\n")[:20]
                            for line in lines:
                                match = re.search(r"REQ-\d{4}-\d{3}-[a-z0-9-]+", line)
                                if match:
                                    req_id = match.group(0)
                                    break
                    except Exception:
                        pass

                    # 2. 如果找不到REQ-ID，尝试从git log中查找
                    if not req_id:
                        try:
                            result = subprocess.run(
                                ["git", "log", "--oneline", "-1", "--", file_path],
                                capture_output=True,
                                text=True,
                                check=False,
                            )
                            if result.returncode == 0:
                                commit_msg = result.stdout
                                match = re.search(
                                    r"REQ-\d{4}-\d{3}-[a-z0-9-]+", commit_msg
                                )
                                if match:
                                    req_id = match.group(0)
                        except Exception:
                            pass

                    # 3. 检查PRD的deletable字段
                    if req_id:
                        prd_path = Path(
                            f"docs/00_product/requirements/{req_id}/{req_id}.md"
                        )
                        if prd_path.exists():
                            try:
                                content = prd_path.read_text(encoding="utf-8")
                                # 提取Frontmatter
                                if content.startswith("---"):
                                    parts = content.split("---", 2)
                                    if len(parts) >= 3:
                                        import yaml

                                        frontmatter = yaml.safe_load(parts[1])
                                        deletable = frontmatter.get("deletable", False)

                                        if not deletable:
                                            self.errors.append(
                                                f"检测到功能代码删除，但PRD ({req_id}) "
                                                "的deletable字段为false。"
                                                "请先修改PRD的deletable字段为true，"
                                                "或使用[BUGFIX]/[REFACTOR]标记"
                                            )
                            except Exception as e:
                                self.warnings.append(f"无法读取PRD文件验证删除授权: {e}")
                        else:
                            self.errors.append(
                                f"检测到功能代码删除，但未找到对应的PRD文件: {prd_path}。"
                                "请先创建或更新PRD，设置deletable字段"
                            )
                    else:
                        # 检查提交消息是否包含[BUGFIX]或[REFACTOR]
                        try:
                            result = subprocess.run(
                                ["git", "log", "-1", "--pretty=%B"],
                                capture_output=True,
                                text=True,
                                check=False,
                            )
                            if result.returncode == 0:
                                commit_msg = result.stdout
                                if not (
                                    "[BUGFIX]" in commit_msg
                                    or "[REFACTOR]" in commit_msg
                                    or "[HOTFIX]" in commit_msg
                                ):
                                    self.errors.append(
                                        "检测到功能代码删除，但提交消息中未包含"
                                        "[BUGFIX]/[REFACTOR]/[HOTFIX]标记，"
                                        "且无法找到对应的PRD授权。"
                                        "请先修改PRD的deletable字段或添加相应标记"
                                    )
                        except Exception:
                            pass
        except Exception as e:
            # 如果检查过程中出现异常，记录警告但不阻止提交
            self.warnings.append(f"检查删除授权时出错: {e}")

    def _check_file_in_prd_implementation_files(self, file_path: str, req_id: str):
        """
        ⭐ 阶段2：检查文件是否在PRD的implementation_files中
        """
        # 查找项目根目录
        file_path_obj = Path(file_path)
        project_root = None
        for parent in [file_path_obj] + list(file_path_obj.parents):
            if (parent / "docs" / "00_product" / "requirements").exists():
                project_root = parent
                break

        if not project_root:
            self.warnings.append("无法定位项目根目录，跳过PRD文件关联检查")
            return

        # 查找PRD文件
        prd_path = (
            project_root
            / "docs"
            / "00_product"
            / "requirements"
            / req_id
            / f"{req_id}.md"
        )

        if not prd_path.exists():
            self.warnings.append(f"无法找到PRD文件 {prd_path}，跳过文件关联检查")
            return

        try:
            import yaml

            content = prd_path.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                self.warnings.append(f"PRD frontmatter格式错误：{prd_path}")
                return

            metadata = yaml.safe_load(parts[1]) or {}
            implementation_files = metadata.get("implementation_files", [])

            # 将文件路径转换为相对路径（相对于项目根目录）
            try:
                file_path_resolved = file_path_obj.resolve()
                project_root_resolved = project_root.resolve()
                relative_file_path = str(
                    file_path_resolved.relative_to(project_root_resolved)
                )
            except (ValueError, AttributeError):
                # 如果无法转换为相对路径，使用原始路径
                relative_file_path = file_path

            # 检查文件是否在implementation_files中
            # 支持相对路径和绝对路径匹配
            file_found = False
            for impl_file in implementation_files:
                impl_file_path = (
                    project_root / impl_file
                    if not Path(impl_file).is_absolute()
                    else Path(impl_file)
                )
                try:
                    if impl_file_path.resolve() == file_path_resolved:
                        file_found = True
                        break
                except Exception:
                    # 如果路径解析失败，尝试字符串匹配
                    if relative_file_path == impl_file or file_path == impl_file:
                        file_found = True
                        break

            if not file_found:
                self.warnings.append(
                    f"代码文件 {file_path} 不在PRD ({req_id}) 的implementation_files列表中。"
                    f"请确保PRD的implementation_files字段包含此文件。"
                )
        except Exception as e:
            self.warnings.append(f"无法读取PRD文件以验证文件关联: {e}")

    def _check_api_contract_consistency(self, file_path: str, req_id: str):
        """
        ⭐ 阶段3：检查API契约一致性
        当后端API代码（views.py/serializers.py）修改时，检查对应的API契约文件是否存在并提醒保持一致性

        Args:
            file_path: 代码文件路径
            req_id: 需求ID
        """
        # 查找项目根目录
        file_path_obj = Path(file_path)
        project_root = None
        for parent in [file_path_obj] + list(file_path_obj.parents):
            if (parent / "docs" / "00_product" / "requirements").exists():
                project_root = parent
                break

        if not project_root:
            # 无法定位项目根目录，跳过检查
            return

        # 查找PRD文件
        prd_path = (
            project_root
            / "docs"
            / "00_product"
            / "requirements"
            / req_id
            / f"{req_id}.md"
        )

        if not prd_path.exists():
            # PRD文件不存在，跳过检查
            return

        try:
            import yaml

            # 读取PRD获取api_contract字段
            prd_content = prd_path.read_text(encoding="utf-8")
            parts = prd_content.split("---", 2)
            if len(parts) < 3:
                return  # PRD格式错误，跳过

            metadata = yaml.safe_load(parts[1]) or {}
            api_contract_path = metadata.get("api_contract")

            if not api_contract_path:
                # PRD中没有声明api_contract，给出建议
                self.warnings.append(
                    f"后端API代码文件 {file_path} 已修改，但PRD ({req_id}) 中未声明api_contract字段。"
                    f"建议：在PRD中添加api_contract字段，指向对应的OpenAPI契约文件，以便验证API实现与契约的一致性。"
                )
                return

            # 构建契约文件路径
            contract_path = Path(str(api_contract_path))
            if not contract_path.is_absolute():
                contract_path = project_root / contract_path

            # 检查契约文件是否存在
            if not contract_path.exists():
                # 尝试容器内路径
                container_path = Path("/app") / contract_path.relative_to(project_root)
                if container_path.exists():
                    contract_path = container_path
                else:
                    self.warnings.append(
                        f"后端API代码文件 {file_path} 已修改，"
                        f"但PRD声明的API契约文件不存在: {api_contract_path}。"
                        f"请确保契约文件存在，并在代码修改后同步更新契约文件以保持一致性。"
                    )
                    return

            # 验证契约文件格式（基本验证）
            try:
                contract_content = contract_path.read_text(encoding="utf-8")
                contract_spec = yaml.safe_load(contract_content)

                # 检查OpenAPI版本
                if "openapi" not in contract_spec:
                    self.errors.append(
                        f"API契约文件格式错误: {contract_path} 缺少openapi版本字段。"
                        f"请确保契约文件符合OpenAPI 3.0规范。"
                    )
                    return

                # 检查paths定义
                if "paths" not in contract_spec or not contract_spec["paths"]:
                    self.warnings.append(
                        f"API契约文件 {contract_path} 缺少paths定义。" f"请确保契约文件定义了API路径。"
                    )
                    return

                # ⚠️ 注意：完整的一致性验证（代码生成Schema vs 契约文件）需要在CI/CD中完成
                # 这里只做基本的存在性和格式验证，提醒开发者需要保持一致性
                self.warnings.append(
                    f"⚠️ 后端API代码文件 {file_path} 已修改。"
                    f"请确保代码实现与API契约文件 {contract_path} 保持一致。"
                    f"建议：运行 'python manage.py spectacular "
                    f"--file schema-from-code.json' 生成当前代码的OpenAPI Schema，"
                    f"并与契约文件对比验证一致性。"
                    f"完整的契约一致性验证将在CI/CD中自动执行。"
                )

            except yaml.YAMLError as e:
                self.errors.append(f"API契约文件YAML解析错误: {contract_path} - {str(e)}")
            except Exception as e:
                self.warnings.append(f"无法读取API契约文件以验证一致性: {contract_path} - {str(e)}")

        except Exception as e:
            self.warnings.append(f"检查API契约一致性时出错: {str(e)}")

    def _check_req_id_in_tasks_json(self, file_path: str, req_id: str):
        """
        ⭐ 阶段2：检查REQ-ID是否在tasks.json中存在
        """
        # 查找项目根目录
        file_path_obj = Path(file_path)
        project_root = None
        for parent in [file_path_obj] + list(file_path_obj.parents):
            if (parent / "docs" / "00_product" / "requirements").exists():
                project_root = parent
                break

            if not project_root:
                self.warnings.append("无法定位项目根目录，跳过tasks.json关联检查")
                return

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
                    f"代码文件的REQ-ID ({req_id}) 在tasks.json中不存在对应的任务组。"
                    f"请运行 'task-master parse-prd' 生成任务。"
                )
            else:
                # 检查任务组中是否有任务
                req_tasks = tasks_data.get(req_id, {}).get("tasks", [])
                if not req_tasks:
                    self.warnings.append(
                        f"代码文件的REQ-ID ({req_id}) 在tasks.json中存在，但没有任务。"
                        f"请运行 'task-master parse-prd' 生成任务。"
                    )
        except Exception as e:
            self.warnings.append(f"无法读取tasks.json以验证任务关联: {e}")
