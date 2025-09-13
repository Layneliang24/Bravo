#!/usr/bin/env python3
"""
Bravo 项目健康监控系统
功能：
- 服务健康检查
- 性能指标收集
- 异常检测和告警
- 自动恢复机制
"""

import json
import logging
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
import requests

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/health_monitor.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    """服务健康状态"""

    name: str
    status: str  # 'healthy', 'warning', 'critical', 'unknown'
    response_time: float
    last_check: str
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class SystemMetrics:
    """系统性能指标"""

    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int


class HealthMonitor:
    """健康监控器主类"""

    def __init__(self, config_path: str = "config/monitoring.json"):
        self.config = self._load_config(config_path)
        self.services = self.config.get("services", {})
        self.thresholds = self.config.get("thresholds", {})
        self.alerts = self.config.get("alerts", {})

        # 创建日志目录
        Path("logs").mkdir(exist_ok=True)
        Path("reports").mkdir(exist_ok=True)

    def _load_config(self, config_path: str) -> Dict:
        """加载监控配置"""
        default_config = {
            "services": {
                "backend": {
                    "url": "http://localhost:8000/health/",
                    "timeout": 10,
                    "critical_threshold": 5000,  # ms
                },
                "frontend": {
                    "url": "http://localhost:3000",
                    "timeout": 5,
                    "critical_threshold": 3000,
                },
                "mysql": {"host": "localhost", "port": 3306, "timeout": 3},
                "redis": {"host": "localhost", "port": 6379, "timeout": 3},
            },
            "thresholds": {
                "cpu_warning": 70,
                "cpu_critical": 90,
                "memory_warning": 80,
                "memory_critical": 95,
                "disk_warning": 85,
                "disk_critical": 95,
                "response_time_warning": 2000,
                "response_time_critical": 5000,
            },
            "alerts": {
                "slack_webhook": None,
                "email_recipients": [],
                "enable_auto_recovery": True,
            },
        }

        try:
            if Path(config_path).exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")

        return default_config

    def check_http_service(self, name: str, config: Dict) -> ServiceHealth:
        """检查HTTP服务健康状态"""
        start_time = time.time()
        try:
            response = requests.get(config["url"], timeout=config.get("timeout", 10))
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                status = "healthy"
                if response_time > config.get("critical_threshold", 5000):
                    status = "critical"
                elif response_time > self.thresholds.get("response_time_warning", 2000):
                    status = "warning"

                return ServiceHealth(
                    name=name,
                    status=status,
                    response_time=response_time,
                    last_check=datetime.now().isoformat(),
                    details={"status_code": response.status_code},
                )
            else:
                return ServiceHealth(
                    name=name,
                    status="critical",
                    response_time=response_time,
                    last_check=datetime.now().isoformat(),
                    error_message=f"HTTP {response.status_code}",
                )

        except requests.RequestException as e:
            return ServiceHealth(
                name=name,
                status="critical",
                response_time=-1,
                last_check=datetime.now().isoformat(),
                error_message=str(e),
            )

    def check_tcp_service(self, name: str, config: Dict) -> ServiceHealth:
        """检查TCP服务健康状态"""
        import socket

        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(config.get("timeout", 3))
            result = sock.connect_ex((config["host"], config["port"]))
            response_time = (time.time() - start_time) * 1000
            sock.close()

            if result == 0:
                return ServiceHealth(
                    name=name,
                    status="healthy",
                    response_time=response_time,
                    last_check=datetime.now().isoformat(),
                )
            else:
                return ServiceHealth(
                    name=name,
                    status="critical",
                    response_time=response_time,
                    last_check=datetime.now().isoformat(),
                    error_message=f"Connection failed: {result}",
                )

        except Exception as e:
            return ServiceHealth(
                name=name,
                status="critical",
                response_time=-1,
                last_check=datetime.now().isoformat(),
                error_message=str(e),
            )

    def check_all_services(self) -> List[ServiceHealth]:
        """检查所有服务健康状态"""
        results = []

        for service_name, service_config in self.services.items():
            logger.info(f"Checking service: {service_name}")

            if "url" in service_config:
                health = self.check_http_service(service_name, service_config)
            elif "host" in service_config and "port" in service_config:
                health = self.check_tcp_service(service_name, service_config)
            else:
                health = ServiceHealth(
                    name=service_name,
                    status="unknown",
                    response_time=-1,
                    last_check=datetime.now().isoformat(),
                    error_message="Invalid service configuration",
                )

            results.append(health)
            logger.info(
                f"{service_name}: {health.status} ({health.response_time:.2f}ms)"
            )

        return results

    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统性能指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 磁盘使用率
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # 网络I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

            # 进程数量
            process_count = len(psutil.pids())

            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                network_io=network_io,
                process_count=process_count,
            )

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=-1,
                memory_percent=-1,
                disk_percent=-1,
                network_io={},
                process_count=-1,
            )

    def analyze_health(
        self, services: List[ServiceHealth], metrics: SystemMetrics
    ) -> Dict[str, Any]:
        """分析健康状态并生成报告"""
        critical_services = [s for s in services if s.status == "critical"]
        warning_services = [s for s in services if s.status == "warning"]
        healthy_services = [s for s in services if s.status == "healthy"]

        # 系统健康评级
        system_status = "healthy"
        if critical_services:
            system_status = "critical"
        elif warning_services:
            system_status = "warning"
        elif (
            metrics.cpu_percent > self.thresholds["cpu_critical"]
            or metrics.memory_percent > self.thresholds["memory_critical"]
            or metrics.disk_percent > self.thresholds["disk_critical"]
        ):
            system_status = "critical"
        elif (
            metrics.cpu_percent > self.thresholds["cpu_warning"]
            or metrics.memory_percent > self.thresholds["memory_warning"]
            or metrics.disk_percent > self.thresholds["disk_warning"]
        ):
            system_status = "warning"

        return {
            "timestamp": datetime.now().isoformat(),
            "system_status": system_status,
            "services": {
                "total": len(services),
                "healthy": len(healthy_services),
                "warning": len(warning_services),
                "critical": len(critical_services),
            },
            "service_details": [asdict(s) for s in services],
            "system_metrics": asdict(metrics),
            "recommendations": self._generate_recommendations(services, metrics),
        }

    def _generate_recommendations(
        self, services: List[ServiceHealth], metrics: SystemMetrics
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 服务建议
        for service in services:
            if service.status == "critical":
                recommendations.append(f"🚨 {service.name} 服务异常，需要立即检查")
            elif service.status == "warning" and service.response_time > 2000:
                recommendations.append(
                    f"⚠️ {service.name} 响应时间过长({service.response_time:.0f}ms)，建议优化"
                )

        # 系统建议
        if metrics.cpu_percent > self.thresholds["cpu_warning"]:
            recommendations.append(f"🔥 CPU使用率过高({metrics.cpu_percent:.1f}%)，建议检查进程")

        if metrics.memory_percent > self.thresholds["memory_warning"]:
            recommendations.append(f"💾 内存使用率过高({metrics.memory_percent:.1f}%)，建议释放内存")

        if metrics.disk_percent > self.thresholds["disk_warning"]:
            recommendations.append(f"💿 磁盘使用率过高({metrics.disk_percent:.1f}%)，建议清理文件")

        return recommendations

    def save_report(self, report: Dict[str, Any]) -> str:
        """保存健康检查报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = f"reports/health_report_{timestamp}.json"

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Health report saved to {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return ""

    def send_alerts(self, report: Dict[str, Any]):
        """发送告警通知"""
        if report["system_status"] in ["warning", "critical"]:
            logger.warning(f"System status: {report['system_status']}")

            # 发送Slack通知
            if self.alerts.get("slack_webhook"):
                self._send_slack_alert(report)

            # 发送邮件通知
            if self.alerts.get("email_recipients"):
                self._send_email_alert(report)

    def _send_slack_alert(self, report: Dict[str, Any]):
        """发送Slack告警"""
        try:
            webhook_url = self.alerts["slack_webhook"]
            color = {"healthy": "good", "warning": "warning", "critical": "danger"}

            message = {
                "attachments": [
                    {
                        "color": color.get(report["system_status"], "warning"),
                        "title": f"🚨 Bravo 系统健康告警",
                        "text": f"系统状态: {report['system_status']}",
                        "fields": [
                            {
                                "title": "服务状态",
                                "value": f"健康: {report['services']['healthy']}, 警告: {report['services']['warning']}, 异常: {report['services']['critical']}",
                                "short": True,
                            },
                            {
                                "title": "系统指标",
                                "value": f"CPU: {report['system_metrics']['cpu_percent']:.1f}%, 内存: {report['system_metrics']['memory_percent']:.1f}%",
                                "short": True,
                            },
                        ],
                        "ts": int(time.time()),
                    }
                ]
            }

            requests.post(webhook_url, json=message, timeout=10)
            logger.info("Slack alert sent successfully")

        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")

    def auto_recovery(self, report: Dict[str, Any]):
        """自动恢复机制"""
        if not self.alerts.get("enable_auto_recovery", False):
            return

        for service_detail in report["service_details"]:
            if service_detail["status"] == "critical":
                service_name = service_detail["name"]
                logger.info(f"Attempting auto-recovery for {service_name}")

                # 重启服务的逻辑
                self._restart_service(service_name)

    def _restart_service(self, service_name: str):
        """重启服务"""
        try:
            if service_name == "backend":
                subprocess.run(["docker-compose", "restart", "backend"], check=True)
            elif service_name == "frontend":
                subprocess.run(["docker-compose", "restart", "frontend"], check=True)
            elif service_name in ["mysql", "redis"]:
                subprocess.run(["docker-compose", "restart", service_name], check=True)

            logger.info(f"Service {service_name} restarted successfully")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to restart {service_name}: {e}")

    def run_once(self) -> Dict[str, Any]:
        """执行一次完整的健康检查"""
        logger.info("Starting health check...")

        # 检查服务
        services = self.check_all_services()

        # 收集系统指标
        metrics = self.collect_system_metrics()

        # 分析健康状态
        report = self.analyze_health(services, metrics)

        # 保存报告
        self.save_report(report)

        # 发送告警
        self.send_alerts(report)

        # 自动恢复
        self.auto_recovery(report)

        logger.info(f"Health check completed. System status: {report['system_status']}")
        return report

    def run_continuous(self, interval: int = 60):
        """持续监控模式"""
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")

        while True:
            try:
                self.run_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Bravo 健康监控系统")
    parser.add_argument("--config", default="config/monitoring.json", help="配置文件路径")
    parser.add_argument("--continuous", action="store_true", help="持续监控模式")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔(秒)")

    args = parser.parse_args()

    monitor = HealthMonitor(args.config)

    if args.continuous:
        monitor.run_continuous(args.interval)
    else:
        report = monitor.run_once()
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
