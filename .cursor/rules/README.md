# Cursor规则系统索引

## 📋 规则组织结构

本项目的Cursor规则系统采用**分层管理 + 意图路由**策略：

### 三层架构

1. **核心原则层**（alwaysApply，2个规则）

   - 总是生效，不依赖文件或意图
   - `00-core/v4-core.mdc` (priority: 1000)
   - `00-core/intent-recognition.mdc` (priority: 980) - 路由层

2. **意图路由层**（alwaysApply，1个规则）

   - `00-core/intent-recognition.mdc`
   - 根据用户意图动态加载工作流程规则

3. **工作流程层**（按需加载）
   - 通过意图路由或文件类型匹配触发
   - 不设置 alwaysApply

### 目录结构（按阶段编号）

```
.cursor/
└── rules/
    ├── README.md                     # 本文件（规则索引）
    ├── 00-core/                      # 核心原则（alwaysApply）
    │   ├── intent-recognition.mdc    # 意图识别与路由
    │   ├── v4-core.mdc               # V4架构核心原则
    │   ├── v4-traceability.mdc       # 追溯链规则
    │   ├── v4-tdd.mdc                # TDD工作流规则
    │   ├── v4-directory-structure.mdc # 目录结构规范
    │   └── v4-containerization.mdc   # Docker容器化规范
    ├── 01-product/                   # 产品阶段
    │   ├── prd-standards.mdc         # PRD设计标准
    │   └── prd-refinement.mdc        # PRD精化规则
    ├── 02-testing/                   # 测试阶段
    │   ├── test-types.mdc            # 测试类型与TDD
    │   ├── test-case-standards.mdc   # 测试用例标准
    │   ├── test-case-review.mdc      # 测试用例评审
    │   ├── test-coverage.mdc         # 测试覆盖率
    │   ├── e2e-testing.mdc           # E2E测试规则
    │   ├── contract-testing.mdc      # 契约测试
    │   └── golden-tests.mdc          # 黄金测试
    ├── 03-taskmaster/                # 任务管理阶段
    │   ├── task-generation.mdc       # 任务生成规则
    │   ├── taskmaster-workflow.mdc   # Task-Master工作流
    │   ├── taskmaster-cli.mdc        # Task-Master CLI
    │   └── hamster-integration.mdc   # Hamster集成
    ├── 04-development/               # 开发阶段
    │   ├── development-workflow.mdc  # 开发工作流
    │   ├── task-execution.mdc        # 任务执行规则
    │   ├── code-standards.mdc        # 代码标准
    │   ├── django-development.mdc    # Django开发规范
    │   └── vue-development.mdc       # Vue开发规范
    ├── 05-debugging/                 # 调试阶段
    │   ├── debugging-methodology.mdc # 调试方法论
    │   └── troubleshooting-checklist.mdc # 排查检查清单
    ├── 06-cicd/                      # CI/CD阶段
    │   ├── pre-commit.mdc            # Pre-commit规则
    │   ├── compliance.mdc            # 合规检查
    │   ├── ci-workflow.mdc           # CI工作流
    │   └── cd-workflow.mdc           # CD工作流
    ├── 07-documentation/             # 文档维护
    │   ├── documentation-standards.mdc # 文档标准
    │   └── script-conventions.mdc    # 脚本规范
    ├── 08-project/                   # 项目启动
    │   └── project-setup.mdc         # 项目初始化
    ├── 09-roles/                     # 角色规则
    │   ├── architect.mdc             # 架构专家
    │   ├── developer.mdc             # 开发专家
    │   ├── tester.mdc                # 测试专家
    │   └── prd-designer.mdc          # PRD设计专家
    ├── 1-quality/                    # 质量保障
    │   ├── code-review.mdc           # 代码审查
    │   ├── performance.mdc           # 性能优化
    │   └── security.mdc              # 安全规则
    └── 10-tools/                     # 工具规则
        └── directory-guard.mdc       # 目录守卫
```

## 🎯 规则优先级

数字越大优先级越高：

- **1000**: `00-core/v4-core.mdc`（核心原则，alwaysApply）
- **980**: `00-core/intent-recognition.mdc`（意图路由，alwaysApply）
- **950**: `06-cicd/pre-commit.mdc`（提交前强校验）
- **900**: `09-roles/architect.mdc`、`01-product/prd-standards.mdc`、`00-core/v4-traceability.mdc`
- **850**: `09-roles/tester.mdc`、`02-testing/contract-testing.mdc`、`02-testing/test-types.mdc`
- **800**: `09-roles/developer.mdc`、`03-taskmaster/task-generation.mdc`
- **750**: `04-development/development-workflow.mdc`
- **700**: `04-development/task-execution.mdc`
- **650**: `06-cicd/ci-workflow.mdc`、`06-cicd/cd-workflow.mdc`
- **600**: `05-debugging/debugging-methodology.mdc`
- **500**: `1-quality/*`、`10-tools/*`（除pre-commit）

## 📚 规则分类（按目录）

### 00-core/ 核心原则

| 规则文件                     | 说明                              | alwaysApply |
| ---------------------------- | --------------------------------- | ----------- |
| `v4-core.mdc`                | V4五条铁律、TDD、契约驱动、追溯链 | ✅          |
| `intent-recognition.mdc`     | 意图识别与规则路由                | ✅          |
| `v4-traceability.mdc`        | 追溯链格式、实现方式、验证规则    | ❌          |
| `v4-tdd.mdc`                 | TDD三阶段循环规则                 | ❌          |
| `v4-directory-structure.mdc` | 目录结构强制规范                  | ❌          |
| `v4-containerization.mdc`    | Docker容器化开发规范              | ❌          |

### 01-product/ 产品阶段

| 规则文件             | 说明        | 触发条件          |
| -------------------- | ----------- | ----------------- |
| `prd-standards.mdc`  | PRD设计标准 | 编辑PRD           |
| `prd-refinement.mdc` | PRD精化规则 | 处理原始需求/草稿 |

### 02-testing/ 测试阶段

| 规则文件                  | 说明                | 触发条件     |
| ------------------------- | ------------------- | ------------ |
| `test-types.mdc`          | 测试类型与TDD三阶段 | 编辑测试     |
| `test-case-standards.mdc` | 测试用例设计标准    | 设计测试用例 |
| `test-case-review.mdc`    | 测试用例评审规则    | 评审测试用例 |
| `test-coverage.mdc`       | 测试覆盖率要求      | 检查覆盖率   |
| `e2e-testing.mdc`         | E2E测试规则         | 编写E2E测试  |
| `contract-testing.mdc`    | 契约测试规则        | API契约测试  |
| `golden-tests.mdc`        | 黄金测试保护        | 黄金测试     |

### 03-taskmaster/ 任务管理阶段

| 规则文件                  | 说明                | 触发条件           |
| ------------------------- | ------------------- | ------------------ |
| `task-generation.mdc`     | 任务生成规则        | Task-Master解析PRD |
| `taskmaster-workflow.mdc` | Task-Master工作流   | Task-Master操作    |
| `taskmaster-cli.mdc`      | Task-Master CLI使用 | CLI命令            |
| `hamster-integration.mdc` | Hamster集成         | Hamster任务        |

### 04-development/ 开发阶段

| 规则文件                   | 说明           | 触发条件   |
| -------------------------- | -------------- | ---------- |
| `development-workflow.mdc` | 开发工作流     | 开发代码   |
| `task-execution.mdc`       | 任务执行规则   | 执行任务   |
| `code-standards.mdc`       | 代码质量标准   | 代码编写   |
| `django-development.mdc`   | Django开发规范 | Django代码 |
| `vue-development.mdc`      | Vue开发规范    | Vue代码    |

### 05-debugging/ 调试阶段

| 规则文件                        | 说明         | 触发条件 |
| ------------------------------- | ------------ | -------- |
| `debugging-methodology.mdc`     | 调试方法论   | 调试问题 |
| `troubleshooting-checklist.mdc` | 排查检查清单 | 排查问题 |

### 06-cicd/ CI/CD阶段

| 规则文件          | 说明                   | 触发条件 |
| ----------------- | ---------------------- | -------- |
| `pre-commit.mdc`  | Pre-commit和本地通行证 | 提交代码 |
| `compliance.mdc`  | 合规检查               | 合规验证 |
| `ci-workflow.mdc` | CI工作流               | CI流程   |
| `cd-workflow.mdc` | CD工作流               | CD流程   |

### 07-documentation/ 文档维护

| 规则文件                      | 说明            | 触发条件 |
| ----------------------------- | --------------- | -------- |
| `documentation-standards.mdc` | 文档维护规则    | 维护文档 |
| `script-conventions.mdc`      | 脚本与Shell规则 | 编写脚本 |

### 08-project/ 项目启动

| 规则文件            | 说明           | 触发条件   |
| ------------------- | -------------- | ---------- |
| `project-setup.mdc` | 项目初始化规则 | 项目初始化 |

### 09-roles/ 角色规则

| 规则文件           | 说明            | 触发条件        |
| ------------------ | --------------- | --------------- |
| `architect.mdc`    | 架构专家角色    | 架构相关操作    |
| `developer.mdc`    | 开发专家角色    | 开发相关操作    |
| `tester.mdc`       | 测试专家角色    | 测试相关操作    |
| `prd-designer.mdc` | PRD设计专家角色 | PRD设计相关操作 |

### 1-quality/ 质量保障

| 规则文件          | 说明         | 触发条件 |
| ----------------- | ------------ | -------- |
| `code-review.mdc` | 代码审查规则 | 代码审查 |
| `performance.mdc` | 性能优化规则 | 性能优化 |
| `security.mdc`    | 安全规则     | 安全检查 |

### 10-tools/ 工具规则

| 规则文件              | 说明         | 触发条件 |
| --------------------- | ------------ | -------- |
| `directory-guard.mdc` | 目录守卫规则 | 目录操作 |

## 🔗 规则引用

规则文件之间可以相互引用：

**引用语法**: `@文件路径`

**示例**:

```markdown
参考: @.cursor/rules/02-testing/test-types.mdc
参考: @docs/architecture/V4/AI-WORKFLOW-V4-PART1-ARCH.md
```

## 🎨 规则编写规范

### Frontmatter格式

```yaml
---
description: 规则描述
globs: **/*.py, **/*.ts        # 触发条件（Glob模式）
alwaysApply: true              # 是否总是应用（可选）
priority: 900                  # 优先级（可选，默认500）
---
```

### 内容结构

1. **角色切换**（如果适用）
2. **核心规则**
3. **工作流程**
4. **示例代码**
5. **禁止事项**
6. **参考文档**

### 使用示例标签

```markdown
<example>
// Good
function login(email: string, password: string) {
  return api.post('/auth/login', { email, password });
}

// Bad
function login(e: string, p: string) {
return fetch('/login', { body: JSON.stringify({e, p}) });
}
</example>
```

## 🎯 意图路由机制

### 工作原理

规则通过两种方式触发：

1. **意图路由**（推荐）：

   - 用户表达意图（如"生成PRD"、"写测试"）
   - `00-core/intent-recognition.mdc` 识别意图
   - 动态加载相应规则
   - **即使文件还没打开，规则也会生效**

2. **文件类型匹配**：
   - 打开特定类型的文件（如 `.py`、`.vue`）
   - 通过 `globs` 匹配触发规则
   - 传统方式，仍然有效

### 已注册的意图

| 意图类型   | 关键词示例              | 应用规则                                       | 角色                   |
| ---------- | ----------------------- | ---------------------------------------------- | ---------------------- |
| PRD设计    | "生成PRD"、"分析PRD"    | `01-product/prd-standards.mdc`                 | PRD设计专家 + 架构专家 |
| PRD精化    | "精化需求"、"原始需求"  | `01-product/prd-refinement.mdc`                | PRD设计专家            |
| 任务生成   | "生成任务"、"parse-prd" | `03-taskmaster/task-generation.mdc`            | 任务管理专家           |
| 开发实现   | "实现功能"、"写代码"    | `04-development/development-workflow.mdc`      | 开发专家               |
| 测试编写   | "写测试"、"E2E"         | `02-testing/test-types.mdc`                    | 测试专家               |
| 提交代码   | "提交代码"、"commit"    | `06-cicd/pre-commit.mdc`                       | 无特定角色             |
| 调试问题   | "调试"、"排查问题"      | `05-debugging/debugging-methodology.mdc`       | 无特定角色             |
| API契约    | "API契约"、"OpenAPI"    | `02-testing/contract-testing.mdc`              | 架构专家               |
| 文档维护   | "更新文档"、"写文档"    | `07-documentation/documentation-standards.mdc` | 无特定角色             |
| 代码审查   | "代码审查"、"review"    | `1-quality/code-review.mdc`                    | 无特定角色             |
| 项目初始化 | "项目初始化"、"setup"   | `08-project/project-setup.mdc`                 | 无特定角色             |
| 架构分析   | "架构"、"架构设计"      | `09-roles/architect.mdc`                       | 架构专家               |
| 性能优化   | "性能优化"、"优化性能"  | `1-quality/performance.mdc`                    | 无特定角色             |
| 安全检查   | "安全检查"、"安全漏洞"  | `1-quality/security.mdc`                       | 无特定角色             |

**参考**: `@.cursor/rules/00-core/intent-recognition.mdc`

## 📖 快速导航

### 按场景查找规则

**我要设计/精化PRD**:
→ `01-product/prd-standards.mdc` + `01-product/prd-refinement.mdc` + `09-roles/prd-designer.mdc`

**我要生成任务**:
→ `03-taskmaster/task-generation.mdc` + `03-taskmaster/taskmaster-workflow.mdc`

**我要执行开发任务**:
→ `04-development/task-execution.mdc` + `09-roles/developer.mdc` + `04-development/development-workflow.mdc`

**我要编写测试**:
→ `02-testing/test-types.mdc` + `09-roles/tester.mdc` + `02-testing/test-coverage.mdc`

**我要写E2E**:
→ `02-testing/e2e-testing.mdc`

**我要调试问题**:
→ `05-debugging/debugging-methodology.mdc` + `05-debugging/troubleshooting-checklist.mdc`

**我要提交代码**:
→ `06-cicd/pre-commit.mdc` + `06-cicd/compliance.mdc` + `00-core/v4-traceability.mdc`

**我要部署**:
→ `06-cicd/cd-workflow.mdc`

**我要审查代码**:
→ `1-quality/code-review.mdc`

**我要维护文档**:
→ `07-documentation/documentation-standards.mdc`

**我要优化性能**:
→ `1-quality/performance.mdc`

**我要安全检查**:
→ `1-quality/security.mdc`

### 按技术栈查找规则

**Django开发**:
→ `04-development/django-development.mdc` + `04-development/development-workflow.mdc`

**Vue开发**:
→ `04-development/vue-development.mdc` + `04-development/development-workflow.mdc`

**测试编写**:
→ `02-testing/test-types.mdc` + `02-testing/test-coverage.mdc`

## 🔄 规则维护

### 添加新规则

1. **确定规则分类**：

   - 根据工作流程阶段选择对应目录（00-core到10-tools）
   - 参考现有目录结构确定放置位置

2. **使用模板创建规则**：

   - 参考 `RULE_TEMPLATE.mdc`
   - 包含完整的 frontmatter（description, globs, priority）
   - **不要设置 alwaysApply**（除非是核心原则）

3. **注册到意图路由**（如果是工作流程规则）：

   - 在 `00-core/intent-recognition.mdc` 中添加意图识别
   - 定义触发关键词
   - 指定应用规则

4. **更新文档**：
   - 更新本 README.md，添加到相应分类
   - 确保规则边界清晰，不与其他规则重复

### 更新现有规则

1. **直接编辑对应的`.mdc`文件**
2. **保持frontmatter格式一致**
3. **更新相关引用**
4. **如果修改了意图关键词，更新 `intent-recognition.mdc`**

### 规则边界原则

- **单一职责**：每个规则文件只负责一个明确的职责
- **避免重复**：不要在不同规则文件中重复相同的内容，使用引用
- **清晰边界**：规则之间边界清晰，不重叠
- **可扩展性**：新规则可以轻松添加，不影响现有规则

### 规则版本控制

- 所有规则文件纳入Git版本控制
- 重大变更应在规则文件中记录变更历史
- 保持向后兼容性

## 📚 参考文档

- **V4架构文档**: `docs/architecture/V4/AI-WORKFLOW-V4-*.md`
- **API契约指南**: `docs/01_guideline/api-contracts/README.md`
- **规则系统分析**: `@.cursor/rules/RULE_SYSTEM_ANALYSIS.md`
- **最佳实践**: https://github.com/PatrickJS/awesome-cursorrules
