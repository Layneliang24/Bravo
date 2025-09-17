#!/usr/bin/env python3
"""简单的workflow测试脚本"""

from pathlib import Path

import yaml


def test_workflow_file(file_path):
    """测试单个workflow文件"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        print(f"✅ {file_path.name}: {workflow.get('name', 'Unknown')}")
        print(f"   Jobs: {len(workflow.get('jobs', {}))}")
        return True
    except Exception as e:
        print(f"❌ {file_path.name}: {e}")
        return False


def main():
    workflows_dir = Path(".github/workflows")

    if not workflows_dir.exists():
        print("❌ .github/workflows目录不存在")
        return

    print("🔍 测试新创建的workflow文件:")

    # 新创建的文件列表
    new_workflows = [
        "setup-cache.yml",
        "test-unit-backend.yml",
        "test-unit-frontend.yml",
        "test-integration.yml",
        "test-e2e-smoke.yml",
        "test-e2e-full.yml",
        "test-regression.yml",
        "quality-security.yml",
        "quality-performance.yml",
        "quality-coverage.yml",
        "on-pr.yml",
        "on-push-dev.yml",
    ]

    passed = 0
    failed = 0

    for workflow_name in new_workflows:
        workflow_path = workflows_dir / workflow_name
        if workflow_path.exists():
            if test_workflow_file(workflow_path):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  {workflow_name}: 文件不存在")
            failed += 1

    print(f"\n📊 结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("🎉 所有workflow文件验证通过！")
    else:
        print("⚠️  部分文件有问题，需要检查")


if __name__ == "__main__":
    main()
