#!/usr/bin/env python3
"""
自动回滚机制
检测到严重违规时自动执行git revert
"""

import subprocess
import sys


def execute_rollback(commit_sha: str, reason: str) -> bool:
    """
    执行自动回滚

    Args:
        commit_sha: 要回滚的提交哈希
        reason: 回滚原因

    Returns:
        是否成功
    """
    try:
        # 记录回滚操作
        print(f"🔄 开始自动回滚提交: {commit_sha}", file=sys.stderr)
        print(f"📋 原因: {reason}", file=sys.stderr)

        # 执行git revert
        result = subprocess.run(
            ["git", "revert", commit_sha, "--no-edit"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            print("✅ 自动回滚成功", file=sys.stderr)
            return True
        else:
            print(f"❌ 自动回滚失败: {result.stderr}", file=sys.stderr)
            return False

    except Exception as e:
        print(f"❌ 回滚过程出错: {e}", file=sys.stderr)
        return False


def check_severe_violations(commit_sha: str):
    """
    检查提交是否包含严重违规

    Args:
        commit_sha: 提交哈希

    Returns:
        tuple: (是否违规, 违规原因)
    """
    try:
        # 获取提交的变更
        result = subprocess.run(
            ["git", "show", "--stat", commit_sha],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return False, ""

        # 检查是否有大量删除
        deleted_count = result.stdout.count("deleted:")
        if deleted_count > 10:
            return True, f"检测到大量文件删除（{deleted_count}个文件）"

        # 检查是否有未授权的功能删除
        diff_result = subprocess.run(
            ["git", "diff", f"{commit_sha}^..{commit_sha}", "--unified=0"],
            capture_output=True,
            text=True,
            check=False,
        )

        if diff_result.returncode == 0:
            # 检查删除的函数/类数量
            deleted_functions = diff_result.stdout.count(
                "def "
            ) + diff_result.stdout.count("class ")
            if deleted_functions > 5:
                return True, f"检测到大量功能删除（{deleted_functions}个函数/类）"

        return False, ""

    except Exception as e:
        print(f"⚠️ 检查违规时出错: {e}", file=sys.stderr)
        return False, ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python rollback.py <commit_sha>", file=sys.stderr)
        sys.exit(1)

    commit_sha = sys.argv[1]
    is_violation, reason = check_severe_violations(commit_sha)

    if is_violation:
        if execute_rollback(commit_sha, reason):
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print("✅ 未检测到严重违规，无需回滚", file=sys.stderr)
        sys.exit(0)
