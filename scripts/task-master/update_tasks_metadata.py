#!/usr/bin/env python3
"""
更新tasks.json的metadata，记录source_prd_path或source_prd_paths
"""
import argparse
import json
import sys
from pathlib import Path


def update_tasks_metadata(tag: str, prd_path: str, append: bool = False) -> None:
    """
    更新tasks.json的metadata，记录PRD路径

    Args:
        tag: tag名称
        prd_path: PRD文件路径（容器内路径）
        append: 是否是append模式
    """
    tasks_json_path = Path(".taskmaster/tasks/tasks.json")

    if not tasks_json_path.exists():
        print(f"❌ tasks.json不存在: {tasks_json_path}", file=sys.stderr)
        sys.exit(1)

    # 读取tasks.json
    with open(tasks_json_path, "r", encoding="utf-8") as f:
        tasks_data = json.load(f)

    # 检查tag是否存在
    if tag not in tasks_data:
        print(f"❌ tag '{tag}' 不存在于tasks.json中", file=sys.stderr)
        sys.exit(1)

    # 获取tag的metadata
    if "metadata" not in tasks_data[tag]:
        tasks_data[tag]["metadata"] = {}

    metadata = tasks_data[tag]["metadata"]

    # 根据append模式更新metadata
    if append:
        # append模式：使用source_prd_paths数组
        if "source_prd_paths" not in metadata:
            metadata["source_prd_paths"] = []

        # 检查是否已存在
        if prd_path not in metadata["source_prd_paths"]:
            metadata["source_prd_paths"].append(prd_path)
            print(f"✅ 添加PRD路径到tag '{tag}' 的source_prd_paths: {prd_path}")
        else:
            print(f"ℹ️ PRD路径已存在于source_prd_paths: {prd_path}")
    else:
        # 覆盖模式：使用source_prd_path（单个）
        metadata["source_prd_path"] = prd_path
        print(f"✅ 设置tag '{tag}' 的source_prd_path: {prd_path}")

    # 写回tasks.json
    with open(tasks_json_path, "w", encoding="utf-8") as f:
        json.dump(tasks_data, f, ensure_ascii=False, indent=2)

    print("✅ tasks.json metadata已更新")


def main():
    parser = argparse.ArgumentParser(description="更新tasks.json的metadata，记录PRD路径")
    parser.add_argument("--tag", required=True, help="tag名称")
    parser.add_argument("--prd-path", required=True, help="PRD文件路径（容器内路径）")
    parser.add_argument("--append", default="false", help="是否是append模式（'true'或'false'）")

    args = parser.parse_args()

    # 转换append参数
    append = args.append.lower() == "true"

    try:
        update_tasks_metadata(tag=args.tag, prd_path=args.prd_path, append=append)
        sys.exit(0)
    except Exception as e:
        print(f"❌ 更新metadata失败: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
