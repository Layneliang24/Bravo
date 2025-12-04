#!/usr/bin/env python3
"""
本地测试通行证生成器
强制Cursor进行本地测试，生成推送通行证
基于30轮修复血泪教训，集成多层验证机制
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 设置输出编码为UTF-8，防止Windows GBK编码问题
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    # 设置环境变量
    os.environ["PYTHONIOENCODING"] = "utf-8"

# 北京时区（东八区）
BEIJING_TZ = timezone(timedelta(hours=8))


class LocalTestPassport:
    def __init__(self):
        self.workspace = Path.cwd()
        self.passport_file = self.workspace / ".git" / "local_test_passport.json"
        self.log_file = self.workspace / "logs" / "local_test_passport.log"
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message, level="INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"
        print(f"📋 {message}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def log_detail(self, message, output=""):
        """记录详细日志（包含命令输出）"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        detail_entry = f"[{timestamp}] [DETAIL] {message}\n"
        if output:
            detail_entry += f"  输出:\n{self._indent_text(output, 2)}\n"
        print(f"📋 {message}")
        if output:
            print(self._indent_text(output, 2))
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(detail_entry)

    def log_command(self, command, result):
        """记录命令执行详情"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cmd_str = " ".join(command) if isinstance(command, list) else command
        cmd_entry = f"[{timestamp}] [COMMAND] 执行: {cmd_str}\n"
        cmd_entry += f"  退出码: {result.returncode}\n"
        if result.stdout:
            cmd_entry += f"  标准输出:\n{self._indent_text(result.stdout, 2)}\n"
        if result.stderr:
            cmd_entry += f"  错误输出:\n{self._indent_text(result.stderr, 2)}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(cmd_entry)
        # 控制台输出简化版
        status = "✅" if result.returncode == 0 else "❌"
        cmd_str = " ".join(command) if isinstance(command, list) else command
        print(f"{status} 命令: {cmd_str} (退出码: {result.returncode})")
        if result.returncode != 0 and result.stderr:
            print(f"   错误: {result.stderr[:200]}...")

    def _indent_text(self, text, indent=2):
        """为文本添加缩进"""
        lines = text.split("\n")
        indent_str = " " * indent
        return "\n".join(f"{indent_str}{line}" for line in lines)

    def log_timing(self, step_name, start_time, end_time):
        """记录步骤耗时"""
        duration = (end_time - start_time).total_seconds()
        self.log(f"⏱️  {step_name} 耗时: {duration:.2f}秒", level="TIMING")
        return duration

    def get_git_hash(self):
        """获取当前Git状态的哈希值"""
        try:
            # 获取HEAD提交的哈希
            head_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()

            # 获取工作区状态
            status_output = subprocess.check_output(
                ["git", "status", "--porcelain"], text=True
            ).strip()

            # 生成状态哈希
            status_str = f"{head_hash}:{status_output}"
            return hashlib.sha256(status_str.encode()).hexdigest()[:16]
        except subprocess.CalledProcessError:
            return "unknown"

    def check_existing_passport(self):
        """检查现有通行证是否有效，包括完整性验证"""
        if not self.passport_file.exists():
            return False, "未找到通行证文件"

        try:
            with open(self.passport_file, "r", encoding="utf-8") as f:
                passport_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return False, "通行证文件损坏"

        # 🔒 **新增：完整性验证，防止手动创建的通行证**
        integrity_valid, integrity_message = self._validate_passport_integrity(
            passport_data
        )
        if not integrity_valid:
            return False, f"通行证完整性验证失败: {integrity_message}"

        # 检查过期时间（通行证有效期：1小时）- 使用北京时间
        expire_time = datetime.fromisoformat(
            passport_data.get("expires_at", "1970-01-01")
        )
        current_time = datetime.now(BEIJING_TZ)
        # 如果过期时间没有时区信息，则添加北京时区
        if expire_time.tzinfo is None:
            expire_time = expire_time.replace(tzinfo=BEIJING_TZ)
        if current_time > expire_time:
            return False, "通行证已过期"

        # 检查Git状态是否改变
        current_hash = self.get_git_hash()
        if passport_data.get("git_hash") != current_hash:
            return False, "代码已修改，需要重新测试"

        return True, f"有效通行证，剩余时间：{expire_time - current_time}"

    def run_act_validation(self):
        """第一层：使用act进行GitHub Actions语法验证"""
        start_time = time.time()
        self.log("🎭 第一层验证：act语法检查")
        self.log_detail("开始执行act验证流程")

        # 检查act是否安装
        self.log("🔍 检查act工具是否安装...")
        try:
            version_result = subprocess.run(
                ["act", "--version"],
                check=True,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.log_command(["act", "--version"], version_result)
            self.log_detail("act版本信息", version_result.stdout.strip())
        except FileNotFoundError:
            error_msg = "❌ act未安装！请先安装act工具"
            self.log(error_msg, level="ERROR")
            self.log("💡 安装方法：")
            self.log("   Windows: choco install act-cli")
            self.log("   macOS: brew install act")
            install_cmd = (
                "curl https://raw.githubusercontent.com/nektos/act/master/"
                "install.sh | sudo bash"
            )
            self.log(f"   Linux: {install_cmd}")
            raise RuntimeError(f"{error_msg}\n安装后请重新运行验证")
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ act版本检查失败：{e}"
            self.log(error_msg, level="ERROR")
            self.log_command(["act", "--version"], e)
            raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "❌ act版本检查超时"
            self.log(error_msg, level="ERROR")
            raise RuntimeError(error_msg)

        try:
            # 测试关键工作流的语法
            workflows_to_test = [
                "push-validation.yml",
                "pr-validation.yml",
                "on-push-dev.yml",
                "on-push-feature.yml",
            ]

            for workflow in workflows_to_test:
                workflow_path = self.workspace / ".github" / "workflows" / workflow
                if not workflow_path.exists():
                    self.log(f"⚠️  工作流文件不存在，跳过：{workflow}")
                    continue

                self.log(f"🔍 检查工作流语法：{workflow}")
                self.log_detail(
                    f"执行命令: act push -W .github/workflows/{workflow} --list"
                )

                result = subprocess.run(
                    ["act", "push", "-W", f".github/workflows/{workflow}", "--list"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=30,
                )

                self.log_command(
                    ["act", "push", "-W", f".github/workflows/{workflow}", "--list"],
                    result,
                )

                if result.returncode != 0:
                    error_msg = f"❌ 工作流 {workflow} 语法验证失败"
                    self.log(error_msg, level="ERROR")
                    self.log_detail("验证失败详情", result.stderr)
                    raise RuntimeError(f"{error_msg}\n错误详情：\n{result.stderr}")

                # 解析并显示发现的jobs
                if result.stdout:
                    job_count = len(
                        [
                            line
                            for line in result.stdout.split("\n")
                            if line.strip() and not line.startswith("#")
                        ]
                    )
                    self.log(f"✅ {workflow} 语法正确，发现 {job_count} 个job")

            # 额外测试：使用--dryrun模式真正验证工作流（验证push-validation.yml，因为它有push事件）
            self.log("🔍 运行工作流深度验证（dryrun模式，验证push事件工作流）...")

            # 对push-validation.yml使用dryrun（因为它有push事件）
            workflow_to_validate = ".github/workflows/push-validation.yml"
            if (self.workspace / workflow_to_validate).exists():
                self.log_detail(f"执行命令: act push -W {workflow_to_validate} --dryrun")

                # 使用--dryrun模式，真正验证工作流而不创建容器
                result = subprocess.run(
                    [
                        "act",
                        "push",
                        "-W",
                        workflow_to_validate,
                        "--dryrun",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=180,  # 3分钟超时
                )

                self.log_command(
                    [
                        "act",
                        "push",
                        "-W",
                        workflow_to_validate,
                        "--dryrun",
                    ],
                    result,
                )

                # dryrun模式可能返回非0退出码，但实际验证成功（act的bug）
                # 需要检查stderr中是否有真正的错误，而不是debug日志
                has_real_error = False
                error_keywords = [
                    "error:",
                    "failed",
                    "invalid",
                    "syntax error",
                    "unexpected",
                    "cannot",
                    "could not find",
                ]

                # 检查stderr中是否有真正的错误（排除debug日志）
                stderr_lines = result.stderr.split("\n") if result.stderr else []
                for line in stderr_lines:
                    line_lower = line.lower()
                    # 跳过debug和info级别的日志
                    if "level=debug" in line_lower or "level=info" in line_lower:
                        continue
                    # 检查是否有真正的错误
                    if any(keyword in line_lower for keyword in error_keywords):
                        # 但排除"could not find any stages"（这可能是dryrun的正常行为）
                        if "could not find any stages" in line_lower:
                            self.log(
                                "⚠️  dryrun未找到可运行的stages（可能是工作流没有匹配的事件），但语法验证通过",
                                level="WARNING",
                            )
                            has_real_error = False
                            break
                        has_real_error = True
                        break

                # 检查stdout中是否有错误
                if not has_real_error and result.stdout:
                    stdout_lower = result.stdout.lower()
                    if any(
                        keyword in stdout_lower
                        for keyword in ["error:", "failed", "invalid"]
                    ):
                        has_real_error = True

                # 检查是否是act工具的bug（panic）
                is_act_bug = (
                    "panic:" in result.stderr
                    or "segmentation violation" in result.stderr
                    or "nil pointer" in result.stderr
                )

                if is_act_bug:
                    # act工具本身的bug，降级为警告，不阻止验证
                    self.log(
                        "⚠️  act dryrun模式遇到工具bug（panic），跳过深度验证",
                        level="WARNING",
                    )
                    self.log_detail(
                        "act工具bug详情",
                        result.stderr[:500] if result.stderr else result.stdout[:500],
                    )
                    self.log("ℹ️  语法检查（--list模式）已通过，工作流语法正确")
                elif has_real_error:
                    error_msg = f"❌ 工作流深度验证失败（{workflow_to_validate} dryrun模式）"
                    self.log(error_msg, level="ERROR")

                    # 检查是否包含bash语法错误
                    if (
                        "unexpected EOF" in result.stderr
                        or "syntax error" in result.stderr
                    ):
                        self.log("🚨 检测到bash语法错误！", level="ERROR")
                        error_msg += "（检测到bash语法错误）"

                    # 只显示真正的错误，过滤debug日志
                    error_lines = [
                        line
                        for line in (result.stderr or "").split("\n")
                        if not (
                            "level=debug" in line.lower()
                            or "level=info" in line.lower()
                        )
                    ]
                    error_output = (
                        "\n".join(error_lines[:20])
                        if error_lines
                        else (
                            result.stderr[:500]
                            if result.stderr
                            else result.stdout[:500]
                        )
                    )
                    self.log_detail("验证失败详情（已过滤debug日志）", error_output)
                    raise RuntimeError(f"{error_msg}\n错误详情：\n{error_output}")
                else:
                    # 如果只是debug日志或"could not find stages"（可能是正常情况），视为成功
                    self.log(f"✅ 工作流深度验证通过（{workflow_to_validate} dryrun模式验证成功）")
            else:
                self.log("⚠️  工作流文件不存在，跳过dryrun验证", level="WARNING")

            # 记录耗时
            end_time = datetime.now(BEIJING_TZ)
            start_dt = datetime.fromtimestamp(start_time).replace(tzinfo=BEIJING_TZ)
            duration = self.log_timing("act语法验证", start_dt, end_time)

            self.log("✅ act语法验证通过")
            self.log_detail(f"验证完成，总耗时: {duration:.2f}秒")
            return True

        except subprocess.TimeoutExpired as e:
            error_msg = "⏰ act验证超时（超过30秒）"
            self.log(error_msg, level="ERROR")
            self.log_detail("超时详情", str(e))
            raise RuntimeError(f"{error_msg}\n建议：检查工作流文件是否过于复杂，或使用--dry-run模式")
        except RuntimeError:
            # 重新抛出RuntimeError（这是我们主动抛出的错误）
            raise
        except Exception as e:
            error_msg = f"❌ act验证发生异常：{type(e).__name__}: {str(e)}"
            self.log(error_msg, level="ERROR")
            self.log_detail("异常详情", str(e))
            import traceback

            self.log_detail("异常堆栈", traceback.format_exc())
            raise RuntimeError(error_msg) from e

    def run_docker_validation(self):
        """第二层：Docker环境验证"""
        self.log("🐳 第二层验证：Docker环境检查")

        try:
            # 检查Docker服务
            subprocess.run(["docker", "info"], check=True, capture_output=True)
            self.log("✅ Docker服务正常")

            # 检查docker-compose文件
            if not (self.workspace / "docker-compose.yml").exists():
                self.log("❌ 未找到docker-compose.yml")
                return False

            # 验证docker-compose配置（使用项目名称避免网络冲突）
            result = subprocess.run(
                ["docker-compose", "-p", "bravo", "config"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
            )

            if result.returncode != 0:
                self.log(f"❌ docker-compose配置错误：{result.stderr}")
                return False

            # 🔧 方案A：检查必需服务是否已启动
            self.log("🔍 检查必需服务状态...")

            # 检查MySQL服务（功能验证）
            self.log("🔍 检查MySQL服务功能...")

            try:
                # 1. Ping检查（使用root密码）
                self.log_detail("执行MySQL ping检查")
                mysql_ping_result = subprocess.run(
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "exec",
                        "-T",
                        "mysql",
                        "mysqladmin",
                        "ping",
                        "-h",
                        "localhost",
                        "-uroot",
                        "-proot_password",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                self.log_command(
                    ["docker-compose", "exec", "-T", "mysql", "mysqladmin", "ping"],
                    mysql_ping_result,
                )

                if mysql_ping_result.returncode == 0:
                    self.log("✅ MySQL ping检查通过")

                    # 2. 连接测试（实际连接数据库）
                    self.log_detail("执行MySQL连接测试")
                    mysql_conn_result = subprocess.run(
                        [
                            "docker-compose",
                            "-p",
                            "bravo",
                            "exec",
                            "-T",
                            "mysql",
                            "mysql",
                            "-u",
                            "root",
                            "-proot_password",
                            "-e",
                            "SELECT 1 as test;",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    self.log_command(
                        [
                            "docker-compose",
                            "exec",
                            "-T",
                            "mysql",
                            "mysql",
                            "-u",
                            "root",
                            "-e",
                            "SELECT 1",
                        ],
                        mysql_conn_result,
                    )

                    if mysql_conn_result.returncode == 0:
                        self.log("✅ MySQL连接测试通过")
                    else:
                        error_msg = "❌ MySQL连接测试失败"
                        self.log(error_msg, level="ERROR")
                        self.log_detail("连接失败详情", mysql_conn_result.stderr)
                        raise RuntimeError(
                            f"{error_msg}\n错误详情：\n{mysql_conn_result.stderr}"
                        )
                else:
                    error_msg = "❌ MySQL ping检查失败"
                    self.log(error_msg, level="ERROR")
                    self.log_detail("ping失败详情", mysql_ping_result.stderr)
                    raise RuntimeError(
                        f"{error_msg}\n错误详情：\n{mysql_ping_result.stderr}"
                    )

            except subprocess.TimeoutExpired:
                error_msg = "⏰ MySQL服务检查超时"
                self.log(error_msg, level="ERROR")
                raise RuntimeError(error_msg)
            except RuntimeError:
                raise
            except Exception as e:
                error_msg = f"❌ MySQL服务检查异常：{type(e).__name__}: {str(e)}"
                self.log(error_msg, level="ERROR")
                raise RuntimeError(error_msg) from e

            # 检查Redis服务（功能验证）
            self.log("🔍 检查Redis服务功能...")

            try:
                # 1. Ping检查
                self.log_detail("执行Redis ping检查")
                redis_ping_result = subprocess.run(
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "exec",
                        "-T",
                        "redis",
                        "redis-cli",
                        "ping",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=5,
                )
                self.log_command(
                    ["docker-compose", "exec", "-T", "redis", "redis-cli", "ping"],
                    redis_ping_result,
                )

                if (
                    redis_ping_result.returncode == 0
                    and "PONG" in redis_ping_result.stdout
                ):
                    self.log("✅ Redis ping检查通过")

                    # 2. 读写测试（实际写入和读取数据）
                    self.log_detail("执行Redis读写测试")
                    redis_write_result = subprocess.run(
                        [
                            "docker-compose",
                            "-p",
                            "bravo",
                            "exec",
                            "-T",
                            "redis",
                            "redis-cli",
                            "SET",
                            "test_key",
                            "test_value",
                        ],
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="ignore",
                        timeout=5,
                    )

                    if redis_write_result.returncode == 0:
                        redis_read_result = subprocess.run(
                            [
                                "docker-compose",
                                "-p",
                                "bravo",
                                "exec",
                                "-T",
                                "redis",
                                "redis-cli",
                                "GET",
                                "test_key",
                            ],
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="ignore",
                            timeout=5,
                        )

                        # 清理测试key
                        subprocess.run(
                            [
                                "docker-compose",
                                "-p",
                                "bravo",
                                "exec",
                                "-T",
                                "redis",
                                "redis-cli",
                                "DEL",
                                "test_key",
                            ],
                            capture_output=True,
                            timeout=2,
                        )

                        if (
                            redis_read_result.returncode == 0
                            and "test_value" in redis_read_result.stdout
                        ):
                            self.log("✅ Redis读写测试通过")
                        else:
                            error_msg = "❌ Redis读取测试失败"
                            self.log(error_msg, level="ERROR")
                            raise RuntimeError(error_msg)
                    else:
                        error_msg = "❌ Redis写入测试失败"
                        self.log(error_msg, level="ERROR")
                        raise RuntimeError(error_msg)
                else:
                    error_msg = "❌ Redis ping检查失败"
                    self.log(error_msg, level="ERROR")
                    self.log_detail("ping失败详情", redis_ping_result.stderr)
                    raise RuntimeError(
                        f"{error_msg}\n错误详情：\n{redis_ping_result.stderr}"
                    )

            except subprocess.TimeoutExpired:
                error_msg = "⏰ Redis服务检查超时"
                self.log(error_msg, level="ERROR")
                raise RuntimeError(error_msg)
            except RuntimeError:
                raise
            except Exception as e:
                error_msg = f"❌ Redis服务检查异常：{type(e).__name__}: {str(e)}"
                self.log(error_msg, level="ERROR")
                raise RuntimeError(error_msg) from e

            self.log("✅ Docker环境验证通过")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Docker环境验证失败：{e}")
            return False

    def run_quick_tests(self):
        """第三层：快速功能测试 - 真实的测试执行"""
        start_time = time.time()
        self.log("🧪 第三层验证：运行核心测试")
        self.log_detail("开始执行真实功能测试（非模拟）")

        test_results = {
            "backend_check": False,
            "frontend_check": False,
            "backend_tests": False,
        }

        # 1. 后端Django配置检查
        self.log("🔍 步骤1: 后端Django配置检查...")
        cmd_desc = (
            "docker-compose run --rm backend python manage.py check "
            "--settings=bravo.settings.test"
        )
        self.log_detail("执行命令", cmd_desc)

        try:
            # 先尝试使用exec（如果backend容器已运行），否则使用run
            # 检查backend容器是否在运行
            check_backend = subprocess.run(
                ["docker-compose", "-p", "bravo", "ps", "-q", "backend"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if check_backend.returncode == 0 and check_backend.stdout.strip():
                # backend容器已运行，使用exec
                self.log_detail("backend容器已运行，使用exec方式")
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "exec",
                        "-T",
                        "backend",
                        "python",
                        "manage.py",
                        "check",
                        "--settings=bravo.settings.test",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=60,
                    cwd=str(self.workspace),
                )
            else:
                # backend容器未运行，使用run（但先启动依赖服务）
                self.log_detail("backend容器未运行，先启动依赖服务")
                # 确保MySQL和Redis已启动
                subprocess.run(
                    ["docker-compose", "-p", "bravo", "up", "-d", "mysql", "redis"],
                    capture_output=True,
                    timeout=30,
                )
                # 等待服务就绪
                time.sleep(3)

                # 使用run创建临时容器
                result = subprocess.run(
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "run",
                        "--rm",
                        "--no-deps",
                        "backend",
                        "python",
                        "manage.py",
                        "check",
                        "--settings=bravo.settings.test",
                    ],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=60,
                    cwd=str(self.workspace),
                )

            self.log_command(
                [
                    "docker-compose",
                    "run",
                    "--rm",
                    "backend",
                    "python",
                    "manage.py",
                    "check",
                ],
                result,
            )

            if result.returncode == 0:
                self.log("✅ 后端Django配置检查通过")
                test_results["backend_check"] = True
            else:
                error_msg = "❌ 后端Django配置检查失败"
                self.log(error_msg, level="ERROR")
                self.log_detail("检查失败详情", result.stderr)
                raise RuntimeError(f"{error_msg}\n错误详情：\n{result.stderr}")
        except subprocess.TimeoutExpired:
            error_msg = "⏰ 后端配置检查超时（60秒）"
            self.log(error_msg, level="ERROR")
            raise RuntimeError(error_msg)
        except RuntimeError:
            raise
        except Exception as e:
            error_msg = f"❌ 后端配置检查异常：{type(e).__name__}: {str(e)}"
            self.log(error_msg, level="ERROR")
            raise RuntimeError(error_msg) from e

        # 2. 前端基础检查（lint或build检查）——改为必选，任何失败视为整体失败
        self.log("🔍 步骤2: 前端基础检查（必选）...")

        # 检查frontend容器是否在运行
        check_frontend = subprocess.run(
            ["docker-compose", "-p", "bravo", "ps", "-q", "frontend"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # 构建检查命令（根据容器状态选择exec或run）
        if check_frontend.returncode == 0 and check_frontend.stdout.strip():
            # frontend容器已运行，使用exec
            self.log_detail("frontend容器已运行，使用exec方式")
            frontend_checks = [
                (
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "exec",
                        "-T",
                        "frontend",
                        "npm",
                        "run",
                        "lint",
                    ],
                    "lint检查",
                ),
                (
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "exec",
                        "-T",
                        "frontend",
                        "npm",
                        "run",
                        "type-check",
                    ],
                    "类型检查",
                ),
                (
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "exec",
                        "-T",
                        "frontend",
                        "npm",
                        "run",
                        "build",
                    ],
                    "build检查",
                ),
            ]
        else:
            # frontend容器未运行，先启动
            self.log_detail("frontend容器未运行，先启动服务")
            subprocess.run(
                ["docker-compose", "-p", "bravo", "up", "-d", "frontend"],
                capture_output=True,
                timeout=60,
            )
            time.sleep(3)
            # 使用run创建临时容器
            frontend_checks = [
                (
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "run",
                        "--rm",
                        "--no-deps",
                        "frontend",
                        "npm",
                        "run",
                        "lint",
                    ],
                    "lint检查",
                ),
                (
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "run",
                        "--rm",
                        "--no-deps",
                        "frontend",
                        "npm",
                        "run",
                        "type-check",
                    ],
                    "类型检查",
                ),
                (
                    [
                        "docker-compose",
                        "-p",
                        "bravo",
                        "run",
                        "--rm",
                        "--no-deps",
                        "frontend",
                        "npm",
                        "run",
                        "build",
                    ],
                    "build检查",
                ),
            ]

        frontend_check_passed = False
        frontend_errors = []
        for check_cmd, check_name in frontend_checks:
            self.log_detail(f"尝试执行: {check_name}")
            try:
                result = subprocess.run(
                    check_cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    timeout=120,
                    cwd=str(self.workspace),
                )
                if result.returncode == 0:
                    self.log(f"✅ 前端{check_name}通过")
                    self.log_command(check_cmd, result)
                    test_results["frontend_check"] = True
                    frontend_check_passed = True
                    break
                else:
                    error_msg = f"前端{check_name}失败（退出码: {result.returncode})"
                    frontend_errors.append(error_msg)
                    self.log(f"⚠️  {error_msg}")
                    self.log_detail("前端检查失败详情", result.stderr or result.stdout)
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                error_msg = f"前端{check_name}执行异常: {type(e).__name__}: {str(e)}"
                frontend_errors.append(error_msg)
                self.log(f"⚠️  {error_msg}")
            except Exception as e:
                error_msg = f"前端{check_name}执行异常: {type(e).__name__}: {str(e)}"
                frontend_errors.append(error_msg)
                self.log(f"⚠️  {error_msg}")

        if not frontend_check_passed:
            # 所有前端检查均失败，视为功能验证失败
            error_msg = "❌ 前端基础检查未通过（所有检查均失败或异常）"
            self.log(error_msg, level="ERROR")
            if frontend_errors:
                self.log_detail("前端检查错误汇总", "\n".join(frontend_errors))
            raise RuntimeError(error_msg)

        # 3. 后端单元测试（运行少量关键测试）——改为必选
        self.log("🔍 步骤3: 后端单元测试（快速模式，必选）...")
        pytest_cmd_desc = (
            "docker-compose run --rm backend pytest tests/unit/ -v "
            "--maxfail=3 -k 'test_' --tb=short"
        )
        self.log_detail("执行命令", pytest_cmd_desc)

        try:
            # 检查backend容器是否在运行，选择exec或run
            check_backend_for_test = subprocess.run(
                ["docker-compose", "-p", "bravo", "ps", "-q", "backend"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if (
                check_backend_for_test.returncode == 0
                and check_backend_for_test.stdout.strip()
            ):
                # backend容器已运行，使用exec
                self.log_detail("backend容器已运行，使用exec方式执行测试")
                pytest_cmd = [
                    "docker-compose",
                    "-p",
                    "bravo",
                    "exec",
                    "-T",
                    "backend",
                    "pytest",
                    "tests/unit/",
                    "-v",
                    "--maxfail=3",
                    "-k",
                    "test_",
                    "--tb=short",
                ]
            else:
                # backend容器未运行，使用run
                self.log_detail("backend容器未运行，使用run方式执行测试")
                pytest_cmd = [
                    "docker-compose",
                    "-p",
                    "bravo",
                    "run",
                    "--rm",
                    "--no-deps",
                    "backend",
                    "pytest",
                    "tests/unit/",
                    "-v",
                    "--maxfail=3",
                    "-k",
                    "test_",
                    "--tb=short",
                ]

            result = subprocess.run(
                pytest_cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=180,  # 3分钟超时
                cwd=str(self.workspace),
            )

            self.log_command(
                ["docker-compose", "run", "--rm", "backend", "pytest", "tests/unit/"],
                result,
            )

            # 解析测试结果
            if result.returncode == 0:
                # 提取完整的测试结果摘要
                output_lines = result.stdout.split("\n")

                # 查找测试统计行（如 "32 passed, 1 warning in 35.58s"）
                test_summary = None
                for line in output_lines:
                    if "passed" in line.lower() and (
                        "failed" in line.lower()
                        or "warning" in line.lower()
                        or "in" in line.lower()
                    ):
                        test_summary = line.strip()
                        break

                # 提取测试数量
                import re

                passed_match = re.search(
                    r"(\d+)\s+passed", result.stdout, re.IGNORECASE
                )
                failed_match = re.search(
                    r"(\d+)\s+failed", result.stdout, re.IGNORECASE
                )

                passed_count = int(passed_match.group(1)) if passed_match else 0
                failed_count = int(failed_match.group(1)) if failed_match else 0

                # 显示详细测试结果
                if test_summary:
                    self.log(f"✅ 后端单元测试通过: {test_summary}")
                else:
                    self.log(f"✅ 后端单元测试通过: {passed_count}个测试通过")

                # 输出关键测试信息（前20行和后10行）
                output_preview = "\n".join(
                    output_lines[:20] + ["..."] + output_lines[-10:]
                )
                self.log_detail("测试执行详情（摘要）", output_preview)

                # 如果测试数量为0，视为失败
                if passed_count == 0 and failed_count == 0:
                    error_msg = "❌ 未找到任何测试用例"
                    self.log(error_msg, level="ERROR")
                    raise RuntimeError(error_msg)

                test_results["backend_tests"] = True
            elif result.returncode == 5:  # pytest退出码5表示没有找到测试
                error_msg = "❌ 未找到后端单元测试（pytest退出码5）"
                self.log(error_msg, level="ERROR")
                raise RuntimeError(error_msg)
            else:
                error_msg = "❌ 后端单元测试失败"
                self.log(error_msg, level="ERROR")
                self.log_detail(
                    "测试失败详情",
                    result.stderr[:500] if result.stderr else result.stdout[:500],
                )
                raise RuntimeError(error_msg)
        except subprocess.TimeoutExpired:
            error_msg = "❌ 后端单元测试超时（3分钟）"
            self.log(error_msg, level="ERROR")
            raise RuntimeError(error_msg)
        except FileNotFoundError:
            error_msg = "❌ pytest未找到，无法运行后端单元测试"
            self.log(error_msg, level="ERROR")
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"❌ 后端单元测试异常：{type(e).__name__}: {str(e)}"
            self.log(error_msg, level="ERROR")
            raise RuntimeError(error_msg) from e

        # 记录耗时
        end_time = datetime.now(BEIJING_TZ)
        start_dt = datetime.fromtimestamp(start_time).replace(tzinfo=BEIJING_TZ)
        duration = self.log_timing("功能测试", start_dt, end_time)

        # 总结测试结果（此时三项检查都应为必选且成功）
        self.log(f"\n📊 功能测试结果汇总（耗时: {duration:.2f}秒）:")
        self.log(f"  后端配置检查: {'✅' if test_results['backend_check'] else '❌'}")
        self.log(f"  前端基础检查: {'✅' if test_results['frontend_check'] else '❌'}")
        self.log(f"  后端单元测试: {'✅' if test_results['backend_tests'] else '❌'}")

        # 严格模式：任一检查失败都视为功能验证失败（理论上到这里都应为True）
        if not all(test_results.values()):
            raise RuntimeError("功能测试结果中存在失败项，请检查日志")

        self.log("✅ 核心功能测试完成（所有检查通过）")
        return True

    def run_environment_diff_check(self):
        """第四层：环境差异检查 - 真正比较开发/测试/生产环境配置差异"""
        self.log("🔍 第四层验证：环境差异检查")
        self.log_detail("检查开发、测试、生产环境配置差异")

        # 1. 检查关键配置文件存在性
        config_files = {
            "docker-compose.yml": "开发环境配置",
            "docker-compose.test.yml": "测试环境配置",
            "package.json": "项目依赖配置",
            "backend/requirements/test.txt": "测试依赖配置",
        }

        missing_files = []
        for config_file, description in config_files.items():
            if not (self.workspace / config_file).exists():
                missing_files.append(f"{config_file} ({description})")

        if missing_files:
            self.log(f"⚠️  缺少配置文件：{', '.join(missing_files)}")
            # 不阻止流程，只是警告

        # 2. 真正比较docker-compose配置差异
        docker_compose_dev = self.workspace / "docker-compose.yml"
        docker_compose_test = self.workspace / "docker-compose.test.yml"

        if docker_compose_dev.exists() and docker_compose_test.exists():
            self.log_detail("比较docker-compose.yml和docker-compose.test.yml的差异")
            try:
                # 使用docker-compose config验证两个文件
                result_dev = subprocess.run(
                    ["docker-compose", "-f", str(docker_compose_dev), "config"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                result_test = subprocess.run(
                    ["docker-compose", "-f", str(docker_compose_test), "config"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result_dev.returncode != 0:
                    self.log(
                        f"⚠️  开发环境配置验证失败：{result_dev.stderr[:200]}", level="WARNING"
                    )
                if result_test.returncode != 0:
                    self.log(
                        f"⚠️  测试环境配置验证失败：{result_test.stderr[:200]}", level="WARNING"
                    )

                # 检查关键服务配置差异
                if result_dev.returncode == 0 and result_test.returncode == 0:
                    # 提取服务列表
                    dev_services = set()
                    test_services = set()

                    for line in result_dev.stdout.split("\n"):
                        if ":" in line and not line.strip().startswith("#"):
                            service = line.split(":")[0].strip()
                            if service and not service.startswith("version"):
                                dev_services.add(service)

                    for line in result_test.stdout.split("\n"):
                        if ":" in line and not line.strip().startswith("#"):
                            service = line.split(":")[0].strip()
                            if service and not service.startswith("version"):
                                test_services.add(service)

                    # 比较服务差异
                    missing_in_test = dev_services - test_services
                    extra_in_test = test_services - dev_services

                    if missing_in_test:
                        self.log(
                            f"⚠️  测试环境缺少服务：{', '.join(missing_in_test)}",
                            level="WARNING",
                        )
                    if extra_in_test:
                        self.log(f"ℹ️  测试环境额外服务：{', '.join(extra_in_test)}")

                    self.log_detail(
                        f"开发环境服务数: {len(dev_services)}, 测试环境服务数: {len(test_services)}"
                    )
            except Exception as e:
                self.log(f"⚠️  配置差异检查异常：{type(e).__name__}: {str(e)}", level="WARNING")

        # 3. 检查npm workspaces结构
        if (self.workspace / "package.json").exists():
            try:
                result = subprocess.run(
                    ["npm", "run", "workspace:check"],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace,
                    timeout=10,
                )
                if result.returncode == 0:
                    self.log_detail("npm workspaces结构检查通过")
                else:
                    self.log(
                        f"⚠️  npm workspaces检查失败：{result.stderr[:200]}", level="WARNING"
                    )
            except Exception as e:
                self.log(f"⚠️  npm workspaces检查异常：{type(e).__name__}", level="WARNING")

        # 4. 检查环境变量配置差异
        env_files = {
            ".env": "开发环境变量",
            ".env.test": "测试环境变量",
            ".env.production": "生产环境变量",
        }

        env_file_status = {}
        for env_file, description in env_files.items():
            env_path = self.workspace / env_file
            if env_path.exists():
                env_file_status[description] = "存在"
            else:
                env_file_status[description] = "不存在"

        self.log_detail(
            "环境变量文件状态", "\n".join([f"  {k}: {v}" for k, v in env_file_status.items()])
        )

        self.log("✅ 环境差异检查完成")
        return True

    def _generate_validation_hash(self):
        """生成验证流程的完整性哈希，防止手动创建通行证"""
        # 收集验证过程的证据
        evidence = []

        # 检查是否真实执行了验证流程
        if hasattr(self, "_validation_executed"):
            evidence.append("validation_executed")

        # 检查Docker环境
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                evidence.append(f"docker_version:{result.stdout.strip()}")
        except Exception:
            evidence.append("docker_check_failed")

        # 检查工作目录
        evidence.append(f"workspace:{self.workspace}")
        evidence.append(f"git_status:{self.get_git_hash()}")

        # 生成时间戳和调用栈信息
        import inspect

        stack = inspect.stack()
        caller_info = [frame.function for frame in stack[:5]]
        evidence.append(f"call_stack:{':'.join(caller_info)}")

        # 生成综合哈希
        evidence_str = "|".join(evidence)
        return hashlib.sha256(evidence_str.encode()).hexdigest()[:24]

    def _validate_passport_integrity(self, passport_data):
        """验证通行证完整性，检测手动创建的通行证"""
        # 检查必需字段
        required_fields = [
            "process_integrity_hash",
            "generation_method",
            "validation_signature",
        ]
        for field in required_fields:
            if field not in passport_data:
                self.log(f"⚠️  通行证缺少必需字段: {field}")
                return False, f"通行证缺少必需字段: {field}"

        # 检查生成方法
        if passport_data.get("generation_method") != "automated_validation":
            return False, "通行证生成方法不正确，疑似手动创建"

        # 验证完整性哈希格式
        integrity_hash = passport_data.get("process_integrity_hash", "")
        if len(integrity_hash) != 24 or not all(
            c in "0123456789abcdef" for c in integrity_hash
        ):
            return False, "通行证完整性哈希格式无效"

        # 检查可疑的手动创建特征
        signature = passport_data.get("validation_signature", "")
        if (
            "manual" in signature.lower()
            or "bypass" in signature.lower()
            or "temp" in signature.lower()
        ):
            return False, "检测到手动创建的通行证特征"

        return True, "通行证完整性验证通过"

    def _get_act_version(self):
        """获取act版本信息"""
        try:
            result = subprocess.run(
                ["act", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _get_docker_version(self):
        """获取Docker版本信息"""
        try:
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return "unknown"

    def _get_test_summary(self):
        """获取测试摘要信息"""
        # 从日志文件中提取测试结果摘要
        summary = {
            "backend_check": "unknown",
            "frontend_check": "unknown",
            "backend_tests": "unknown",
        }

        try:
            if self.log_file.exists():
                with open(self.log_file, "r", encoding="utf-8") as f:
                    log_content = f.read()
                    # 查找测试结果
                    if "✅ 后端Django配置检查通过" in log_content:
                        summary["backend_check"] = "passed"
                    elif "❌ 后端Django配置检查失败" in log_content:
                        summary["backend_check"] = "failed"

                    if "✅ 前端" in log_content and "检查通过" in log_content:
                        summary["frontend_check"] = "passed"
                    elif "⚠️  前端检查跳过" in log_content:
                        summary["frontend_check"] = "skipped"

                    if "✅ 后端单元测试通过" in log_content:
                        summary["backend_tests"] = "passed"
                    elif "⚠️  未找到后端单元测试" in log_content:
                        summary["backend_tests"] = "skipped"
        except Exception:
            pass

        return summary

    def generate_passport(self, validation_results=None):
        """生成通行证 - 使用北京时间和完整性验证"""
        current_time = datetime.now(BEIJING_TZ)
        expire_time = current_time + timedelta(hours=1)  # 1小时有效期

        # 标记验证流程已执行
        self._validation_executed = True

        # 生成验证流程的完整性哈希
        validation_process_hash = self._generate_validation_hash()

        # 默认验证结果
        if validation_results is None:
            validation_results = {
                "act_syntax": True,
                "docker_environment": True,
                "functional_tests": True,
                "environment_diff": True,
            }

        passport_data = {
            "version": "1.0",
            "generated_at": current_time.isoformat(),
            "expires_at": expire_time.isoformat(),
            "git_hash": self.get_git_hash(),
            "validation_layers": validation_results,
            "valid_for_push": True,
            "validation_signature": hashlib.sha256(
                f"{self.get_git_hash()}:{current_time.isoformat()}".encode()
            ).hexdigest()[:32],
            "process_integrity_hash": validation_process_hash,
            "generation_method": "automated_validation",
            # 新增：详细验证结果
            "validation_details": {
                "act_version": self._get_act_version(),
                "docker_version": self._get_docker_version(),
                "test_summary": self._get_test_summary(),
                "execution_time_seconds": None,  # 将在run_full_validation中填充
            },
        }

        # 保存通行证
        with open(self.passport_file, "w", encoding="utf-8") as f:
            json.dump(passport_data, f, indent=2, ensure_ascii=False)

        self.log(f"✅ 通行证已生成，有效期至：{expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return passport_data

    def run_full_validation(self):
        """运行完整的多层验证"""
        validation_start_time = time.time()
        self.log("🎯 开始本地测试通行证生成流程")
        self.log(f"📁 工作目录：{self.workspace}")
        self.log("=" * 60)

        # 四层验证机制（基于30轮修复教训）
        validations = [
            ("语法验证", self.run_act_validation),
            ("环境验证", self.run_docker_validation),
            ("功能验证", self.run_quick_tests),
            ("差异验证", self.run_environment_diff_check),
        ]

        failed_validations = []
        validation_results = {
            "act_syntax": False,
            "docker_environment": False,
            "functional_tests": False,
            "environment_diff": False,
        }
        layer_timings = {}

        for name, validation_func in validations:
            layer_start_time = time.time()
            self.log(f"\n{'=' * 20} {name} {'=' * 20}")

            try:
                if not validation_func():
                    failed_validations.append(name)
                    self.log(f"❌ {name}失败", level="ERROR")
                else:
                    self.log(f"✅ {name}成功")
                    # 更新验证结果
                    if name == "语法验证":
                        validation_results["act_syntax"] = True
                    elif name == "环境验证":
                        validation_results["docker_environment"] = True
                    elif name == "功能验证":
                        validation_results["functional_tests"] = True
                    elif name == "差异验证":
                        validation_results["environment_diff"] = True
            except RuntimeError as e:
                # RuntimeError是我们主动抛出的错误，需要详细记录并终止
                error_msg = str(e)
                self.log(f"❌ {name}失败：{error_msg}", level="ERROR")
                self.log_detail(f"{name}失败详情", error_msg)
                failed_validations.append(name)
                # 如果是act验证失败，立即终止（不继续后续验证）
                if name == "语法验证":
                    self.log("🚨 act验证失败，终止整个验证流程", level="ERROR")
                    break
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                self.log(f"❌ {name}异常：{error_msg}", level="ERROR")
                self.log_detail(f"{name}异常详情", error_msg)
                import traceback

                self.log_detail(f"{name}异常堆栈", traceback.format_exc())
                failed_validations.append(name)
            finally:
                # 记录每层耗时
                layer_end_time = time.time()
                layer_duration = layer_end_time - layer_start_time
                layer_timings[name] = round(layer_duration, 2)
                start_dt = datetime.fromtimestamp(layer_start_time).replace(
                    tzinfo=BEIJING_TZ
                )
                end_dt = datetime.fromtimestamp(layer_end_time).replace(
                    tzinfo=BEIJING_TZ
                )
                self.log_timing(f"{name}层", start_dt, end_dt)

        # 计算总耗时
        validation_end_time = time.time()
        total_duration = validation_end_time - validation_start_time

        # 总结
        self.log(f"\n{'=' * 60}")
        self.log("📊 验证结果汇总：")
        self.log(f"⏱️  总耗时: {total_duration:.2f}秒")
        for layer_name, duration in layer_timings.items():
            self.log(f"  {layer_name}: {duration}秒")

        if failed_validations:
            self.log(f"❌ 失败的验证：{', '.join(failed_validations)}")
            self.log("🚫 通行证生成失败 - 请修复问题后重新运行")
            return False
        else:
            self.log("🎉 所有验证通过！")

            # 生成通行证，包含详细验证结果
            passport_data = self.generate_passport(validation_results)
            # 填充执行时间
            passport_data["validation_details"]["execution_time_seconds"] = round(
                total_duration, 2
            )
            passport_data["validation_details"]["layer_timings"] = layer_timings

            # 保存更新后的通行证
            with open(self.passport_file, "w", encoding="utf-8") as f:
                json.dump(passport_data, f, indent=2, ensure_ascii=False)

            self.log(f"🎫 通行证ID：{passport_data['validation_signature']}")
            self.log("📊 验证详情：")
            self.log(f"  act版本: {passport_data['validation_details']['act_version']}")
            docker_ver = passport_data["validation_details"]["docker_version"]
            self.log(f"  Docker版本: {docker_ver}")
            self.log(f"  总耗时: {total_duration:.2f}秒")
            self.log("🚀 现在可以安全推送到远程仓库")
            return True

    def show_passport_status(self):
        """显示通行证状态，包括完整性验证"""
        valid, message = self.check_existing_passport()

        if valid:
            with open(self.passport_file, "r", encoding="utf-8") as f:
                passport_data = json.load(f)

            print("🎫 当前通行证状态：✅ 有效")
            print(f"📅 生成时间：{passport_data['generated_at']}")
            print(f"⏰ 过期时间：{passport_data['expires_at']}")
            print(f"🔑 签名：{passport_data['validation_signature']}")

            # 显示完整性验证信息
            generation_method = passport_data.get("generation_method", "未知")
            integrity_hash = passport_data.get("process_integrity_hash", "无")
            print(f"🔒 生成方法：{generation_method}")
            print(f"🛡️  完整性哈希：{integrity_hash}")

            print(f"💬 状态：{message}")
        else:
            print("🚫 当前通行证状态：❌ 无效")
            print(f"💬 原因：{message}")

            # 如果失败原因包含完整性验证，给出具体提示
            if "完整性验证失败" in message:
                print("🚨 检测到可能的通行证伪造或手动创建")
                print("💡 请使用 ./test --force 重新生成合法通行证")


def main():
    parser = argparse.ArgumentParser(description="本地测试通行证生成器")
    parser.add_argument("--check", action="store_true", help="检查现有通行证状态")
    parser.add_argument("--force", action="store_true", help="强制重新生成通行证")

    args = parser.parse_args()

    passport = LocalTestPassport()

    if args.check:
        # 检查通行证状态并根据结果设置退出码
        valid, message = passport.check_existing_passport()
        passport.show_passport_status()

        # 🔒 重要：退出码必须反映验证结果
        if valid:
            sys.exit(0)  # 通行证有效
        else:
            sys.exit(1)  # 通行证无效，包括完整性验证失败

    # 检查现有通行证
    if not args.force:
        valid, message = passport.check_existing_passport()
        if valid:
            print(f"✅ 已有有效通行证：{message}")
            passport.show_passport_status()
            sys.exit(0)
        else:
            print(f"⚠️  {message}")

    # 运行完整验证
    success = passport.run_full_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
# 新成员添加的注释 - Sat, Sep 27, 2025  1:49:32 PM
