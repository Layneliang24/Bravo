"""
Task-0自检检查器
验证PRD完整性和项目准备就绪（按照V4-PART2文档设计）

Task-0职责（针对每个REQ-ID）：
1. Subtask-1: 验证PRD元数据完整性
2. Subtask-2: 检查测试目录存在
3. Subtask-3: 验证API契约文件
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml


class Task0Checker:
    """Task-0自检检查器 - PRD完整性验证"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化Task-0检查器

        Args:
            config: 配置字典
        """
        self.config = config
        self.strict_mode = config.get("strict_mode", True)
        self.errors = []
        self.warnings = []

    def check(self, files: List[str]) -> List[Dict[str, Any]]:
        """
        检查Task-0（PRD完整性验证）

        Args:
            files: 待检查的文件列表

        Returns:
            检查结果列表
        """
        results = []

        # ⭐ 新增：检查tasks.json文件，验证对应的PRD状态
        tasks_json_files = [f for f in files if ".taskmaster/tasks/tasks.json" in f]
        if tasks_json_files:
            tasks_json_result = self._check_tasks_json_prd_status(files)
            if tasks_json_result:
                results.append(tasks_json_result)

        # 只检查代码文件（排除PRD、测试、配置文件）
        code_files = self._filter_code_files(files)
        print(f"[Task0Checker DEBUG] 过滤后的代码文件: {code_files}", file=sys.stderr)
        if not code_files and not tasks_json_files:
            print("[Task0Checker DEBUG] 没有代码文件或tasks.json，跳过检查", file=sys.stderr)
            return results

        # 提取所有相关的REQ-ID（只从代码文件中提取）
        req_ids, format_errors = self._extract_req_ids(code_files)
        print(f"[Task0Checker DEBUG] 提取到的REQ-ID: {req_ids}", file=sys.stderr)
        print(f"[Task0Checker DEBUG] 格式错误数量: {len(format_errors)}", file=sys.stderr)

        # 如果有格式错误，先返回格式错误
        if format_errors:
            print("[Task0Checker DEBUG] 发现格式错误，返回错误信息", file=sys.stderr)
            results.extend(format_errors)
            # 格式错误是严重问题，直接返回
            return results

        # Subtask-2: 检查测试目录（全局检查，不依赖REQ-ID）
        test_dir_result = self._check_test_directories()
        if test_dir_result:
            results.append(test_dir_result)

        # 如果没有提取到REQ-ID，给出警告
        if not req_ids:
            results.append(
                {
                    "level": "warning",
                    "message": "Task-0检查: 无法从代码文件中提取REQ-ID",
                    "file": ", ".join(code_files[:3]),  # 显示前3个文件
                    "help": (
                        "请在代码文件头部注释中包含REQ-ID，格式：\n"
                        "  # REQ-ID: REQ-2025-001-user-login\n"
                        "或\n"
                        "  // REQ-ID: REQ-2025-001-user-login\n\n"
                        "REQ-ID标准格式：REQ-YYYY-NNN-description\n"
                        "示例：REQ-2025-001-user-login\n\n"
                        "如果没有REQ-ID，Task-0无法验证PRD完整性。"
                    ),
                }
            )
            return results  # 没有REQ-ID时，只返回测试目录检查和警告

        # 对每个REQ-ID执行Task-0检查
        for req_id in req_ids:
            # Subtask-1: 验证PRD元数据
            prd_result = self._validate_prd_metadata(req_id)
            if prd_result:
                results.append(prd_result)

            # Subtask-3: 验证API契约
            api_result = self._validate_api_contract(req_id)
            if api_result:
                results.append(api_result)

            # Subtask-4: 检查Task Master任务排序
            ordering_result = self._check_task_ordering(req_id)
            if ordering_result:
                results.append(ordering_result)

            # Subtask-5: 检查任务是否已展开
            expansion_result = self._check_task_expansion(req_id)
            if expansion_result:
                results.append(expansion_result)

            # Subtask-6: 检查txt文件生成
            files_result = self._check_task_files_generated(req_id)
            if files_result:
                results.append(files_result)

        return results

    def _filter_code_files(self, files: List[str]) -> List[str]:
        """
        过滤出代码文件

        Args:
            files: 文件列表

        Returns:
            代码文件列表
        """
        code_files = []
        exclude_patterns = [
            "docs/",
            "tests/",
            ".compliance/",
            ".github/",
            "scripts/",
            ".taskmaster/",
            "node_modules/",
            "venv/",
            "__pycache__/",
        ]

        for file in files:
            # 排除非代码文件
            if any(pattern in file for pattern in exclude_patterns):
                continue

            # 只检查Python和TypeScript/JavaScript文件
            if file.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".vue")):
                code_files.append(file)

        return code_files

    def _extract_req_ids(
        self, files: List[str]
    ) -> tuple[List[str], List[Dict[str, Any]]]:
        """
        从文件列表中提取REQ-ID

        Args:
            files: 文件列表

        Returns:
            (REQ-ID列表（去重）, 格式错误列表)
        """
        req_ids = set()
        format_errors = []  # 存储不符合格式的REQ-ID错误信息

        # REQ-ID标准格式：REQ-YYYY-NNN-description
        # 示例：REQ-2025-001-user-login
        # 格式要求：
        # - REQ- 前缀（必须）
        # - 4位年份（YYYY，必须）
        # - 3位序号（NNN，必须）
        # - 描述（小写字母、数字、连字符，必须）
        req_id_pattern = re.compile(r"REQ-\d{4}-\d{3}-[a-z0-9-]+", re.IGNORECASE)

        for file in files:
            print(f"[Task0Checker DEBUG] 处理文件: {file}", file=sys.stderr)
            # 1. 从文件路径中提取REQ-ID
            match = req_id_pattern.search(file)
            if match:
                req_id = match.group(0).upper()  # 统一转为大写
                print(f"[Task0Checker DEBUG] 从路径提取到REQ-ID: {req_id}", file=sys.stderr)
                req_ids.add(req_id)
                continue

            # 2. 尝试从文件内容中提取
            try:
                # 处理绝对路径和相对路径
                path = Path(file)
                if not path.is_absolute():
                    # 相对路径：尝试多个可能的根目录
                    possible_paths = [
                        path,  # 当前目录
                        Path("/app") / path,  # Docker容器内路径
                        Path(".") / path,  # 项目根目录
                    ]
                else:
                    possible_paths = [path]

                # 先尝试从文件系统读取
                content = None
                for possible_path in possible_paths:
                    if possible_path.exists() and possible_path.suffix in [
                        ".py",
                        ".ts",
                        ".tsx",
                        ".js",
                        ".jsx",
                        ".vue",
                    ]:
                        content = possible_path.read_text(
                            encoding="utf-8", errors="ignore"
                        )
                        break

                # 如果文件不存在，尝试从git暂存区读取（pre-commit阶段）
                if content is None:
                    print(
                        f"[Task0Checker DEBUG] 文件不存在，尝试从git暂存区读取: {file}",
                        file=sys.stderr,
                    )
                    try:
                        result = subprocess.run(
                            ["git", "show", f":{file}"],
                            capture_output=True,
                            text=True,
                            check=False,
                            cwd="/app",
                        )
                        if result.returncode == 0:
                            content = result.stdout
                            msg = (
                                f"[Task0Checker DEBUG] 从git暂存区读取成功，"
                                f"内容长度: {len(content)}"
                            )
                            print(msg, file=sys.stderr)
                        else:
                            print(
                                f"[Task0Checker DEBUG] git show失败: {result.stderr}",
                                file=sys.stderr,
                            )
                    except Exception as e:
                        print(f"[Task0Checker DEBUG] git show异常: {e}", file=sys.stderr)

                # 如果读取到内容，进行REQ-ID提取和格式检查
                if content:
                    line_count = len(content.split(chr(10)))
                    msg = f"[Task0Checker DEBUG] 开始解析文件内容，行数: {line_count}"
                    print(msg, file=sys.stderr)
                    # 检查前30行（增加范围）
                    lines = content.split("\n")[:30]
                    for line_num, line in enumerate(lines, 1):
                        # 先尝试匹配标准格式
                        match = req_id_pattern.search(line)
                        if match:
                            req_id = match.group(0).upper()
                            msg = (
                                f"[Task0Checker DEBUG] 第{line_num}行匹配到"
                                f"标准格式REQ-ID: {req_id}"
                            )
                            print(msg, file=sys.stderr)
                            req_ids.add(req_id)
                            break

                        # 检查是否有不符合格式的REQ-ID
                        # 匹配任何以REQ-开头的完整标识符（至少包含一个连字符）
                        # 避免匹配到 "REQ-ID:" 这样的注释标签
                        invalid_match = re.search(
                            r"REQ-[A-Z0-9]+(?:-[A-Z0-9-]+)+", line, re.IGNORECASE
                        )
                        if invalid_match:
                            invalid_req_id = invalid_match.group(0)
                            msg = (
                                f"[Task0Checker DEBUG] 第{line_num}行发现"
                                f"可能的REQ-ID: {invalid_req_id}"
                            )
                            print(msg, file=sys.stderr)
                            # 验证是否符合标准格式
                            if not req_id_pattern.match(invalid_req_id):
                                msg = (
                                    f"[Task0Checker DEBUG] REQ-ID格式不正确: "
                                    f"{invalid_req_id}"
                                )
                                print(msg, file=sys.stderr)
                                # 确定文件路径（优先使用实际路径，否则使用原始路径）
                                file_path_for_error = file
                                for pp in possible_paths:
                                    if pp.exists():
                                        file_path_for_error = str(pp)
                                        break

                                format_errors.append(
                                    {
                                        "level": "error",
                                        "message": (
                                            f"Task-0检查失败: REQ-ID格式不正确\n"
                                            f"发现: {invalid_req_id}"
                                        ),
                                        "file": file_path_for_error,
                                        "help": (
                                            "REQ-ID必须符合标准格式："
                                            "REQ-YYYY-NNN-description\n"
                                            "示例：REQ-2025-001-user-login\n\n"
                                            f"当前格式：{invalid_req_id}\n"
                                            f"格式要求：\n"
                                            f"  - REQ- 前缀（必须）\n"
                                            f"  - 4位年份（YYYY，必须）\n"
                                            f"  - 3位序号（NNN，必须）\n"
                                            f"  - 描述（小写字母、数字、连字符，必须）\n\n"
                                            f"请修正第 {line_num} 行的REQ-ID格式。"
                                        ),
                                    }
                                )
                    break  # 找到文件后不再尝试其他路径
            except Exception:
                # 文件读取失败，跳过
                pass

        return list(req_ids), format_errors

    def _validate_prd_metadata(self, req_id: str) -> Dict[str, Any]:
        """
        Subtask-1: 验证PRD元数据完整性

        Args:
            req_id: 需求ID

        Returns:
            检查结果，如果有问题则返回错误
        """
        # 构建PRD文件路径（尝试多个可能的路径）
        possible_prd_paths = [
            Path(f"docs/00_product/requirements/{req_id}/{req_id}.md"),  # 相对路径
            Path(
                f"/app/docs/00_product/requirements/{req_id}/{req_id}.md"
            ),  # Docker容器内路径
        ]

        prd_path = None
        for possible_path in possible_prd_paths:
            if possible_path.exists():
                prd_path = possible_path
                break

        # 检查PRD文件是否存在
        if prd_path is None:
            # 使用第一个路径作为错误信息中的路径
            prd_path = possible_prd_paths[0]
            return {
                "level": "error",
                "message": "Task-0检查失败: PRD文件不存在",
                "file": str(prd_path),
                "help": (
                    f"需求 {req_id} 缺少PRD文件。\n"
                    f"请先创建PRD文件: {prd_path}\n"
                    "PRD必须包含完整的YAML frontmatter元数据。"
                ),
            }

        # 读取并解析PRD
        try:
            content = prd_path.read_text(encoding="utf-8")

            # 提取Frontmatter
            if not content.startswith("---"):
                return {
                    "level": "error",
                    "message": "Task-0检查失败: PRD缺少YAML frontmatter",
                    "file": str(prd_path),
                    "help": "PRD文件必须以YAML frontmatter开始（---）",
                }

            parts = content.split("---", 2)
            if len(parts) < 3:
                return {
                    "level": "error",
                    "message": "Task-0检查失败: PRD frontmatter格式错误",
                    "file": str(prd_path),
                    "help": "Frontmatter必须以---开始和结束",
                }

            # 解析YAML
            metadata = yaml.safe_load(parts[1])

            # ⭐ 新增：PRD状态机检查
            status_check_result = self._check_prd_status_for_development(
                prd_path, metadata
            )
            if status_check_result:
                return status_check_result

            # 检查必需字段
            required_fields = ["test_files", "implementation_files"]
            missing_fields = []

            for field in required_fields:
                if field not in metadata:
                    missing_fields.append(field)
                elif not metadata[field]:
                    missing_fields.append(f"{field} (为空)")

            if missing_fields:
                return {
                    "level": "error",
                    "message": (
                        "Task-0检查失败: PRD元数据不完整\n" f"缺少字段: {', '.join(missing_fields)}"
                    ),
                    "file": str(prd_path),
                    "help": (
                        "PRD的YAML frontmatter必须包含：\n"
                        "- test_files: 测试文件列表\n"
                        "- implementation_files: 实现文件列表\n"
                        "- api_contract: API契约文件路径（可选）\n\n"
                        "示例：\n"
                        "---\n"
                        "req_id: REQ-2025-001\n"
                        "test_files:\n"
                        "  - backend/tests/unit/test_example.py\n"
                        "implementation_files:\n"
                        "  - backend/apps/example/views.py\n"
                        "---"
                    ),
                }

            # 检查api_contract字段（可选但建议有）
            if "api_contract" not in metadata or not metadata["api_contract"]:
                self.warnings.append(
                    {
                        "level": "warning",
                        "message": "Task-0建议: PRD缺少api_contract字段",
                        "file": str(prd_path),
                        "help": "建议在PRD中定义API契约文件路径，便于API开发",
                    }
                )

            return None  # 检查通过

        except yaml.YAMLError as e:
            return {
                "level": "error",
                "message": "Task-0检查失败: PRD YAML解析错误",
                "file": str(prd_path),
                "help": f"YAML解析错误: {str(e)}",
            }
        except Exception as e:
            return {
                "level": "error",
                "message": "Task-0检查失败: 读取PRD时出错",
                "file": str(prd_path),
                "help": f"错误详情: {str(e)}",
            }

    def _check_test_directories(self) -> Dict[str, Any]:
        """
        Subtask-2: 检查测试目录是否存在

        Returns:
            检查结果，如果目录不存在则返回错误
        """
        required_dirs = [
            "backend/tests/unit/",
            "backend/tests/integration/",
            "e2e/tests/",
        ]

        missing_dirs = []
        for dir_path in required_dirs:
            # 尝试多个可能的路径（处理Docker容器内路径）
            possible_paths = [
                Path(dir_path),  # 相对路径
                Path("/app") / dir_path,  # Docker容器内路径
            ]

            found = False
            for possible_path in possible_paths:
                if possible_path.exists():
                    found = True
                    break

            if not found:
                missing_dirs.append(dir_path)

        if missing_dirs:
            return {
                "level": "error",
                "message": (f"Task-0检查失败: 测试目录不存在\n缺少目录: {', '.join(missing_dirs)}"),
                "file": "测试目录结构",
                "help": (
                    "请创建必需的测试目录：\n"
                    "  mkdir -p backend/tests/unit\n"
                    "  mkdir -p backend/tests/integration\n"
                    "  mkdir -p backend/tests/regression\n"
                    "  mkdir -p e2e/tests/smoke\n"
                    "  mkdir -p e2e/tests/regression\n\n"
                    "这些目录是TDD开发的基础设施。"
                ),
            }

        return None  # 检查通过

    def _validate_api_contract(self, req_id: str) -> Dict[str, Any]:
        """
        Subtask-3: 验证API契约文件

        Args:
            req_id: 需求ID

        Returns:
            检查结果，如果API契约有问题则返回错误
        """
        # 构建API契约文件路径（尝试多个可能的路径）
        possible_contract_paths = [
            Path(f"docs/01_guideline/api-contracts/{req_id}/{req_id}-api.yaml"),  # 相对路径
            Path(
                f"/app/docs/01_guideline/api-contracts/{req_id}/{req_id}-api.yaml"
            ),  # Docker容器内路径
        ]

        contract_path = None
        for possible_path in possible_contract_paths:
            if possible_path.exists():
                contract_path = possible_path
                break

        # 检查API契约文件是否存在
        if contract_path is None:
            # 使用第一个路径作为错误信息中的路径
            contract_path = possible_contract_paths[0]
            # API契约是可选的，但建议有
            return {
                "level": "warning",
                "message": "Task-0建议: API契约文件不存在",
                "file": str(contract_path),
                "help": (
                    f"建议为 {req_id} 创建API契约文件。\n"
                    "API契约文件用于定义接口规范，便于前后端协作。\n\n"
                    "创建步骤：\n"
                    f"  mkdir -p docs/01_guideline/api-contracts/{req_id}\n"
                    f"  # 创建OpenAPI 3.0规范文件\n"
                    f"  # {contract_path}"
                ),
            }

        # 验证API契约格式
        try:
            content = contract_path.read_text(encoding="utf-8")
            api_spec = yaml.safe_load(content)

            # 检查OpenAPI版本
            if "openapi" not in api_spec:
                return {
                    "level": "error",
                    "message": "Task-0检查失败: API契约缺少openapi版本字段",
                    "file": str(contract_path),
                    "help": "API契约文件必须包含openapi版本字段（如: openapi: 3.0.0）",
                }

            # 检查paths定义
            if "paths" not in api_spec or not api_spec["paths"]:
                return {
                    "level": "error",
                    "message": "Task-0检查失败: API契约缺少paths定义",
                    "file": str(contract_path),
                    "help": "API契约文件必须定义至少一个API路径",
                }

            return None  # 检查通过

        except yaml.YAMLError as e:
            return {
                "level": "error",
                "message": "Task-0检查失败: API契约YAML解析错误",
                "file": str(contract_path),
                "help": f"YAML解析错误: {str(e)}",
            }
        except Exception as e:
            return {
                "level": "error",
                "message": "Task-0检查失败: 读取API契约时出错",
                "file": str(contract_path),
                "help": f"错误详情: {str(e)}",
            }

    def _check_task_ordering(self, req_id: str) -> Dict[str, Any]:
        """
        检查Task Master任务排序是否符合TDD流程

        TDD标准流程：
        1. 编写测试（红色）
        2. 实现功能
        3. 运行测试（绿色）
        4. 重构优化

        Args:
            req_id: 需求ID

        Returns:
            检查结果，如果有问题则返回警告
        """
        # 读取tasks.json
        tasks_file = Path(".taskmaster/tasks/tasks.json")
        if not tasks_file.exists():
            return None

        try:
            import json

            tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[Task0Checker] 读取tasks.json失败: {e}", file=sys.stderr)
            return None

        # 查找与REQ-ID相关的任务
        related_tasks = self._find_tasks_by_req_id(tasks_data, req_id)

        if not related_tasks:
            return None

        # 检查任务排序
        ordering_issues = []

        for task in related_tasks:
            subtasks = task.get("subtasks", [])
            if not subtasks:
                continue

            # 分析子任务顺序
            test_keywords = ["测试", "test", "单元测试", "集成测试", "编写测试"]

            first_task_is_test = False
            if subtasks:
                first_title = subtasks[0].get("title", "").lower()
                first_desc = subtasks[0].get("description", "").lower()
                first_task_is_test = any(
                    kw in first_title or kw in first_desc for kw in test_keywords
                )

            if not first_task_is_test:
                ordering_issues.append(
                    f"任务 {task['id']} '{task['title']}' 建议第一个子任务应该是" "'编写测试'（TDD红色阶段）"
                )

        if ordering_issues:
            # 从配置中读取帮助信息
            task_master_config = self.config.get("task_master_checks", {})
            ordering_config = task_master_config.get("task_ordering", {})
            help_text = ordering_config.get(
                "help",
                (
                    "发现以下排序建议：\n"
                    + "\n".join(f"  - {issue}" for issue in ordering_issues)
                    + "\n\nTDD最佳实践流程：\n"
                    "1. 子任务1：编写失败的测试（红色阶段）\n"
                    "2. 子任务2-N：实现功能直到测试通过（绿色阶段）\n"
                    "3. 子任务N+1：重构优化（保持测试通过）\n\n"
                    "这样可以确保：\n"
                    "- 测试驱动开发\n"
                    "- 防止过度设计\n"
                    "- 持续验证功能正确性"
                ),
            )

            return {
                "level": ordering_config.get("level", "warning"),
                "message": "Task Master任务排序建议优化（TDD流程）",
                "file": ".taskmaster/tasks/tasks.json",
                "help": help_text.replace(
                    "{issues}", "\n".join(f"  - {issue}" for issue in ordering_issues)
                ),
            }

        return None

    def _check_task_expansion(self, req_id: str) -> Dict[str, Any]:
        """
        检查任务是否已展开为子任务

        避免过粗粒度的任务直接实施

        Args:
            req_id: 需求ID

        Returns:
            检查结果，如果有问题则返回警告
        """
        tasks_file = Path(".taskmaster/tasks/tasks.json")
        if not tasks_file.exists():
            return None

        try:
            import json

            tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
        except Exception:
            return None

        related_tasks = self._find_tasks_by_req_id(tasks_data, req_id)

        if not related_tasks:
            return None

        unexpanded_tasks = []

        # 从配置中读取最小复杂度阈值
        task_master_config = self.config.get("task_master_checks", {})
        expansion_config = task_master_config.get("task_expansion", {})
        min_complexity = expansion_config.get("min_complexity_for_expansion", 5)

        for task in related_tasks:
            subtasks = task.get("subtasks", [])

            # 检查任务是否已展开
            if not subtasks or len(subtasks) == 0:
                # 判断任务复杂度（简单任务可以不展开）
                complexity = task.get("complexity", 5)
                if complexity >= min_complexity:  # 使用配置的阈值
                    unexpanded_tasks.append(
                        {
                            "id": task["id"],
                            "title": task["title"],
                            "complexity": complexity,
                        }
                    )

        if unexpanded_tasks:
            task_list = "\n".join(
                [
                    f"  - 任务 {t['id']}: {t['title']} (复杂度: {t['complexity']}/10)"
                    for t in unexpanded_tasks
                ]
            )

            # 使用配置的帮助信息
            help_text = expansion_config.get(
                "help",
                (
                    f"以下任务复杂度较高，建议展开为子任务：\n{task_list}\n\n"
                    "展开方法：\n"
                    "1. 分析任务复杂度：task-master analyze-complexity --research\n"
                    "2. 展开单个任务：task-master expand --id=<任务ID> --research\n"
                    "3. 批量展开所有任务：task-master expand --all --research\n\n"
                    "展开后的子任务可以：\n"
                    "- 提供更清晰的实施路径\n"
                    "- 便于跟踪进度\n"
                    "- 降低单个任务的复杂度"
                ),
            )

            return {
                "level": expansion_config.get("level", "warning"),
                "message": "部分任务未展开为子任务",
                "file": ".taskmaster/tasks/tasks.json",
                "help": help_text.replace("{task_list}", task_list),
            }

        return None

    def _check_task_files_generated(self, req_id: str) -> Dict[str, Any]:
        """
        检查Task Master是否生成了txt文件

        txt文件用于AI查看任务详情

        Args:
            req_id: 需求ID

        Returns:
            检查结果，如果有问题则返回提示
        """
        tasks_file = Path(".taskmaster/tasks/tasks.json")
        if not tasks_file.exists():
            return None

        try:
            import json

            tasks_data = json.loads(tasks_file.read_text(encoding="utf-8"))
        except Exception:
            return None

        related_tasks = self._find_tasks_by_req_id(tasks_data, req_id)

        if not related_tasks:
            return None

        # 检查tasks目录中是否有对应的txt文件
        tasks_dir = Path(".taskmaster/tasks")
        missing_files = []

        for task in related_tasks:
            task_id = task["id"]
            # Task Master生成的文件格式可能是task-{id}.txt或task-{id}.md
            task_file_txt = tasks_dir / f"task-{task_id}.txt"
            task_file_md = tasks_dir / f"task-{task_id}.md"

            if not task_file_txt.exists() and not task_file_md.exists():
                missing_files.append({"id": task_id, "title": task["title"]})

        if missing_files:
            file_list = "\n".join(
                [f"  - task-{f['id']}.txt ({f['title']})" for f in missing_files]
            )

            # 从配置中读取帮助信息
            task_master_config = self.config.get("task_master_checks", {})
            files_config = task_master_config.get("task_files_generation", {})
            help_text = files_config.get(
                "help",
                (
                    f"缺少以下任务文件：\n{file_list}\n\n"
                    "生成方法：\n"
                    "  task-master generate\n\n"
                    "txt/md文件的作用：\n"
                    "- 方便AI查看任务详情（无需解析JSON）\n"
                    "- 提供人类可读的任务描述\n"
                    "- 用于项目文档和任务追踪"
                ),
            )

            return {
                "level": files_config.get("level", "info"),
                "message": "部分Task Master任务未生成txt/md文件",
                "file": ".taskmaster/tasks/",
                "help": help_text.replace("{file_list}", file_list),
            }

        return None

    def _find_tasks_by_req_id(self, tasks_data: dict, req_id: str) -> list:
        """
        从tasks.json中查找与REQ-ID相关的任务

        Args:
            tasks_data: tasks.json的数据
            req_id: 需求ID

        Returns:
            相关任务列表
        """
        related_tasks = []

        # 遍历所有tag
        for tag_name, tag_data in tasks_data.items():
            if not isinstance(tag_data, dict):
                continue

            tasks = tag_data.get("tasks", [])

            for task in tasks:
                # 检查任务标题、描述、details中是否包含REQ-ID
                task_text = " ".join(
                    [
                        str(task.get("title", "")),
                        str(task.get("description", "")),
                        str(task.get("details", "")),
                    ]
                ).upper()

                if req_id.upper() in task_text:
                    related_tasks.append(task)

        return related_tasks

    def _check_prd_status_for_development(
        self, prd_path: Path, metadata: Dict
    ) -> Dict[str, Any]:
        """
        检查PRD状态是否允许开发（状态机校验）

        规则：
        - draft: 不允许提交任何代码
        - review: 只允许修改PRD本身，不允许提交实现代码
        - approved/implementing/completed: 允许开发
        - archived: 不允许开发

        Args:
            prd_path: PRD文件路径
            metadata: PRD元数据

        Returns:
            检查结果，如果有问题则返回错误信息
        """
        status = metadata.get("status", "").lower()

        # 状态1：draft - 完全拒绝
        if status == "draft":
            return {
                "level": "error",
                "message": "Task-0检查失败: PRD状态为draft，不允许开发",
                "file": str(prd_path),
                "help": (
                    "❌ PRD状态为 'draft'（草稿），不允许提交实现代码\n\n"
                    "📋 开发前置条件：\n"
                    "  1. 完善PRD内容\n"
                    "  2. 提交审核：status改为 'review'\n"
                    "  3. 审核通过：status改为 'approved'\n"
                    "  4. 解析任务：task-master parse-prd\n"
                    "  5. 开始开发：status自动变为 'implementing'\n\n"
                    "🔄 如果PRD还在草稿阶段，请先完善内容并提交审核\n\n"
                    "⚠️  状态转换只能人工修改（除了approved→implementing是自动的）"
                ),
            }

        # 状态2：review - 检查是否在提交实现代码
        elif status == "review":
            impl_files = metadata.get("implementation_files", [])

            # 获取当前提交的文件
            staged_files = self._get_staged_files()

            # 检查是否有实现代码被提交
            blocked_files = []
            for staged_file in staged_files:
                # 跳过PRD文件本身
                if "docs/00_product/requirements" in staged_file:
                    continue

                # 检查是否匹配implementation_files
                for impl_pattern in impl_files:
                    # 简单匹配：检查文件路径是否包含impl_pattern
                    if impl_pattern in staged_file or staged_file in impl_pattern:
                        blocked_files.append(staged_file)
                        break

            if blocked_files:
                blocked_list = "\n".join(f"  - {f}" for f in blocked_files[:5])
                if len(blocked_files) > 5:
                    blocked_list += f"\n  - ... 还有 {len(blocked_files) - 5} 个文件"

                return {
                    "level": "error",
                    "message": "Task-0检查失败: PRD状态为review，不允许提交实现代码",
                    "file": str(prd_path),
                    "help": (
                        "❌ PRD状态为 'review'（审核中），不允许提交实现代码\n\n"
                        f"📋 被阻止的文件：\n{blocked_list}\n\n"
                        "✅ 当前可以做的：\n"
                        "  - 修改PRD文件本身（完善需求）\n"
                        "  - 提交文档修改\n\n"
                        "❌ 不允许做的：\n"
                        "  - 提交implementation_files中的代码\n\n"
                        "🔄 等待PRD审核通过后再开发：\n"
                        "  1. 审核人将status改为 'approved'\n"
                        "  2. 运行 task-master parse-prd\n"
                        "  3. 开始开发（status自动变为 'implementing'）"
                    ),
                }

        # 状态3：archived - 不允许开发
        elif status == "archived":
            return {
                "level": "warning",
                "message": "Task-0警告: PRD状态为archived，不建议继续开发",
                "file": str(prd_path),
                "help": (
                    "⚠️ PRD状态为 'archived'（已归档），不建议继续开发\n\n"
                    "如果需要重新开发，请先评估需求是否仍然有效，"
                    "并将status改回合适的状态（如draft或review）"
                ),
            }

        # 状态4：approved/implementing/completed - 允许开发
        elif status in ["approved", "implementing", "completed"]:
            # 通过检查
            return None

        # 其他未知状态
        else:
            return {
                "level": "warning",
                "message": f"Task-0警告: PRD状态 '{status}' 不在标准状态列表中",
                "file": str(prd_path),
                "help": (
                    f"⚠️ PRD状态为 '{status}'，不是标准状态\n\n"
                    "标准状态列表：\n"
                    "  - draft: 草稿\n"
                    "  - review: 审核中\n"
                    "  - approved: 已批准（可parse）\n"
                    "  - implementing: 实施中（parse后自动设置）\n"
                    "  - completed: 已完成\n"
                    "  - archived: 已归档"
                ),
            }

    def _check_tasks_json_prd_status(self, files: List[str] = None) -> Dict[str, Any]:
        """
        检查tasks.json对应的PRD状态（pre-commit阶段）

        从tasks.json的metadata中读取source_prd_path或source_prd_paths，
        只检查这些PRD的状态，避免误报。

        策略：
        1. 检查tasks.json是否在files列表中（被修改）
        2. 如果是，从tasks.json的metadata读取PRD路径
        3. 只检查这些相关PRD的状态
        4. 如果发现任何相关PRD状态为draft/review，报错

        Args:
            files: 待检查的文件列表（从check()方法传入）

        Returns:
            检查结果，如果有问题则返回错误信息
        """
        import json

        # 检查tasks.json是否在files列表中（被修改）
        if files:
            tasks_json_staged = any(".taskmaster/tasks/tasks.json" in f for f in files)
        else:
            # 如果没有传入files，尝试从git暂存区获取（兼容性）
            staged_files = self._get_staged_files()
            tasks_json_staged = any(
                ".taskmaster/tasks/tasks.json" in f for f in staged_files
            )

        # 如果tasks.json没有被修改，跳过检查
        if not tasks_json_staged:
            return None

        # 读取tasks.json
        tasks_json_path = Path(".taskmaster/tasks/tasks.json")
        if not tasks_json_path.exists():
            return None

        try:
            with open(tasks_json_path, "r", encoding="utf-8") as f:
                tasks_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(
                f"[Task0Checker] 读取tasks.json失败: {e}",
                file=sys.stderr,
            )
            return None

        # 收集所有需要检查的PRD路径
        prd_paths_to_check = set()

        for tag_name, tag_data in tasks_data.items():
            if not isinstance(tag_data, dict):
                continue

            metadata = tag_data.get("metadata", {})
            if not isinstance(metadata, dict):
                continue

            # 检查source_prd_path（单个）
            if "source_prd_path" in metadata:
                prd_paths_to_check.add(metadata["source_prd_path"])

            # 检查source_prd_paths（数组）
            if "source_prd_paths" in metadata:
                prd_paths = metadata["source_prd_paths"]
                if isinstance(prd_paths, list):
                    prd_paths_to_check.update(prd_paths)

        # 如果没有找到任何PRD路径，跳过检查
        if not prd_paths_to_check:
            return None

        # 检查这些PRD的状态
        errors = []
        for prd_path in prd_paths_to_check:
            prd_file = Path(prd_path)

            # 尝试多个可能的路径
            possible_paths = [
                prd_file,
                Path("docs/00_product/requirements") / prd_file.name,
                Path("/app/docs/00_product/requirements") / prd_file.name,
            ]

            prd_file_found = None
            for path in possible_paths:
                if path.exists():
                    prd_file_found = path
                    break

            if not prd_file_found:
                errors.append(f"PRD文件不存在: {prd_path}")
                continue

            # 读取PRD的frontmatter
            try:
                with open(prd_file_found, "r", encoding="utf-8") as f:
                    content = f.read()

                # 解析frontmatter
                parts = content.split("---", 2)
                if len(parts) < 3:
                    errors.append(f"PRD {prd_path} 缺少frontmatter")
                    continue

                metadata_str = parts[1].strip()
                if not metadata_str:
                    errors.append(f"PRD {prd_path} frontmatter为空")
                    continue

                metadata = yaml.safe_load(metadata_str)
                if not isinstance(metadata, dict):
                    errors.append(f"PRD {prd_path} frontmatter格式错误")
                    continue

                # 检查status字段
                status = metadata.get("status", "").lower()
                if status in ["draft", "review"]:
                    req_id = metadata.get("req_id", prd_file_found.stem)
                    title = metadata.get("title", "未命名PRD")
                    error_msg = (
                        f"PRD '{req_id}' ({title}) 状态为 '{status}'，"
                        f"不允许修改tasks.json\n"
                        f"  文件: {prd_path}"
                    )
                    errors.append(error_msg)

            except Exception as e:
                errors.append(f"读取PRD失败 {prd_path}: {e}")
                continue

        if errors:
            return {
                "level": "error",
                "message": (
                    "tasks.json被修改，但以下PRD状态不是'approved'：\n"
                    + "\n".join(f"  • {e}" for e in errors)
                    + "\n\n💡 请先将PRD状态改为'approved'后再修改tasks.json"
                ),
                "file": ".taskmaster/tasks/tasks.json",
                "help": (
                    "❌ 检测到tasks.json被修改，但相关PRD状态不是'approved'\n\n"
                    "📋 解决方案：\n"
                    "  1. 如果PRD应该被parse，请将status改为 'approved'\n"
                    "  2. 如果PRD不应该被parse，请撤销tasks.json的修改\n\n"
                    "🔄 标准流程：\n"
                    "  1. PRD状态改为 'approved'\n"
                    "  2. 运行 task-master parse-prd <prd_file>\n"
                    "  3. PRD状态自动变为 'implementing'\n"
                    "  4. 开始开发\n\n"
                    "⚠️  无论通过命令行还是MCP工具调用parse-prd，"
                    "都必须确保PRD状态为approved"
                ),
            }

        return None

    def _get_staged_files(self) -> List[str]:
        """
        获取git暂存区的文件列表

        Returns:
            暂存区文件路径列表
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split("\n")
            return []
        except Exception as e:
            print(f"[Task0Checker] 获取staged files失败: {e}", file=sys.stderr)
            return []


def create_checker(config: Dict[str, Any]) -> Task0Checker:
    """
    创建Task-0检查器实例

    Args:
        config: 配置字典

    Returns:
        Task0Checker实例
    """
    return Task0Checker(config)
