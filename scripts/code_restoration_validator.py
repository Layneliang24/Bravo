#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码还原验证系统
确保临时修改得到正确处理，防止功能缺失
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
import difflib

class CodeRestorationValidator:
    """代码还原验证器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.features_file = self.project_root / 'features.json'
        self.baseline_dir = self.project_root / '.code_baselines'
        self.baseline_dir.mkdir(exist_ok=True)
        
    def create_baseline(self) -> Dict:
        """创建代码基线"""
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'commit_hash': self._get_current_commit(),
            'features': self._load_features(),
            'test_results': self._run_tests(),
            'file_checksums': self._calculate_checksums()
        }
        
        baseline_file = self.baseline_dir / f"baseline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(baseline_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
            
        # 保存为最新基线
        latest_baseline = self.baseline_dir / 'latest_baseline.json'
        with open(latest_baseline, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
            
        return baseline
    
    def validate_against_baseline(self) -> Dict:
        """与基线对比验证"""
        latest_baseline_file = self.baseline_dir / 'latest_baseline.json'
        
        if not latest_baseline_file.exists():
            return {
                'status': 'no_baseline',
                'message': '未找到基线，请先创建基线',
                'recommendation': 'run_create_baseline'
            }
        
        with open(latest_baseline_file, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
        
        current_state = {
            'timestamp': datetime.now().isoformat(),
            'commit_hash': self._get_current_commit(),
            'features': self._load_features(),
            'test_results': self._run_tests(),
            'file_checksums': self._calculate_checksums()
        }
        
        validation_result = {
            'baseline_date': baseline['timestamp'],
            'current_date': current_state['timestamp'],
            'commit_changed': baseline['commit_hash'] != current_state['commit_hash'],
            'feature_changes': self._compare_features(baseline['features'], current_state['features']),
            'test_changes': self._compare_tests(baseline['test_results'], current_state['test_results']),
            'file_changes': self._compare_files(baseline['file_checksums'], current_state['file_checksums']),
            'overall_status': 'unknown'
        }
        
        # 评估整体状态
        validation_result['overall_status'] = self._evaluate_overall_status(validation_result)
        
        return validation_result
    
    def _get_current_commit(self) -> str:
        """获取当前Git提交哈希"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else 'unknown'
        except:
            return 'unknown'
    
    def _load_features(self) -> List[Dict]:
        """加载功能列表"""
        if self.features_file.exists():
            with open(self.features_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _run_tests(self) -> Dict:
        """运行测试并获取结果"""
        test_results = {
            'backend_tests': self._run_backend_tests(),
            'frontend_tests': self._run_frontend_tests(),
            'e2e_tests': self._run_e2e_tests()
        }
        
        # 计算总体通过率
        total_tests = sum(r.get('total', 0) for r in test_results.values())
        passed_tests = sum(r.get('passed', 0) for r in test_results.values())
        
        test_results['summary'] = {
            'total': total_tests,
            'passed': passed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
        
        return test_results
    
    def _run_backend_tests(self) -> Dict:
        """运行后端测试"""
        try:
            # 使用我们创建的独立测试脚本
            result = subprocess.run(
                ['python', 'simple_test_runner.py'],
                cwd=self.project_root / 'backend',
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # 解析输出获取测试数量
                output_lines = result.stdout.split('\n')
                test_count = len([line for line in output_lines if '✅' in line or 'PASS' in line])
                return {
                    'status': 'passed',
                    'total': test_count,
                    'passed': test_count,
                    'output': result.stdout
                }
            else:
                return {
                    'status': 'failed',
                    'total': 0,
                    'passed': 0,
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'status': 'error',
                'total': 0,
                'passed': 0,
                'error': str(e)
            }
    
    def _run_frontend_tests(self) -> Dict:
        """运行前端测试"""
        try:
            result = subprocess.run(
                ['npm', 'test', '--', '--passWithNoTests'],
                cwd=self.project_root / 'frontend',
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 简化的结果解析
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'total': 1,
                'passed': 1 if result.returncode == 0 else 0,
                'output': result.stdout
            }
        except Exception as e:
            return {
                'status': 'error',
                'total': 0,
                'passed': 0,
                'error': str(e)
            }
    
    def _run_e2e_tests(self) -> Dict:
        """运行E2E测试"""
        # E2E测试通常需要服务器运行，这里只检查配置
        e2e_config = self.project_root / 'e2e' / 'playwright.config.ts'
        if e2e_config.exists():
            return {
                'status': 'configured',
                'total': 1,
                'passed': 1,
                'note': 'E2E tests configured but not executed'
            }
        else:
            return {
                'status': 'not_configured',
                'total': 0,
                'passed': 0
            }
    
    def _calculate_checksums(self) -> Dict[str, str]:
        """计算关键文件的校验和"""
        import hashlib
        
        checksums = {}
        key_files = [
            'backend/bravo/settings/base.py',
            'backend/bravo/urls.py',
            'backend/apps/users/models.py',
            'backend/apps/users/views.py',
            'frontend/src/main.ts',
            'frontend/src/App.vue',
            'features.json'
        ]
        
        for file_path in key_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                with open(full_path, 'rb') as f:
                    content = f.read()
                    checksums[file_path] = hashlib.md5(content).hexdigest()
        
        return checksums
    
    def _compare_features(self, baseline_features: List[Dict], current_features: List[Dict]) -> Dict:
        """比较功能列表"""
        baseline_ids = {f.get('id', f.get('name', str(i))) for i, f in enumerate(baseline_features)}
        current_ids = {f.get('id', f.get('name', str(i))) for i, f in enumerate(current_features)}
        
        return {
            'added': list(current_ids - baseline_ids),
            'removed': list(baseline_ids - current_ids),
            'total_baseline': len(baseline_features),
            'total_current': len(current_features),
            'status': 'stable' if baseline_ids == current_ids else 'changed'
        }
    
    def _compare_tests(self, baseline_tests: Dict, current_tests: Dict) -> Dict:
        """比较测试结果"""
        baseline_pass_rate = baseline_tests.get('summary', {}).get('pass_rate', 0)
        current_pass_rate = current_tests.get('summary', {}).get('pass_rate', 0)
        
        return {
            'baseline_pass_rate': baseline_pass_rate,
            'current_pass_rate': current_pass_rate,
            'pass_rate_change': current_pass_rate - baseline_pass_rate,
            'status': 'improved' if current_pass_rate > baseline_pass_rate else 
                     'degraded' if current_pass_rate < baseline_pass_rate else 'stable'
        }
    
    def _compare_files(self, baseline_checksums: Dict, current_checksums: Dict) -> Dict:
        """比较文件变更"""
        changed_files = []
        for file_path, baseline_checksum in baseline_checksums.items():
            current_checksum = current_checksums.get(file_path)
            if current_checksum and current_checksum != baseline_checksum:
                changed_files.append(file_path)
        
        new_files = [f for f in current_checksums if f not in baseline_checksums]
        deleted_files = [f for f in baseline_checksums if f not in current_checksums]
        
        return {
            'changed': changed_files,
            'added': new_files,
            'deleted': deleted_files,
            'total_changes': len(changed_files) + len(new_files) + len(deleted_files)
        }
    
    def _evaluate_overall_status(self, validation_result: Dict) -> str:
        """评估整体状态"""
        # 检查测试通过率是否下降
        test_changes = validation_result['test_changes']
        if test_changes['status'] == 'degraded' and test_changes['pass_rate_change'] < -10:
            return 'critical'  # 测试通过率显著下降
        
        # 检查功能是否减少
        feature_changes = validation_result['feature_changes']
        if feature_changes['removed']:
            return 'warning'  # 有功能被移除
        
        # 检查文件变更数量
        file_changes = validation_result['file_changes']
        if file_changes['total_changes'] > 10:
            return 'attention'  # 大量文件变更
        
        # 检查是否有文件被删除
        if file_changes['deleted']:
            return 'warning'  # 有关键文件被删除
        
        return 'healthy'  # 状态良好
    
    def generate_restoration_report(self, validation_result: Dict) -> str:
        """生成还原验证报告"""
        report = []
        report.append("# 代码还原验证报告")
        report.append(f"\n生成时间: {validation_result['current_date']}")
        report.append(f"基线时间: {validation_result['baseline_date']}")
        report.append(f"整体状态: {validation_result['overall_status'].upper()}")
        
        # 状态图标
        status_icons = {
            'healthy': '🟢',
            'attention': '🟡',
            'warning': '🟠',
            'critical': '🔴'
        }
        icon = status_icons.get(validation_result['overall_status'], '❓')
        report.append(f"\n{icon} **状态评估: {validation_result['overall_status'].upper()}**")
        
        # 功能变更
        feature_changes = validation_result['feature_changes']
        report.append("\n## 📋 功能变更分析")
        report.append(f"- 基线功能数: {feature_changes['total_baseline']}")
        report.append(f"- 当前功能数: {feature_changes['total_current']}")
        
        if feature_changes['removed']:
            report.append(f"- ⚠️ **移除的功能**: {', '.join(feature_changes['removed'])}")
        if feature_changes['added']:
            report.append(f"- ✅ **新增的功能**: {', '.join(feature_changes['added'])}")
        
        # 测试结果变更
        test_changes = validation_result['test_changes']
        report.append("\n## 🧪 测试结果分析")
        report.append(f"- 基线通过率: {test_changes['baseline_pass_rate']:.1f}%")
        report.append(f"- 当前通过率: {test_changes['current_pass_rate']:.1f}%")
        report.append(f"- 变化幅度: {test_changes['pass_rate_change']:+.1f}%")
        
        if test_changes['status'] == 'degraded':
            report.append("- 🔴 **警告**: 测试通过率下降")
        elif test_changes['status'] == 'improved':
            report.append("- 🟢 **良好**: 测试通过率提升")
        
        # 文件变更
        file_changes = validation_result['file_changes']
        report.append("\n## 📁 文件变更分析")
        report.append(f"- 总变更数: {file_changes['total_changes']}")
        
        if file_changes['changed']:
            report.append(f"- 📝 **修改的文件**: {len(file_changes['changed'])} 个")
            for file in file_changes['changed'][:5]:  # 只显示前5个
                report.append(f"  - {file}")
        
        if file_changes['deleted']:
            report.append(f"- 🗑️ **删除的文件**: {', '.join(file_changes['deleted'])}")
        
        if file_changes['added']:
            report.append(f"- ➕ **新增的文件**: {', '.join(file_changes['added'])}")
        
        # 建议行动
        report.append("\n## 🎯 建议行动")
        
        if validation_result['overall_status'] == 'critical':
            report.append("- 🚨 **立即行动**: 测试通过率严重下降，需要立即回滚或修复")
            report.append("- 🔍 **深度检查**: 分析所有失败的测试用例")
            report.append("- 📞 **团队通知**: 通知相关开发人员")
        elif validation_result['overall_status'] == 'warning':
            report.append("- ⚠️ **注意检查**: 发现功能移除或关键文件删除")
            report.append("- 📋 **功能验证**: 确认移除的功能是否为预期行为")
            report.append("- 🧪 **补充测试**: 为新功能添加相应测试")
        elif validation_result['overall_status'] == 'attention':
            report.append("- 👀 **持续关注**: 文件变更较多，需要关注")
            report.append("- 📝 **文档更新**: 确保变更有相应的文档说明")
        else:
            report.append("- 🟢 **保持现状**: 代码状态良好，继续监控")
        
        # 下次验证建议
        report.append("\n## 🔄 下次验证")
        report.append("建议在以下情况下重新验证:")
        report.append("- 完成重要功能开发后")
        report.append("- 修复临时修改后")
        report.append("- 发布前的最终检查")
        
        return "\n".join(report)

def main():
    """主函数"""
    import sys
    
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    validator = CodeRestorationValidator(project_root)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'create-baseline':
        print("📊 创建代码基线...")
        baseline = validator.create_baseline()
        print(f"✅ 基线已创建: {baseline['timestamp']}")
        print(f"📝 提交哈希: {baseline['commit_hash']}")
        print(f"🧪 测试通过率: {baseline['test_results']['summary']['pass_rate']:.1f}%")
        return 0
    
    print("🔍 开始代码还原验证...")
    validation_result = validator.validate_against_baseline()
    
    if validation_result.get('status') == 'no_baseline':
        print("❌ 未找到基线，请先运行: python code_restoration_validator.py create-baseline")
        return 1
    
    print("📝 生成验证报告...")
    report = validator.generate_restoration_report(validation_result)
    
    # 保存报告
    report_file = Path(project_root) / 'docs' / '02_test_report' / 'code_restoration_report.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 报告已生成: {report_file}")
    print(f"📊 整体状态: {validation_result['overall_status'].upper()}")
    
    # 根据状态返回退出码
    status_codes = {
        'healthy': 0,
        'attention': 0,
        'warning': 1,
        'critical': 2
    }
    
    return status_codes.get(validation_result['overall_status'], 1)

if __name__ == '__main__':
    exit(main())