#!/usr/bin/env python3
"""
Task-Master任务合规检查器
验证任务文件的结构和状态
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple


class TaskChecker:
    """任务文件检查器"""

    def __init__(self, rule_config: Dict):
        self.rule_config = rule_config
        self.errors = []
        self.warnings = []

    def check(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查任务文件

        Args:
            file_path: 任务文件路径（tasks.json或task.md）

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

        # 根据文件类型选择检查方法
        if file_path.endswith(".json"):
            self._check_json_task(file_path, file_from_git)
        elif file_path.endswith(".md"):
            self._check_markdown_task(file_path, file_from_git)
        else:
            self.warnings.append(f"未知的任务文件类型: {file_path}")

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_json_task(self, file_path: str, file_from_git: bool = False):
        """检查JSON格式的任务文件"""
        try:
            if file_from_git:
                # 从git暂存区读取
                import subprocess

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
                data = json.loads(content)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON格式错误: {e}")
            return
        except Exception as e:
            self.errors.append(f"无法读取文件: {e}")
            return

        # 检查任务结构
        structure_rules = self.rule_config.get("structure", {})

        if structure_rules.get("require_status_tracking", False):
            # 检查任务是否包含状态字段
            if isinstance(data, list):
                for task in data:
                    if not isinstance(task, dict):
                        continue
                    if "status" not in task:
                        self.warnings.append("任务缺少status字段")

    def _check_markdown_task(self, file_path: str, file_from_git: bool = False):
        """检查Markdown格式的任务文件"""
        try:
            if file_from_git:
                # 从git暂存区读取
                import subprocess

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
            else:
                content = Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            self.errors.append(f"无法读取文件: {e}")
            return

        # 检查必需的结构
        structure_rules = self.rule_config.get("structure", {})

        if structure_rules.get("require_task_md", False):
            # 检查是否包含任务描述
            if len(content.strip()) < 50:
                self.warnings.append("任务描述过短，建议提供更详细的说明")

        # 检查状态
        status_rules = self.rule_config.get("status", {})
        valid_states = status_rules.get("valid_states", [])

        if valid_states:
            # 尝试从内容中提取状态
            status_pattern = r"status:\s*(\w+)"
            import re

            match = re.search(status_pattern, content, re.IGNORECASE)
            if match:
                status = match.group(1).lower()
                if status not in valid_states:
                    self.errors.append(f"无效的任务状态: {status}，" f"必须是 {valid_states} 之一")
