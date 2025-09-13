#!/usr/bin/env python3
"""
Bravo 基础设施管理器
功能：
- 一键部署开发环境
- 健康检查和监控
- 安全扫描
- 性能测试
- 日志分析
- 备份恢复
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class InfrastructureManager:
    """基础设施管理器"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.scripts_dir = self.project_root / "scripts"
        self.logs_dir = self.project_root / "logs"
        self.reports_dir = self.project_root / "reports"

        # 确保目录存在
        for directory in [self.logs_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)

    def run_command(
        self, cmd: List[str], cwd: Optional[Path] = None, timeout: int = 300
    ) -> subprocess.CompletedProcess:
        """安全地运行系统命令"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return result
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {' '.join(cmd)}")
            raise
        except Exception as e:
            logger.error(f"Command failed: {' '.join(cmd)}, Error: {e}")
            raise

    def check_prerequisites(self) -> Dict[str, bool]:
        """检查系统依赖和前置条件"""
        logger.info("🔍 Checking prerequisites...")

        checks = {
            "docker": False,
            "docker-compose": False,
            "node": False,
            "npm": False,
            "python": False,
            "git": False,
        }

        # 检查 Docker
        try:
            result = self.run_command(["docker", "--version"], timeout=10)
            checks["docker"] = result.returncode == 0
        except:
            pass

        # 检查 Docker Compose
        try:
            result = self.run_command(["docker-compose", "--version"], timeout=10)
            checks["docker-compose"] = result.returncode == 0
        except:
            pass

        # 检查 Node.js
        try:
            result = self.run_command(["node", "--version"], timeout=10)
            checks["node"] = result.returncode == 0
        except:
            pass

        # 检查 npm
        try:
            result = self.run_command(["npm", "--version"], timeout=10)
            checks["npm"] = result.returncode == 0
        except:
            pass

        # 检查 Python
        try:
            result = self.run_command(["python", "--version"], timeout=10)
            if result.returncode != 0:
                result = self.run_command(["python3", "--version"], timeout=10)
            checks["python"] = result.returncode == 0
        except:
            pass

        # 检查 Git
        try:
            result = self.run_command(["git", "--version"], timeout=10)
            checks["git"] = result.returncode == 0
        except:
            pass

        # 输出检查结果
        for tool, available in checks.items():
            status = "✅" if available else "❌"
            logger.info(f"{status} {tool}")

        return checks

    def setup_development_environment(self, mode: str = "docker") -> bool:
        """设置开发环境"""
        logger.info(f"🚀 Setting up development environment (mode: {mode})...")

        try:
            if mode == "docker":
                return self._setup_docker_environment()
            elif mode == "local":
                return self._setup_local_environment()
            else:
                logger.error(f"Unknown setup mode: {mode}")
                return False
        except Exception as e:
            logger.error(f"Failed to setup development environment: {e}")
            return False

    def _setup_docker_environment(self) -> bool:
        """设置 Docker 开发环境"""
        logger.info("🐳 Setting up Docker development environment...")

        # 停止现有容器
        logger.info("Stopping existing containers...")
        self.run_command(["docker-compose", "down"])

        # 构建镜像
        logger.info("Building Docker images...")
        result = self.run_command(["docker-compose", "build"], timeout=600)
        if result.returncode != 0:
            logger.error("Failed to build Docker images")
            return False

        # 启动服务
        logger.info("Starting services...")
        result = self.run_command(["docker-compose", "up", "-d"], timeout=300)
        if result.returncode != 0:
            logger.error("Failed to start services")
            return False

        # 等待服务启动
        logger.info("Waiting for services to be ready...")
        time.sleep(30)

        # 运行数据库迁移
        logger.info("Running database migrations...")
        result = self.run_command(
            [
                "docker-compose",
                "exec",
                "-T",
                "backend",
                "python",
                "manage.py",
                "migrate",
            ]
        )

        if result.returncode != 0:
            logger.warning("Database migration failed, but continuing...")

        logger.info("✅ Docker environment setup completed")
        return True

    def _setup_local_environment(self) -> bool:
        """设置本地开发环境"""
        logger.info("💻 Setting up local development environment...")

        # 安装后端依赖
        logger.info("Installing backend dependencies...")
        backend_dir = self.project_root / "backend"
        if backend_dir.exists():
            result = self.run_command(
                ["pip", "install", "-r", "requirements/local.txt"], cwd=backend_dir
            )
            if result.returncode != 0:
                logger.error("Failed to install backend dependencies")
                return False

        # 安装前端依赖
        logger.info("Installing frontend dependencies...")
        frontend_dir = self.project_root / "frontend"
        if frontend_dir.exists():
            result = self.run_command(["npm", "install"], cwd=frontend_dir)
            if result.returncode != 0:
                logger.error("Failed to install frontend dependencies")
                return False

        # 安装E2E测试依赖
        logger.info("Installing E2E dependencies...")
        e2e_dir = self.project_root / "e2e"
        if e2e_dir.exists():
            result = self.run_command(["npm", "install"], cwd=e2e_dir)
            if result.returncode != 0:
                logger.error("Failed to install E2E dependencies")
                return False

        logger.info("✅ Local environment setup completed")
        return True

    def run_health_check(self) -> Dict[str, Any]:
        """运行健康检查"""
        logger.info("🏥 Running health check...")

        try:
            # 导入健康监控模块
            sys.path.append(str(self.scripts_dir))
            from monitoring.health_monitor import HealthMonitor

            monitor = HealthMonitor()
            report = monitor.run_once()

            logger.info(f"Health check completed. Status: {report['system_status']}")
            return report

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"system_status": "unknown", "error": str(e)}

    def run_security_scan(self) -> Dict[str, Any]:
        """运行安全扫描"""
        logger.info("🔒 Running security scan...")

        try:
            # 导入安全扫描模块
            sys.path.append(str(self.scripts_dir))
            from security.security_scanner import SecurityScanner

            scanner = SecurityScanner(str(self.project_root))
            report = scanner.run_full_scan()
            report_path = scanner.save_report(report)

            logger.info(f"Security scan completed. Found {report.total_issues} issues.")

            return {
                "total_issues": report.total_issues,
                "critical_count": report.critical_count,
                "high_count": report.high_count,
                "report_path": report_path,
            }

        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return {"error": str(e)}

    def run_performance_test(self) -> Dict[str, Any]:
        """运行性能测试"""
        logger.info("⚡ Running performance test...")

        try:
            # 检查前端构建
            frontend_dir = self.project_root / "frontend"
            if frontend_dir.exists():
                logger.info("Building frontend for performance test...")
                result = self.run_command(["npm", "run", "build"], cwd=frontend_dir)
                if result.returncode != 0:
                    logger.warning("Frontend build failed")

            # 运行 Lighthouse CI
            if (self.project_root / "lighthouserc.json").exists():
                logger.info("Running Lighthouse CI...")
                result = self.run_command(["lhci", "autorun"])

                lighthouse_results = {}
                if result.returncode == 0:
                    # 尝试读取 Lighthouse 结果
                    lighthouse_dir = self.project_root / ".lighthouseci"
                    if lighthouse_dir.exists():
                        for report_file in lighthouse_dir.glob("lhr-*.json"):
                            try:
                                with open(report_file, "r") as f:
                                    data = json.load(f)
                                    lighthouse_results[report_file.name] = {
                                        "performance": data.get("categories", {})
                                        .get("performance", {})
                                        .get("score", 0)
                                        * 100,
                                        "accessibility": data.get("categories", {})
                                        .get("accessibility", {})
                                        .get("score", 0)
                                        * 100,
                                        "best-practices": data.get("categories", {})
                                        .get("best-practices", {})
                                        .get("score", 0)
                                        * 100,
                                        "seo": data.get("categories", {})
                                        .get("seo", {})
                                        .get("score", 0)
                                        * 100,
                                    }
                            except Exception as e:
                                logger.warning(
                                    f"Failed to parse Lighthouse report {report_file}: {e}"
                                )

                return {
                    "lighthouse_success": result.returncode == 0,
                    "lighthouse_results": lighthouse_results,
                }
            else:
                logger.warning("lighthouserc.json not found, skipping Lighthouse test")
                return {"lighthouse_success": False, "reason": "No lighthouse config"}

        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            return {"error": str(e)}

    def run_tests(self, test_type: str = "all") -> Dict[str, Any]:
        """运行测试套件"""
        logger.info(f"🧪 Running tests (type: {test_type})...")

        results = {}

        try:
            # 前端测试
            if test_type in ["all", "frontend"]:
                frontend_dir = self.project_root / "frontend"
                if frontend_dir.exists():
                    logger.info("Running frontend tests...")
                    result = self.run_command(["npm", "test"], cwd=frontend_dir)
                    results["frontend"] = {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr,
                    }

            # 后端测试
            if test_type in ["all", "backend"]:
                backend_dir = self.project_root / "backend"
                if backend_dir.exists():
                    logger.info("Running backend tests...")
                    result = self.run_command(
                        ["python", "-m", "pytest", "tests/", "-v"], cwd=backend_dir
                    )
                    results["backend"] = {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr,
                    }

            # E2E测试
            if test_type in ["all", "e2e"]:
                e2e_dir = self.project_root / "e2e"
                if e2e_dir.exists():
                    logger.info("Running E2E tests...")
                    result = self.run_command(["npm", "test"], cwd=e2e_dir)
                    results["e2e"] = {
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr,
                    }

            logger.info("Tests completed")
            return results

        except Exception as e:
            logger.error(f"Tests failed: {e}")
            return {"error": str(e)}

    def generate_infrastructure_report(self) -> str:
        """生成基础设施状态报告"""
        logger.info("📊 Generating infrastructure report...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"infrastructure_report_{timestamp}.json"

        # 收集各种信息
        report = {
            "timestamp": datetime.now().isoformat(),
            "prerequisites": self.check_prerequisites(),
            "health_check": self.run_health_check(),
            "security_scan": self.run_security_scan(),
            "performance_test": self.run_performance_test(),
            "test_results": self.run_tests(),
        }

        # 保存报告
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"Infrastructure report saved to {report_path}")
            return str(report_path)

        except Exception as e:
            logger.error(f"Failed to save infrastructure report: {e}")
            return ""

    def cleanup(self):
        """清理临时文件和资源"""
        logger.info("🧹 Cleaning up...")

        try:
            # 停止 Docker 容器
            self.run_command(["docker-compose", "down"])

            # 清理构建缓存
            self.run_command(["docker", "system", "prune", "-f"])

            # 清理 npm 缓存
            frontend_dir = self.project_root / "frontend"
            if frontend_dir.exists():
                self.run_command(["npm", "cache", "clean", "--force"], cwd=frontend_dir)

            logger.info("✅ Cleanup completed")

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Bravo 基础设施管理器")
    parser.add_argument("--project-root", default=".", help="项目根目录")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 检查前置条件
    subparsers.add_parser("check", help="检查系统前置条件")

    # 设置环境
    setup_parser = subparsers.add_parser("setup", help="设置开发环境")
    setup_parser.add_argument(
        "--mode", choices=["docker", "local"], default="docker", help="设置模式"
    )

    # 健康检查
    subparsers.add_parser("health", help="运行健康检查")

    # 安全扫描
    subparsers.add_parser("security", help="运行安全扫描")

    # 性能测试
    subparsers.add_parser("performance", help="运行性能测试")

    # 运行测试
    test_parser = subparsers.add_parser("test", help="运行测试套件")
    test_parser.add_argument(
        "--type",
        choices=["all", "frontend", "backend", "e2e"],
        default="all",
        help="测试类型",
    )

    # 生成报告
    subparsers.add_parser("report", help="生成基础设施报告")

    # 清理
    subparsers.add_parser("cleanup", help="清理临时文件")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = InfrastructureManager(args.project_root)

    try:
        if args.command == "check":
            checks = manager.check_prerequisites()
            missing = [tool for tool, available in checks.items() if not available]
            if missing:
                print(f"❌ Missing tools: {', '.join(missing)}")
                sys.exit(1)
            else:
                print("✅ All prerequisites are available")

        elif args.command == "setup":
            success = manager.setup_development_environment(args.mode)
            if not success:
                sys.exit(1)

        elif args.command == "health":
            report = manager.run_health_check()
            print(json.dumps(report, indent=2, ensure_ascii=False))

        elif args.command == "security":
            report = manager.run_security_scan()
            print(json.dumps(report, indent=2, ensure_ascii=False))

        elif args.command == "performance":
            report = manager.run_performance_test()
            print(json.dumps(report, indent=2, ensure_ascii=False))

        elif args.command == "test":
            results = manager.run_tests(args.type)
            print(json.dumps(results, indent=2, ensure_ascii=False))

        elif args.command == "report":
            report_path = manager.generate_infrastructure_report()
            print(f"Report generated: {report_path}")

        elif args.command == "cleanup":
            manager.cleanup()

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
