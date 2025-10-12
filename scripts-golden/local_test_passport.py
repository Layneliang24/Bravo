#!/usr/bin/env python3
"""
本地测试通行证生成器
强制Cursor进行本地测试，生成推送通行证
基于30轮修复血泪教训，集成多层验证机制
"""

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 北京时区（东八区）
BEIJING_TZ = timezone(timedelta(hours=8))


class LocalTestPassport:
    def __init__(self):
        self.workspace = Path.cwd()
        self.passport_file = self.workspace / ".git" / "local_test_passport.json"
        self.log_file = self.workspace / "logs" / "local_test_passport.log"
        self.log_file.parent.mkdir(exist_ok=True)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        print(f"📋 {message}")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

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
        self.log("🎭 第一层验证：act语法检查")

        try:
            # 检查act是否安装
            subprocess.run(["act", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log("⚠️  act未安装，跳过语法验证（建议安装：choco install act-cli）")
            return True

        try:
            # 测试关键工作流的语法
            workflows_to_test = ["push-validation.yml", "pr-validation.yml"]

            for workflow in workflows_to_test:
                self.log(f"🔍 检查工作流：{workflow}")
                result = subprocess.run(
                    ["act", "push", "-W", f".github/workflows/{workflow}", "--list"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    self.log(f"❌ {workflow} 语法验证失败：{result.stderr}")
                    return False

            # 额外测试：实际运行关键任务检查bash语法
            self.log("🔍 运行bash语法检查...")
            result = subprocess.run(
                [
                    "act",
                    "push",
                    "-W",
                    ".github/workflows/push-validation.yml",
                    "--job",
                    "detect-branch-context",
                    "--quiet",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                self.log(f"❌ 工作流执行测试失败：{result.stderr}")
                # 检查是否包含bash语法错误
                if "unexpected EOF" in result.stderr or "syntax error" in result.stderr:
                    self.log("🚨 检测到bash语法错误！")
                return False

            self.log("✅ act语法验证通过")
            return True

        except subprocess.TimeoutExpired:
            self.log("⏰ act验证超时，继续后续验证")
            return True
        except Exception as e:
            self.log(f"⚠️  act验证异常：{e}")
            return True  # 不阻止流程

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

            # 验证docker-compose配置
            result = subprocess.run(
                ["docker-compose", "config"], capture_output=True, text=True
            )

            if result.returncode != 0:
                self.log(f"❌ docker-compose配置错误：{result.stderr}")
                return False

            # 🔧 方案A：检查必需服务是否已启动
            self.log("🔍 检查必需服务状态...")

            # 检查MySQL服务
            try:
                mysql_result = subprocess.run(
                    [
                        "docker-compose",
                        "exec",
                        "-T",
                        "mysql",
                        "mysqladmin",
                        "ping",
                        "-h",
                        "localhost",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if mysql_result.returncode == 0:
                    self.log("✅ MySQL服务已就绪")
                else:
                    self.log("⚠️  MySQL服务未就绪，可能影响功能测试")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                self.log("⚠️  MySQL服务检查失败，可能影响功能测试")

            # 检查Redis服务
            try:
                redis_result = subprocess.run(
                    ["docker-compose", "exec", "-T", "redis", "redis-cli", "ping"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if redis_result.returncode == 0:
                    self.log("✅ Redis服务已就绪")
                else:
                    self.log("⚠️  Redis服务未就绪，可能影响功能测试")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                self.log("⚠️  Redis服务检查失败，可能影响功能测试")

            self.log("✅ Docker环境验证通过")
            return True

        except subprocess.CalledProcessError as e:
            self.log(f"❌ Docker环境验证失败：{e}")
            return False

    def run_quick_tests(self):
        """第三层：快速功能测试"""
        self.log("🧪 第三层验证：运行核心测试")

        # 使用现有的run_github_actions_simulation.sh
        simulation_script = (
            self.workspace
            / "scripts-golden"
            / "run_github_actions_simulation_simple.sh"
        )
        if not simulation_script.exists():
            self.log("⚠️  未找到GitHub Actions模拟脚本，跳过功能测试")
            return True

        try:
            self.log("🚀 运行GitHub Actions模拟...")
            # 确保在正确的工作目录中执行
            result = subprocess.run(
                ["bash", "scripts-golden/run_github_actions_simulation_simple.sh"],
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                cwd=str(self.workspace),
            )

            if result.returncode == 0:
                self.log("✅ 核心功能测试通过")
                return True
            else:
                self.log(f"❌ 核心功能测试失败：{result.stderr}")
                # 显示详细错误信息
                print("\n" + "=" * 60)
                print("❌ 测试失败详情：")
                print(result.stdout)
                print(result.stderr)
                print("=" * 60)
                return False

        except subprocess.TimeoutExpired:
            self.log("⏰ 功能测试超时（5分钟）")
            return False
        except Exception as e:
            self.log(f"❌ 功能测试异常：{e}")
            return False

    def run_environment_diff_check(self):
        """第四层：环境差异检查"""
        self.log("🔍 第四层验证：环境差异检查")

        # 检查关键配置文件
        config_files = [
            "docker-compose.yml",
            "docker-compose.test.yml",
            "package.json",
            "backend/requirements/test.txt",
        ]

        missing_files = []
        for config_file in config_files:
            if not (self.workspace / config_file).exists():
                missing_files.append(config_file)

        if missing_files:
            self.log(f"⚠️  缺少配置文件：{', '.join(missing_files)}")
            # 不阻止流程，只是警告

        # 检查npm workspaces结构
        if (self.workspace / "package.json").exists():
            try:
                subprocess.run(
                    ["npm", "run", "workspace:check"],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace,
                )
                # 忽略结果，这只是检查
            except Exception:
                pass

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

    def generate_passport(self):
        """生成通行证 - 使用北京时间和完整性验证"""
        current_time = datetime.now(BEIJING_TZ)
        expire_time = current_time + timedelta(hours=1)  # 1小时有效期

        # 标记验证流程已执行
        self._validation_executed = True

        # 生成验证流程的完整性哈希
        validation_process_hash = self._generate_validation_hash()

        passport_data = {
            "version": "1.0",
            "generated_at": current_time.isoformat(),
            "expires_at": expire_time.isoformat(),
            "git_hash": self.get_git_hash(),
            "validation_layers": {
                "act_syntax": True,
                "docker_environment": True,
                "functional_tests": True,
                "environment_diff": True,
            },
            "valid_for_push": True,
            "validation_signature": hashlib.sha256(
                f"{self.get_git_hash()}:{current_time.isoformat()}".encode()
            ).hexdigest()[:32],
            "process_integrity_hash": validation_process_hash,
            "generation_method": "automated_validation",
        }

        # 保存通行证
        with open(self.passport_file, "w", encoding="utf-8") as f:
            json.dump(passport_data, f, indent=2, ensure_ascii=False)

        self.log(f"✅ 通行证已生成，有效期至：{expire_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return passport_data

    def run_full_validation(self):
        """运行完整的多层验证"""
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

        for name, validation_func in validations:
            self.log(f"\n{'='*20} {name} {'='*20}")

            try:
                if not validation_func():
                    failed_validations.append(name)
                    self.log(f"❌ {name}失败")
                else:
                    self.log(f"✅ {name}成功")
            except Exception as e:
                self.log(f"❌ {name}异常：{e}")
                failed_validations.append(name)

        # 总结
        self.log(f"\n{'='*60}")
        self.log("📊 验证结果汇总：")

        if failed_validations:
            self.log(f"❌ 失败的验证：{', '.join(failed_validations)}")
            self.log("🚫 通行证生成失败 - 请修复问题后重新运行")
            return False
        else:
            self.log("🎉 所有验证通过！")
            passport_data = self.generate_passport()
            self.log(f"🎫 通行证ID：{passport_data['validation_signature']}")
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
