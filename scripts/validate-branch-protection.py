#!/usr/bin/env python3
"""
验证分支保护规则与工作流Job名称一致性
确保分支保护规则中要求的所有job名称都在工作流中存在
"""

import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


def extract_job_names_from_workflow(workflow_file: Path) -> Set[str]:
    """从工作流文件中提取所有job名称"""
    with open(workflow_file, encoding="utf-8") as f:
        workflow = yaml.safe_load(f)

    jobs = workflow.get("jobs", {})
    job_names = set()

    for job_id, job_config in jobs.items():
        # 优先使用job的name字段，如果没有则使用job_id
        job_display_name = job_config.get("name", job_id)

        # 添加job ID（用于向后兼容）
        job_names.add(job_id)
        # 添加job的显示名称（GitHub实际使用的名称）
        job_names.add(job_display_name)

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
                        # 生成格式: job_name (value) 和 job_id (value)
                        combined_name_id = f"{job_id} ({value})"
                        combined_name_display = f"{job_display_name} ({value})"
                        job_names.add(combined_name_id)
                        job_names.add(combined_name_display)

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


def get_github_repo_info() -> Optional[tuple[str, str]]:
    """获取GitHub仓库的owner和repo名称"""
    try:
        # 尝试从git remote获取
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()

        # 解析URL格式: git@github.com:owner/repo.git 或 https://github.com/owner/repo.git
        if "github.com" in remote_url:
            if remote_url.startswith("git@"):
                # git@github.com:owner/repo.git
                parts = remote_url.split(":")[-1].replace(".git", "").split("/")
            else:
                # https://github.com/owner/repo.git
                parts = (
                    remote_url.split("github.com/")[-1].replace(".git", "").split("/")
                )

            if len(parts) >= 2:
                return (parts[0], parts[1])
    except (subprocess.SubprocessError, IndexError):
        pass

    # 尝试从环境变量获取
    repo_env = os.getenv("GITHUB_REPOSITORY")
    if repo_env:
        parts = repo_env.split("/")
        if len(parts) == 2:
            return (parts[0], parts[1])

    return None


def get_required_checks_from_github_api(branch: str = "dev") -> Optional[List[str]]:
    """通过GitHub API查询分支保护规则中的必需检查"""
    repo_info = get_github_repo_info()
    if not repo_info:
        return None

    owner, repo = repo_info

    # 方法1: 使用GitHub CLI (gh)
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                f"repos/{owner}/{repo}/branches/{branch}/protection",
                "--jq",
                ".required_status_checks.contexts",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        if result.returncode == 0 and result.stdout.strip():
            contexts = json.loads(result.stdout.strip())
            if isinstance(contexts, list) and contexts:
                print(f"📡 从GitHub API获取到 {branch} 分支的 {len(contexts)} 个必需检查")
                return contexts
    except (subprocess.SubprocessError, json.JSONDecodeError, FileNotFoundError):
        pass

    # 方法2: 使用GitHub API (curl + token)
    github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if github_token:
        try:
            import urllib.error
            import urllib.request

            url = (
                f"https://api.github.com/repos/{owner}/{repo}/branches/"
                f"{branch}/protection"
            )
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"token {github_token}",
            }

            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                contexts = data.get("required_status_checks", {}).get("contexts", [])
                if contexts:
                    print(f"📡 从GitHub API获取到 {branch} 分支的 {len(contexts)} 个必需检查")
                    return contexts
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            json.JSONDecodeError,
            KeyError,
        ):
            pass

    return None


def get_required_checks_from_config_file() -> Optional[List[str]]:
    """从配置文件读取必需检查"""
    config_file = Path(".github/branch-protection-checks.yaml")
    if config_file.exists():
        try:
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                checks = config.get("required_checks", [])
                if checks:
                    print(f"📄 从配置文件读取到 {len(checks)} 个必需检查")
                    return checks
        except (yaml.YAMLError, KeyError):
            pass

    return None


def get_required_checks_fallback() -> List[str]:
    """回退方案：硬编码的必需检查（仅在没有其他方法时使用）"""
    print("⚠️  无法从GitHub API或配置文件获取，使用硬编码的必需检查")
    print("💡 建议：配置GITHUB_TOKEN环境变量或创建.github/branch-protection-checks.yaml")
    return [
        "Push Validation Pipeline / run-tests (backend-unit-tests)",
        "Push Validation Pipeline / run-tests (frontend-unit-tests)",
        "Test Suite Component / unit-tests (backend)",
        "Test Suite Component / unit-tests (frontend)",
        "Test Suite Component / integration-tests",
        "Test Suite Component / e2e-tests",
        "Pre-Release Quality Check / basic-checks (lint-backend)",
        "Pre-Release Quality Check / basic-checks (lint-frontend)",
    ]


def get_required_checks(branches: List[str] = None) -> List[str]:
    """
    获取必需的状态检查，按优先级：
    1. GitHub API查询（dev和main分支）
    2. 配置文件
    3. 硬编码回退
    """
    if branches is None:
        branches = ["dev", "main"]

    all_checks = set()

    # 优先从GitHub API获取
    for branch in branches:
        api_checks = get_required_checks_from_github_api(branch)
        if api_checks:
            all_checks.update(api_checks)

    if all_checks:
        return sorted(list(all_checks))

    # 回退到配置文件
    config_checks = get_required_checks_from_config_file()
    if config_checks:
        return config_checks

    # 最后回退到硬编码
    return get_required_checks_fallback()


def validate_branch_protection():
    """验证分支保护规则与工作流Job名称一致性"""
    print("🔍 验证分支保护规则与工作流Job名称一致性...")
    print("")

    # 1. 解析所有工作流文件
    all_workflows = parse_all_workflow_jobs()

    if not all_workflows:
        print("⚠️  未找到工作流文件")
        return True

    # 2. 获取必需的检查（从GitHub API、配置文件或回退方案）
    required_checks = get_required_checks()

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
