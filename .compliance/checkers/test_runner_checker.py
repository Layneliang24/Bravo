"""
测试运行器检查器
在提交前运行测试，确保测试通过（TDD红绿循环）
"""

import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any


class TestRunnerChecker:
    """测试运行器检查器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化测试运行器检查器

        Args:
            config: 配置字典
        """
        self.config = config
        self.strict_mode = config.get('strict_mode', True)
        self.project_root = Path.cwd()

    def check(self, files: List[str]) -> List[Dict[str, Any]]:
        """
        运行测试并检查结果

        Args:
            files: 待检查的文件列表

        Returns:
            检查结果列表
        """
        results = []

        # 只在有代码或测试文件变更时运行测试
        relevant_files = self._filter_relevant_files(files)
        if not relevant_files:
            return results

        # 确定需要运行的测试
        tests_to_run = self._determine_tests(relevant_files)
        if not tests_to_run:
            return results

        # 运行测试
        test_result = self._run_tests(tests_to_run)
        if test_result:
            results.append(test_result)

        return results

    def _filter_relevant_files(self, files: List[str]) -> List[str]:
        """
        过滤出相关文件（代码文件和测试文件）

        Args:
            files: 文件列表

        Returns:
            相关文件列表
        """
        relevant_files = []
        relevant_patterns = [
            'backend/apps/',
            'backend/tests/',
            'frontend/src/',
            'e2e/tests/',
        ]

        for file in files:
            if any(pattern in file for pattern in relevant_patterns):
                if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.vue')):
                    relevant_files.append(file)

        return relevant_files

    def _determine_tests(self, files: List[str]) -> List[str]:
        """
        确定需要运行的测试

        Args:
            files: 文件列表

        Returns:
            测试文件列表
        """
        tests = []

        for file in files:
            # 如果是测试文件，直接添加
            if 'tests/' in file or file.startswith('test_') or file.endswith('_test.py'):
                tests.append(file)
            # 如果是代码文件，查找对应的测试文件
            elif file.endswith('.py') and 'backend/apps/' in file:
                test_file = self._find_test_for_code(file)
                if test_file and test_file not in tests:
                    tests.append(test_file)

        return tests

    def _find_test_for_code(self, code_file: str) -> str:
        """
        查找代码文件对应的测试文件

        Args:
            code_file: 代码文件路径

        Returns:
            测试文件路径，如果不存在则返回None
        """
        # backend/apps/example/views.py -> backend/tests/unit/test_example_views.py
        if 'backend/apps/' in code_file:
            parts = code_file.split('/')
            # 找到apps后的路径
            apps_index = parts.index('apps')
            module_parts = parts[apps_index + 1:]
            
            # 构建测试文件路径
            if len(module_parts) >= 2:
                module_name = module_parts[0]
                file_name = module_parts[-1].replace('.py', '')
                test_file = f'backend/tests/unit/test_{module_name}_{file_name}.py'
                
                if Path(test_file).exists():
                    return test_file

        return None

    def _run_tests(self, tests: List[str]) -> Dict[str, Any]:
        """
        运行测试

        Args:
            tests: 测试文件列表

        Returns:
            测试结果，如果测试失败则返回错误信息
        """
        if not tests:
            return None

        # 检查是否在Docker容器内
        in_docker = os.path.exists('/.dockerenv')

        # 构建pytest命令
        if in_docker:
            # 在Docker容器内直接运行pytest
            cmd = ['pytest', '-v', '--tb=short'] + tests
        else:
            # 在宿主机上通过docker-compose运行
            cmd = ['docker-compose', 'exec', '-T', 'backend', 'pytest', '-v', '--tb=short'] + tests

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=self.project_root
            )

            # 解析测试结果
            if result.returncode == 0:
                # 测试通过
                return None
            else:
                # 测试失败
                return {
                    'level': 'error',
                    'message': '测试失败，不允许提交（TDD红色阶段）',
                    'file': ', '.join(tests),
                    'help': (
                        f'测试失败输出：\n{result.stdout}\n\n'
                        f'错误信息：\n{result.stderr}\n\n'
                        '请修复测试失败后再提交。\n'
                        'TDD流程：红色（测试失败）→ 绿色（测试通过）→ 重构'
                    )
                }

        except subprocess.TimeoutExpired:
            return {
                'level': 'error',
                'message': '测试运行超时（5分钟）',
                'file': ', '.join(tests),
                'help': '测试运行时间过长，请检查测试代码或优化测试性能'
            }
        except FileNotFoundError:
            return {
                'level': 'warning',
                'message': 'pytest未安装或docker-compose不可用',
                'file': ', '.join(tests),
                'help': (
                    '无法运行测试。请确保：\n'
                    '1. 在Docker容器内：pytest已安装\n'
                    '2. 在宿主机上：docker-compose可用且backend服务正在运行'
                )
            }
        except Exception as e:
            return {
                'level': 'error',
                'message': f'运行测试时出错: {str(e)}',
                'file': ', '.join(tests),
                'help': '查看详细错误信息'
            }


def create_checker(config: Dict[str, Any]) -> TestRunnerChecker:
    """
    创建测试运行器检查器实例

    Args:
        config: 配置字典

    Returns:
        TestRunnerChecker实例
    """
    return TestRunnerChecker(config)

