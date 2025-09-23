#!/usr/bin/env python3
"""
Git包装脚本 - 拦截所有--no-verify调用

原理：替换git命令，检测--no-verify参数并拦截
位置：需要放在PATH的git之前，或者通过alias调用

目标：彻底阻止Cursor或任何工具使用--no-verify绕过检查
"""

import sys
import subprocess
import os
import time
from pathlib import Path


class NoVerifyGuard:
    def __init__(self):
        self.real_git = self._find_real_git()
        self.log_file = Path("logs/git-no-verify-attempts.log")
        self.log_file.parent.mkdir(exist_ok=True)

    def _find_real_git(self):
        """找到真正的git可执行文件"""
        # 从PATH中找到git，但排除当前脚本
        current_script = os.path.abspath(__file__)
        
        for path in os.environ.get('PATH', '').split(os.pathsep):
            git_path = os.path.join(path, 'git.exe' if os.name == 'nt' else 'git')
            if (os.path.exists(git_path) and 
                os.path.abspath(git_path) != current_script):
                return git_path
        
        # 备用路径
        return 'git'

    def _log_attempt(self, command_args, blocked=False):
        """记录--no-verify使用尝试"""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        status = "🚫 BLOCKED" if blocked else "✅ ALLOWED"
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {status} | {' '.join(command_args)}\n")

    def _show_violation_message(self):
        """显示违规提示信息"""
        print("\n" + "="*60)
        print("🚨 检测到 --no-verify 违规行为！")
        print("="*60)
        print("❌ 禁止使用 --no-verify 跳过检查流程")
        print("📋 原因: 基于30轮修复血泪教训，绕过检查会导致:")
        print("   • 依赖漂移问题")
        print("   • 代码质量下降") 
        print("   • 架构违规扩散")
        print()
        print("✅ 正确做法:")
        print("   • 修复检查发现的问题，而非绕过检查")
        print("   • 如果是误报，更新检查规则")
        print("   • 如果紧急情况，请联系架构负责人")
        print()
        print("🔗 相关文档: docs/architecture/ADR-001-npm-workspaces.md")
        print("📊 此次尝试已记录到: logs/git-no-verify-attempts.log")
        print("="*60)

    def check_and_filter_args(self, args):
        """检查并过滤命令参数"""
        # 检测各种no-verify模式
        no_verify_patterns = [
            '--no-verify',
            '-n',  # git commit -n 是 --no-verify 的简写
        ]
        
        found_no_verify = False
        filtered_args = []
        
        for arg in args:
            if any(pattern in arg for pattern in no_verify_patterns):
                found_no_verify = True
                # 不添加到filtered_args，即过滤掉
                continue
            filtered_args.append(arg)
        
        return filtered_args, found_no_verify

    def run(self, args):
        """主执行逻辑"""
        if len(args) < 1:
            # 直接调用git，没有参数
            return subprocess.run([self.real_git] + args[1:]).returncode
        
        # 检查是否是commit命令
        is_commit_command = (
            len(args) > 1 and 
            args[1] in ['commit', 'ci']
        )
        
        if is_commit_command:
            filtered_args, found_no_verify = self.check_and_filter_args(args)
            
            if found_no_verify:
                self._log_attempt(args, blocked=True)
                self._show_violation_message()
                
                # 询问用户是否继续（可选，也可以直接拒绝）
                response = input("\n是否强制继续提交？(输入 'FORCE' 确认): ")
                if response != 'FORCE':
                    print("❌ 提交被取消")
                    return 1
                
                print("⚠️  强制继续，但已记录违规行为")
            
            # 执行过滤后的命令
            self._log_attempt(filtered_args, blocked=False)
            return subprocess.run([self.real_git] + filtered_args[1:]).returncode
        
        else:
            # 非commit命令，直接执行
            return subprocess.run([self.real_git] + args[1:]).returncode


def main():
    guard = NoVerifyGuard()
    return guard.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
