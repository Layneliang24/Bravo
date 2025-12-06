#!/usr/bin/env python3
"""
任务状态同步脚本
同步任务状态到PRD元数据和追溯链
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict

import yaml


class TaskStatusSyncer:
    """任务状态同步器"""

    def __init__(self, req_id: str):
        self.req_id = req_id
        self.root_dir = Path.cwd()
        self.taskmaster_dir = self.root_dir / ".taskmaster" / "tasks" / req_id
        self.tasks_json_path = self.taskmaster_dir / "tasks.json"
        self.prd_path = (
            self.root_dir
            / "docs"
            / "00_product"
            / "requirements"
            / req_id
            / f"{req_id}.md"
        )

    def sync(self):
        """主入口：同步任务状态"""
        print(f"🔄 开始同步 {self.req_id} 的任务状态")

        # 1. 读取tasks.json
        if not self.tasks_json_path.exists():
            print(f"❌ tasks.json不存在: {self.tasks_json_path}")
            sys.exit(1)

        with open(self.tasks_json_path, "r", encoding="utf-8") as f:
            tasks_data = json.load(f)

        # 2. 计算任务完成度
        completion_stats = self._calculate_completion(tasks_data)

        # 3. 更新PRD元数据
        self._update_prd_metadata(tasks_data, completion_stats)

        # 4. 更新追溯链
        self._update_traceability(tasks_data)

        print("✅ 状态同步完成")
        completed = completion_stats["completed_tasks"]
        total = completion_stats["total_tasks"]
        print(f"📊 完成度: {completed}/{total} 任务")
        completed_sub = completion_stats["completed_subtasks"]
        total_sub = completion_stats["total_subtasks"]
        print(f"📊 子任务: {completed_sub}/{total_sub} 子任务")

    def _calculate_completion(self, tasks_data: Dict) -> Dict:
        """计算任务完成度"""
        tasks = tasks_data.get("tasks", [])

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "done")

        total_subtasks = 0
        completed_subtasks = 0

        for task in tasks:
            subtasks = task.get("subtasks", [])
            total_subtasks += len(subtasks)
            completed_subtasks += sum(
                1 for st in subtasks if st.get("status") == "done"
            )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "total_subtasks": total_subtasks,
            "completed_subtasks": completed_subtasks,
            "task_completion_rate": (completed_tasks / total_tasks * 100)
            if total_tasks > 0
            else 0,
            "subtask_completion_rate": (completed_subtasks / total_subtasks * 100)
            if total_subtasks > 0
            else 0,
        }

    def _update_prd_metadata(self, tasks_data: Dict, completion_stats: Dict):
        """更新PRD元数据"""
        if not self.prd_path.exists():
            print(f"⚠️ PRD文件不存在: {self.prd_path}，" "跳过PRD元数据更新")
            return

        try:
            content = self.prd_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️ 无法读取PRD文件: {e}")
            return

        # 解析Frontmatter
        if not content.startswith("---"):
            print("⚠️ PRD文件缺少Frontmatter，跳过更新")
            return

        parts = content.split("---", 2)
        if len(parts) < 3:
            print("⚠️ PRD文件Frontmatter格式错误，跳过更新")
            return

        frontmatter_text = parts[1]
        body_content = parts[2]

        try:
            metadata = yaml.safe_load(frontmatter_text)
        except Exception as e:
            print(f"⚠️ PRD Frontmatter YAML解析错误: {e}")
            return

        # 更新元数据
        metadata["updated_at"] = datetime.now().isoformat()
        metadata["task_completion"] = {
            "total_tasks": completion_stats["total_tasks"],
            "completed_tasks": completion_stats["completed_tasks"],
            "total_subtasks": completion_stats["total_subtasks"],
            "completed_subtasks": completion_stats["completed_subtasks"],
            "task_completion_rate": round(completion_stats["task_completion_rate"], 2),
            "subtask_completion_rate": round(
                completion_stats["subtask_completion_rate"], 2
            ),
        }

        # 更新任务状态
        tasks = tasks_data.get("tasks", [])
        task_statuses = []
        for task in tasks:
            task_statuses.append(
                {
                    "id": task["id"],
                    "title": task["title"],
                    "status": task.get("status", "pending"),
                    "directory": task.get("directory", ""),
                }
            )

        metadata["task_statuses"] = task_statuses

        # 重新组合文件
        new_frontmatter = yaml.dump(
            metadata, allow_unicode=True, default_flow_style=False
        )
        new_content = f"---\n{new_frontmatter}---{body_content}"

        # 写回文件
        self.prd_path.write_text(new_content, encoding="utf-8")
        rel_path = self.prd_path.relative_to(self.root_dir)
        print(f"  ✅ 更新PRD元数据: {rel_path}")

    def _update_traceability(self, tasks_data: Dict):
        """更新追溯链（简化实现）"""
        # 这里可以创建一个追溯矩阵文件
        traceability_file = self.taskmaster_dir / "traceability.json"

        tasks = tasks_data.get("tasks", [])
        traceability = {
            "req_id": self.req_id,
            "updated_at": datetime.now().isoformat(),
            "tasks": [],
        }

        for task in tasks:
            task_trace = {
                "task_id": f"task-{task['id']}",
                "title": task["title"],
                "status": task.get("status", "pending"),
                "test_files": [],
                "implementation_files": [],
            }

            # 收集所有测试文件和实现文件
            for subtask in task.get("subtasks", []):
                task_trace["test_files"].extend(subtask.get("test_files", []))
                task_trace["implementation_files"].extend(
                    subtask.get("implementation_files", [])
                )

            # 去重
            task_trace["test_files"] = list(set(task_trace["test_files"]))
            task_trace["implementation_files"] = list(
                set(task_trace["implementation_files"])
            )

            traceability["tasks"].append(task_trace)

        # 写入追溯链文件
        with open(traceability_file, "w", encoding="utf-8") as f:
            json.dump(traceability, f, indent=2, ensure_ascii=False)

        print(f"  ✅ 更新追溯链: {traceability_file.relative_to(self.root_dir)}")


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python scripts/task-master/sync_status.py <REQ-ID>")
        print("示例: python scripts/task-master/sync_status.py REQ-2025-001-user-login")
        sys.exit(1)

    req_id = sys.argv[1]

    try:
        syncer = TaskStatusSyncer(req_id)
        syncer.sync()
    except Exception as e:
        print(f"❌ 同步失败: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
