#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码提交前监控脚本
自动检查临时修改、测试覆盖率和功能完整性
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class PreCommitMonitor:
    """提交前监控器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / 'docs' / '02_test_report'
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 风险阈值配置
        self.thresholds = {
            'max_high_severity_issues': 20,  # 最大高严重性问题数
            'min_test_pass_rate': 80.0,      # 最小测试通过率
            'max_temp_modifications': 50,    # 最大临时修改数
            'critical_files': [              # 关键文件列表
                'backend/bravo/settings/base.py',
                'backend/bravo/urls.py',
                'backend/apps/users/models.py',
                'frontend/src/main.ts',
                'frontend/src/App.vue'
            ]
        }
    
    def run_comprehensive_check(self) -> Dict:
        """运行综合检查"""
        print("[INFO] 运行提交前综合检查...")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'git_status': self._check_git_status(),
            'temp_modifications': self._check_temp_modifications(),
            'test_results': self._run_tests(),
            'code_quality': self._check_code_quality(),
            'feature_integrity': self._check_feature_integrity(),
            'critical_files': self._check_critical_files()
        }
        
        # 评估整体风险
        results['risk_assessment'] = self._assess_commit_risk(results)
        
        return results
    
    def _check_git_status(self) -> Dict:
        """检查Git状态"""
        try:
            # 检查未提交的更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []
                return {
                    'status': 'success',
                    'uncommitted_changes': len(changes),
                    'changes': changes[:10]  # 只显示前10个
                }
            else:
                return {
                    'status': 'error',
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_temp_modifications(self) -> Dict:
        """检查临时修改"""
        try:
            # 运行临时修改检测
            result = subprocess.run(
                ['python', 'scripts/temp_modification_detector.py'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode in [0, 2]:  # 0=无问题, 2=发现问题但正常
                # 解析输出获取统计信息
                output_lines = result.stdout.split('\n')
                
                high_risk = 0
                medium_risk = 0
                low_risk = 0
                total_modifications = 0
                
                for line in output_lines:
                    if '高风险' in line and '处' in line:
                        try:
                            high_risk = int(line.split('高风险')[1].split('处')[0].strip())
                        except:
                            pass
                    elif '中风险' in line and '处' in line:
                        try:
                            medium_risk = int(line.split('中风险')[1].split('处')[0].strip())
                        except:
                            pass
                    elif '低风险' in line and '处' in line:
                        try:
                            low_risk = int(line.split('低风险')[1].split('处')[0].strip())
                        except:
                            pass
                    elif '发现' in line and '处临时修改' in line:
                        try:
                            total_modifications = int(line.split('发现')[1].split('处临时修改')[0].strip())
                        except:
                            pass
                
                return {
                    'status': 'success',
                    'total_modifications': total_modifications,
                    'high_risk': high_risk,
                    'medium_risk': medium_risk,
                    'low_risk': low_risk,
                    'risk_level': 'high' if high_risk > 10 else 'medium' if high_risk > 5 else 'low'
                }
            else:
                return {
                    'status': 'error',
                    'error': result.stderr or 'Unknown error'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _run_tests(self) -> Dict:
        """运行测试"""
        try:
            # 运行简单测试
            result = subprocess.run(
                ['python', 'simple_test_runner.py'],
                cwd=self.project_root / 'backend',
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                # 解析测试结果
                output_lines = result.stdout.split('\n')
                passed_count = len([line for line in output_lines if '✅' in line])
                failed_count = len([line for line in output_lines if '❌' in line])
                total_tests = passed_count + failed_count
                
                pass_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
                
                return {
                    'status': 'success',
                    'total_tests': total_tests,
                    'passed_tests': passed_count,
                    'failed_tests': failed_count,
                    'pass_rate': pass_rate
                }
            else:
                return {
                    'status': 'failed',
                    'error': result.stderr,
                    'pass_rate': 0.0
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'pass_rate': 0.0
            }
    
    def _check_code_quality(self) -> Dict:
        """检查代码质量"""
        try:
            # 运行综合代码管理器
            result = subprocess.run(
                ['python', 'scripts/comprehensive_code_manager.py'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                # 解析风险等级
                output_lines = result.stdout.split('\n')
                risk_level = 'unknown'
                
                for line in output_lines:
                    if '整体风险等级' in line:
                        if 'LOW' in line:
                            risk_level = 'low'
                        elif 'MEDIUM' in line:
                            risk_level = 'medium'
                        elif 'HIGH' in line:
                            risk_level = 'high'
                        elif 'CRITICAL' in line:
                            risk_level = 'critical'
                        break
                
                return {
                    'status': 'success',
                    'risk_level': risk_level
                }
            else:
                return {
                    'status': 'error',
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_feature_integrity(self) -> Dict:
        """检查功能完整性"""
        features_file = self.project_root / 'features.json'
        
        if not features_file.exists():
            return {
                'status': 'warning',
                'message': 'features.json文件不存在'
            }
        
        try:
            with open(features_file, 'r', encoding='utf-8') as f:
                features = json.load(f)
            
            total_features = len(features)
            active_features = len([f for f in features if f.get('status') == 'active'])
            
            return {
                'status': 'success',
                'total_features': total_features,
                'active_features': active_features,
                'completion_rate': (active_features / total_features * 100) if total_features > 0 else 0
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_critical_files(self) -> Dict:
        """检查关键文件"""
        results = {
            'status': 'success',
            'files_status': {},
            'missing_files': [],
            'modified_files': []
        }
        
        # 检查关键文件是否存在
        for file_path in self.thresholds['critical_files']:
            full_path = self.project_root / file_path
            if full_path.exists():
                results['files_status'][file_path] = 'exists'
            else:
                results['files_status'][file_path] = 'missing'
                results['missing_files'].append(file_path)
        
        # 检查是否有未提交的关键文件修改
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                modified_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
                for file_path in self.thresholds['critical_files']:
                    if file_path in modified_files:
                        results['modified_files'].append(file_path)
        except:
            pass
        
        return results
    
    def _assess_commit_risk(self, results: Dict) -> Dict:
        """评估提交风险"""
        risk_factors = []
        risk_score = 0
        
        # 检查临时修改
        temp_mods = results.get('temp_modifications', {})
        if temp_mods.get('status') == 'success':
            high_risk_count = temp_mods.get('high_risk', 0)
            if high_risk_count > self.thresholds['max_high_severity_issues']:
                risk_factors.append(f'高风险临时修改过多: {high_risk_count}')
                risk_score += 3
            elif high_risk_count > 10:
                risk_factors.append(f'高风险临时修改较多: {high_risk_count}')
                risk_score += 2
        
        # 检查测试通过率
        test_results = results.get('test_results', {})
        if test_results.get('status') == 'success':
            pass_rate = test_results.get('pass_rate', 0)
            if pass_rate < self.thresholds['min_test_pass_rate']:
                risk_factors.append(f'测试通过率过低: {pass_rate:.1f}%')
                risk_score += 3
        elif test_results.get('status') == 'failed':
            risk_factors.append('测试执行失败')
            risk_score += 4
        
        # 检查代码质量
        code_quality = results.get('code_quality', {})
        if code_quality.get('risk_level') in ['high', 'critical']:
            risk_factors.append(f'代码质量风险: {code_quality.get("risk_level")}')
            risk_score += 2 if code_quality.get('risk_level') == 'high' else 4
        
        # 检查关键文件
        critical_files = results.get('critical_files', {})
        if critical_files.get('missing_files'):
            risk_factors.append(f'关键文件缺失: {len(critical_files.get("missing_files", []))}')
            risk_score += 3
        
        if critical_files.get('modified_files'):
            risk_factors.append(f'关键文件被修改: {len(critical_files.get("modified_files", []))}')
            risk_score += 1
        
        # 评估整体风险等级
        if risk_score >= 8:
            overall_risk = 'critical'
            recommendation = 'BLOCK_COMMIT'
        elif risk_score >= 5:
            overall_risk = 'high'
            recommendation = 'REVIEW_REQUIRED'
        elif risk_score >= 2:
            overall_risk = 'medium'
            recommendation = 'CAUTION_ADVISED'
        else:
            overall_risk = 'low'
            recommendation = 'PROCEED'
        
        return {
            'risk_factors': risk_factors,
            'risk_score': risk_score,
            'overall_risk': overall_risk,
            'recommendation': recommendation
        }
    
    def generate_commit_report(self, results: Dict) -> str:
        """生成提交报告"""
        lines = []
        lines.append("# 代码提交前检查报告")
        lines.append(f"\n**检查时间**: {results['timestamp']}")
        
        # 风险评估
        risk_assessment = results['risk_assessment']
        risk_icons = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        recommendation_icons = {
            'PROCEED': '✅',
            'CAUTION_ADVISED': '⚠️',
            'REVIEW_REQUIRED': '🔍',
            'BLOCK_COMMIT': '🚫'
        }
        
        risk = risk_assessment['overall_risk']
        recommendation = risk_assessment['recommendation']
        
        lines.append(f"\n{risk_icons.get(risk, '❓')} **整体风险**: {risk.upper()}")
        lines.append(f"{recommendation_icons.get(recommendation, '❓')} **建议**: {recommendation}")
        
        if risk_assessment['risk_factors']:
            lines.append("\n**风险因素**:")
            for factor in risk_assessment['risk_factors']:
                lines.append(f"- {factor}")
        
        # Git状态
        git_status = results.get('git_status', {})
        lines.append("\n## 📋 Git状态")
        if git_status.get('status') == 'success':
            lines.append(f"- 未提交更改: {git_status.get('uncommitted_changes', 0)} 个文件")
        else:
            lines.append(f"- ❌ 检查失败: {git_status.get('error', 'Unknown')}")
        
        # 临时修改
        temp_mods = results.get('temp_modifications', {})
        lines.append("\n## 🔧 临时修改检查")
        if temp_mods.get('status') == 'success':
            lines.append(f"- 总计: {temp_mods.get('total_modifications', 0)} 处")
            lines.append(f"- 高风险: {temp_mods.get('high_risk', 0)} 处")
            lines.append(f"- 中风险: {temp_mods.get('medium_risk', 0)} 处")
            lines.append(f"- 低风险: {temp_mods.get('low_risk', 0)} 处")
        else:
            lines.append(f"- ❌ 检查失败: {temp_mods.get('error', 'Unknown')}")
        
        # 测试结果
        test_results = results.get('test_results', {})
        lines.append("\n## 🧪 测试结果")
        if test_results.get('status') == 'success':
            lines.append(f"- 总测试数: {test_results.get('total_tests', 0)}")
            lines.append(f"- 通过: {test_results.get('passed_tests', 0)}")
            lines.append(f"- 失败: {test_results.get('failed_tests', 0)}")
            lines.append(f"- 通过率: {test_results.get('pass_rate', 0):.1f}%")
        else:
            lines.append(f"- ❌ 测试失败: {test_results.get('error', 'Unknown')}")
        
        # 代码质量
        code_quality = results.get('code_quality', {})
        lines.append("\n## 📊 代码质量")
        if code_quality.get('status') == 'success':
            lines.append(f"- 风险等级: {code_quality.get('risk_level', 'unknown').upper()}")
        else:
            lines.append(f"- ❌ 检查失败: {code_quality.get('error', 'Unknown')}")
        
        # 功能完整性
        feature_integrity = results.get('feature_integrity', {})
        lines.append("\n## 🎯 功能完整性")
        if feature_integrity.get('status') == 'success':
            lines.append(f"- 总功能数: {feature_integrity.get('total_features', 0)}")
            lines.append(f"- 活跃功能: {feature_integrity.get('active_features', 0)}")
            lines.append(f"- 完成率: {feature_integrity.get('completion_rate', 0):.1f}%")
        else:
            lines.append(f"- ⚠️ {feature_integrity.get('message', feature_integrity.get('error', 'Unknown'))}")
        
        # 关键文件
        critical_files = results.get('critical_files', {})
        lines.append("\n## 📁 关键文件状态")
        if critical_files.get('missing_files'):
            lines.append("- ❌ 缺失文件:")
            for file_path in critical_files['missing_files']:
                lines.append(f"  - {file_path}")
        
        if critical_files.get('modified_files'):
            lines.append("- 🔄 修改文件:")
            for file_path in critical_files['modified_files']:
                lines.append(f"  - {file_path}")
        
        if not critical_files.get('missing_files') and not critical_files.get('modified_files'):
            lines.append("- ✅ 所有关键文件状态正常")
        
        # 建议行动
        lines.append("\n## 🎯 建议行动")
        
        if recommendation == 'BLOCK_COMMIT':
            lines.append("- 🚫 **阻止提交**: 存在严重问题，不建议提交")
            lines.append("- 🔧 **修复问题**: 请先解决上述风险因素")
            lines.append("- 🧪 **重新测试**: 修复后重新运行检查")
        elif recommendation == 'REVIEW_REQUIRED':
            lines.append("- 🔍 **需要审查**: 建议团队成员审查代码")
            lines.append("- 📋 **记录问题**: 在PR中详细说明已知问题")
            lines.append("- ⚠️ **谨慎提交**: 确认风险可接受后再提交")
        elif recommendation == 'CAUTION_ADVISED':
            lines.append("- ⚠️ **谨慎操作**: 存在一些需要注意的问题")
            lines.append("- 📝 **文档记录**: 建议在提交信息中说明变更")
            lines.append("- 🔄 **后续跟进**: 计划后续解决发现的问题")
        else:
            lines.append("- ✅ **可以提交**: 检查通过，可以安全提交")
            lines.append("- 🔄 **持续监控**: 建议定期运行此检查")
        
        return "\n".join(lines)

def main():
    """主函数"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    monitor = PreCommitMonitor(project_root)
    
    # 运行检查
    results = monitor.run_comprehensive_check()
    
    # 生成报告
    report = monitor.generate_commit_report(results)
    
    # 保存报告
    report_file = monitor.reports_dir / 'pre_commit_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    # 输出结果
    risk_assessment = results['risk_assessment']
    recommendation = risk_assessment['recommendation']
    
    print(f"[SUCCESS] 提交前检查完成")
    print(f"[INFO] 风险等级: {risk_assessment['overall_risk'].upper()}")
    print(f"[INFO] 建议: {recommendation}")
    print(f"[INFO] 详细报告: {report_file}")
    
    # 根据建议返回退出码
    exit_codes = {
        'PROCEED': 0,
        'CAUTION_ADVISED': 0,
        'REVIEW_REQUIRED': 1,
        'BLOCK_COMMIT': 2
    }
    
    return exit_codes.get(recommendation, 1)

if __name__ == '__main__':
    exit(main())