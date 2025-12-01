#!/usr/bin/env python3
"""
代码文件合规检查器
验证代码文件的关联性和质量
"""

import re
import subprocess
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
        if not path.exists():
            import subprocess

            # 尝试多个可能的git工作目录
            git_dirs = ["/app", str(Path.cwd()), str(Path.cwd().parent)]
            for git_dir in git_dirs:
                git_path = Path(git_dir) / ".git"
                if git_path.exists():
                    try:
                        result = subprocess.run(
                            ["git", "show", f":{file_path}"],
                            capture_output=True,
                            text=True,
                            check=False,
                            cwd=git_dir,
                        )
                        if result.returncode == 0:
                            file_content = result.stdout
                            break
                    except (FileNotFoundError, subprocess.SubprocessError):
                        continue

            if not file_content:
                self.errors.append(f"文件不存在且无法从git获取: {file_path}")
                return False, self.errors, self.warnings

        # 检查文件关联性（如果规则要求）
        traceability = self.rule_config.get("traceability", {})
        if traceability.get("require_prd_link", False):
            self._check_prd_link(file_path)
        if traceability.get("require_test_link", False):
            self._check_test_link(file_path)
        if traceability.get("require_task_link", False):
            self._check_task_link(file_path)

        # 检查删除功能授权（如果规则要求）
        modification_validation = self.rule_config.get("modification_validation", {})
        if modification_validation.get("require_prd_approval_for_deletion", False):
            self._check_deletion_authorization(file_path)

        # 检查代码质量
        self._check_quality(file_path)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_prd_link(self, file_path: str):
        """检查PRD关联（通过文件路径或注释）"""
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

        # 获取文件内容
        content = None
        try:
            if path.exists():
                content = path.read_text(encoding="utf-8", errors="ignore")
            else:
                # 文件不存在，尝试从git获取（暂存文件）
                import subprocess

                result = subprocess.run(
                    ["git", "show", f":{file_path}"],
                    capture_output=True,
                    text=True,
                    check=False,
                    cwd="/app" if Path("/app").exists() else Path.cwd(),
                )
                if result.returncode == 0:
                    content = result.stdout
                else:
                    self.errors.append("无法读取文件以检查PRD关联（文件不存在且无法从git获取）")
                    return
        except Exception as e:
            self.errors.append(f"无法读取文件以检查PRD关联: {str(e)}")
            return

        if content:
            # 检查文件头部是否有REQ-ID注释
            lines = content.split("\n")[:20]  # 只检查前20行
            has_req_id = any(
                re.search(r"REQ-\d{4}(-\d{3})?-[A-Z0-9-]+", line) for line in lines
            )
            if not has_req_id:
                # 在strict_mode下，这是错误而非警告
                self.errors.append("代码文件必须包含REQ-ID关联（在文件头部注释中）")

    def _check_test_link(self, file_path: str):
        """检查测试文件是否存在"""
        # 推断对应的测试文件路径
        path = Path(file_path)

        # 如果是backend代码文件，查找对应的测试文件
        if "backend/apps/" in file_path or "backend/bravo/" in file_path:
            # 提取模块名
            module_name = path.stem
            # 可能的测试文件位置
            test_locations = [
                f"backend/tests/unit/test_{module_name}.py",
                f"backend/tests/integration/test_{module_name}.py",
            ]

            # 检查是否存在测试文件
            has_test = any(Path(loc).exists() for loc in test_locations)
            if not has_test:
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

    def _check_task_link(self, file_path: str):
        """检查Task-Master任务是否存在"""
        # 从文件路径或注释中提取REQ-ID
        req_id = None
        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")[:20]
            for line in lines:
                match = re.search(r"REQ-(\d{4})-(\d{3})-", line)
                if match:
                    req_id = match.group(0).rstrip("-")
                    break
        except Exception:
            pass

        # 如果找不到REQ-ID，尝试从文件路径推断
        if not req_id:
            # 从路径中查找REQ-ID模式
            match = re.search(r"REQ-\d{4}-\d{3}-[a-z0-9-]+", file_path)
            if match:
                req_id = match.group(0)

        if req_id:
            # 检查Task-Master任务目录是否存在
            task_dir = Path(f".taskmaster/tasks/{req_id}")
            if not task_dir.exists():
                # 在strict_mode下，这是错误而非警告
                self.errors.append(
                    f"代码文件缺少Task-Master任务关联。"
                    f"未找到任务目录: {task_dir}。"
                    "请先运行Task-Master生成任务，或创建对应的任务结构"
                )
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
                            self.errors.append(
                                "检测到功能代码删除，但无法验证PRD授权。"
                                "请确保PRD的deletable字段为true，或在提交消息中包含[BUGFIX]/[REFACTOR]标记"
                            )
        except Exception as e:
            # 如果无法检查删除授权，给出警告
            self.warnings.append(f"无法检查删除授权: {e}")
