#!/usr/bin/env python3
"""
新Workflow架构本地测试脚本
测试原子化组件和场景触发器的有效性
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict


class WorkflowTester:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.compose_file = self.project_root / "docker-compose.github-actions.yml"

    def setup_environment(self):
        """设置测试环境"""
        print("🚀 设置本地workflow测试环境...")

        # 创建GitHub Actions事件模拟文件
        event_file = self.project_root / ".github" / "event.json"
        event_file.parent.mkdir(exist_ok=True)

        # PR事件模拟
        pr_event = {
            "action": "opened",
            "number": 1,
            "pull_request": {
                "id": 1,
                "number": 1,
                "head": {"ref": "feature/test", "sha": "abc123"},
                "base": {"ref": "dev", "sha": "def456"},
                "title": "Test PR for workflow validation",
            },
            "repository": {"name": "Bravo", "full_name": "Layneliang24/Bravo"},
        }

        with open(event_file, "w") as f:
            json.dump(pr_event, f, indent=2)

        print("✅ GitHub Actions事件文件已创建")

    def start_services(self):
        """启动测试服务"""
        print("🐳 启动测试服务...")

        try:
            # 启动基础服务
            subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    str(self.compose_file),
                    "up",
                    "-d",
                    "mysql-test",
                    "redis-test",
                ],
                check=True,
                cwd=self.project_root,
            )

            print("✅ 数据库服务已启动")

            # 等待服务就绪
            print("⏳ 等待服务就绪...")
            time.sleep(10)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 服务启动失败: {e}")
            return False

    def test_atomic_component(self, component_name: str, inputs: Dict = None) -> bool:
        """测试原子组件"""
        print(f"🧪 测试原子组件: {component_name}")

        workflow_file = self.workflows_dir / f"{component_name}.yml"
        if not workflow_file.exists():
            print(f"❌ Workflow文件不存在: {workflow_file}")
            return False

        # 使用act工具模拟GitHub Actions
        try:
            cmd = [
                "docker",
                "run",
                "--rm",
                "-it",
                "-v",
                f"{self.project_root}:/workspace",
                "-v",
                "/var/run/docker.sock:/var/run/docker.sock",
                "--network",
                "bravo-github-actions-network",
                "-w",
                "/workspace",
                "ghcr.io/catthehacker/ubuntu:act-latest",
                "bash",
                "-c",
                f"""
                # 安装act工具
                curl -s https://raw.githubusercontent.com/nektos/act/master/ \\
                install.sh | bash

                # 设置环境变量
                export GITHUB_WORKSPACE=/workspace
                export GITHUB_REPOSITORY=Layneliang24/Bravo
                export GITHUB_EVENT_NAME=workflow_call

                # 运行workflow组件
                echo "测试组件: {component_name}"
                act workflow_call -W .github/workflows/{component_name}.yml --verbose
                """,
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(f"✅ {component_name} 测试通过")
                return True
            else:
                print(f"❌ {component_name} 测试失败")
                print(f"错误输出: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            return False

    def test_scenario_workflow(self, scenario: str) -> bool:
        """测试场景workflow"""
        print(f"🎯 测试场景workflow: {scenario}")

        workflow_mapping = {
            "pr": "on-pr.yml",
            "dev": "on-push-dev.yml",
            "main": "on-push-main.yml",
        }

        workflow_file = workflow_mapping.get(scenario)
        if not workflow_file:
            print(f"❌ 未知场景: {scenario}")
            return False

        workflow_path = self.workflows_dir / workflow_file
        if not workflow_path.exists():
            print(f"❌ Workflow文件不存在: {workflow_path}")
            return False

        # 模拟不同事件类型（根据workflow文件名推断）

        try:
            # 使用简化的测试方法 - 验证workflow语法和依赖关系
            cmd = [
                "docker",
                "run",
                "--rm",
                "-v",
                f"{self.project_root}:/workspace",
                "-w",
                "/workspace",
                "python:3.11-slim",
                "python",
                "-c",
                f"""
import yaml
import sys

# 读取workflow文件
with open('.github/workflows/{workflow_file}', 'r') as f:
    workflow = yaml.safe_load(f)

print(f"✅ {scenario} workflow语法正确")

# 检查jobs依赖关系
jobs = workflow.get('jobs', {{}})
print(f"📋 包含 {{len(jobs)}} 个jobs:")

for job_name, job_config in jobs.items():
    needs = job_config.get('needs', [])
    if isinstance(needs, str):
        needs = [needs]
    elif isinstance(needs, list):
        pass
    else:
        needs = []

    uses = job_config.get('uses', '')
    if uses:
        print(f"  🧩 {{job_name}} -> {{uses}} (依赖: {{needs}})")
    else:
        print(f"  🔧 {{job_name}} (依赖: {{needs}})")

print(f"✅ {scenario} workflow结构验证通过")
                """,
            ]

            result = subprocess.run(
                cmd, cwd=self.project_root, capture_output=True, text=True
            )

            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print(f"❌ {scenario} workflow验证失败")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ 测试执行异常: {e}")
            return False

    def test_cache_strategy(self) -> bool:
        """测试缓存策略"""
        print("💾 测试缓存策略...")

        try:
            # 启动前端构建容器测试缓存
            cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "run",
                "--rm",
                "frontend-builder",
                "sh",
                "-c",
                """
                echo "🔍 测试前端依赖缓存..."

                # 模拟首次安装
                cd /workspace/frontend
                if [ -f "package.json" ]; then
                    echo "📦 安装依赖 (首次)..."
                    time npm ci --prefer-offline --no-audit
                    echo "✅ 首次安装完成"

                    # 模拟缓存命中
                    echo "🚀 模拟缓存命中..."
                    time npm ci --prefer-offline --no-audit
                    echo "✅ 缓存测试完成"
                else
                    echo "⚠️  package.json不存在，跳过前端缓存测试"
                fi
                """,
            ]

            result = subprocess.run(cmd, cwd=self.project_root)

            if result.returncode == 0:
                print("✅ 缓存策略测试通过")
                return True
            else:
                print("❌ 缓存策略测试失败")
                return False

        except Exception as e:
            print(f"❌ 缓存测试异常: {e}")
            return False

    def test_parallel_execution(self) -> bool:
        """测试并行执行能力"""
        print("⚡ 测试并行执行能力...")

        try:
            # 同时启动多个测试容器
            print("🚀 启动并行测试容器...")

            # 后端测试
            backend_cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "run",
                "--rm",
                "-d",
                "backend-tester",
                "sh",
                "-c",
                """
                echo "🐍 后端并行测试开始..."
                cd /workspace/backend
                if [ -f "requirements/test.txt" ]; then
                    pip install -r requirements/test.txt > /dev/null 2>&1
                    echo "✅ 后端依赖安装完成"
                fi
                sleep 5
                echo "✅ 后端并行测试完成"
                """,
            ]

            # 前端测试
            frontend_cmd = [
                "docker-compose",
                "-f",
                str(self.compose_file),
                "run",
                "--rm",
                "-d",
                "frontend-builder",
                "sh",
                "-c",
                """
                echo "🎨 前端并行测试开始..."
                cd /workspace/frontend
                if [ -f "package.json" ]; then
                    npm ci --prefer-offline --no-audit > /dev/null 2>&1
                    echo "✅ 前端依赖安装完成"
                fi
                sleep 3
                echo "✅ 前端并行测试完成"
                """,
            ]

            # 启动并行测试
            backend_proc = subprocess.Popen(backend_cmd, cwd=self.project_root)
            frontend_proc = subprocess.Popen(frontend_cmd, cwd=self.project_root)

            # 等待完成
            backend_result = backend_proc.wait()
            frontend_result = frontend_proc.wait()

            if backend_result == 0 and frontend_result == 0:
                print("✅ 并行执行测试通过")
                return True
            else:
                print("❌ 并行执行测试失败")
                return False

        except Exception as e:
            print(f"❌ 并行测试异常: {e}")
            return False

    def cleanup(self):
        """清理测试环境"""
        print("🧹 清理测试环境...")

        try:
            subprocess.run(
                ["docker-compose", "-f", str(self.compose_file), "down", "-v"],
                cwd=self.project_root,
                capture_output=True,
            )

            print("✅ 测试环境已清理")

        except Exception as e:
            print(f"⚠️  清理过程中出现警告: {e}")

    def run_full_test_suite(self):
        """运行完整测试套件"""
        print("🎯 开始新Workflow架构完整测试")
        print("=" * 50)

        # 设置环境
        self.setup_environment()

        # 启动服务
        if not self.start_services():
            return False

        test_results = []

        try:
            # 测试原子组件
            atomic_components = [
                "setup-cache",
                "test-unit-backend",
                "test-unit-frontend",
                "test-integration",
                "test-e2e-smoke",
                "quality-security",
                "quality-performance",
                "quality-coverage",
            ]

            print("\n🧩 测试原子组件...")
            for component in atomic_components:
                if self.workflows_dir.joinpath(f"{component}.yml").exists():
                    result = self.test_atomic_component(component)
                    test_results.append((f"原子组件-{component}", result))
                else:
                    print(f"⚠️  跳过不存在的组件: {component}")

            # 测试场景workflow
            print("\n🎯 测试场景workflow...")
            scenarios = ["pr", "dev"]  # main workflow还未创建
            for scenario in scenarios:
                result = self.test_scenario_workflow(scenario)
                test_results.append((f"场景-{scenario}", result))

            # 测试缓存策略
            print("\n💾 测试缓存策略...")
            cache_result = self.test_cache_strategy()
            test_results.append(("缓存策略", cache_result))

            # 测试并行执行
            print("\n⚡ 测试并行执行...")
            parallel_result = self.test_parallel_execution()
            test_results.append(("并行执行", parallel_result))

        finally:
            self.cleanup()

        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总:")
        print("=" * 50)

        passed = 0
        failed = 0

        for test_name, result in test_results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name:<20} {status}")
            if result:
                passed += 1
            else:
                failed += 1

        print(f"\n总计: {passed} 通过, {failed} 失败")

        if failed == 0:
            print("🎉 所有测试通过！新Workflow架构验证成功！")
            return True
        else:
            print("⚠️  部分测试失败，需要进一步调试")
            return False


def main():
    parser = argparse.ArgumentParser(description="测试新Workflow架构")
    parser.add_argument("--component", help="测试特定组件")
    parser.add_argument("--scenario", help="测试特定场景")
    parser.add_argument("--cache-only", action="store_true", help="只测试缓存策略")
    parser.add_argument("--parallel-only", action="store_true", help="只测试并行执行")

    args = parser.parse_args()

    tester = WorkflowTester()

    if args.component:
        tester.setup_environment()
        tester.start_services()
        result = tester.test_atomic_component(args.component)
        tester.cleanup()
        sys.exit(0 if result else 1)

    elif args.scenario:
        result = tester.test_scenario_workflow(args.scenario)
        sys.exit(0 if result else 1)

    elif args.cache_only:
        tester.setup_environment()
        tester.start_services()
        result = tester.test_cache_strategy()
        tester.cleanup()
        sys.exit(0 if result else 1)

    elif args.parallel_only:
        tester.setup_environment()
        tester.start_services()
        result = tester.test_parallel_execution()
        tester.cleanup()
        sys.exit(0 if result else 1)

    else:
        # 运行完整测试套件
        result = tester.run_full_test_suite()
        sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()
