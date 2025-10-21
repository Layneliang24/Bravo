#!/usr/bin/env python3
"""
@deletable: false
@purpose: Pre-commit检查工具 - 防止根目录docker-compose文件数量无限增长
@created: 2025-10-21
@author: Claude Sonnet 4.5
@safe_to_delete: no
@dependencies: Pre-commit系统核心依赖
"""

import io
import sys
from pathlib import Path
from typing import List, Set

# 修复Windows终端中文乱码问题
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# 允许存在的 docker-compose 文件白名单
ALLOWED_DOCKER_COMPOSE_FILES = {
    "docker-compose.yml",  # 主配置文件
    "docker-compose.ci.yml",  # CI 环境配置
    "docker-compose.monitoring.yml",  # 监控服务配置
    "docker-compose.prod.yml",  # 生产/开发环境配置
    "docker-compose.test.yml",  # 测试环境配置
    "docker-compose.tools.yml",  # 工具服务配置
}

# 每个文件的用途说明
FILE_PURPOSES = {
    "docker-compose.yml": "主配置文件，定义核心服务",
    "docker-compose.ci.yml": "CI环境专用配置",
    "docker-compose.monitoring.yml": "监控服务（Prometheus, Grafana等）",
    "docker-compose.prod.yml": "生产和开发环境配置",
    "docker-compose.test.yml": "测试环境配置",
    "docker-compose.tools.yml": "工具服务配置",
}


class DockerComposeGuard:
    """Docker Compose 文件数量守护"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.violations: List[str] = []

    def find_docker_compose_files(self) -> Set[str]:
        """查找根目录下的所有 docker-compose 文件"""
        patterns = ["docker-compose*.yml", "docker-compose*.yaml"]
        found_files = set()

        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    found_files.add(file_path.name)

        return found_files

    def check_files(self) -> bool:
        """检查 docker-compose 文件是否符合规范"""
        current_files = self.find_docker_compose_files()

        # 检查是否有新增的文件
        new_files = current_files - ALLOWED_DOCKER_COMPOSE_FILES
        if new_files:
            self.violations.append(
                f"检测到未授权的 docker-compose 文件: {', '.join(sorted(new_files))}"
            )

        # 检查是否有文件被删除（警告）
        missing_files = ALLOWED_DOCKER_COMPOSE_FILES - current_files
        if missing_files:
            # 文件被删除是允许的，只是给出警告
            print(
                f"⚠️  警告: 以下 docker-compose 文件已被删除: {', '.join(sorted(missing_files))}"
            )

        return len(self.violations) == 0

    def print_violations(self) -> None:
        """打印违规信息"""
        if not self.violations:
            return

        print("")
        print("=" * 80)
        print("🚫 Docker Compose 文件限制检查失败")
        print("=" * 80)
        print("")

        for violation in self.violations:
            print(f"  ❌ {violation}")

        print("")
        print("=" * 80)
        print("📋 当前允许的 docker-compose 文件列表:")
        print("=" * 80)
        print("")

        for file_name in sorted(ALLOWED_DOCKER_COMPOSE_FILES):
            purpose = FILE_PURPOSES.get(file_name, "无说明")
            print(f"  ✅ {file_name}")
            print(f"     用途: {purpose}")
            print("")

        print("=" * 80)
        print("💡 如何添加新的 docker-compose 文件:")
        print("=" * 80)
        print("")
        print("如果确实需要添加新的 docker-compose 文件，请遵循以下步骤：")
        print("")
        print("1. 📝 评估必要性：")
        print("   - 是否可以合并到现有文件中？")
        print("   - 是否可以通过环境变量区分？")
        print("   - 是否真的需要独立配置文件？")
        print("")
        print("2. 📋 准备说明文档：")
        print("   - 新文件的具体用途")
        print("   - 为什么不能使用现有文件")
        print("   - 长期维护计划")
        print("")
        print("3. 🔧 修改限制脚本：")
        print("   - 编辑 scripts/check_docker_compose_limit.py")
        print("   - 将新文件名添加到 ALLOWED_DOCKER_COMPOSE_FILES")
        print("   - 在 FILE_PURPOSES 中添加用途说明")
        print("")
        print("4. 📄 提交说明：")
        print("   - 在提交信息中详细说明添加原因")
        print("   - 在 PR 中附上评审讨论")
        print("")
        print("=" * 80)
        print("")


def main():
    """主函数"""
    print("🔍 检查根目录 docker-compose 文件...")

    guard = DockerComposeGuard()
    is_valid = guard.check_files()

    if not is_valid:
        guard.print_violations()
        print("❌ Docker Compose 文件限制检查失败")
        sys.exit(1)
    else:
        current_count = len(guard.find_docker_compose_files())
        allowed_count = len(ALLOWED_DOCKER_COMPOSE_FILES)
        print(
            f"✅ Docker Compose 文件限制检查通过 " f"(当前: {current_count}/{allowed_count} 个文件)"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
