#!/usr/bin/env python3
"""
测试文件合规检查器
验证测试文件的命名、位置和内容
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


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
                        result = subprocess.run(
                            ["git", "show", f":{file_path}"],
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
                    result = subprocess.run(
                        ["git", "show", f":{file_path}"],
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
