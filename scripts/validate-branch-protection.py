#!/usr/bin/env python3
"""
验证分支保护规则与工作流Job名称一致性
确保分支保护规则中要求的所有job名称都在工作流中存在
"""

import sys
from pathlib import Path
from typing import Dict, List, Set

import yaml


def extract_job_names_from_workflow(workflow_file: Path) -> Set[str]:
    """从工作流文件中提取所有job名称"""
    with open(workflow_file, encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    jobs = workflow.get("jobs", {})
    job_names = set()

    for job_name, job_config in jobs.items():
        # 基础job名称
        job_names.add(job_name)

        # 如果使用matrix策略，生成所有组合
        strategy = job_config.get("strategy", {})
        matrix = strategy.get("matrix", {})
        if matrix:
            # 提取matrix的键和值
            matrix_keys = list(matrix.keys())
            matrix_values = {}

            for key in matrix_keys:
                values = matrix[key]
                if isinstance(values, list):
                    matrix_values[key] = values
                elif isinstance(values, dict):
                    # 处理include/exclude等复杂情况
                    if "include" in values:
                        # 简化处理：只提取include中的值
                        matrix_values[key] = [
                            item.get(key) for item in values["include"] if key in item
                        ]

            # 生成所有组合
            if matrix_values:
                # 简化：只生成第一个键的所有值组合
                first_key = matrix_keys[0]
                if first_key in matrix_values:
                    for value in matrix_values[first_key]:
                        # 生成格式: job_name (value)
                        combined_name = f"{job_name} ({value})"
                        job_names.add(combined_name)

    return job_names


def get_workflow_name(workflow_file: Path) -> str:
    """获取工作流的显示名称"""
    with open(workflow_file, encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    return workflow.get("name", workflow_file.stem)


def parse_all_workflow_jobs() -> Dict[str, Dict]:
    """解析所有工作流文件，提取job信息"""
    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        return {}

    workflow_files = list(workflows_dir.glob("*.yml")) + list(
        workflows_dir.glob("*.yaml")
    )

    all_jobs = {}

    for workflow_file in workflow_files:
        # 跳过某些特殊工作流
        if workflow_file.name in ["workflow-validation-monitor.yml"]:
            continue

        workflow_name = get_workflow_name(workflow_file)
        job_names = extract_job_names_from_workflow(workflow_file)

        all_jobs[workflow_name] = {
            "file": str(workflow_file),
            "jobs": job_names,
        }

    return all_jobs


def get_required_checks_from_config() -> List[str]:
    """
    从配置文件或文档中获取必需的状态检查
    这里我们硬编码已知的必需检查，实际应该从GitHub API或配置文件读取
    """
    # 这些是从复盘报告中提取的必需检查
    required_checks = [
        "Push Validation Pipeline / run-tests (backend-unit-tests)",
        "Push Validation Pipeline / run-tests (frontend-unit-tests)",
        "Test Suite Component / unit-tests (backend)",
        "Test Suite Component / unit-tests (frontend)",
        "Test Suite Component / integration-tests",
        "Test Suite Component / e2e-tests",
        "Pre-Release Quality Check / basic-checks (lint-backend)",
        "Pre-Release Quality Check / basic-checks (lint-frontend)",
    ]

    return required_checks


def validate_branch_protection():
    """验证分支保护规则与工作流Job名称一致性"""
    print("🔍 验证分支保护规则与工作流Job名称一致性...")
    print("")

    # 1. 解析所有工作流文件
    all_workflows = parse_all_workflow_jobs()

    if not all_workflows:
        print("⚠️  未找到工作流文件")
        return True

    # 2. 获取必需的检查
    required_checks = get_required_checks_from_config()

    # 3. 构建所有可用的job名称（包含工作流名称前缀）
    all_available_jobs = set()
    for workflow_name, workflow_info in all_workflows.items():
        for job_name in workflow_info["jobs"]:
            # 格式: Workflow Name / job_name
            full_job_name = f"{workflow_name} / {job_name}"
            all_available_jobs.add(full_job_name)
            # 也添加不带前缀的版本
            all_available_jobs.add(job_name)

    # 4. 验证每个必需的检查
    missing_checks = []
    found_checks = []

    for required_check in required_checks:
        # 尝试精确匹配
        if required_check in all_available_jobs:
            found_checks.append(required_check)
            continue

        # 尝试部分匹配（检查job名称是否包含在required_check中）
        check_parts = required_check.split(" / ")
        if len(check_parts) >= 2:
            job_part = check_parts[-1]  # 最后一部分是job名称
            if any(job_part in job for job in all_available_jobs):
                found_checks.append(required_check)
                continue

        missing_checks.append(required_check)

    # 5. 显示结果
    if found_checks:
        print("✅ 找到的必需检查:")
        for check in found_checks:
            print(f"  ✅ {check}")

    if missing_checks:
        print("")
        print("❌ 缺失的必需检查:")
        for check in missing_checks:
            print(f"  ❌ {check}")

        print("")
        print("💡 修复建议:")
        print("  1. 检查工作流文件中的job名称是否正确")
        print("  2. 确保工作流名称与分支保护规则中的名称匹配")
        print("  3. 如果使用matrix策略，确保生成的job名称格式正确")
        print("")
        print("📋 当前工作流中的job:")
        for workflow_name, workflow_info in all_workflows.items():
            print(f"  {workflow_name}:")
            for job_name in sorted(workflow_info["jobs"]):
                print(f"    - {job_name}")

        return False

    print("")
    print("✅ 所有必需检查都在工作流中找到")
    return True


def main():
    """主函数"""
    is_valid = validate_branch_protection()
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
