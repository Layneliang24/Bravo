#!/usr/bin/env python3
"""
Task-Master适配层
将Task-Master生成的tasks.json转换为三层目录结构
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class TaskMasterAdapter:
    """Task-Master适配器"""

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

    def convert(self):
        """主入口：转换Task-Master输出为三层结构"""
        print(f"🚀 开始转换 {self.req_id}")

        # 1. 检查tasks.json是否存在
        if not self.tasks_json_path.exists():
            print(f"❌ tasks.json不存在: {self.tasks_json_path}")
            sys.exit(1)

        # 2. 读取原始tasks.json
        with open(self.tasks_json_path, "r", encoding="utf-8") as f:
            original_tasks = json.load(f)

        # 3. 生成Task-0自检任务
        task_0 = self._generate_task_0()

        # 4. 为每个任务生成增强版本
        enhanced_tasks = [task_0]
        for task in original_tasks.get("tasks", []):
            enhanced_task = self._enhance_task(task)
            enhanced_tasks.append(enhanced_task)

        # 5. 更新tasks.json（增强版）
        enhanced_json = {
            "req_id": self.req_id,
            "project": "Bravo",
            "prd_path": str(self.prd_path.relative_to(self.root_dir)),
            "created_at": original_tasks.get("created_at", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            "tasks": enhanced_tasks,
        }

        with open(self.tasks_json_path, "w", encoding="utf-8") as f:
            json.dump(enhanced_json, f, indent=2, ensure_ascii=False)

        # 6. 创建目录和Markdown文件
        for task in enhanced_tasks:
            self._create_task_directory(task)
            self._create_task_md(task)
            for subtask in task.get("subtasks", []):
                self._create_subtask_md(task, subtask)

        print("✅ 转换完成！")
        print(f"📁 任务目录: {self.taskmaster_dir}")

    def _generate_task_0(self) -> Dict:
        """生成Task-0自检任务"""
        return {
            "id": 0,
            "title": "Self-check and validation",
            "description": (
                "Validate PRD metadata, check test directories, "
                "and verify API contract"
            ),
            "status": "pending",
            "priority": "high",
            "directory": "task-0-self-check",
            "dependencies": [],
            "subtasks": [
                {
                    "id": 1,
                    "title": "Validate PRD metadata",
                    "description": "Check PRD frontmatter and required fields",
                    "status": "pending",
                    "file": "subtask-1-validate-prd-metadata.md",
                    "test_files": [],
                    "implementation_files": [],
                },
                {
                    "id": 2,
                    "title": "Check test directories",
                    "description": "Ensure all required test directories exist",
                    "status": "pending",
                    "file": "subtask-2-check-test-directories.md",
                    "test_files": [],
                    "implementation_files": [],
                },
                {
                    "id": 3,
                    "title": "Verify API contract",
                    "description": "Check if API contract file exists and is valid",
                    "status": "pending",
                    "file": "subtask-3-verify-api-contract.md",
                    "test_files": [],
                    "implementation_files": [],
                },
            ],
        }

    def _enhance_task(self, task: Dict) -> Dict:
        """增强任务（添加文件关联和目录信息）"""
        subtasks = task.get("subtasks", [])
        enhanced_subtasks = []

        for subtask in subtasks:
            # 关联测试文件和代码文件
            enhanced_subtask = self._link_files_to_subtask(subtask, task)
            # 关联PRD章节
            enhanced_subtask = self._link_prd_section(enhanced_subtask, task)
            # 添加文件名字段
            if "file" not in enhanced_subtask:
                enhanced_subtask[
                    "file"
                ] = f"subtask-{subtask['id']}-{self._slugify(subtask['title'])}.md"
            enhanced_subtasks.append(enhanced_subtask)

        # 生成目录名
        task_slug = self._slugify(task["title"])
        directory = f"task-{task['id']}-{task_slug}"

        return {
            "id": task["id"],
            "title": task["title"],
            "description": task.get("description", ""),
            "status": task.get("status", "pending"),
            "priority": task.get("priority", "medium"),
            "directory": directory,
            "dependencies": task.get("dependencies", []),
            "subtasks": enhanced_subtasks,
        }

    def _link_files_to_subtask(self, subtask: Dict, parent_task: Dict) -> Dict:
        """为子任务关联测试文件和代码文件"""
        title_lower = subtask["title"].lower()
        app_name = self._guess_app_name(subtask, parent_task)

        # 初始化文件列表
        if "test_files" not in subtask:
            subtask["test_files"] = []
        if "implementation_files" not in subtask:
            subtask["implementation_files"] = []

        # 根据子任务标题关联文件
        if "model" in title_lower or "database" in title_lower or "数据库" in title_lower:
            subtask["implementation_files"].append(f"backend/apps/{app_name}/models.py")
            subtask["test_files"].append(
                f"backend/tests/unit/test_{app_name}_models.py"
            )

        elif "view" in title_lower or "endpoint" in title_lower or "api" in title_lower:
            subtask["implementation_files"].append(f"backend/apps/{app_name}/views.py")
            subtask["test_files"].append(f"backend/tests/unit/test_{app_name}_views.py")
            subtask["test_files"].append(
                f"backend/tests/integration/test_{app_name}_api.py"
            )

        elif "serializer" in title_lower:
            subtask["implementation_files"].append(
                f"backend/apps/{app_name}/serializers.py"
            )
            subtask["test_files"].append(
                f"backend/tests/unit/test_{app_name}_serializers.py"
            )

        elif "component" in title_lower or "vue" in title_lower or "ui" in title_lower:
            feature = self._extract_feature_name(subtask["title"])
            subtask["implementation_files"].append(
                f"frontend/src/components/{feature}.vue"
            )
            subtask["test_files"].append(f"e2e/tests/test-{feature}.spec.ts")

        elif "e2e" in title_lower or (
            "test" in title_lower and "unit" not in title_lower
        ):
            feature = self._extract_feature_name(subtask["title"])
            subtask["test_files"].append(f"e2e/tests/test-{feature}.spec.ts")

        elif "unit" in title_lower and "test" in title_lower:
            app_name = self._guess_app_name(subtask, parent_task)
            subtask["test_files"].append(f"backend/tests/unit/test_{app_name}.py")

        elif "integration" in title_lower and "test" in title_lower:
            app_name = self._guess_app_name(subtask, parent_task)
            subtask["test_files"].append(
                f"backend/tests/integration/test_{app_name}.py"
            )

        return subtask

    def _link_prd_section(self, subtask: Dict, parent_task: Dict) -> Dict:
        """关联PRD章节"""
        # 简化实现：基于任务标题生成章节链接
        if "prd_section" not in subtask:
            subtask["prd_section"] = f"#{self._slugify(parent_task['title'])}"
        return subtask

    def _guess_app_name(self, subtask: Dict, parent_task: Dict) -> str:
        """推断Django App名称"""
        text = f"{subtask['title']} {parent_task['title']}".lower()

        if any(kw in text for kw in ["user", "auth", "login", "register"]):
            return "users"
        elif "product" in text:
            return "products"
        elif "order" in text or "cart" in text:
            return "orders"
        elif "blog" in text or "post" in text:
            return "blog"
        else:
            return "core"

    def _extract_feature_name(self, title: str) -> str:
        """从标题提取功能名"""
        # 移除常见关键词
        title = re.sub(
            r"\b(create|implement|write|add|build|develop)\b",
            "",
            title,
            flags=re.IGNORECASE,
        )
        # 取第一个有意义的单词
        words = title.split()
        if words:
            return self._slugify(words[0])
        return "feature"

    def _slugify(self, text: str) -> str:
        """将文本转换为URL友好的slug"""
        # 转换为小写
        text = text.lower()
        # 替换空格和特殊字符为短横线
        text = re.sub(r"[^\w\s-]", "", text)
        text = re.sub(r"[-\s]+", "-", text)
        # 移除首尾短横线
        return text.strip("-")

    def _create_task_directory(self, task: Dict):
        """创建任务目录"""
        task_dir = self.taskmaster_dir / task["directory"]
        task_dir.mkdir(parents=True, exist_ok=True)

    def _create_task_md(self, task: Dict):
        """创建任务主文件task.md"""
        task_dir = self.taskmaster_dir / task["directory"]
        task_md_path = task_dir / "task.md"

        # 生成Markdown内容
        lines = [
            f"# {task['title']}",
            "",
            f"**Task ID**: task-{task['id']}",
            f"**Status**: {task['status']}",
            f"**Priority**: {task.get('priority', 'medium')}",
            "",
        ]

        if task.get("dependencies"):
            deps = ", ".join([f"task-{dep}" for dep in task["dependencies"]])
            lines.append(f"**Dependencies**: {deps}")
            lines.append("")

        lines.extend(
            ["## Description", "", task.get("description", ""), "", "## Subtasks", ""]
        )

        # 添加子任务列表
        for subtask in task.get("subtasks", []):
            status_icon = self._get_status_icon(subtask.get("status", "pending"))
            file_name = subtask.get("file", f"subtask-{subtask['id']}.md")
            lines.append(
                f"- [{status_icon}] {subtask['title']} ([{file_name}](./{file_name}))"
            )

        lines.extend(["", "## Test Files", ""])

        # 收集所有测试文件
        test_files = set()
        for subtask in task.get("subtasks", []):
            test_files.update(subtask.get("test_files", []))

        if test_files:
            for test_file in sorted(test_files):
                lines.append(f"- `{test_file}`")
        else:
            lines.append("*暂无测试文件*")

        lines.extend(["", "## Implementation Files", ""])

        # 收集所有实现文件
        impl_files = set()
        for subtask in task.get("subtasks", []):
            impl_files.update(subtask.get("implementation_files", []))

        if impl_files:
            for impl_file in sorted(impl_files):
                lines.append(f"- `{impl_file}`")
        else:
            lines.append("*暂无实现文件*")

        lines.append("")

        # 写入文件
        task_md_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  ✅ 创建: {task_md_path.relative_to(self.root_dir)}")

    def _create_subtask_md(self, task: Dict, subtask: Dict):
        """创建子任务Markdown文件"""
        task_dir = self.taskmaster_dir / task["directory"]
        file_name = subtask.get("file", f"subtask-{subtask['id']}.md")
        subtask_md_path = task_dir / file_name

        # 生成Markdown内容
        lines = [
            f"# {subtask['title']}",
            "",
            f"**Subtask ID**: subtask-{subtask['id']}",
            f"**Parent Task**: [{task['title']}](./task.md)",
            f"**Status**: {subtask.get('status', 'pending')}",
            "",
        ]

        if subtask.get("prd_section"):
            lines.append(f"**PRD Section**: {subtask['prd_section']}")
            lines.append("")

        lines.extend(
            [
                "## Description",
                "",
                subtask.get("description", ""),
                "",
                "## Checklist",
                "",
                "- [ ] 理解任务需求",
                "- [ ] 编写测试用例（TDD红色阶段）",
                "- [ ] 实现功能代码（TDD绿色阶段）",
                "- [ ] 运行测试并确保通过",
                "- [ ] 代码重构和优化",
                "- [ ] 更新任务状态",
                "",
            ]
        )

        # 添加测试文件
        if subtask.get("test_files"):
            lines.extend(["## Test Files", ""])
            for test_file in subtask["test_files"]:
                lines.append(f"- `{test_file}`")
            lines.append("")

        # 添加实现文件
        if subtask.get("implementation_files"):
            lines.extend(["## Implementation Files", ""])
            for impl_file in subtask["implementation_files"]:
                lines.append(f"- `{impl_file}`")
            lines.append("")

        # 写入文件
        subtask_md_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"  ✅ 创建: {subtask_md_path.relative_to(self.root_dir)}")

    def _get_status_icon(self, status: str) -> str:
        """获取状态图标"""
        icons = {
            "done": "✅",
            "in-progress": "⏳",
            "pending": "⬜",
            "blocked": "🚫",
            "cancelled": "❌",
        }
        return icons.get(status, "⬜")


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python scripts/task-master/adapter.py <REQ-ID>")
        print("示例: python scripts/task-master/adapter.py REQ-2025-001-user-login")
        sys.exit(1)

    req_id = sys.argv[1]

    try:
        adapter = TaskMasterAdapter(req_id)
        adapter.convert()
    except Exception as e:
        print(f"❌ 转换失败: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
