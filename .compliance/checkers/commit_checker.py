#!/usr/bin/env python3
"""
提交消息合规检查器
验证提交消息格式
"""

import re
from typing import Dict, List, Tuple


class CommitChecker:
    """提交消息检查器"""

    def __init__(self, rule_config: Dict):
        self.rule_config = rule_config
        self.errors = []
        self.warnings = []

    def check(self, commit_msg: str) -> Tuple[bool, List[str], List[str]]:
        """
        检查提交消息

        Args:
            commit_msg: 提交消息内容

        Returns:
            (是否通过, 错误列表, 警告列表)
        """
        self.errors = []
        self.warnings = []

        if not commit_msg:
            self.errors.append("提交消息不能为空")
            return False, self.errors, self.warnings

        # 去除首尾空白
        commit_msg = commit_msg.strip()

        # 检查格式
        self._check_format(commit_msg)

        # 检查长度
        self._check_length(commit_msg)

        # 检查禁止的模式
        self._check_forbidden_patterns(commit_msg)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_format(self, commit_msg: str):
        """检查提交消息格式"""
        format_rules = self.rule_config.get("message_format", {})
        pattern = format_rules.get("pattern", "")

        if pattern:
            if not re.match(pattern, commit_msg):
                self.errors.append(f"提交消息格式错误: 必须匹配 {pattern}")
                # 提供示例
                examples = format_rules.get("examples", [])
                if examples:
                    self.errors.append("正确格式示例:")
                    for example in examples[:3]:  # 只显示前3个
                        self.errors.append(f"  {example}")

    def _check_length(self, commit_msg: str):
        """检查提交消息长度"""
        length_rules = self.rule_config.get("length", {})
        min_length = length_rules.get("min", 0)
        max_length = length_rules.get("max", 200)

        msg_length = len(commit_msg)

        if min_length and msg_length < min_length:
            self.errors.append(f"提交消息太短: 当前 {msg_length} 字符，" f"至少需要 {min_length} 字符")

        if max_length and msg_length > max_length:
            self.warnings.append(
                f"提交消息较长: 当前 {msg_length} 字符，" f"建议不超过 {max_length} 字符"
            )

    def _check_forbidden_patterns(self, commit_msg: str):
        """检查禁止的模式"""
        forbidden_patterns = self.rule_config.get("forbidden_patterns", [])

        for pattern in forbidden_patterns:
            if re.match(pattern, commit_msg, re.IGNORECASE):
                self.errors.append(f"提交消息包含禁止的模式: {pattern}")
