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

        if not path.exists():
            self.errors.append(f"文件不存在: {file_path}")
            return False, self.errors, self.warnings

        # 根据文件类型选择检查方法
        if file_path.endswith(".json"):
            self._check_json_task(file_path)
        elif file_path.endswith(".md"):
            self._check_markdown_task(file_path)
        else:
            self.warnings.append(f"未知的任务文件类型: {file_path}")

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_json_task(self, file_path: str):
        """检查JSON格式的任务文件"""
        try:
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

    def _check_markdown_task(self, file_path: str):
        """检查Markdown格式的任务文件"""
        try:
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
