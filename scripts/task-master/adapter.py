#!/usr/bin/env python3
"""
Task-Master适配层
将Task-Master生成的tasks.json转换为三层目录结构
适配标签化结构，自动生成Task-0
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict


class TaskMasterAdapter:
    """Task-Master适配器（适配标签化结构）"""

    def __init__(self, req_id: str):
        self.req_id = req_id
        self.root_dir = Path.cwd()
        # ⭐ 适配标签化结构：tasks.json在根目录，不是每个REQ-ID一个
        self.tasks_json_path = self.root_dir / ".taskmaster" / "tasks" / "tasks.json"
        self.prd_path = (
            self.root_dir
            / "docs"
            / "00_product"
            / "requirements"
            / req_id
            / f"{req_id}.md"
        )

    def convert(self):
        """主入口：生成Task-0并插入到tasks.json"""
        # 修复Windows编码问题
        if sys.platform == "win32":
            import io

            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )

        print(f"[Adapter] 开始为 {self.req_id} 生成Task-0")  # noqa: F541

        # 1. 检查tasks.json是否存在
        if not self.tasks_json_path.exists():
            print(f"[Adapter] 错误: tasks.json不存在: {self.tasks_json_path}")
            sys.exit(1)

        # 2. 读取tasks.json（标签化结构）
        with open(self.tasks_json_path, "r", encoding="utf-8") as f:
            all_tasks_data = json.load(f)

        # 3. 检查REQ-ID是否存在于tasks.json中
        if self.req_id not in all_tasks_data:
            print(f"[Adapter] 错误: REQ-ID {self.req_id} 不在tasks.json中")
            sys.exit(1)

        req_tag_data = all_tasks_data[self.req_id]
        if not isinstance(req_tag_data, dict):
            print(f"[Adapter] 错误: REQ-ID {self.req_id} 的数据格式不正确")
            sys.exit(1)

        original_tasks = req_tag_data.get("tasks", [])

        # 4. 检查Task-0是否已存在
        has_task_0 = any(task.get("id") == 0 for task in original_tasks)
        if has_task_0:
            print("[Adapter] 警告: Task-0已存在，跳过生成")
            return

        # 5. 生成Task-0自检任务
        task_0 = self._generate_task_0()
        print(f"[Adapter] 已生成Task-0: {task_0['title']}")

        # 6. 将Task-0插入到tasks列表的第一位
        enhanced_tasks = [task_0] + original_tasks
        req_tag_data["tasks"] = enhanced_tasks

        # 7. 更新metadata
        if "metadata" not in req_tag_data:
            req_tag_data["metadata"] = {}
        req_tag_data["metadata"]["updated_at"] = datetime.now().isoformat()
        req_tag_data["metadata"]["taskCount"] = len(enhanced_tasks)

        # 8. 写回tasks.json
        with open(self.tasks_json_path, "w", encoding="utf-8") as f:
            json.dump(all_tasks_data, f, indent=2, ensure_ascii=False)

        print(f"[Adapter] Task-0已成功添加到 {self.req_id} 的tasks列表")
        print(f"[Adapter] 当前任务总数: {len(enhanced_tasks)}")

    def _generate_task_0(self) -> Dict:
        """
        生成Task-0自检任务

        ⭐ Task-0的检查任务是固定的，包含3个子任务：
        1. 验证PRD元数据完整性
        2. 检查测试目录存在
        3. 验证API契约文件

        这与task0_checker.py中的检查逻辑对应。
        """
        return {
            "id": 0,
            "title": "Task-0: 自检与验证",
            "description": "验证PRD元数据完整性、检查测试目录存在、验证API契约文件",
            "details": (
                "Task-0是强制性的自检任务，确保PRD完整性和项目准备就绪。\n"
                "包含3个子任务：\n"
                "1. 验证PRD元数据完整性"
                "（test_files、implementation_files、testcase_file等必需字段）\n"
                "2. 检查测试目录存在"
                "（backend/tests/unit/、backend/tests/integration/、e2e/tests/）\n"
                "3. 验证API契约文件（如果存在则验证OpenAPI格式）"
            ),
            "testStrategy": (
                "Task-0不需要代码测试，它是合规检查任务，通过合规引擎的task0_checker自动验证。\n"
                "当代码文件提交时，task0_checker会自动执行这3个检查。"
            ),
            "status": "pending",
            "priority": "high",
            "dependencies": [],
            "subtasks": [
                {
                    "id": 1,
                    "title": "验证PRD元数据完整性",
                    "description": (
                        "检查PRD frontmatter和必需字段"
                        "（test_files、implementation_files、"
                        "testcase_file、testcase_status）"
                    ),
                    "status": "pending",
                    "dependencies": [],
                },
                {
                    "id": 2,
                    "title": "检查测试目录存在",
                    "description": (
                        "确保所有必需的测试目录存在"
                        "（backend/tests/unit/、backend/tests/integration/、e2e/tests/）"
                    ),
                    "status": "pending",
                    "dependencies": [],
                },
                {
                    "id": 3,
                    "title": "验证API契约文件",
                    "description": (
                        "检查API契约文件是否存在且格式正确" "（OpenAPI 3.0格式，包含openapi和paths字段）"
                    ),
                    "status": "pending",
                    "dependencies": [],
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
        print("示例: python scripts/task-master/adapter.py REQ-2025-003-user-login")
        sys.exit(1)

    req_id = sys.argv[1]

    try:
        adapter = TaskMasterAdapter(req_id)
        adapter.convert()
    except Exception as e:
        print(f"[Adapter] 错误: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
