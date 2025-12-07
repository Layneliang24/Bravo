#!/usr/bin/env python3
"""
PRD状态验证器
在执行parse-prd前验证PRD状态，只允许approved状态的PRD被解析
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import yaml


class PRDStatusValidator:
    """PRD状态验证器"""

    VALID_STATES = [
        "draft",
        "review",
        "approved",
        "implementing",
        "completed",
        "archived",
    ]

    def __init__(self, prd_path: str):
        self.prd_path = Path(prd_path)

    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        验证PRD状态是否允许parse

        Returns:
            Tuple[bool, Optional[str]]: (是否允许parse, 错误消息)
        """
        # 1. 检查文件是否存在
        if not self.prd_path.exists():
            return False, f"❌ PRD文件不存在: {self.prd_path}"

        # 2. 检查文件是否在docs/00_product/requirements/下（标准PRD路径）
        is_standard_prd = self._is_standard_prd_path()

        # 3. 如果不在标准路径，跳过状态检查（允许.taskmaster/docs/下的快速需求）
        if not is_standard_prd:
            print("ℹ️  检测到快速需求文件（非标准PRD路径），跳过状态检查")
            print(f"📁 路径: {self.prd_path}")
            return True, None

        # 4. 读取PRD元数据
        metadata = self._extract_metadata()
        if metadata is None:
            return False, (
                f"❌ 无法解析PRD元数据\n"
                f"📁 文件: {self.prd_path}\n"
                f"💡 标准PRD必须包含YAML frontmatter"
            )

        # 5. 检查status字段
        status = metadata.get("status", "").lower()

        if not status:
            return False, (
                f"❌ PRD缺少status字段\n" f"📁 文件: {self.prd_path}\n" f"💡 标准PRD必须包含status字段"
            )

        # 6. 验证状态值是否有效
        if status not in self.VALID_STATES:
            return False, (
                f"❌ PRD状态无效: '{status}'\n\n"
                f"📋 有效状态: {', '.join(self.VALID_STATES)}\n"
                f"📁 文件: {self.prd_path}"
            )

        # 7. 检查是否允许parse
        if status != "approved":
            error_msg = self._generate_status_error_message(status, metadata)
            return False, error_msg

        # 8. 状态为approved，允许parse
        return True, None

    def _is_standard_prd_path(self) -> bool:
        """判断是否是标准PRD路径"""
        path_str = str(self.prd_path.resolve())
        return (
            "docs/00_product/requirements" in path_str
            or "docs\\00_product\\requirements" in path_str
        )

    def _extract_metadata(self) -> Optional[Dict]:
        """提取PRD frontmatter元数据"""
        try:
            content = self.prd_path.read_text(encoding="utf-8")

            # 检查frontmatter格式
            if not content.startswith("---"):
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            # 解析YAML
            metadata = yaml.safe_load(parts[1])

            if not isinstance(metadata, dict):
                return None

            return metadata

        except Exception as e:
            print(f"⚠️  解析PRD元数据时出错: {e}", file=sys.stderr)
            return None

    def _generate_status_error_message(self, status: str, metadata: Dict) -> str:
        """根据不同状态生成详细错误消息"""
        req_id = metadata.get("req_id", "未知")
        title = metadata.get("title", "未知")

        if status == "draft":
            return (
                f"❌ PRD状态为 'draft'（草稿），无法执行parse-prd\n\n"
                f"📋 PRD信息:\n"
                f"   REQ-ID: {req_id}\n"
                f"   标题: {title}\n"
                f"   文件: {self.prd_path}\n\n"
                f"🔄 PRD必须处于 'approved' 状态才能解析为任务\n\n"
                f"✅ 状态转换流程:\n"
                f"   1. draft（草稿） → 完善PRD内容\n"
                f"   2. review（审核中） → 提交审核\n"
                f"   3. approved（已批准） → 可以parse\n\n"
                f"📝 操作步骤:\n"
                f"   1. 打开PRD文件: {self.prd_path}\n"
                f"   2. 修改frontmatter中的status字段:\n"
                f"      status: draft  →  status: approved\n"
                f"   3. 保存文件后重新运行parse-prd\n\n"
                f"⚠️  状态只能人工修改，不能自动修改"
            )

        elif status == "review":
            return (
                f"❌ PRD状态为 'review'（审核中），无法执行parse-prd\n\n"
                f"📋 PRD信息:\n"
                f"   REQ-ID: {req_id}\n"
                f"   标题: {title}\n"
                f"   文件: {self.prd_path}\n\n"
                f"🔄 PRD正在审核中，需要审核通过后才能parse\n\n"
                f"📝 操作步骤:\n"
                f"   1. 完成PRD审核\n"
                f"   2. 修改status字段: review → approved\n"
                f"   3. 重新运行parse-prd\n\n"
                f"⚠️  如果PRD已审核通过，请人工修改status为approved"
            )

        elif status == "implementing":
            return (
                f"❌ PRD状态为 'implementing'（开发中），不能重复parse\n\n"
                f"📋 PRD信息:\n"
                f"   REQ-ID: {req_id}\n"
                f"   标题: {title}\n"
                f"   文件: {self.prd_path}\n\n"
                f"💡 该PRD已经被parse过，任务已生成\n\n"
                f"📁 任务位置: .taskmaster/tasks/{req_id}/\n\n"
                f"✅ 如需查看任务:\n"
                f"   task-master list\n"
                f"   task-master show <task-id>\n\n"
                f"⚠️  如果确实需要重新parse，请先修改status为approved\n"
                f"   （这会覆盖现有任务，请谨慎操作）"
            )

        elif status == "completed":
            return (
                f"❌ PRD状态为 'completed'（已完成），不能parse\n\n"
                f"📋 PRD信息:\n"
                f"   REQ-ID: {req_id}\n"
                f"   标题: {title}\n"
                f"   文件: {self.prd_path}\n\n"
                f"✅ 该PRD对应的需求已完成开发\n\n"
                f"💡 如果需要修改需求，请创建新的PRD"
            )

        elif status == "archived":
            return (
                f"❌ PRD状态为 'archived'（已归档），不能parse\n\n"
                f"📋 PRD信息:\n"
                f"   REQ-ID: {req_id}\n"
                f"   标题: {title}\n"
                f"   文件: {self.prd_path}\n\n"
                f"💡 该PRD已被归档（废弃或取消）\n\n"
                f"📝 如果需要恢复，请人工修改status字段"
            )

        else:
            return (
                f"❌ PRD状态为 '{status}'，不是 'approved'\n\n"
                f"📋 PRD必须处于 'approved' 状态才能parse\n"
                f"📁 文件: {self.prd_path}\n\n"
                f"💡 请修改status字段为 'approved' 后重试"
            )

    def update_status_to_implementing(self) -> bool:
        """
        Parse成功后，自动更新PRD状态为implementing
        这是唯一允许的自动状态修改

        Returns:
            bool: 是否更新成功
        """
        if not self._is_standard_prd_path():
            # 非标准PRD路径，跳过状态更新
            return True

        try:
            content = self.prd_path.read_text(encoding="utf-8")

            if not content.startswith("---"):
                print("⚠️  无法更新PRD状态：缺少frontmatter", file=sys.stderr)
                return False

            parts = content.split("---", 2)
            if len(parts) < 3:
                print("⚠️  无法更新PRD状态：frontmatter格式错误", file=sys.stderr)
                return False

            # 解析并更新元数据
            metadata = yaml.safe_load(parts[1])
            old_status = metadata.get("status", "unknown")
            metadata["status"] = "implementing"
            metadata["updated_at"] = self._get_current_timestamp()

            # 重新生成frontmatter
            new_frontmatter = yaml.dump(
                metadata,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
            )
            new_content = f"---\n{new_frontmatter}---{parts[2]}"

            # 写回文件
            self.prd_path.write_text(new_content, encoding="utf-8")

            print(f"✅ PRD状态已自动更新: {old_status} → implementing")
            print(f"📁 文件: {self.prd_path}")

            return True

        except Exception as e:
            print(f"⚠️  更新PRD状态失败: {e}", file=sys.stderr)
            return False

    def _get_current_timestamp(self) -> str:
        """获取当前时间戳（ISO 8601格式）"""
        from datetime import datetime

        return datetime.now().isoformat()


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python prd_status_validator.py <prd-file-path>")
        print("\n示例:")
        print(
            "  python prd_status_validator.py "
            "docs/00_product/requirements/REQ-2025-001/"
            "REQ-2025-001.md"
        )
        print("  python prd_status_validator.py " ".taskmaster/docs/user-login.txt")
        sys.exit(1)

    prd_path = sys.argv[1]
    validator = PRDStatusValidator(prd_path)

    # 执行验证
    is_valid, error_msg = validator.validate()

    if not is_valid:
        print(error_msg, file=sys.stderr)
        print("\n" + "=" * 60, file=sys.stderr)
        print("🚫 PRD状态验证失败，parse-prd操作被拒绝", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        sys.exit(1)

    # 验证通过
    print("✅ PRD状态验证通过")
    print(f"📁 文件: {prd_path}")
    print("🚀 可以执行parse-prd")
    sys.exit(0)


if __name__ == "__main__":
    main()
