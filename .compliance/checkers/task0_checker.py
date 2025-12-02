"""
Task-0自检检查器
验证Task-0是否已完成，确保Task-0是强制入口
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any


class Task0Checker:
    """Task-0自检检查器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化Task-0检查器

        Args:
            config: 配置字典
        """
        self.config = config
        self.strict_mode = config.get('strict_mode', True)
        self.task_master_dir = Path('.taskmaster')
        self.tasks_file = self.task_master_dir / 'tasks' / 'tasks.json'

    def check(self, files: List[str]) -> List[Dict[str, Any]]:
        """
        检查Task-0是否已完成

        Args:
            files: 待检查的文件列表

        Returns:
            检查结果列表
        """
        results = []

        # 只检查代码文件（排除PRD、测试、配置文件）
        code_files = self._filter_code_files(files)
        if not code_files:
            return results

        # 检查Task-0状态
        task0_result = self._check_task0_status()
        if task0_result:
            results.append(task0_result)

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
            'docs/',
            'tests/',
            '.compliance/',
            '.github/',
            'scripts/',
            '.taskmaster/',
            'node_modules/',
            'venv/',
            '__pycache__/',
        ]

        for file in files:
            # 排除非代码文件
            if any(pattern in file for pattern in exclude_patterns):
                continue

            # 只检查Python和TypeScript/JavaScript文件
            if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.vue')):
                code_files.append(file)

        return code_files

    def _check_task0_status(self) -> Dict[str, Any]:
        """
        检查Task-0状态

        Returns:
            检查结果，如果Task-0未完成则返回错误
        """
        # 检查tasks.json是否存在
        if not self.tasks_file.exists():
            return {
                'level': 'warning',
                'message': 'Task-Master任务文件不存在，跳过Task-0检查',
                'file': str(self.tasks_file),
                'help': '运行 task-master init 初始化Task-Master'
            }

        try:
            # 读取tasks.json
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 获取当前tag的任务
            current_tag = data.get('state', {}).get('currentTag', 'master')
            tags = data.get('tags', {})

            if current_tag not in tags:
                return {
                    'level': 'warning',
                    'message': f'当前tag "{current_tag}" 不存在',
                    'file': str(self.tasks_file),
                    'help': f'检查tasks.json中的tags配置'
                }

            tasks = tags[current_tag].get('tasks', [])

            # 查找Task-0
            task0 = None
            for task in tasks:
                task_id = str(task.get('id', ''))
                if task_id == '0' or task_id.lower() == 'task-0':
                    task0 = task
                    break

            # 如果没有Task-0，返回警告
            if not task0:
                return {
                    'level': 'warning',
                    'message': 'Task-0不存在，建议创建Task-0作为项目自检入口',
                    'file': str(self.tasks_file),
                    'help': '创建Task-0用于项目环境自检和配置验证'
                }

            # 检查Task-0状态
            task0_status = task0.get('status', '').lower()
            task0_title = task0.get('title', 'Task-0')

            if task0_status != 'done':
                # 在strict_mode下返回错误，否则返回警告
                level = 'error' if self.strict_mode else 'warning'
                return {
                    'level': level,
                    'message': f'Task-0 "{task0_title}" 状态为 "{task0_status}"，必须先完成Task-0自检',
                    'file': str(self.tasks_file),
                    'help': (
                        'Task-0是项目的强制入口，用于验证开发环境配置。\n'
                        '完成Task-0后，使用以下命令更新状态：\n'
                        '  task-master set-status --id=0 --status=done'
                    )
                }

            # Task-0已完成，返回None
            return None

        except json.JSONDecodeError as e:
            return {
                'level': 'error',
                'message': f'tasks.json格式错误: {str(e)}',
                'file': str(self.tasks_file),
                'help': '检查tasks.json是否为有效的JSON格式'
            }
        except Exception as e:
            return {
                'level': 'error',
                'message': f'检查Task-0状态时出错: {str(e)}',
                'file': str(self.tasks_file),
                'help': '查看详细错误信息'
            }


def create_checker(config: Dict[str, Any]) -> Task0Checker:
    """
    创建Task-0检查器实例

    Args:
        config: 配置字典

    Returns:
        Task0Checker实例
    """
    return Task0Checker(config)

