#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用例追溯性检查脚本

检查PRD、测试用例CSV和实际测试代码的对应关系：
1. PRD中声明的test_files是否实际存在
2. 测试用例CSV中的用例是否在测试代码中实现
3. 测试代码中的用例ID是否在CSV中声明
"""

import csv
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent


def extract_prd_metadata(prd_path: Path) -> Dict:
    """提取PRD的元数据"""
    content = prd_path.read_text(encoding="utf-8")

    # 提取YAML frontmatter
    if not content.startswith("---"):
        return {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    import yaml

    try:
        metadata = yaml.safe_load(parts[1])
        return metadata
    except Exception:
        return {}


def read_testcase_csv(csv_path: Path) -> List[Dict]:
    """读取测试用例CSV文件"""
    if not csv_path.exists():
        return []

    testcases = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            testcases.append(row)

    return testcases


def extract_testcase_ids_from_code(file_path: Path) -> Set[str]:
    """从测试代码文件中提取用例ID"""
    if not file_path.exists():
        return set()

    content = file_path.read_text(encoding="utf-8")
    testcase_ids = set()

    # 匹配 TESTCASE-IDS: TC-XXX-001, TC-XXX-002 格式
    pattern1 = r"TESTCASE-IDS:\s*([A-Z0-9_-]+(?:\s*,\s*[A-Z0-9_-]+)*)"
    matches1 = re.findall(pattern1, content)
    for match in matches1:
        ids = [id.strip() for id in match.split(",")]
        testcase_ids.update(ids)

    # 匹配 test('TC-XXX-001: ...') 格式
    pattern2 = r"test\(['\"]TC-([A-Z0-9_-]+):"
    matches2 = re.findall(pattern2, content)
    for match in matches2:
        testcase_ids.add(f"TC-{match}")

    # 匹配 test('TC-XXX-001', ...) 格式
    pattern3 = r"test\(['\"]TC-([A-Z0-9_-]+)['\"]"
    matches3 = re.findall(pattern3, content)
    for match in matches3:
        testcase_ids.add(f"TC-{match}")

    return testcase_ids


def check_prd_test_files(prd_path: Path, metadata: Dict) -> Tuple[List[str], List[str]]:
    """检查PRD中声明的test_files是否存在"""
    missing_files = []
    existing_files = []

    test_files = metadata.get("test_files", [])
    for test_file in test_files:
        file_path = PROJECT_ROOT / test_file
        if file_path.exists():
            existing_files.append(test_file)
        else:
            missing_files.append(test_file)

    return existing_files, missing_files


def check_testcase_coverage(prd_path: Path, csv_path: Path, metadata: Dict) -> Dict:
    """检查测试用例覆盖情况"""
    # 读取CSV中的用例ID
    testcases = read_testcase_csv(csv_path)
    csv_case_ids = {tc["用例ID"] for tc in testcases if "用例ID" in tc}

    # 从测试代码中提取用例ID
    code_case_ids = set()
    test_files = metadata.get("test_files", [])
    for test_file in test_files:
        file_path = PROJECT_ROOT / test_file
        if file_path.exists():
            ids = extract_testcase_ids_from_code(file_path)
            code_case_ids.update(ids)

    # 对比
    missing_in_code = csv_case_ids - code_case_ids
    extra_in_code = code_case_ids - csv_case_ids

    return {
        "csv_total": len(csv_case_ids),
        "code_total": len(code_case_ids),
        "matched": len(csv_case_ids & code_case_ids),
        "missing_in_code": sorted(missing_in_code),
        "extra_in_code": sorted(extra_in_code),
        "csv_case_ids": sorted(csv_case_ids),
        "code_case_ids": sorted(code_case_ids),
    }


def main():
    """主函数"""
    prd_dir = PROJECT_ROOT / "docs/00_product/requirements"

    if not prd_dir.exists():
        print(f"❌ PRD目录不存在: {prd_dir}")
        return

    print("=" * 80)
    print("测试用例追溯性检查报告")
    print("=" * 80)
    print()

    all_issues = []

    # 遍历所有PRD文件
    for prd_path in prd_dir.glob("**/*.md"):
        if prd_path.name.startswith("."):
            continue

        # 跳过非PRD文件
        if not prd_path.name.startswith("REQ-"):
            continue

        print(f"\n📄 检查PRD: {prd_path.relative_to(PROJECT_ROOT)}")
        print("-" * 80)

        # 提取元数据
        metadata = extract_prd_metadata(prd_path)
        if not metadata:
            print("  ⚠️  无法解析PRD元数据")
            continue

        req_id = metadata.get("req_id", "UNKNOWN")
        print(f"  REQ-ID: {req_id}")

        # 1. 检查test_files是否存在
        existing_files, missing_files = check_prd_test_files(prd_path, metadata)

        if missing_files:
            print(f"\n  ❌ 缺失的测试文件 ({len(missing_files)}个):")
            for f in missing_files:
                print(f"     - {f}")
                all_issues.append(
                    {"type": "missing_test_file", "req_id": req_id, "file": f}
                )
        else:
            print(f"\n  ✅ 所有测试文件都存在 ({len(existing_files)}个)")

        # 2. 检查测试用例CSV
        testcase_file = metadata.get("testcase_file", "")
        if not testcase_file:
            print("\n  ⚠️  PRD中未声明testcase_file")
            all_issues.append(
                {"type": "missing_testcase_file_metadata", "req_id": req_id}
            )
            continue

        csv_path = PROJECT_ROOT / testcase_file
        if not csv_path.exists():
            print(f"\n  ❌ 测试用例CSV文件不存在: {testcase_file}")
            all_issues.append(
                {
                    "type": "missing_testcase_csv",
                    "req_id": req_id,
                    "file": testcase_file,
                }
            )
            continue

        print(f"\n  ✅ 测试用例CSV存在: {csv_path.relative_to(PROJECT_ROOT)}")

        # 3. 检查测试用例覆盖
        coverage = check_testcase_coverage(prd_path, csv_path, metadata)

        print("\n  📊 测试用例覆盖情况:")
        print(f"     CSV中用例总数: {coverage['csv_total']}")
        print(f"     代码中用例总数: {coverage['code_total']}")
        print(f"     已匹配用例数: {coverage['matched']}")

        if coverage["missing_in_code"]:
            print(f"\n  ❌ CSV中有但代码中缺失的用例 ({len(coverage['missing_in_code'])}个):")
            for case_id in coverage["missing_in_code"][:10]:  # 只显示前10个
                print(f"     - {case_id}")
            if len(coverage["missing_in_code"]) > 10:
                print(f"     ... 还有 {len(coverage['missing_in_code']) - 10} 个")
            all_issues.append(
                {
                    "type": "missing_testcase_in_code",
                    "req_id": req_id,
                    "cases": coverage["missing_in_code"],
                }
            )

        if coverage["extra_in_code"]:
            print(f"\n  ⚠️  代码中有但CSV中未声明的用例 ({len(coverage['extra_in_code'])}个):")
            for case_id in coverage["extra_in_code"][:5]:  # 只显示前5个
                print(f"     - {case_id}")
            if len(coverage["extra_in_code"]) > 5:
                print(f"     ... 还有 {len(coverage['extra_in_code']) - 5} 个")

    # 总结
    print("\n" + "=" * 80)
    print("检查总结")
    print("=" * 80)

    if not all_issues:
        print("\n✅ 所有检查通过！PRD、测试用例CSV和测试代码完全对应。")
        return 0
    else:
        print(f"\n❌ 发现 {len(all_issues)} 类问题需要修复：")

        issue_types = {}
        for issue in all_issues:
            issue_type = issue["type"]
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)

        for issue_type, issues in issue_types.items():
            print(f"\n  {issue_type}: {len(issues)} 个")

        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
