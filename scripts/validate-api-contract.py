#!/usr/bin/env python3
"""
API契约一致性验证脚本
用于CI/CD中验证代码实现与API契约文件的一致性

使用方法:
    python scripts/validate-api-contract.py <REQ-ID>

功能:
    1. 从代码生成OpenAPI Schema（使用drf-spectacular）
    2. 读取静态契约文件
    3. 对比两者差异
    4. 报告不一致的地方
"""

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML未安装，请运行: pip install pyyaml")
    sys.exit(1)


def find_project_root() -> Path:
    """查找项目根目录"""
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "docs" / "00_product" / "requirements").exists():
            return parent
    return Path.cwd()


def load_prd_metadata(req_id: str, project_root: Path) -> dict:
    """加载PRD元数据"""
    prd_path = (
        project_root / "docs" / "00_product" / "requirements" / req_id / f"{req_id}.md"
    )

    if not prd_path.exists():
        print(f"ERROR: PRD文件不存在: {prd_path}")
        sys.exit(1)

    content = prd_path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        print(f"ERROR: PRD frontmatter格式错误: {prd_path}")
        sys.exit(1)

    metadata = yaml.safe_load(parts[1]) or {}
    return metadata


def load_contract_file(contract_path: Path) -> dict:
    """加载API契约文件"""
    if not contract_path.exists():
        print(f"ERROR: API契约文件不存在: {contract_path}")
        sys.exit(1)

    content = contract_path.read_text(encoding="utf-8")
    contract_spec = yaml.safe_load(content)

    if "openapi" not in contract_spec:
        print(f"ERROR: API契约文件缺少openapi版本字段: {contract_path}")
        sys.exit(1)

    return contract_spec


def generate_schema_from_code(project_root: Path) -> dict:
    """
    从代码生成OpenAPI Schema
    使用Django的spectacular命令
    """
    import subprocess
    import tempfile

    # 生成临时文件保存Schema
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # 运行spectacular命令生成Schema
        result = subprocess.run(
            ["python", "manage.py", "spectacular", "--file", tmp_path],
            cwd=project_root / "backend",
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            print("WARNING: 无法从代码生成OpenAPI Schema")
            print(f"错误信息: {result.stderr}")
            return None

        # 读取生成的Schema
        with open(tmp_path, "r", encoding="utf-8") as f:
            schema = json.load(f)

        return schema
    except FileNotFoundError:
        print("WARNING: Django manage.py不存在，跳过代码Schema生成")
        return None
    except Exception as e:
        print(f"WARNING: 生成代码Schema时出错: {e}")
        return None
    finally:
        # 清理临时文件
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


def compare_paths(contract_paths: dict, code_paths: dict) -> list:
    """对比API路径差异"""
    differences = []

    # 检查契约中的路径是否在代码中存在
    for path in contract_paths.keys():
        if path not in code_paths:
            differences.append(f"  - 契约文件定义了路径 {path}，但代码中未实现")

    # 检查代码中的路径是否在契约中定义
    for path in code_paths.keys():
        if path not in contract_paths:
            differences.append(f"  - 代码中实现了路径 {path}，但契约文件中未定义")

    return differences


def compare_methods(contract_methods: dict, code_methods: dict, path: str) -> list:
    """对比HTTP方法差异"""
    differences = []

    for method in contract_methods.keys():
        if method not in code_methods:
            differences.append(f"  - 路径 {path}: 契约定义了 {method.upper()} 方法，但代码中未实现")

    return differences


def compare_schemas(contract_spec: dict, code_schema: dict) -> list:
    """对比两个OpenAPI Schema的差异"""
    differences = []

    if not code_schema:
        differences.append("  - 无法从代码生成OpenAPI Schema，跳过详细对比")
        return differences

    contract_paths = contract_spec.get("paths", {})
    code_paths = code_schema.get("paths", {})

    # 对比路径
    path_diffs = compare_paths(contract_paths, code_paths)
    differences.extend(path_diffs)

    # 对比每个路径下的方法
    for path in contract_paths.keys():
        if path in code_paths:
            contract_methods = contract_paths[path]
            code_methods = code_paths[path]
            method_diffs = compare_methods(contract_methods, code_methods, path)
            differences.extend(method_diffs)

    return differences


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python scripts/validate-api-contract.py <REQ-ID>")
        sys.exit(1)

    req_id = sys.argv[1]
    project_root = find_project_root()

    print(f"验证API契约一致性: {req_id}")
    print(f"项目根目录: {project_root}")

    # 1. 加载PRD元数据
    print("\n1. 加载PRD元数据...")
    metadata = load_prd_metadata(req_id, project_root)
    api_contract_path = metadata.get("api_contract")

    if not api_contract_path:
        print("WARNING: PRD中未声明api_contract字段，跳过契约验证")
        sys.exit(0)

    # 2. 加载契约文件
    print(f"\n2. 加载API契约文件: {api_contract_path}")
    contract_path = project_root / api_contract_path
    if not contract_path.is_absolute():
        contract_path = project_root / contract_path

    contract_spec = load_contract_file(contract_path)
    openapi_ver = contract_spec.get("openapi", "unknown")
    print(f"   ✅ 契约文件加载成功（OpenAPI {openapi_ver}）")

    # 3. 从代码生成Schema
    print("\n3. 从代码生成OpenAPI Schema...")
    code_schema = generate_schema_from_code(project_root)
    if code_schema:
        print("   ✅ 代码Schema生成成功")
    else:
        print("   ⚠️  代码Schema生成失败（可能在非Django环境中运行）")

    # 4. 对比差异
    print("\n4. 对比契约文件与代码实现...")
    differences = compare_schemas(contract_spec, code_schema)

    # 5. 报告结果
    if differences:
        print(f"\n❌ 发现 {len(differences)} 处不一致:")
        for diff in differences:
            print(diff)
        contract_path_str = str(contract_path)
        print(f"\n请修复不一致之处，" f"确保代码实现与API契约文件 {contract_path_str} 保持一致。")
        sys.exit(1)
    else:
        print("\n✅ API契约与代码实现一致")
        sys.exit(0)


if __name__ == "__main__":
    main()
