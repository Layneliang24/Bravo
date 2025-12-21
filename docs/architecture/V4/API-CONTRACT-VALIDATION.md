# API契约一致性验证

> **V4架构增强**: 在合规检查中添加API契约一致性验证

## 📋 概述

根据V4契约驱动开发原则，API契约文件应该与代码实现保持一致。本功能在合规检查引擎中添加了契约一致性验证，确保API实现与契约文件同步更新。

## 🔍 验证机制

### 1. Pre-commit阶段检查（基础验证）

**位置**: `.compliance/checkers/code_checker.py`

**触发条件**:

- 后端API代码文件修改（`backend/apps/**/views.py` 或 `serializers.py`）
- 代码文件包含REQ-ID注释
- `code.yaml`规则中`require_api_contract_consistency: true`

**检查内容**:

1. ✅ 检查PRD中是否声明了`api_contract`字段
2. ✅ 检查API契约文件是否存在
3. ✅ 验证契约文件格式（OpenAPI版本、paths定义等）
4. ⚠️ 提醒开发者需要保持一致性

**检查结果**:

- **错误（error）**: 契约文件格式错误（阻止提交）
- **警告（warning）**: 契约文件不存在或需要保持一致性（不阻止提交，但提醒）

### 2. CI/CD阶段检查（完整验证）

**位置**: `scripts/validate-api-contract.py`

**使用方法**:

```bash
# 验证特定REQ的API契约一致性
python scripts/validate-api-contract.py REQ-2025-003-user-login
```

**检查内容**:

1. ✅ 从代码生成OpenAPI Schema（使用`drf-spectacular`）
2. ✅ 读取静态契约文件
3. ✅ 对比路径（paths）差异
4. ✅ 对比HTTP方法差异
5. ✅ 报告所有不一致之处

**检查结果**:

- **通过**: API契约与代码实现一致
- **失败**: 发现不一致，列出所有差异

## 📝 配置说明

### code.yaml规则配置

```yaml
# 代码修改验证
modification_validation:
  require_api_contract_consistency: true # 启用API契约一致性检查
```

### PRD配置要求

PRD的frontmatter中需要声明`api_contract`字段：

```yaml
---
req_id: REQ-2025-003-user-login
api_contract: docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml
---
```

## 🚀 使用流程

### 场景1：修改后端API代码

**步骤**:

1. 修改`backend/apps/**/views.py`或`serializers.py`
2. 运行`git commit`
3. Pre-commit hook自动检查：
   - ✅ 契约文件是否存在
   - ✅ 契约文件格式是否正确
   - ⚠️ 提醒需要保持一致性
4. 提交代码

**如果需要完整验证**:

```bash
# 在本地运行完整验证（需要Django环境）
python scripts/validate-api-contract.py REQ-2025-003-user-login
```

### 场景2：CI/CD自动验证

**在CI/CD Pipeline中添加**:

```yaml
# .github/workflows/pr-validation.yml
- name: Validate API Contract Consistency
  run: |
    # 获取修改的REQ-ID列表
    MODIFIED_REQS=$(git diff --name-only origin/main...HEAD | \
      grep -E "backend/apps/.*/(views|serializers)\.py" | \
      xargs grep -h "REQ-ID" | \
      sed 's/.*REQ-ID: //' | \
      sort -u)

    # 对每个REQ-ID进行验证
    for REQ_ID in $MODIFIED_REQS; do
      python scripts/validate-api-contract.py $REQ_ID
    done
```

## ⚠️ 注意事项

### Pre-commit阶段限制

由于pre-commit阶段无法运行Django环境，所以：

- ✅ **只能做基础验证**（文件存在、格式正确）
- ❌ **无法做完整的一致性验证**（代码生成Schema vs 契约文件）
- ✅ **完整验证需要在CI/CD中完成**

### 完整验证要求

运行完整验证需要：

- ✅ Django环境已配置
- ✅ `drf-spectacular`已安装
- ✅ 数据库连接可用（可选，某些情况下需要）

## 📊 检查结果示例

### Pre-commit警告示例

```
⚠️ 后端API代码文件 backend/apps/users/views.py 已修改。
请确保代码实现与API契约文件 docs/01_guideline/api-contracts/REQ-2025-003-user-login/REQ-2025-003-user-login-api.yaml 保持一致。
建议：运行 'python manage.py spectacular --file schema-from-code.json' 生成当前代码的OpenAPI Schema，并与契约文件对比验证一致性。完整的契约一致性验证将在CI/CD中自动执行。
```

### CI/CD验证失败示例

```
❌ 发现 3 处不一致:
  - 契约文件定义了路径 /api/auth/preview/，但代码中未实现
  - 路径 /api/auth/login/: 契约定义了 POST 方法，但代码中未实现
  - 代码中实现了路径 /api/auth/new-endpoint/，但契约文件中未定义

请修复不一致之处，确保代码实现与API契约文件保持一致。
```

## 🔧 故障排查

### 问题1：Pre-commit检查未触发

**原因**:

- `code.yaml`中`require_api_contract_consistency: false`
- 修改的文件不是`views.py`或`serializers.py`

**解决**:

- 检查规则配置
- 确认文件路径包含`backend/apps/`且文件名匹配

### 问题2：CI/CD验证失败但本地正常

**原因**:

- CI/CD环境与本地环境不同
- Django配置差异

**解决**:

- 检查CI/CD中的Django环境配置
- 确认`drf-spectacular`已正确安装

### 问题3：契约文件存在但检查报错

**原因**:

- 契约文件路径不正确
- 契约文件格式错误

**解决**:

- 检查PRD中的`api_contract`字段路径
- 验证契约文件YAML格式
- 使用Swagger Editor在线验证: https://editor.swagger.io/

## 📚 相关文档

- [V4契约驱动开发规则](.cursor/rules/principles/v4-contract-driven.mdc)
- [API契约文档目录](docs/01_guideline/api-contracts/README.md)
- [合规引擎文档](.compliance/README.md)

## 🔄 后续改进

计划中的改进：

1. ✅ Pre-commit基础验证（已完成）
2. ⏳ CI/CD完整验证脚本（已完成）
3. ⏳ 集成到CI/CD Pipeline（待实现）
4. ⏳ 支持增量验证（只验证修改的API）
5. ⏳ 自动修复建议（生成差异报告和建议）
