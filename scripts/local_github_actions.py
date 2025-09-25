#!/usr/bin/env python3
"""
本地GitHub Actions仿真器
模拟GitHub Actions环境，在本地容器中运行工作流
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


class LocalGitHubActions:
    def __init__(self, workflow_file=None, event_type="pull_request"):
        self.workflow_file = workflow_file
        self.event_type = event_type
        self.workspace = Path.cwd()
        self.docker_compose_file = "docker-compose.github-actions.yml"

    def setup_environment(self):
        """设置GitHub Actions环境变量和事件文件"""
        print("🔧 设置GitHub Actions仿真环境...")

        # 创建事件文件
        event_data = {
            "action": "opened",
            "number": 1,
            "pull_request": {
                "head": {
                    "ref": "feature/infrastructure-enhancement",
                    "sha": subprocess.check_output(["git", "rev-parse", "HEAD"])
                    .decode()
                    .strip(),
                },
                "base": {
                    "ref": "dev",
                    "sha": subprocess.check_output(["git", "rev-parse", "origin/dev"])
                    .decode()
                    .strip(),
                },
            },
            "repository": {"name": "Bravo", "full_name": "Layneliang24/Bravo"},
        }

        event_file = self.workspace / ".github" / "event.json"
        event_file.parent.mkdir(exist_ok=True)
        with open(event_file, "w") as f:
            json.dump(event_data, f, indent=2)

        print(f"✅ 事件文件已创建: {event_file}")

    def start_services(self):
        """启动测试服务"""
        print("🚀 启动GitHub Actions仿真服务...")

        cmd = [
            "docker-compose",
            "-f",
            self.docker_compose_file,
            "up",
            "-d",
            "--timeout",
            "60",
        ]
        print(f"🔧 执行命令: {' '.join(cmd)}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            print("❌ Docker Compose启动超时（120秒）")
            return False

        if result.returncode != 0:
            print("❌ 启动服务失败:")
            print(f"   返回码: {result.returncode}")
            print(f"   错误输出: {result.stderr}")
            print(f"   标准输出: {result.stdout}")
            return False

        print("✅ 服务启动成功")

        # 等待MySQL就绪
        print("⏳ 等待MySQL服务就绪...")
        for i in range(30):
            mysql_ready = subprocess.run(
                [
                    "docker",
                    "exec",
                    "bravo-mysql-test",
                    "mysqladmin",
                    "ping",
                    "-h",
                    "localhost",
                    "-u",
                    "root",
                    "-proot_password",
                ],
                capture_output=True,
            )

            if mysql_ready.returncode == 0:
                print("✅ MySQL服务就绪")
                break
            time.sleep(2)
        else:
            print("❌ MySQL服务启动超时")
            return False

        return True

    def run_workflow_job(self, job_name):
        """运行特定的工作流作业"""
        print(f"🔄 运行作业: {job_name}")

        job_commands = {
            "smart-dependencies": self._run_dependencies_job,
            "frontend-tests": self._run_frontend_tests,
            "backend-tests": self._run_backend_tests,
            "e2e-tests": self._run_e2e_tests,
            "security-validation": self._run_security_validation,
            "quality-gates": self._run_quality_gates,
        }

        if job_name in job_commands:
            return job_commands[job_name]()
        else:
            print(f"❌ 未知作业: {job_name}")
            return False

    def _run_dependencies_job(self):
        """运行依赖管理作业"""
        print("📦 安装依赖...")

        # 安装前端依赖
        frontend_cmd = [
            "docker",
            "exec",
            "bravo-frontend-builder",
            "sh",
            "-c",
            "npm run build:frontend",
        ]
        result = subprocess.run(frontend_cmd)
        if result.returncode != 0:
            return False

        # 安装系统依赖
        print("🔧 安装系统依赖...")
        system_deps_cmd = [
            "docker",
            "exec",
            "bravo-backend-tester",
            "sh",
            "-c",
            "apt-get update && apt-get install -y pkg-config "
            "default-libmysqlclient-dev gcc",
        ]
        result = subprocess.run(system_deps_cmd)
        if result.returncode != 0:
            print("⚠️  系统依赖安装失败，尝试继续...")

        # 安装后端依赖
        print("🐍 安装Python依赖...")
        backend_cmd = [
            "docker",
            "exec",
            "bravo-backend-tester",
            "sh",
            "-c",
            "cd /workspace/backend && pip install -r requirements/test.txt",
        ]
        result = subprocess.run(backend_cmd)
        if result.returncode != 0:
            return False

        # 安装E2E依赖
        e2e_cmd = [
            "docker",
            "exec",
            "bravo-e2e-tester",
            "sh",
            "-c",
            "npx playwright install --with-deps",
        ]
        result = subprocess.run(e2e_cmd)
        return result.returncode == 0

    def _run_frontend_tests(self):
        """运行前端测试"""
        print("🧪 运行前端测试...")

        cmd = [
            "docker",
            "exec",
            "bravo-frontend-builder",
            "sh",
            "-c",
            "cd /workspace/frontend && npm run test:coverage",
        ]
        result = subprocess.run(cmd)
        return result.returncode == 0

    def _run_backend_tests(self):
        """运行后端测试"""
        print("🧪 运行后端测试...")

        # 设置数据库
        setup_cmd = [
            "docker",
            "exec",
            "bravo-backend-tester",
            "sh",
            "-c",
            "cd /workspace/backend && "
            "python manage.py migrate --settings=bravo.settings.test",
        ]
        subprocess.run(setup_cmd)

        # 运行测试
        test_cmd = [
            "docker",
            "exec",
            "bravo-backend-tester",
            "sh",
            "-c",
            "cd /workspace/backend && pytest --maxfail=0 " "--cov=. --cov-report=xml",
        ]
        result = subprocess.run(test_cmd)
        return result.returncode == 0

    def _run_e2e_tests(self):
        """运行E2E测试"""
        print("🧪 运行E2E测试...")

        # 启动后端服务
        backend_start = [
            "docker",
            "exec",
            "-d",
            "bravo-backend-tester",
            "sh",
            "-c",
            "cd /workspace/backend && "
            "python manage.py runserver 0.0.0.0:8000 "
            "--settings=bravo.settings.test",
        ]
        subprocess.run(backend_start)

        # 启动前端服务
        frontend_start = [
            "docker",
            "exec",
            "-d",
            "bravo-frontend-builder",
            "sh",
            "-c",
            "cd /workspace/frontend && npm run preview -- "
            "--port 3001 --host 0.0.0.0",
        ]
        subprocess.run(frontend_start)

        # 等待服务启动
        time.sleep(10)

        # 运行E2E测试
        e2e_cmd = [
            "docker",
            "exec",
            "bravo-e2e-tester",
            "sh",
            "-c",
            "cd /workspace/e2e && npx playwright test",
        ]
        result = subprocess.run(e2e_cmd)
        return result.returncode == 0

    def _run_security_validation(self):
        """运行安全验证"""
        print("🔒 运行安全验证...")

        # 运行bandit安全扫描
        bandit_cmd = [
            "docker",
            "exec",
            "bravo-backend-tester",
            "sh",
            "-c",
            "cd /workspace && pip install bandit && " "bandit -r backend/apps/ -f json",
        ]
        result = subprocess.run(bandit_cmd)
        return result.returncode == 0

    def _run_quality_gates(self):
        """运行质量门控"""
        print("🚀 运行质量门控...")

        # 运行pre-commit检查
        precommit_cmd = [
            "docker",
            "exec",
            "bravo-github-actions-runner",
            "sh",
            "-c",
            "cd /workspace && pip install pre-commit && " "pre-commit run --all-files",
        ]
        result = subprocess.run(precommit_cmd)
        return result.returncode == 0

    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")

        cmd = ["docker-compose", "-f", self.docker_compose_file, "down", "-v"]
        subprocess.run(cmd, capture_output=True)

        # 删除事件文件
        event_file = self.workspace / ".github" / "event.json"
        if event_file.exists():
            event_file.unlink()

        print("✅ 清理完成")

    def run_full_workflow(self):
        """运行完整的工作流"""
        print("🎯 开始运行完整的GitHub Actions工作流仿真")
        print(f"📁 工作空间: {self.workspace}")
        print(f"📋 事件类型: {self.event_type}")
        print("-" * 60)

        try:
            # 设置环境
            self.setup_environment()

            # 启动服务
            if not self.start_services():
                return False

            # 运行作业
            jobs = [
                "smart-dependencies",
                "frontend-tests",
                "backend-tests",
                "e2e-tests",
                "security-validation",
                "quality-gates",
            ]

            failed_jobs = []
            for job in jobs:
                print(f"\n{'=' * 20} {job.upper()} {'=' * 20}")
                if not self.run_workflow_job(job):
                    failed_jobs.append(job)
                    print(f"❌ 作业失败: {job}")
                else:
                    print(f"✅ 作业成功: {job}")

            # 总结
            print(f"\n{'=' * 60}")
            print("📊 工作流执行结果:")
            print(f"✅ 成功作业: {len(jobs) - len(failed_jobs)}/{len(jobs)}")
            if failed_jobs:
                print(f"❌ 失败作业: {', '.join(failed_jobs)}")
                return False
            else:
                print("🎉 所有作业执行成功!")
                return True

        except KeyboardInterrupt:
            print("\n⚠️ 用户中断执行")
            return False
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            return False
        finally:
            self.cleanup()


def main():
    parser = argparse.ArgumentParser(description="本地GitHub Actions仿真器")
    parser.add_argument("--workflow", help="指定工作流文件")
    parser.add_argument("--event", default="pull_request", help="事件类型")
    parser.add_argument("--job", help="只运行指定作业")

    args = parser.parse_args()

    simulator = LocalGitHubActions(args.workflow, args.event)

    if args.job:
        # 运行单个作业
        simulator.setup_environment()
        if simulator.start_services():
            success = simulator.run_workflow_job(args.job)
            simulator.cleanup()
            sys.exit(0 if success else 1)
    else:
        # 运行完整工作流
        success = simulator.run_full_workflow()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
