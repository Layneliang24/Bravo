# Cursor规则系统重构方案 - 详细讨论

## 🤔 核心问题分析

### 问题1：命名规范

#### 当前状态

- ✅ 新规则：`lifecycle/task-generation.mdc` (kebab-case)
- ❌ 历史规则：`code_quality.mdc` (snake_case)
- ❌ 历史规则：`django_split.mdc` (snake_case)
- ❌ 历史规则：`compliance_workflow.mdc` (snake_case)

#### 讨论点

**选项A：统一使用 kebab-case，不加分类前缀**

```
workflows/prd-design.mdc
workflows/task-generation.mdc
principles/v4-core.mdc
tech/django.mdc
quality/code-standards.mdc
```

- ✅ 简洁，目录已体现分类
- ✅ 符合Web标准（URL友好）
- ❓ 文件名可能不够自描述

**选项B：统一使用 kebab-case，加分类前缀**

```
workflows/workflow-prd-design.mdc
principles/principle-v4-core.mdc
tech/tech-django.mdc
quality/quality-code-standards.mdc
```

- ✅ 文件名自描述
- ❌ 冗余（目录已体现分类）
- ❌ 文件名过长

**选项C：混合方案（推荐）**

- 目录内文件：不加前缀，直接语义化名称
- 特殊情况：如果文件名可能产生歧义，加前缀区分

```
workflows/prd-design.mdc          # 清晰，无需前缀
workflows/task-generation.mdc     # 清晰，无需前缀
principles/v4-core.mdc            # 清晰，无需前缀
tech/django.mdc                   # 清晰，无需前缀
quality/code-standards.mdc        # 清晰，无需前缀
tools/taskmaster.mdc              # 清晰，无需前缀
tools/taskmaster-workflow.mdc     # 需要区分，加前缀
```

**我的建议**：选项C（混合方案）

- 默认不加前缀，保持简洁
- 仅在可能产生歧义时加前缀

---

### 问题2：文件夹分类逻辑

#### 当前分类的问题

**"lifecycle" 概念模糊**：

- 包含工作流程（prd-design, task-generation）
- 包含工具规则（pre-commit）
- 包含阶段规则（development, testing）
- 概念边界不清晰

**"v4" 单独分类不合理**：

- V4是核心原则，应该放在 `principles/`
- 不应该因为"V4"这个名称而单独分类

#### 新分类方案分析

**方案A：按规则类型分类（当前方案）**

```
principles/    # 核心原则
workflows/     # 工作流程
roles/         # 角色定义
tools/         # 工具相关
tech/          # 技术栈
quality/       # 质量保证
```

**优点**：

- ✅ 分类维度清晰（按规则性质）
- ✅ 易于理解和维护
- ✅ 扩展性好

**缺点**：

- ❓ `workflows/` 和 `tools/` 可能有重叠（如 pre-commit 既是工具又是流程）
- ❓ `quality/` 和 `tech/` 可能有重叠（如代码质量标准可能涉及技术栈）

**方案B：按触发时机分类**

```
always/        # 总是应用（principles）
on-edit/       # 编辑时触发（workflows, tech）
on-commit/     # 提交时触发（pre-commit, quality）
on-role/       # 角色切换（roles）
```

**优点**：

- ✅ 按触发机制分类，逻辑清晰

**缺点**：

- ❌ 过于技术化，不直观
- ❌ 很多规则可能同时属于多个分类

**方案C：扁平化 + 标签系统**

```
rules/
├── prd-design.mdc          # 标签: workflow, prd
├── task-generation.mdc     # 标签: workflow, taskmaster
├── v4-core.mdc            # 标签: principle, v4, always
├── django.mdc             # 标签: tech, backend
└── code-standards.mdc     # 标签: quality, always
```

**优点**：

- ✅ 结构简单
- ✅ 通过标签灵活分类

**缺点**：

- ❌ Cursor不支持标签系统
- ❌ 文件多了难以管理

**我的建议**：方案A（按规则类型分类），但需要明确边界

#### 边界定义

**workflows vs tools**：

- `workflows/`：开发流程、工作流程（PRD设计、任务生成、开发、测试、部署）
- `tools/`：工具使用规范（Task-Master命令、Git Hooks配置、Pre-commit规则）

**quality vs tech**：

- `quality/`：质量标准和检查规则（代码标准、测试覆盖率、安全扫描、合规检查）
- `tech/`：技术栈编码规范（Django应用结构、Vue组件写法、TypeScript类型）

**重叠处理**：

- `pre-commit.mdc` → `tools/`（它是Git工具的使用规范）
- `code-standards.mdc` → `quality/`（它是质量标准，不是技术栈规范）

---

### 问题3：历史规则处理

#### 需要处理的文件

1. **根目录散乱文件**：

   - `code_quality.mdc` → `quality/code-standards.mdc`
   - `test_coverage.mdc` → `quality/test-coverage.mdc`
   - `security_scan.mdc` → `quality/security.mdc`
   - `compliance_workflow.mdc` → `quality/compliance.mdc`
   - `golden_test_protection.mdc` → `quality/golden-tests.mdc`
   - `django_split.mdc` → `tech/django.mdc`
   - `vue_component.mdc` → `tech/vue.mdc`
   - `directory_guard.mdc` → `tools/directory-guard.mdc`
   - `project_startup.mdc` → `workflows/project-setup.mdc`
   - `prd-refinement.md` → 需要确认是规则文件还是文档

2. **内容完善**：
   - 检查是否有 frontmatter
   - 补充缺失的 description、globs、priority
   - 统一格式和风格
   - 更新过时的内容

#### 处理策略

**策略A：直接迁移 + 内容完善**

- 迁移文件到新位置
- 重命名文件
- 更新 frontmatter
- 完善内容

**策略B：渐进式迁移**

- 先迁移，保持内容不变
- 后续逐步完善内容
- 降低风险

**我的建议**：策略A（直接迁移 + 内容完善）

- 一次性完成，避免后续混乱
- 可以统一检查和验证

---

### 问题4：命名细节

#### 具体文件命名讨论

**V4相关文件**：

- `v4/v4-core-principles.mdc` → `principles/v4-core.mdc`
  - ❓ 是否保留 "v4" 前缀？
  - ✅ 建议保留，因为V4是项目特定的架构名称

**Task-Master相关文件**：

- `taskmaster/taskmaster.mdc` → `tools/taskmaster.mdc`
- `taskmaster/dev_workflow.mdc` → `tools/taskmaster-workflow.mdc`
  - ❓ `taskmaster-workflow.mdc` vs `taskmaster-dev-workflow.mdc`？
  - ✅ 建议 `taskmaster-workflow.mdc`（简洁）

**工作流程文件**：

- `lifecycle/supplementary.mdc` → `workflows/code-review.mdc`
  - ❓ 是否应该叫 `code-review.mdc`？
  - ❓ 还是应该拆分？补充规则可能包含多个内容

**技术栈文件**：

- `django_split.mdc` → `tech/django.mdc`
  - ❓ 是否需要更具体的名称？如 `django-app-structure.mdc`？
  - ✅ 建议 `django.mdc`（简洁，内容可以包含所有Django规则）

---

### 问题5：优先级重新规划

#### 当前优先级问题

- 优先级设置比较随意
- 没有明确的优先级分配规则
- 某些规则优先级可能不合理

#### 新优先级方案

**原则**：

1. `principles/` 最高优先级（1000），alwaysApply: true
2. `tools/pre-commit.mdc` 高优先级（950），提交前必须检查
3. `roles/` 按重要性分配（800-900）
4. `workflows/` 按执行顺序分配（550-750）
5. `tech/` 和 `quality/` 基础优先级（500）

**具体分配**：

| 优先级 | 规则                           | 理由                   |
| ------ | ------------------------------ | ---------------------- |
| 1000   | `principles/*`                 | 核心原则，必须始终应用 |
| 950    | `tools/pre-commit.mdc`         | 提交前检查，高优先级   |
| 900    | `roles/architect.mdc`          | 架构设计，影响全局     |
| 850    | `roles/tester.mdc`             | 测试质量，重要         |
| 800    | `roles/developer.mdc`          | 开发实现，重要         |
| 750    | `workflows/development.mdc`    | 开发流程               |
| 700    | `workflows/task-execution.mdc` | 任务执行               |
| 650    | `workflows/ci-cd.mdc`          | CI/CD流程              |
| 600    | `workflows/debugging.mdc`      | 调试流程               |
| 550    | `workflows/deployment.mdc`     | 部署流程               |
| 500    | `tech/*`, `quality/*`          | 技术栈和质量规则       |

**讨论点**：

- ❓ `workflows/prd-design.mdc` 应该设置什么优先级？
- ❓ `workflows/task-generation.mdc` 应该设置什么优先级？
- ❓ 是否需要为不同阶段设置不同的优先级范围？

---

### 问题6：向后兼容

#### 兼容策略

**选项A：完全迁移，不保留旧路径**

- ✅ 干净，无冗余
- ❌ 可能破坏现有引用

**选项B：保留旧文件，添加重定向说明**

```markdown
---
description: 此文件已迁移
redirect: .cursor/rules/workflows/prd-design.mdc
---

# 此文件已迁移

此规则文件已迁移到：`.cursor/rules/workflows/prd-design.mdc`

请更新所有引用。
```

**选项C：创建符号链接（如果系统支持）**

- ✅ 完全兼容
- ❌ Windows可能不支持

**我的建议**：选项B（保留旧文件，添加重定向）

- 在迁移后的第一个版本保留旧文件
- 添加重定向说明
- 在后续版本中删除旧文件

---

## 🎯 需要您决策的问题

### 1. 命名规范

- [ ] A. 不加分类前缀（推荐）
- [ ] B. 加分类前缀
- [ ] C. 混合方案

### 2. 文件夹分类

- [ ] A. 按规则类型分类（principles/workflows/roles/tools/tech/quality）
- [ ] B. 其他方案（请说明）

### 3. 边界处理

- [ ] `pre-commit.mdc` 放在 `tools/` 还是 `workflows/`？
  - **我的建议**：`tools/pre-commit.mdc`（它是Git工具的使用规范）
- [ ] `supplementary.mdc` 如何处理？
  - **我的建议**：拆分为4个文件（代码审查、文档维护、性能优化、安全）
- [ ] `prd-refinement.md` 如何处理？
  - **我的建议**：迁移到 `workflows/prd-refinement.mdc` 或合并到 `prd-design.mdc`

### 4. 历史规则

- [ ] A. 直接迁移 + 内容完善（推荐）
- [ ] B. 渐进式迁移

### 5. 优先级

- [ ] 是否同意新的优先级分配方案？
- [ ] 是否需要调整某些规则的优先级？

### 6. 向后兼容

- [ ] A. 完全迁移，不保留旧路径
- [ ] B. 保留旧文件，添加重定向说明（推荐）
- [ ] C. 创建符号链接

---

## 💡 我的推荐方案

### 命名规范

**推荐**：选项C（混合方案）

- 默认不加前缀，保持简洁
- 仅在可能产生歧义时加前缀（如 `taskmaster-workflow.mdc`）

### 文件夹分类

**推荐**：方案A（按规则类型分类）

- 分类清晰，易于理解
- 明确边界定义

### 历史规则

**推荐**：策略A（直接迁移 + 内容完善）

- 一次性完成，避免后续混乱
- 统一检查和验证

### 向后兼容

**推荐**：选项B（保留旧文件，添加重定向）

- 在迁移后的第一个版本保留旧文件
- 添加重定向说明
- 在后续版本中删除旧文件

---

## 📋 待确认的具体问题

### 1. `prd-refinement.md` 处理

**发现**：这是一个规则文件（.md格式），包含PRD精化流程规则
**建议**：

- 迁移到 `workflows/prd-refinement.mdc`
- 或者合并到 `workflows/prd-design.mdc`（因为都是PRD相关流程）

### 2. `supplementary.mdc` 处理

**发现**：包含4个不同主题：

- 代码审查规则
- 文档维护规则
- 性能优化规则
- 安全规则

**建议**：拆分为多个文件

- `workflows/code-review.mdc` - 代码审查规则
- `workflows/documentation.mdc` - 文档维护规则
- `quality/performance.mdc` - 性能优化规则
- `quality/security.mdc` - 安全规则（或合并到现有的 `security.mdc`）

### 3. V4文件命名

**建议**：保留 "v4" 前缀

- `principles/v4-core.mdc` ✅
- `principles/v4-traceability.mdc` ✅
- `principles/v4-contract-driven.mdc` ✅
- 理由：V4是项目特定的架构名称，保留前缀有助于识别

### 4. 优先级细节

**建议**：

- `workflows/prd-design.mdc` → 优先级 900（PRD设计很重要）
- `workflows/task-generation.mdc` → 优先级 800（任务生成重要）
- `workflows/task-execution.mdc` → 优先级 700（任务执行）
- `workflows/development.mdc` → 优先级 750（开发流程）

### 5. `.cursorrules` 中的引用更新

**发现**：`.cursorrules` 中有9处引用需要更新

- `@.cursor/rules/v4/v4-core-principles.mdc` → `@.cursor/rules/principles/v4-core.mdc`
- `@.cursor/rules/lifecycle/testing.mdc` → `@.cursor/rules/workflows/testing.mdc`
- `@.cursor/rules/lifecycle/task-execution.mdc` → `@.cursor/rules/workflows/task-execution.mdc`
- `@.cursor/rules/lifecycle/pre-commit.mdc` → `@.cursor/rules/tools/pre-commit.mdc`

---

## 🔄 下一步

请确认以上问题，我将根据您的决策：

1. 更新重构方案
2. 创建详细的迁移脚本
3. 执行迁移
4. 验证结果
