#!/usr/bin/env python3
"""
架构健康检查脚本

目的：定期检查项目架构健康状况，预防技术债务积累
生成每周架构健康报告，追踪关键指标变化

基于30轮修复教训：预防大于治疗！
"""

import os
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path


class ArchitectureHealthChecker:
    def __init__(self):
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {},
            'violations': [],
            'metrics': {},
            'recommendations': []
        }

    def check_npm_workspaces_violations(self):
        """检查npm workspaces违规"""
        violations = []
        
        # 检查所有相关文件
        patterns_to_check = [
            r'cd\s+(?:frontend|e2e|[^&\s]+)\s*&&\s*npm\s+(?:ci|install)',
            r'working-directory:\s*\.\/(?:frontend|e2e)',
            r'npm\s+install\s+-g',
        ]
        
        file_types = ['*.yml', '*.yaml', '*.py', '*.js', '*.json', '*.sh', 'Makefile']
        
        total_files = 0
        violation_files = 0
        
        for file_type in file_types:
            try:
                result = subprocess.run(
                    ['find', '.', '-name', file_type, '-not', '-path', './node_modules/*'],
                    capture_output=True, text=True
                )
                
                for file_path in result.stdout.strip().split('\n'):
                    if not file_path or not os.path.exists(file_path):
                        continue
                    
                    total_files += 1
                    file_violations = self._check_file_violations(file_path, patterns_to_check)
                    
                    if file_violations:
                        violation_files += 1
                        violations.extend(file_violations)
                        
            except Exception as e:
                print(f"检查文件类型 {file_type} 时出错: {e}")
        
        compliance_rate = ((total_files - violation_files) / total_files * 100) if total_files > 0 else 100
        
        self.report['violations'] = violations
        self.report['metrics']['npm_workspaces'] = {
            'total_files_checked': total_files,
            'violation_files': violation_files,
            'compliance_rate': round(compliance_rate, 2),
            'target_compliance_rate': 100.0
        }
        
        return violations

    def _check_file_violations(self, file_path, patterns):
        """检查单个文件的违规"""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line_num, line in enumerate(content.splitlines(), 1):
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        violations.append({
                            'file': file_path,
                            'line': line_num,
                            'content': line.strip(),
                            'pattern': pattern,
                            'severity': 'HIGH' if 'npm ci' in line or 'npm install' in line else 'MEDIUM'
                        })
        except (UnicodeDecodeError, PermissionError):
            pass
            
        return violations

    def check_complexity_metrics(self):
        """检查复杂度指标"""
        metrics = {}
        
        # GitHub Actions工作流数量
        workflows_count = len(list(Path('.github/workflows').glob('*.yml')))
        
        # Docker配置文件数量  
        docker_configs = len(list(Path('.').glob('docker-compose*.yml')))
        
        # package.json文件数量
        package_jsons = len([p for p in Path('.').rglob('package.json') 
                           if 'node_modules' not in str(p)])
        
        # 代码行数统计
        try:
            result = subprocess.run(
                ['find', '.', '-name', '*.py', '-o', '-name', '*.js', '-o', '-name', '*.ts', 
                 '-o', '-name', '*.vue', '!', '-path', './node_modules/*'],
                capture_output=True, text=True
            )
            
            total_lines = 0
            for file_path in result.stdout.strip().split('\n'):
                if file_path and os.path.exists(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass
                        
            metrics['code_lines'] = total_lines
        except:
            metrics['code_lines'] = 0
        
        metrics['workflows_count'] = workflows_count
        metrics['docker_configs'] = docker_configs  
        metrics['package_jsons'] = package_jsons
        
        # 复杂度评分 (100分制)
        complexity_score = min(100, (workflows_count * 2) + (docker_configs * 5) + (package_jsons * 3))
        metrics['complexity_score'] = complexity_score
        metrics['complexity_level'] = (
            'LOW' if complexity_score < 30 else
            'MEDIUM' if complexity_score < 60 else
            'HIGH' if complexity_score < 90 else
            'VERY_HIGH'
        )
        
        self.report['metrics']['complexity'] = metrics
        return metrics

    def generate_recommendations(self):
        """生成改进建议"""
        recommendations = []
        
        # 基于违规情况
        violation_count = len(self.report['violations'])
        if violation_count > 0:
            recommendations.append({
                'priority': 'HIGH',
                'category': 'Architecture Compliance',
                'description': f'发现 {violation_count} 个npm workspaces架构违规',
                'action': '立即运行 scripts/check_npm_workspaces.py 并修复所有违规'
            })
        
        # 基于复杂度
        complexity = self.report['metrics'].get('complexity', {})
        if complexity.get('complexity_level') == 'VERY_HIGH':
            recommendations.append({
                'priority': 'MEDIUM',
                'category': 'Complexity Reduction',
                'description': f'工具链复杂度过高 (评分: {complexity.get("complexity_score", 0)})',
                'action': '考虑合并工作流文件，减少docker配置数量'
            })
        
        # 基于文件数量
        if complexity.get('workflows_count', 0) > 30:
            recommendations.append({
                'priority': 'MEDIUM', 
                'category': 'Workflow Optimization',
                'description': f'GitHub Actions工作流过多 ({complexity.get("workflows_count")} 个)',
                'action': '合并相似工作流，采用矩阵策略减少重复'
            })
        
        self.report['recommendations'] = recommendations
        return recommendations

    def generate_summary(self):
        """生成总结"""
        violations = len(self.report['violations'])
        compliance_rate = self.report['metrics'].get('npm_workspaces', {}).get('compliance_rate', 0)
        complexity_level = self.report['metrics'].get('complexity', {}).get('complexity_level', 'UNKNOWN')
        
        status = 'HEALTHY' if violations == 0 and compliance_rate == 100 else 'NEEDS_ATTENTION'
        
        summary = {
            'overall_status': status,
            'npm_workspaces_compliance': f"{compliance_rate}%",
            'violations_count': violations,
            'complexity_level': complexity_level,
            'recommendations_count': len(self.report['recommendations'])
        }
        
        self.report['summary'] = summary
        return summary

    def run_full_check(self):
        """运行完整健康检查"""
        print("🔍 开始架构健康检查...")
        
        print("📋 检查npm workspaces合规性...")
        self.check_npm_workspaces_violations()
        
        print("📊 分析复杂度指标...")
        self.check_complexity_metrics()
        
        print("💡 生成改进建议...")
        self.generate_recommendations()
        
        print("📄 生成总结报告...")
        self.generate_summary()
        
        return self.report

    def print_report(self):
        """打印报告到控制台"""
        summary = self.report['summary']
        
        print("\n" + "="*60)
        print("📊 架构健康检查报告")
        print("="*60)
        print(f"🕐 检查时间: {self.report['timestamp']}")
        print(f"🎯 整体状态: {summary['overall_status']}")
        print(f"📈 npm workspaces合规率: {summary['npm_workspaces_compliance']}")
        print(f"⚠️  违规数量: {summary['violations_count']}")
        print(f"🔧 复杂度等级: {summary['complexity_level']}")
        
        # 打印关键指标
        metrics = self.report['metrics']
        if 'complexity' in metrics:
            comp = metrics['complexity']
            print(f"\n📋 复杂度指标:")
            print(f"  • GitHub Actions工作流: {comp['workflows_count']} 个")
            print(f"  • Docker配置文件: {comp['docker_configs']} 个") 
            print(f"  • package.json文件: {comp['package_jsons']} 个")
            print(f"  • 复杂度评分: {comp['complexity_score']}/100")
        
        # 打印违规信息
        if self.report['violations']:
            print(f"\n🚨 发现的违规 ({len(self.report['violations'])} 个):")
            for violation in self.report['violations'][:5]:  # 只显示前5个
                print(f"  • {violation['file']}:{violation['line']} - {violation['severity']}")
            
            if len(self.report['violations']) > 5:
                print(f"  ... 还有 {len(self.report['violations']) - 5} 个违规")
        
        # 打印建议
        if self.report['recommendations']:
            print(f"\n💡 改进建议 ({len(self.report['recommendations'])} 条):")
            for rec in self.report['recommendations']:
                print(f"  • [{rec['priority']}] {rec['description']}")
                print(f"    👉 {rec['action']}")
        
        print("\n" + "="*60)
        
        if summary['overall_status'] == 'HEALTHY':
            print("✅ 架构健康状况良好！")
        else:
            print("⚠️  架构需要注意，请查看上述建议进行改进。")
        
        print("="*60)

    def save_report(self, filename=None):
        """保存报告到文件"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"docs/architecture/health-report-{timestamp}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 报告已保存到: {filename}")
        return filename


def main():
    """主函数"""
    checker = ArchitectureHealthChecker()
    
    print("🏥 架构健康检查工具")
    print("基于30轮修复血泪教训 - 预防大于治疗！\n")
    
    try:
        checker.run_full_check()
        checker.print_report()
        
        # 保存报告
        report_file = checker.save_report()
        
        # 如果有违规，退出码为1
        if checker.report['summary']['violations_count'] > 0:
            print("\n❌ 发现架构违规，请及时修复！")
            return 1
        else:
            print("\n✅ 架构健康检查通过！")
            return 0
            
    except Exception as e:
        print(f"❌ 健康检查过程中发生错误: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
