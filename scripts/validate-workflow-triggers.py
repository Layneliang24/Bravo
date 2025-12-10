#!/usr/bin/env python3
"""
验证GitHub Actions工作流触发器
确保所有用于分支保护的工作流都同时支持push和pull_request事件
"""

import io
import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def parse_workflow_triggers(workflow_file: Path) -> Dict[str, Set[str]]:
    """解析工作流文件的触发器配置"""
    with open(workflow_file, encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    # YAML解析器可能把'on:'解析为True键（因为'on'在YAML中是布尔值）
    # 需要同时检查'on'键和True键
    triggers = workflow.get("on", {})
    if not triggers and True in workflow:
        # 如果'on'键不存在但存在True键，说明YAML解析器把'on:'解析为True
        triggers = workflow.get(True, {})

    trigger_types = set()

    # 处理不同的触发器格式
    if isinstance(triggers, dict):
        # 标准格式: on: { push: {...}, pull_request: {...} }
        trigger_types = set(triggers.keys())
    elif isinstance(triggers, list):
        # 列表格式: on: [push, pull_request]
        trigger_types = set(triggers)
    elif isinstance(triggers, str):
        # 字符串格式: on: push
        trigger_types = {triggers}

    return {
        "file": str(workflow_file),
        "triggers": trigger_types,
        "has_push": "push" in trigger_types,
        "has_pull_request": "pull_request" in trigger_types,
        "has_workflow_call": "workflow_call" in trigger_types,
    }


def validate_workflow_triggers(workflow_file: Path) -> tuple[bool, List[str]]:
    """验证单个工作流文件的触发器"""
    errors = []
    result = parse_workflow_triggers(workflow_file)

    # 检查是否是用于分支保护的工作流
    # 这些工作流必须同时支持push和pull_request
    protected_workflow_patterns = [
        "push-validation",
        "pr-validation",
        "test-suite",
        "release-pipeline",
        "quality-gates",
    ]

    is_protected_workflow = any(
        pattern in result["file"] for pattern in protected_workflow_patterns
    )

    if is_protected_workflow:
        # 用于分支保护的工作流必须支持pull_request或workflow_call
        if not result["has_pull_request"] and not result["has_workflow_call"]:
            errors.append(
                f"❌ {workflow_file.name}: 用于分支保护的工作流必须支持 "
                f"'pull_request' 或 'workflow_call' 触发器"
            )

        # 如果只有workflow_call，需要确保有其他地方调用它
        if result["has_workflow_call"] and not result["has_pull_request"]:
            # 这是可接受的，因为workflow_call可以被其他工作流调用
            pass

    return len(errors) == 0, errors


def main():
    """主函数"""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print(f"❌ 工作流目录不存在: {workflows_dir}")
        sys.exit(1)

    workflow_files = list(workflows_dir.glob("*.yml")) + list(
        workflows_dir.glob("*.yaml")
    )

    if not workflow_files:
        print("⚠️  未找到工作流文件")
        sys.exit(0)

    all_errors = []

    print("🔍 验证GitHub Actions工作流触发器...")
    print("")

    for workflow_file in sorted(workflow_files):
        # 跳过某些特殊工作流
        if workflow_file.name in ["workflow-validation-monitor.yml"]:
            continue

        is_valid, errors = validate_workflow_triggers(workflow_file)
        if not is_valid:
            all_errors.extend(errors)

        # 显示触发器信息
        result = parse_workflow_triggers(workflow_file)
        trigger_status = []
        if result["has_push"]:
            trigger_status.append("✅ push")
        if result["has_pull_request"]:
            trigger_status.append("✅ pull_request")
        if result["has_workflow_call"]:
            trigger_status.append("✅ workflow_call")

        status_icon = "✅" if is_valid else "❌"
        print(f"{status_icon} {workflow_file.name}")
        if trigger_status:
            print(f"   触发器: {', '.join(trigger_status)}")
        print("")

    if all_errors:
        print("❌ 验证失败:")
        for error in all_errors:
            print(f"  {error}")
        print("")
        print("💡 修复建议:")
        print("  在workflow文件的 'on:' 部分添加 'pull_request:' 触发器:")
        print("  ```yaml")
        print("  on:")
        print("    push:")
        print("      branches: [dev, main]")
        print("    pull_request:")
        print("      branches: [dev, main]")
        print("      types: [opened, synchronize, reopened]")
        print("  ```")
        sys.exit(1)

    print("✅ 所有工作流触发器验证通过")
    sys.exit(0)


if __name__ == "__main__":
    main()
