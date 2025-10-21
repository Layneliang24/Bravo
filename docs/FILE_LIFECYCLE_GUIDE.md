# 📂 文件生命周期管理指南

## 🎯 目标

防止项目中积累大量临时文件、测试脚本和调试代码，通过**强制元数据注释**和**命名规范**来管理文件的生命周期。

---

## 📋 核心理念

### 问题

- AI 和开发者经常创建临时测试文件
- 时间久了不知道哪些文件可以删除
- 担心误删重要文件
- 项目中充斥着各种临时文件

### 解决方案

1. **命名规范**：使用 `deletable` 标识符明确标记临时文件
2. **元数据注释**：在文件中注明用途、依赖、是否可删除
3. **自动检查**：Pre-commit 自动验证元数据完整性
4. **工具支持**：提供扫描和清理工具

---

## 🏷️ 文件命名规范

### 可删除文件命名

必须在文件名中包含 `deletable` 标识：

```bash
# 格式1：中间插入 .deletable. （推荐）
test_feature.deletable.py          # 可删除的Python文件
debug_log.deletable.txt            # 可删除的日志文件
temp_analysis.deletable.md         # 可删除的临时文档
mock_data.deletable.json           # 可删除的测试数据

# 格式2：前缀 deletable_
deletable_test_script.py           # 可删除的测试脚本
deletable_debug_output.txt         # 可删除的调试输出

# 目录级别
temp_deletable/                     # 整个目录标记为可删除
  ├── analysis.py
  └── data.json
```

### 永久文件命名

正常命名，不包含 `deletable`：

```bash
user_service.py                    # 业务代码
config.json                        # 配置文件
README.md                          # 文档
```

---

## 📝 元数据注释规范

### Python 文件

```python
#!/usr/bin/env python3
"""
@deletable: true
@purpose: 临时测试脚本，用于验证用户认证流程
@created: 2025-10-20
@author: AI Assistant / Claude
@delete_after: 2025-10-27
@safe_to_delete: yes
@dependencies: none
"""

def test_authentication():
    pass
```

### JavaScript/TypeScript 文件

```javascript
/**
 * @deletable true
 * @purpose 临时测试，验证API响应格式
 * @created 2025-10-20
 * @author AI Assistant
 * @safe_to_delete yes
 * @dependencies none
 */

function testAPI() {
  // test code
}
```

### Shell 脚本

```bash
#!/bin/bash
# @deletable: true
# @purpose: 一次性部署脚本
# @created: 2025-10-20
# @safe_to_delete: yes
# @dependencies: none

echo "Deploy script"
```

### Markdown 文档

```markdown
<!--
@deletable: true
@purpose: 临时调试记录
@created: 2025-10-20
@safe_to_delete: yes
@dependencies: none
-->

# Debug Notes

...
```

---

## 🔍 元数据字段说明

### 必需字段（Missing 会导致 Pre-commit 失败）

| 字段              | 说明           | 可选值                       |
| ----------------- | -------------- | ---------------------------- |
| `@deletable`      | 是否可删除     | `true`, `yes`, `1`           |
| `@purpose`        | 文件用途说明   | 自由文本                     |
| `@safe_to_delete` | 是否可安全删除 | `yes`, `no`, `true`, `false` |

### 可选字段

| 字段            | 说明                     | 示例                        |
| --------------- | ------------------------ | --------------------------- |
| `@delete_after` | 自动删除日期             | `2025-10-27`                |
| `@dependencies` | 依赖说明（哪些地方用到） | `none`, `scripts/deploy.sh` |
| `@created`      | 创建日期                 | `2025-10-20`                |
| `@author`       | 作者                     | `AI Assistant`, `John Doe`  |

---

## ✅ Pre-commit 检查规则

### 触发条件

当提交的文件名包含 `deletable` 时，自动触发元数据检查。

### 检查内容

1. **必需字段检查**：

   - 缺少 `@deletable` → ❌ 失败
   - 缺少 `@purpose` → ❌ 失败
   - 缺少 `@safe_to_delete` → ❌ 失败

2. **字段值验证**：

   - `@deletable` 必须是 `true/yes/1`
   - `@safe_to_delete` 必须是 `yes/no/true/false`

3. **文件类型检查**：
   - 支持：`.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.sh`, `.bash`, `.md`, `.yml`, `.yaml`, `.json`, `.txt`
   - 不支持的类型会给出警告

### 检查示例

```bash
# 提交时自动检查
git commit -m "test: add temp script"

❌ Deletable文件元数据检查失败

🚫 发现 2 个错误：

  📄 文件: test_script.deletable.py
     ❌ 缺少 @deletable

  📄 文件: debug.deletable.txt
     ❌ 缺少 @purpose

💡 请在文件开头添加元数据注释
```

---

## 🛠️ 工具使用

### 1. 扫描工具 - scan_deletable_files.py

扫描项目中的所有 deletable 文件并生成报告。

```bash
# 扫描当前目录
python scripts/scan_deletable_files.py

# 扫描指定目录
python scripts/scan_deletable_files.py --dir ./backend

# 输出JSON格式
python scripts/scan_deletable_files.py --format json

# 保存报告到文件
python scripts/scan_deletable_files.py --output report.json
```

**示例输出**：

```
🔍 扫描项目目录: /path/to/project

===============================================================================
📊 Deletable 文件扫描报告
===============================================================================

📁 扫描目录: /path/to/project
📝 发现文件: 5 个

📈 统计信息：
  ✅ 有完整元数据: 3 个
  ❌ 缺少元数据: 2 个
  ⏰ 已过期: 1 个
  🗑️  可安全删除: 3 个
  💾 总大小: 45.67 KB
```

### 2. 清理工具 - cleanup_deletable_files.py

自动删除过期或标记为可删除的文件。

```bash
# 模拟运行（默认，不实际删除）
python scripts/cleanup_deletable_files.py

# 实际删除
python scripts/cleanup_deletable_files.py --execute

# 清理空目录
python scripts/cleanup_deletable_files.py --execute --clean-empty-dirs

# 清理指定目录
python scripts/cleanup_deletable_files.py --dir ./temp --execute
```

**示例输出**：

```
🔍 扫描目录: /path/to/project

===============================================================================
🔍 模拟运行 - 以下文件将被删除 (3 个)：
===============================================================================

  📄 scripts/test_auth.deletable.py
     📏 大小: 5.23 KB
     💡 原因: 已过期（删除日期: 2025-10-19）
     🔍 [模拟] 将会删除

  📄 debug_log.deletable.txt
     📏 大小: 12.45 KB
     💡 原因: 标记为可安全删除
     🔍 [模拟] 将会删除

===============================================================================
📊 清理统计：
===============================================================================
  📝 待删除: 3 个文件
  💾 总大小: 23.45 KB

💡 这是模拟运行，文件未被实际删除
💡 使用 --execute 参数执行实际删除操作
```

### 3. 元数据检查 - file_metadata_checker.py

Pre-commit 自动调用，也可手动运行。

```bash
# 检查单个文件
python scripts/file_metadata_checker.py test.deletable.py

# 检查多个文件
python scripts/file_metadata_checker.py *.deletable.py
```

---

## 📋 完整工作流程

### 创建临时文件

```bash
# 1. 使用 deletable 命名
touch test_feature.deletable.py

# 2. 添加元数据注释
cat > test_feature.deletable.py << 'EOF'
"""
@deletable: true
@purpose: 测试用户注册功能
@safe_to_delete: yes
@delete_after: 2025-10-27
@dependencies: none
"""

def test_registration():
    pass
EOF

# 3. 提交（会自动检查）
git add test_feature.deletable.py
git commit -m "test: add registration test"
```

### 定期清理

```bash
# 1. 扫描项目
python scripts/scan_deletable_files.py

# 2. 模拟清理（查看将被删除的文件）
python scripts/cleanup_deletable_files.py

# 3. 确认后执行清理
python scripts/cleanup_deletable_files.py --execute

# 4. 提交清理结果
git add -u
git commit -m "chore: cleanup expired deletable files"
```

---

## 🎯 最佳实践

### DO ✅

1. **始终添加元数据**：创建 deletable 文件时立即添加元数据
2. **设置删除日期**：对临时文件设置 `@delete_after`
3. **说明依赖关系**：如果其他文件依赖此文件，在 `@dependencies` 中说明
4. **定期扫描**：每周运行一次扫描工具
5. **谨慎清理**：先模拟运行，确认无误后再执行

### DON'T ❌

1. **不要跳过元数据**：即使是"临时"文件也要添加
2. **不要随意标记**：不确定是否可删除时设置 `@safe_to_delete: no`
3. **不要直接删除**：使用清理工具，有日志可追溯
4. **不要忽略警告**：Pre-commit 失败时修复，不要绕过
5. **不要滥用**：真正的项目文件不要添加 deletable 标识

---

## 🔧 故障排查

### Pre-commit 检查失败

**问题**：提交时报错缺少元数据

**解决**：

1. 检查文件名是否包含 `deletable`
2. 在文件开头添加元数据注释
3. 确保必需字段齐全
4. 重新提交

### 工具无法识别文件类型

**问题**：不支持的文件类型

**解决**：

1. 检查文件扩展名是否支持
2. 如果是特殊类型，可以提 issue 请求支持
3. 临时方案：使用文本文件注释格式 `#`

### 清理工具误删文件

**问题**：重要文件被删除

**解决**：

1. 永远先用 `--execute` 前的模拟运行
2. 检查 `@safe_to_delete` 设置
3. 使用 Git 恢复：`git checkout -- <file>`

---

## 📚 扩展阅读

- [Pre-commit 配置](.code-quality-config.yaml)
- [项目开发规范](CONTRIBUTING.md)
- [Git 保护机制](GIT_PROTECTION_SCENARIOS_ANALYSIS.md)

---

## 🆘 获取帮助

如有问题，请：

1. 查看本文档的故障排查部分
2. 运行 `python scripts/scan_deletable_files.py --help`
3. 查看工具脚本中的详细注释
4. 在项目中提 issue

---

**最后更新**: 2025-10-20
**维护者**: Claude Sonnet 4.5
