#!/usr/bin/env python3
"""
合规引擎Pre-commit入口
从Git暂存区获取文件并执行合规检查
"""

import subprocess
import sys
from pathlib import Path

# 添加引擎路径
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# 导入引擎
try:
    from compliance.engine import ComplianceEngine
except ImportError:
    # 如果直接导入失败，尝试添加路径
    sys.path.insert(0, str(current_dir))
    from engine import ComplianceEngine


def get_staged_files() -> list:
    """获取Git暂存区的文件列表"""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.split("\n") if f.strip()]
        return files
    except subprocess.CalledProcessError as e:
        print(f"❌ 获取暂存文件失败: {e}", file=sys.stderr)
        return []
    except FileNotFoundError:
        print("⚠️ Git未安装或不在Git仓库中", file=sys.stderr)
        return []


def main():
    """Pre-commit入口"""
    # 获取暂存文件
    staged_files = get_staged_files()

    if not staged_files:
        print("ℹ️ 没有暂存的文件，跳过合规检查", file=sys.stderr)
        sys.exit(0)

    print(f"🔍 合规检查: {len(staged_files)} 个文件", file=sys.stderr)

    try:
        # 创建引擎并执行检查
        engine = ComplianceEngine()
        results = engine.check_files(staged_files)
        engine.print_results(results)

        # 严格模式：有失败则拒绝提交
        if engine.config["engine"]["strict_mode"]:
            if results["summary"]["failed"] > 0:
                print("\n❌ 合规检查失败，提交被拒绝", file=sys.stderr)
                print("请修复上述错误后重试", file=sys.stderr)
                sys.exit(1)
            else:
                print("\n✅ 合规检查通过", file=sys.stderr)
                sys.exit(0)
        else:
            # 非严格模式：只警告
            if results["summary"]["failed"] > 0:
                print("\n⚠️ 合规检查发现问题，但非严格模式允许提交", file=sys.stderr)
            sys.exit(0)

    except Exception as e:
        print(f"❌ 合规引擎执行失败: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        # 失败时根据配置决定是否拒绝提交
        # 默认拒绝，确保合规性
        sys.exit(1)


if __name__ == "__main__":
    main()
