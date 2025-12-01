#!/usr/bin/env python3
"""
合规引擎核心：加载规则、执行检查、聚合结果
"""

import fnmatch
import importlib
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import yaml


class ComplianceEngine:
    """合规引擎"""

    def __init__(self, config_path: str = ".compliance/config.yaml"):
        self.config_path = config_path
        # 设置项目根目录
        config_abs_path = Path(config_path).resolve()
        self.project_root = (
            config_abs_path.parent.parent
        )  # .compliance/config.yaml -> 项目根目录
        self.config = self._load_config()
        self.rules = self._load_rules()
        self.checkers = self._load_checkers()
        self.audit_log = []

    def _load_config(self) -> Dict:
        """加载全局配置"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        # 环境变量替换
        config = self._replace_env_vars(config)

        return config

    def _replace_env_vars(self, obj: Any) -> Any:
        """递归替换环境变量 ${VAR_NAME}"""
        if isinstance(obj, dict):
            return {k: self._replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            var_name = obj[2:-1]
            return os.getenv(var_name, obj)
        else:
            return obj

    def _load_rules(self) -> Dict[str, Dict]:
        """加载所有规则文件"""
        rules = {}
        rules_dir = self.config["rules"]["rules_dir"]

        if not os.path.exists(rules_dir):
            print(f"⚠️ 规则目录不存在: {rules_dir}", file=sys.stderr)
            return rules

        for rule_file in Path(rules_dir).glob("*.yaml"):
            rule_name = rule_file.stem
            try:
                with open(rule_file, "r", encoding="utf-8") as f:
                    rules[rule_name] = yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ 加载规则文件失败 {rule_file}: {e}", file=sys.stderr)

        if rules:
            print(f"✅ 加载 {len(rules)} 个规则文件", file=sys.stderr)
        return rules

    def _load_checkers(self) -> Dict[str, Any]:
        """加载所有检查器插件"""
        checkers = {}
        checkers_dir = self.config["checkers"]["checkers_dir"]

        if not os.path.exists(checkers_dir):
            print(f"⚠️ 检查器目录不存在: {checkers_dir}", file=sys.stderr)
            return checkers

        # 动态导入检查器模块
        checkers_parent = os.path.dirname(checkers_dir)
        if checkers_parent not in sys.path:
            sys.path.insert(0, checkers_parent)

        try:
            from compliance.checkers import (
                CodeChecker,
                CommitChecker,
                PRDChecker,
                TaskChecker,
                TestChecker,
            )

            # 创建检查器实例（需要规则配置，稍后设置）
            checker_classes = {
                "prd": PRDChecker,
                "test": TestChecker,
                "code": CodeChecker,
                "commit": CommitChecker,
                "task": TaskChecker,
            }

            for rule_name, checker_class in checker_classes.items():
                if rule_name in self.rules:
                    checkers[rule_name] = checker_class(self.rules[rule_name])
                    print(f"✅ 加载检查器: {rule_name}", file=sys.stderr)
        except ImportError as e:
            print(f"⚠️ 导入检查器失败: {e}", file=sys.stderr)
            # 尝试直接导入
            for checker_file in Path(checkers_dir).glob("*_checker.py"):
                module_name = checker_file.stem
                try:
                    # 构建模块路径
                    module_path = f"compliance.checkers.{module_name}"
                    module = importlib.import_module(module_path)
                    # 查找Checker类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and attr_name.endswith("Checker")
                            and attr_name != "BaseChecker"
                        ):
                            rule_name = module_name.replace("_checker", "")
                            if rule_name in self.rules:
                                checkers[rule_name] = attr(self.rules[rule_name])
                                print(f"✅ 加载检查器: {rule_name}", file=sys.stderr)
                except Exception as e:
                    print(f"❌ 加载检查器失败 {module_name}: {e}", file=sys.stderr)

        return checkers

    def check_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        检查文件列表

        Args:
            file_paths: 文件路径列表

        Returns:
            检查结果字典
        """
        results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "summary": {
                "total": len(file_paths),
                "passed": 0,
                "failed": 0,
                "warnings": 0,
            },
        }

        for file_path in file_paths:
            # 检查是否在排除路径中
            if self._is_excluded(file_path):
                continue

            # 匹配规则
            matched_rules = self._match_rules(file_path)

            if not matched_rules:
                # 没有匹配的规则，跳过
                continue

            # 执行检查
            file_result = self._check_file(file_path, matched_rules)

            if file_result["status"] == "passed":
                results["passed"].append(file_result)
                results["summary"]["passed"] += 1
            elif file_result["status"] == "failed":
                results["failed"].append(file_result)
                results["summary"]["failed"] += 1
            elif file_result["status"] == "warning":
                results["warnings"].append(file_result)
                results["summary"]["warnings"] += 1

        # 记录审计日志
        if self.config["engine"]["enable_audit_log"]:
            self._write_audit_log(results)

        return results

    def _is_excluded(self, file_path: str) -> bool:
        """检查文件是否在排除列表中"""
        exclude_paths = self.config.get("exclude_paths", [])
        for pattern in exclude_paths:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def _match_rules(self, file_path: str) -> List[str]:
        """匹配文件路径对应的规则"""
        matched_rules = []

        file_rules_mapping = self.config.get("file_rules_mapping", [])
        for mapping in file_rules_mapping:
            pattern = mapping["pattern"]
            # 支持glob模式匹配
            if fnmatch.fnmatch(file_path, pattern):
                matched_rules.extend(mapping["rules"])

        # 去重
        return list(set(matched_rules))

    def _check_file(self, file_path: str, rule_names: List[str]) -> Dict[str, Any]:
        """
        对单个文件执行检查

        Args:
            file_path: 文件路径
            rule_names: 规则名称列表

        Returns:
            检查结果
        """
        result = {
            "file": file_path,
            "rules_applied": rule_names,
            "status": "passed",
            "errors": [],
            "warnings": [],
        }

        for rule_name in rule_names:
            if rule_name not in self.rules:
                result["warnings"].append(f"规则不存在: {rule_name}")
                continue

            # 调用对应的检查器
            if rule_name not in self.checkers:
                result["warnings"].append(f"检查器不存在: {rule_name}")
                continue

            checker = self.checkers[rule_name]

            try:
                # 解析文件路径（支持相对路径和绝对路径）
                file_path_abs = Path(file_path)
                if not file_path_abs.is_absolute():
                    # 如果是相对路径，相对于项目根目录
                    file_path_abs = self.project_root / file_path
                file_path_str = str(file_path_abs.resolve())
                
                # 执行检查（使用解析后的绝对路径）
                passed, errors, warnings = checker.check(file_path_str)

                if not passed:
                    result["status"] = "failed"
                    result["errors"].extend(errors)

                if warnings:
                    result["warnings"].extend(warnings)

            except Exception as e:
                result["status"] = "failed"
                result["errors"].append(f"检查器执行失败: {str(e)}")

        return result

    def _write_audit_log(self, results: Dict[str, Any]):
        """写入审计日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "summary": results["summary"],
            "failed_files": [f["file"] for f in results["failed"]],
            "errors": [err for f in results["failed"] for err in f["errors"]],
        }

        # 尝试多个可能的日志路径（支持只读文件系统）
        audit_log_path = self.config["engine"].get(
            "audit_log_path", ".compliance/audit.log"
        )
        possible_paths = [
            Path(self.project_root) / audit_log_path,
            Path(self.project_root) / "logs" / "compliance_audit.log",
            Path("/tmp") / "compliance_audit.log",  # 容器内临时目录
        ]

        log_written = False
        for path in possible_paths:
            try:
                # 确保目录存在
                path.parent.mkdir(parents=True, exist_ok=True)
                # 尝试写入
                with open(path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                log_written = True
                break
            except (OSError, PermissionError):
                # 如果写入失败，尝试下一个路径
                continue

        if not log_written:
            # 如果所有路径都失败，只输出警告，不阻止检查
            print("⚠️ 无法写入审计日志（所有路径都失败），但继续执行检查", file=sys.stderr)

    def print_results(self, results: Dict[str, Any]):
        """打印检查结果"""
        print("\n" + "=" * 60, file=sys.stderr)
        print("合规检查结果", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        summary = results["summary"]
        print(f"总计: {summary['total']} 个文件", file=sys.stderr)
        print(f"✅ 通过: {summary['passed']}", file=sys.stderr)
        print(f"❌ 失败: {summary['failed']}", file=sys.stderr)
        print(f"⚠️ 警告: {summary['warnings']}", file=sys.stderr)

        if results["failed"]:
            print("\n失败文件:", file=sys.stderr)
            for failed in results["failed"]:
                print(f"\n  ❌ {failed['file']}", file=sys.stderr)
                for error in failed["errors"]:
                    print(f"      • {error}", file=sys.stderr)

        if results["warnings"]:
            print("\n警告:", file=sys.stderr)
            for warning_file in results["warnings"]:
                print(f"\n  ⚠️ {warning_file['file']}", file=sys.stderr)
                for warning in warning_file["warnings"]:
                    print(f"      • {warning}", file=sys.stderr)

        print("\n" + "=" * 60, file=sys.stderr)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python .compliance/engine.py <file1> <file2> ...", file=sys.stderr)
        sys.exit(1)

    file_paths = sys.argv[1:]

    try:
        engine = ComplianceEngine()
        results = engine.check_files(file_paths)
        engine.print_results(results)

        # 严格模式：有失败则退出码为1
        if engine.config["engine"]["strict_mode"] and results["summary"]["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    except Exception as e:
        print(f"❌ 合规引擎执行失败: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
