#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scripts-Golden保护系统

防止AI修改核心保护脚本，确保安全机制的完整性。
任何对scripts-golden目录的修改都需要用户亲自输入授权码。
"""

import hashlib
import io
import os
import sys
import threading
from datetime import datetime

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 30秒超时设置
TIMEOUT_SECONDS = 30


def read_with_timeout(prompt):
    """30秒超时输入函数（专为AI阻止设计）"""

    # 显示超时警告
    print("")
    print("WARNING: 30秒后自动超时终止")
    print("INFO: AI无法通过等待绕过此验证")
    print("━━━━━━━━━━━━━━━━━━━━━━━━")
    print(prompt, end="", flush=True)

    # 使用简单的线程超时机制
    result = {"response": None, "finished": False}

    def input_reader():
        try:
            response = input()
            if not result["finished"]:
                result["response"] = response.strip()
                result["finished"] = True
        except KeyboardInterrupt:
            result["finished"] = True
        except EOFError:
            if not result["finished"]:
                result["response"] = "EOF_ERROR"
                result["finished"] = True

    # 启动输入线程
    input_thread = threading.Thread(target=input_reader)
    input_thread.daemon = True
    input_thread.start()

    # 等待30秒或直到输入完成
    input_thread.join(TIMEOUT_SECONDS)
    result["finished"] = True

    if result["response"] is None:
        # 超时或其他错误
        print("\n")
        print("TIMEOUT: 30秒超时 - 自动拒绝修改")
        print("INFO: AI继续修复问题而不是修改保护脚本")
        print("TIP: 建议运行: ./test 生成通行证后再推送")
        log_security_violation("超时拒绝", "30秒内未输入授权码")
        sys.exit(1)

    if result["response"] == "EOF_ERROR":
        print("\nERROR: 非交互式输入被拒绝")
        print("INFO: AI无法通过管道或脚本输入授权码")
        log_security_violation("非交互式拒绝", "检测到EOF或管道输入")
        sys.exit(1)

    return result["response"]


def log_security_violation(violation_type, details):
    """记录安全违规事件"""
    log_file = "logs/security-violations.log"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"{timestamp} | GOLDEN_SCRIPTS_PROTECTION | {violation_type} | {details}\n"
    )

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)


def get_file_hash(filepath):
    """计算文件哈希"""
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        return None


def get_golden_scripts_manifest():
    """获取黄金脚本清单"""
    return {
        "scripts-golden/git-guard.sh": "核心Git命令拦截器",
        "scripts-golden/dependency-guard.sh": "依赖管理保护器",
        "scripts-golden/git-protection-monitor.sh": "保护机制监控器",
        "scripts-golden/local_test_passport.py": "本地测试通行证生成器",
        "scripts-golden/run_github_actions_simulation.sh": "GitHub Actions模拟器",
    }


def check_modification_authorization():
    """检查修改授权"""
    print("=== scripts-golden保护脚本修改检测！===")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("WARNING: 严重安全警告：检测到核心保护脚本被修改！")
    print("")
    print("PROTECTED: 受保护的scripts-golden目录包含：")
    for script, description in get_golden_scripts_manifest().items():
        print("   - {} - {}".format(script, description))
    print("")
    print("INFO: 这些脚本是系统安全的核心组件：")
    print("   - 防止AI绕过本地测试")
    print("   - 拦截危险的依赖管理操作")
    print("   - 监控和恢复保护机制")
    print("   - 生成和验证通行证")
    print("")
    print("WARNING: 修改这些脚本可能导致：")
    print("   - 安全机制完全失效")
    print("   - AI能够自由绕过所有保护")
    print("   - 代码质量控制被破坏")
    print("   - 开发流程失控")
    print("")
    print("CRITICAL: 只有项目维护者才能修改这些核心脚本！")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # 多重验证机制
    print("\nSTEP 1/3: 多重授权验证")
    expected_date = datetime.now().strftime("%Y-%m-%d")
    date_input = read_with_timeout("请输入今天的日期 (格式: YYYY-MM-DD): ")

    if date_input != expected_date:
        print("ERROR: 日期验证失败 - 修改被拒绝")
        log_security_violation("日期验证失败", f"输入: {date_input}, 期望: {expected_date}")
        sys.exit(1)

    print("\nSTEP 2/3: 多重授权验证")
    math_input = read_with_timeout("请输入数学题答案: 89 + 34 = ")

    if math_input != "123":
        print("ERROR: 数学验证失败 - 修改被拒绝")
        log_security_violation("数学验证失败", f"输入: {math_input}")
        sys.exit(1)

    print("\nSTEP 3/3: 多重授权验证")
    print("WARNING: 最后警告：此操作将允许修改核心安全脚本")
    print("WARNING: 这可能危及整个项目的安全防护")
    print("WARNING: 请确认您是项目维护者并完全理解风险")

    auth_code = read_with_timeout("输入最终授权码 (AUTHORIZE-GOLDEN-SCRIPTS-MODIFICATION): ")

    if auth_code == "AUTHORIZE-GOLDEN-SCRIPTS-MODIFICATION":
        print("SUCCESS: 授权验证通过 - 允许修改（已记录操作）")
        log_security_violation("授权通过", "用户通过多重验证授权修改")
        return True
    else:
        print("ERROR: 最终授权失败 - 修改被拒绝")
        log_security_violation("最终授权失败", f"输入的授权码: {auth_code}")
        sys.exit(1)


def get_actually_modified_files(file_list):
    """检查文件是否真的被修改了（通过git diff）"""
    import subprocess

    actually_modified = []
    for file_path in file_list:
        # 检查文件是否在暂存区中被修改
        try:
            # 检查暂存区
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", file_path],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                actually_modified.append(file_path)
                continue
        except Exception:
            pass

        # 检查工作区
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", file_path],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                actually_modified.append(file_path)
        except Exception:
            pass

    return actually_modified


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("ERROR: 未指定要检查的文件")
        sys.exit(1)

    # 获取传入的文件列表
    input_files = sys.argv[1:]
    golden_files = [f for f in input_files if f.startswith("scripts-golden/")]

    if not golden_files:
        # 没有scripts-golden文件，直接通过
        sys.exit(0)

    # 检查人工授权环境变量（静默模式）
    manual_auth = os.environ.get("GOLDEN_SCRIPTS_MANUAL_AUTH")
    if manual_auth == "AUTHORIZED_BY_HUMAN":
        # 静默模式：授权通过时不输出，避免重复信息
        log_security_violation(
            "人工环境变量授权", "GOLDEN_SCRIPTS_MANUAL_AUTH=AUTHORIZED_BY_HUMAN"
        )
        sys.exit(0)

    # 只有在需要授权时才输出文件列表
    print("检测到 {} 个核心保护脚本被修改:".format(len(golden_files)))
    for file in golden_files:
        print("   - {}".format(file))
    print("")

    # 在非交互式环境中（如pre-commit），提供清晰的指导
    if not sys.stdin.isatty():
        print("")
        print("ERROR: 无法在pre-commit环境中进行交互式验证")
        print("INFO: Scripts-Golden Protection需要人工授权才能修改核心脚本")
        print("")
        print("=== 人工授权步骤 ===")
        print("1. 打开新的终端窗口（Git Bash、PowerShell或命令提示符）")
        print("2. 进入项目目录：cd S:/WorkShop/cursor/Bravo")
        print("3. 设置授权环境变量：")
        print(
            "   Windows(PowerShell): "
            "$env:GOLDEN_SCRIPTS_MANUAL_AUTH='AUTHORIZED_BY_HUMAN'"
        )
        print("   Windows(CMD): set GOLDEN_SCRIPTS_MANUAL_AUTH=AUTHORIZED_BY_HUMAN")
        print("   Git Bash: export GOLDEN_SCRIPTS_MANUAL_AUTH=AUTHORIZED_BY_HUMAN")
        print('4. 重新运行提交：git commit -m "你的提交信息"')
        print("")
        print("WARNING: 环境变量将在终端关闭时自动失效，确保安全性")
        print("")
        log_security_violation("非交互式环境", "需要人工在独立终端中授权")
        sys.exit(1)

    # 检查是否在CI环境中
    if os.environ.get("CI") == "true":
        print("ERROR: 检测到CI环境中的修改尝试")
        print("INFO: AI无法在CI环境中修改保护脚本")
        log_security_violation("CI环境修改尝试", "文件: {}".format(", ".join(golden_files)))
        sys.exit(1)

    # 要求授权
    if check_modification_authorization():
        print("SUCCESS: scripts-golden保护脚本修改已授权")
        sys.exit(0)
    else:
        print("ERROR: scripts-golden保护脚本修改被拒绝")
        sys.exit(1)


if __name__ == "__main__":
    main()
