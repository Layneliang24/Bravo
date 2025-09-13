#!/usr/bin/env python3
"""
Bravo 项目安全扫描系统
功能：
- 依赖漏洞扫描
- 代码安全检查
- 配置安全审计
- 安全报告生成
- 自动修复建议
"""

import json
import subprocess
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityIssue:
    """安全问题数据类"""
    severity: str  # 'critical', 'high', 'medium', 'low', 'info'
    category: str  # 'dependency', 'code', 'config', 'secret'
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    cve_id: Optional[str] = None
    fix_suggestion: Optional[str] = None
    references: Optional[List[str]] = None

@dataclass
class SecurityReport:
    """安全报告数据类"""
    timestamp: str
    scan_duration: float
    total_issues: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    issues: List[SecurityIssue]
    scan_summary: Dict[str, Any]

class SecurityScanner:
    """安全扫描器主类"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.report_dir = self.project_root / "reports" / "security"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 扫描配置
        self.scan_config = {
            "python": {
                "enabled": True,
                "tools": ["bandit", "safety", "semgrep"],
                "paths": ["backend/"]
            },
            "javascript": {
                "enabled": True,
                "tools": ["npm-audit", "yarn-audit", "semgrep"],
                "paths": ["frontend/", "e2e/"]
            },
            "docker": {
                "enabled": True,
                "tools": ["hadolint", "trivy"],
                "paths": ["**/Dockerfile*"]
            },
            "secrets": {
                "enabled": True,
                "tools": ["detect-secrets", "gitleaks"],
                "paths": ["."]
            },
            "infrastructure": {
                "enabled": True,
                "tools": ["checkov", "tfsec"],
                "paths": ["docker-compose*.yml", ".github/"]
            }
        }
    
    def run_bandit_scan(self) -> List[SecurityIssue]:
        """运行 Bandit Python 安全扫描"""
        issues = []
        try:
            logger.info("Running Bandit security scan...")
            
            cmd = [
                "bandit", 
                "-r", str(self.project_root / "backend"),
                "-f", "json",
                "-o", "/tmp/bandit_report.json",
                "--skip", "B101,B601"  # 跳过一些误报
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if Path("/tmp/bandit_report.json").exists():
                with open("/tmp/bandit_report.json", 'r') as f:
                    report = json.load(f)
                
                for result_item in report.get('results', []):
                    issue = SecurityIssue(
                        severity=result_item.get('issue_severity', 'medium').lower(),
                        category='code',
                        title=result_item.get('test_name', ''),
                        description=result_item.get('issue_text', ''),
                        file_path=result_item.get('filename', ''),
                        line_number=result_item.get('line_number'),
                        fix_suggestion=result_item.get('more_info', ''),
                        references=[result_item.get('more_info', '')] if result_item.get('more_info') else None
                    )
                    issues.append(issue)
                    
                logger.info(f"Bandit found {len(issues)} issues")
                
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
            
        return issues
    
    def run_safety_scan(self) -> List[SecurityIssue]:
        """运行 Safety 依赖漏洞扫描"""
        issues = []
        try:
            logger.info("Running Safety dependency scan...")
            
            cmd = ["safety", "check", "--json"]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root / "backend")
            
            if result.returncode != 0 and result.stdout:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    for vuln in vulnerabilities:
                        issue = SecurityIssue(
                            severity='high' if vuln.get('vulnerability_id', '').startswith('CVE') else 'medium',
                            category='dependency',
                            title=f"Vulnerable dependency: {vuln.get('package', '')}",
                            description=vuln.get('advisory', ''),
                            cve_id=vuln.get('vulnerability_id'),
                            fix_suggestion=f"Upgrade to version {vuln.get('analyzed_version', '')} or later",
                            references=[vuln.get('more_info_url')] if vuln.get('more_info_url') else None
                        )
                        issues.append(issue)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse Safety output")
                    
            logger.info(f"Safety found {len(issues)} vulnerabilities")
            
        except Exception as e:
            logger.error(f"Safety scan failed: {e}")
            
        return issues
    
    def run_npm_audit_scan(self) -> List[SecurityIssue]:
        """运行 npm audit 前端依赖扫描"""
        issues = []
        
        for js_dir in ["frontend", "e2e"]:
            js_path = self.project_root / js_dir
            if not (js_path / "package.json").exists():
                continue
                
            try:
                logger.info(f"Running npm audit in {js_dir}...")
                
                cmd = ["npm", "audit", "--json"]
                result = subprocess.run(cmd, capture_output=True, text=True, cwd=js_path)
                
                if result.stdout:
                    try:
                        audit_data = json.loads(result.stdout)
                        
                        for vuln_id, vuln in audit_data.get('vulnerabilities', {}).items():
                            severity_map = {
                                'critical': 'critical',
                                'high': 'high', 
                                'moderate': 'medium',
                                'low': 'low',
                                'info': 'info'
                            }
                            
                            issue = SecurityIssue(
                                severity=severity_map.get(vuln.get('severity', 'medium'), 'medium'),
                                category='dependency',
                                title=f"Vulnerable npm package: {vuln.get('name', vuln_id)}",
                                description=vuln.get('title', ''),
                                file_path=f"{js_dir}/package.json",
                                fix_suggestion=f"Run 'npm audit fix' in {js_dir}/ directory",
                                references=vuln.get('url', []) if isinstance(vuln.get('url'), list) else [vuln.get('url')] if vuln.get('url') else None
                            )
                            issues.append(issue)
                            
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse npm audit output for {js_dir}")
                        
                logger.info(f"npm audit found {len([i for i in issues if js_dir in str(i.file_path)])} issues in {js_dir}")
                
            except Exception as e:
                logger.error(f"npm audit scan failed for {js_dir}: {e}")
                
        return issues
    
    def run_secret_scan(self) -> List[SecurityIssue]:
        """运行密钥泄漏扫描"""
        issues = []
        
        # 定义敏感模式
        secret_patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)[\s\'"]*[:=][\s\'"]*[a-zA-Z0-9_-]{20,}',
            'password': r'(?i)(password|passwd|pwd)[\s\'"]*[:=][\s\'"]*[^\s\'"]{8,}',
            'secret': r'(?i)(secret|token)[\s\'"]*[:=][\s\'"]*[a-zA-Z0-9_-]{20,}',
            'private_key': r'-----BEGIN [A-Z]+ PRIVATE KEY-----',
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'github_token': r'ghp_[a-zA-Z0-9]{36}',
            'jwt_token': r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
        }
        
        import re
        
        # 扫描文件
        for pattern_name, pattern in secret_patterns.items():
            for file_path in self.project_root.rglob("*"):
                if (file_path.is_file() and 
                    not any(exclude in str(file_path) for exclude in ['.git', 'node_modules', '__pycache__', '.venv']) and
                    file_path.suffix in ['.py', '.js', '.ts', '.json', '.yml', '.yaml', '.env', '.txt']):
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, 1):
                                if re.search(pattern, line):
                                    issue = SecurityIssue(
                                        severity='critical',
                                        category='secret',
                                        title=f"Potential {pattern_name.replace('_', ' ')} exposed",
                                        description=f"Found potential {pattern_name.replace('_', ' ')} in {file_path.name}",
                                        file_path=str(file_path.relative_to(self.project_root)),
                                        line_number=line_num,
                                        fix_suggestion="Remove or move to environment variables/secure storage"
                                    )
                                    issues.append(issue)
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        logger.info(f"Secret scan found {len(issues)} potential secrets")
        return issues
    
    def run_docker_scan(self) -> List[SecurityIssue]:
        """运行 Docker 安全扫描"""
        issues = []
        
        # 查找所有 Dockerfile
        dockerfiles = list(self.project_root.rglob("Dockerfile*"))
        
        for dockerfile in dockerfiles:
            try:
                logger.info(f"Scanning Dockerfile: {dockerfile}")
                
                # 简单的 Dockerfile 安全检查
                with open(dockerfile, 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # 检查常见安全问题
                    if line.startswith('USER root') or 'USER 0' in line:
                        issue = SecurityIssue(
                            severity='medium',
                            category='config',
                            title="Running container as root user",
                            description="Container is configured to run as root user",
                            file_path=str(dockerfile.relative_to(self.project_root)),
                            line_number=line_num,
                            fix_suggestion="Create and use a non-root user"
                        )
                        issues.append(issue)
                    
                    if 'ADD' in line and ('http://' in line or 'https://' in line):
                        issue = SecurityIssue(
                            severity='medium',
                            category='config',
                            title="Using ADD with remote URL",
                            description="ADD instruction with remote URL can be insecure",
                            file_path=str(dockerfile.relative_to(self.project_root)),
                            line_number=line_num,
                            fix_suggestion="Use COPY instead of ADD for local files"
                        )
                        issues.append(issue)
                    
                    if '--no-check-certificate' in line or '--insecure' in line:
                        issue = SecurityIssue(
                            severity='high',
                            category='config',
                            title="Insecure download detected",
                            description="Downloading without certificate verification",
                            file_path=str(dockerfile.relative_to(self.project_root)),
                            line_number=line_num,
                            fix_suggestion="Remove insecure download flags"
                        )
                        issues.append(issue)
                        
            except Exception as e:
                logger.error(f"Docker scan failed for {dockerfile}: {e}")
        
        logger.info(f"Docker scan found {len(issues)} issues")
        return issues
    
    def run_config_audit(self) -> List[SecurityIssue]:
        """运行配置安全审计"""
        issues = []
        
        # 检查敏感配置文件
        config_files = [
            "docker-compose*.yml",
            ".env*",
            "config/*.json",
            "backend/bravo/settings/*.py"
        ]
        
        for pattern in config_files:
            for config_file in self.project_root.rglob(pattern):
                if config_file.is_file():
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            
                        # 检查硬编码密码
                        if any(keyword in content for keyword in ['password=', 'secret=', 'key=']):
                            if not any(safe in content for safe in ['${', 'env:', 'environ']):
                                issue = SecurityIssue(
                                    severity='high',
                                    category='config',
                                    title="Hardcoded credentials in config",
                                    description="Configuration file contains hardcoded credentials",
                                    file_path=str(config_file.relative_to(self.project_root)),
                                    fix_suggestion="Use environment variables for sensitive data"
                                )
                                issues.append(issue)
                        
                        # 检查调试模式
                        if 'debug=true' in content or 'debug: true' in content:
                            issue = SecurityIssue(
                                severity='medium',
                                category='config',
                                title="Debug mode enabled",
                                description="Debug mode should be disabled in production",
                                file_path=str(config_file.relative_to(self.project_root)),
                                fix_suggestion="Set DEBUG=False in production"
                            )
                            issues.append(issue)
                            
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        logger.info(f"Config audit found {len(issues)} issues")
        return issues
    
    def generate_report(self, all_issues: List[SecurityIssue]) -> SecurityReport:
        """生成安全报告"""
        timestamp = datetime.now().isoformat()
        
        # 统计各严重程度的问题数量
        severity_counts = {
            'critical': len([i for i in all_issues if i.severity == 'critical']),
            'high': len([i for i in all_issues if i.severity == 'high']),
            'medium': len([i for i in all_issues if i.severity == 'medium']),
            'low': len([i for i in all_issues if i.severity == 'low']),
            'info': len([i for i in all_issues if i.severity == 'info'])
        }
        
        # 按类别统计
        category_counts = {}
        for issue in all_issues:
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        scan_summary = {
            'severity_distribution': severity_counts,
            'category_distribution': category_counts,
            'recommendations': self._generate_recommendations(all_issues)
        }
        
        return SecurityReport(
            timestamp=timestamp,
            scan_duration=0,  # Will be updated by caller
            total_issues=len(all_issues),
            critical_count=severity_counts['critical'],
            high_count=severity_counts['high'],
            medium_count=severity_counts['medium'],
            low_count=severity_counts['low'],
            info_count=severity_counts['info'],
            issues=all_issues,
            scan_summary=scan_summary
        )
    
    def _generate_recommendations(self, issues: List[SecurityIssue]) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        critical_issues = [i for i in issues if i.severity == 'critical']
        high_issues = [i for i in issues if i.severity == 'high']
        
        if critical_issues:
            recommendations.append("🚨 立即修复所有严重(critical)安全问题")
        
        if high_issues:
            recommendations.append("⚠️ 优先修复高危(high)安全问题")
        
        # 按类别提供建议
        secret_issues = [i for i in issues if i.category == 'secret']
        if secret_issues:
            recommendations.append("🔐 移除硬编码的密钥和敏感信息")
        
        dependency_issues = [i for i in issues if i.category == 'dependency']
        if dependency_issues:
            recommendations.append("📦 更新存在漏洞的依赖包")
        
        config_issues = [i for i in issues if i.category == 'config']
        if config_issues:
            recommendations.append("⚙️ 加强配置文件安全性")
        
        return recommendations
    
    def save_report(self, report: SecurityReport) -> str:
        """保存安全报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.report_dir / f"security_report_{timestamp}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
            
            # 同时保存简化的HTML报告
            html_path = self.report_dir / f"security_report_{timestamp}.html"
            self._save_html_report(report, html_path)
            
            logger.info(f"Security report saved to {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"Failed to save security report: {e}")
            return ""
    
    def _save_html_report(self, report: SecurityReport, html_path: Path):
        """保存HTML格式的安全报告"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bravo Security Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
                .critical {{ color: #d32f2f; }}
                .high {{ color: #f57c00; }}
                .medium {{ color: #fbc02d; }}
                .low {{ color: #388e3c; }}
                .issue {{ margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }}
                .issue.critical {{ border-left-color: #d32f2f; }}
                .issue.high {{ border-left-color: #f57c00; }}
                .issue.medium {{ border-left-color: #fbc02d; }}
                .issue.low {{ border-left-color: #388e3c; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 Bravo Security Report</h1>
                <p><strong>Generated:</strong> {report.timestamp}</p>
                <p><strong>Total Issues:</strong> {report.total_issues}</p>
                <p>
                    <span class="critical">Critical: {report.critical_count}</span> |
                    <span class="high">High: {report.high_count}</span> |
                    <span class="medium">Medium: {report.medium_count}</span> |
                    <span class="low">Low: {report.low_count}</span>
                </p>
            </div>
            
            <h2>🔍 Issues Found</h2>
        """
        
        for issue in report.issues:
            html_content += f"""
            <div class="issue {issue.severity}">
                <h3>{issue.title}</h3>
                <p><strong>Severity:</strong> {issue.severity.upper()}</p>
                <p><strong>Category:</strong> {issue.category}</p>
                <p><strong>Description:</strong> {issue.description}</p>
                {f'<p><strong>File:</strong> {issue.file_path}:{issue.line_number}</p>' if issue.file_path else ''}
                {f'<p><strong>Fix Suggestion:</strong> {issue.fix_suggestion}</p>' if issue.fix_suggestion else ''}
            </div>
            """
        
        html_content += """
            </body>
        </html>
        """
        
        try:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            logger.error(f"Failed to save HTML report: {e}")
    
    def run_full_scan(self) -> SecurityReport:
        """运行完整安全扫描"""
        start_time = datetime.now()
        logger.info("Starting full security scan...")
        
        all_issues = []
        
        # 运行各种扫描
        try:
            all_issues.extend(self.run_bandit_scan())
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
        
        try:
            all_issues.extend(self.run_safety_scan())
        except Exception as e:
            logger.error(f"Safety scan failed: {e}")
        
        try:
            all_issues.extend(self.run_npm_audit_scan())
        except Exception as e:
            logger.error(f"npm audit scan failed: {e}")
        
        try:
            all_issues.extend(self.run_secret_scan())
        except Exception as e:
            logger.error(f"Secret scan failed: {e}")
        
        try:
            all_issues.extend(self.run_docker_scan())
        except Exception as e:
            logger.error(f"Docker scan failed: {e}")
        
        try:
            all_issues.extend(self.run_config_audit())
        except Exception as e:
            logger.error(f"Config audit failed: {e}")
        
        # 生成报告
        report = self.generate_report(all_issues)
        report.scan_duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Security scan completed. Found {report.total_issues} issues.")
        return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bravo 安全扫描系统')
    parser.add_argument('--project-root', default='.', help='项目根目录')
    parser.add_argument('--output', help='输出报告文件路径')
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.project_root)
    report = scanner.run_full_scan()
    
    # 保存报告
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(asdict(report), f, indent=2, ensure_ascii=False, default=str)
        print(f"Report saved to {args.output}")
    else:
        report_path = scanner.save_report(report)
        print(f"Report saved to {report_path}")
    
    # 输出摘要
    print("\n🔒 Security Scan Summary:")
    print(f"Total Issues: {report.total_issues}")
    print(f"Critical: {report.critical_count}")
    print(f"High: {report.high_count}")
    print(f"Medium: {report.medium_count}")
    print(f"Low: {report.low_count}")
    
    if report.critical_count > 0 or report.high_count > 0:
        print("\n⚠️ High priority security issues found!")
        exit(1)
    else:
        print("\n✅ No critical security issues found.")

if __name__ == '__main__':
    main()
