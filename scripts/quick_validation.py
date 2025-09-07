#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证工具 - 针对单个文件的临时标记检测
用于快速验证代码变更追踪系统的有效性
"""

import re
import sys
import os
from pathlib import Path
from datetime import datetime

class QuickValidator:
    """快速验证器"""
    
    def __init__(self):
        # 临时修改检测规则
        self.temp_patterns = {
            'TODO': {'pattern': r'#\s*TODO[:\s]', 'severity': 'medium', 'description': 'TODO标记'},
            'FIXME': {'pattern': r'#\s*FIXME[:\s]', 'severity': 'high', 'description': 'FIXME标记'},
            'HACK': {'pattern': r'#\s*HACK[:\s]', 'severity': 'high', 'description': 'HACK标记'},
            'XXX': {'pattern': r'#\s*XXX[:\s]', 'severity': 'high', 'description': 'XXX标记'},
            'DEBUG': {'pattern': r'#\s*DEBUG[:\s]', 'severity': 'medium', 'description': 'DEBUG标记'},
            'TEMP': {'pattern': r'#\s*TEMP[:\s]', 'severity': 'medium', 'description': 'TEMP标记'},
            'NOTE': {'pattern': r'#\s*NOTE[:\s]', 'severity': 'low', 'description': 'NOTE标记'},
            'console_log': {'pattern': r'console\.log\s*\(', 'severity': 'medium', 'description': '临时调试输出'},
            'print_debug': {'pattern': r'print\s*\(.*DEBUG', 'severity': 'medium', 'description': '调试打印语句'},
            'commented_code': {'pattern': r'^\s*#\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\(', 'severity': 'low', 'description': '被注释的代码'}
        }
    
    def scan_file(self, file_path):
        """扫描单个文件"""
        if not os.path.exists(file_path):
            print(f"❌ 文件不存在: {file_path}")
            return []
        
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line_issues = self._check_line(line, line_num)
                issues.extend(line_issues)
        
        except Exception as e:
            print(f"❌ 读取文件失败 {file_path}: {e}")
            return []
        
        return issues
    
    def _check_line(self, line, line_num):
        """检查单行代码"""
        issues = []
        
        for pattern_name, pattern_info in self.temp_patterns.items():
            if re.search(pattern_info['pattern'], line, re.IGNORECASE):
                issues.append({
                    'type': pattern_name,
                    'line': line_num,
                    'content': line.strip(),
                    'severity': pattern_info['severity'],
                    'description': pattern_info['description']
                })
        
        return issues
    
    def generate_report(self, file_path, issues):
        """生成验证报告"""
        print(f"\n🔍 快速验证报告 - {os.path.basename(file_path)}")
        print(f"📅 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 文件路径: {file_path}")
        print(f"🐛 发现问题: {len(issues)} 个")
        print("=" * 60)
        
        if not issues:
            print("✅ 未发现临时修改标记")
            return
        
        # 按严重性分组
        severity_groups = {'high': [], 'medium': [], 'low': []}
        for issue in issues:
            severity_groups[issue['severity']].append(issue)
        
        # 显示高严重性问题
        if severity_groups['high']:
            print("\n🔴 高严重性问题:")
            for issue in severity_groups['high']:
                print(f"  第{issue['line']}行: {issue['description']}")
                print(f"    内容: {issue['content']}")
        
        # 显示中等严重性问题
        if severity_groups['medium']:
            print("\n🟡 中等严重性问题:")
            for issue in severity_groups['medium']:
                print(f"  第{issue['line']}行: {issue['description']}")
                print(f"    内容: {issue['content']}")
        
        # 显示低严重性问题
        if severity_groups['low']:
            print("\n🟢 低严重性问题:")
            for issue in severity_groups['low']:
                print(f"  第{issue['line']}行: {issue['description']}")
                print(f"    内容: {issue['content']}")
        
        print("\n" + "=" * 60)
        print(f"✅ 系统有效性验证: 成功检测到 {len(issues)} 个临时修改标记")
        print("🎯 结论: 代码变更追踪系统工作正常")

def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python quick_validation.py <文件路径>")
        print("示例: python quick_validation.py test_validation.py")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # 如果是相对路径，转换为绝对路径
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    validator = QuickValidator()
    
    print(f"🚀 开始快速验证: {os.path.basename(file_path)}")
    start_time = datetime.now()
    
    issues = validator.scan_file(file_path)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    validator.generate_report(file_path, issues)
    print(f"⏱️  扫描耗时: {duration:.2f} 秒")

if __name__ == "__main__":
    main()