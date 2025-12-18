# Cursor规则系统索引

## 📋 规则组织结构

本项目的Cursor规则系统采用**分层管理 + 意图路由**策略：

### 三层架构

1. **核心原则层**（alwaysApply，5个规则）

   - 总是生效，不依赖文件或意图
   - `principles/v4-core.mdc`
   - `principles/v4-traceability.mdc`
   - `tools/pre-commit.mdc`
   - `quality/compliance.mdc`
   - `workflows/intent-recognition.mdc`（路由层）

2. **意图路由层**（alwaysApply，1个规则）

   - `workflows/intent-recognition.mdc`
   - 根据用户意图动态加载工作流程规则

3. **工作流程层**（按需加载）
   - 通过意图路由或文件类型匹配触发
   - 不设置 alwaysApply

### 目录结构（按规则类型）

```
.cursor/
└── rules/
    ├── README.md                     # 本文件（规则索引）
    ├── principles/                   # 核心原则（最高优先级，alwaysApply）
    │   ├── v4-core.mdc               # V4架构核心原则
    │   ├── v4-traceability.mdc       # 追溯链规则
    │   └── v4-contract-driven.mdc    # 契约驱动规则
    ├── workflows/                    # 工作流程（PRD→任务→开发→测试→部署）
    │   ├── prd-design.mdc
    │   ├── prd-refinement.mdc
    │   ├── task-generation.mdc
    │   ├── task-execution.mdc
    │   ├── development.mdc
    │   ├── testing.mdc
    │   ├── debugging.mdc
    │   ├── ci-cd.mdc
    │   ├── deployment.mdc
    │   ├── project-setup.mdc
    │   └── documentation.mdc
    ├── roles/                        # 角色切换规则
    │   ├── developer.mdc
    │   ├── tester.mdc
    │   ├── architect.mdc
    │   └── prd-designer.mdc
    ├── tools/                        # 工具与钩子
    │   ├── pre-commit.mdc
    │   ├── taskmaster.mdc
    │   ├── taskmaster-workflow.mdc
    │   ├── taskmaster-hamster.mdc
    │   └── directory-guard.mdc
    ├── tech/                         # 技术栈规范
    │   ├── django.mdc
    │   └── vue.mdc
    └── quality/                      # 质量与合规
        ├── code-standards.mdc
        ├── test-coverage.mdc
        ├── security.mdc
        ├── compliance.mdc
        ├── golden-tests.mdc
        └── performance.mdc
```

## 🎯 规则优先级（建议）

数字越大优先级越高：

- **1000**: principles/\*（核心原则，alwaysApply）
- **950**: tools/pre-commit.mdc（提交前强校验）
- **900**: roles/architect.mdc；workflows/prd-design.mdc（PRD设计）；principles/v4-traceability.mdc
- **850**: roles/tester.mdc；principles/v4-contract-driven.mdc；workflows/testing.mdc
- **800**: roles/developer.mdc；workflows/task-generation.mdc
- **750**: workflows/development.mdc
- **700**: workflows/task-execution.mdc
- **650**: workflows/ci-cd.mdc
- **600**: workflows/debugging.mdc；workflows/deployment.mdc；workflows/code-review.mdc
- **500**: tech/_，quality/_，tools/\*（除 pre-commit）

## 📚 规则分类（按类型）

### 1. principles/ 核心原则

| 规则文件                            | 说明                              |
| ----------------------------------- | --------------------------------- |
| `principles/v4-core.mdc`            | V4五条铁律、TDD、契约驱动、追溯链 |
| `principles/v4-traceability.mdc`    | 追溯链格式、实现方式、验证规则    |
| `principles/v4-contract-driven.mdc` | 契约驱动工作流、Mock Server使用   |

### 2. workflows/ 工作流程

| 场景     | 规则文件                        | 触发条件          |
| -------- | ------------------------------- | ----------------- |
| PRD设计  | `workflows/prd-design.mdc`      | 编辑 PRD          |
| PRD精化  | `workflows/prd-refinement.mdc`  | 处理原始需求/草稿 |
| 任务生成 | `workflows/task-generation.mdc` | Task-Master 解析  |
| 任务执行 | `workflows/task-execution.mdc`  | 编辑代码          |
| 开发     | `workflows/development.mdc`     | 编辑代码          |
| 测试     | `workflows/testing.mdc`         | 编辑测试          |
| 调试     | `workflows/debugging.mdc`       | 调试/排障         |
| 代码审查 | `workflows/code-review.mdc`     | 代码评审          |
| 文档维护 | `workflows/documentation.mdc`   | 编辑/补充文档     |
| CI/CD    | `workflows/ci-cd.mdc`           | 编辑工作流        |
| 部署     | `workflows/deployment.mdc`      | 部署文件          |
| 项目启动 | `workflows/project-setup.mdc`   | 项目初始化        |

### 3. roles/ 角色切换

| 角色        | 规则文件                 |
| ----------- | ------------------------ |
| 开发专家    | `roles/developer.mdc`    |
| 测试专家    | `roles/tester.mdc`       |
| 架构专家    | `roles/architect.mdc`    |
| PRD设计专家 | `roles/prd-designer.mdc` |

### 4. tools/ 工具与钩子

| 规则文件                        | 说明               |
| ------------------------------- | ------------------ |
| `tools/pre-commit.mdc`          | 提交前检查         |
| `tools/taskmaster.mdc`          | Task-Master 配置   |
| `tools/taskmaster-workflow.mdc` | Task-Master 工作流 |
| `tools/taskmaster-hamster.mdc`  | Hamster 集成       |
| `tools/directory-guard.mdc`     | 目录守护           |

### 5. tech/ 技术栈

| 规则文件          | 说明             |
| ----------------- | ---------------- |
| `tech/django.mdc` | 后端 Django 规范 |
| `tech/vue.mdc`    | 前端 Vue/TS 规范 |

### 6. quality/ 质量与合规

| 规则文件                     | 说明         |
| ---------------------------- | ------------ |
| `quality/code-standards.mdc` | 代码质量标准 |
| `quality/test-coverage.mdc`  | 覆盖率要求   |
| `quality/security.mdc`       | 安全规则     |
| `quality/compliance.mdc`     | 合规检查     |
| `quality/golden-tests.mdc`   | 黄金测试保护 |
| `quality/performance.mdc`    | 性能优化     |

## 🔗 规则引用

规则文件之间可以相互引用：

**引用语法**: `@文件路径`

**示例**:

```markdown
参考: @.cursor/rules/workflows/testing.mdc
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
   - `intent-recognition.mdc` 识别意图
   - 动态加载相应规则
   - **即使文件还没打开，规则也会生效**

2. **文件类型匹配**：
   - 打开特定类型的文件（如 `.py`、`.vue`）
   - 通过 `globs` 匹配触发规则
   - 传统方式，仍然有效

### 已注册的意图

| 意图类型   | 关键词示例              | 应用规则                            |
| ---------- | ----------------------- | ----------------------------------- |
| PRD设计    | "生成PRD"、"分析PRD"    | prd-design.mdc                      |
| 任务生成   | "生成任务"、"parse-prd" | task-generation.mdc                 |
| 开发实现   | "实现功能"、"写代码"    | task-execution.mdc, development.mdc |
| 测试编写   | "写测试"、"E2E"         | testing.mdc, e2e.mdc                |
| 提交代码   | "提交代码"、"commit"    | pre-commit.mdc, compliance.mdc      |
| 调试问题   | "调试"、"排查问题"      | debugging.mdc                       |
| API契约    | "API契约"、"OpenAPI"    | v4-contract-driven.mdc              |
| 文档维护   | "更新文档"、"写文档"    | documentation.mdc                   |
| 代码审查   | "代码审查"、"review"    | code-review.mdc                     |
| 项目初始化 | "项目初始化"、"setup"   | project-setup.mdc                   |

**参考**: `@.cursor/rules/workflows/intent-recognition.mdc`

## 📖 快速导航

### 按场景查找规则

**我要设计/精化PRD**:
→ `workflows/prd-design.mdc` + `workflows/prd-refinement.mdc` + `roles/prd-designer.mdc`

**我要生成任务**:
→ `workflows/task-generation.mdc` + `tools/taskmaster.mdc`

**我要执行开发任务**:
→ `workflows/task-execution.mdc` + `roles/developer.mdc` + `workflows/development.mdc`

**我要编写测试**:
→ `workflows/testing.mdc` + `roles/tester.mdc` + `quality/test-coverage.mdc`

**我要写E2E**:
→ `workflows/e2e.mdc`

**我要调试问题**:
→ `workflows/debugging.mdc`

**我要提交代码**:
→ `tools/pre-commit.mdc` + `quality/compliance.mdc`

**我要写脚本/运维脚本**:
→ `tools/scripts.mdc`

**我要部署**:
→ `workflows/deployment.mdc`

**我要审查代码**:
→ `workflows/code-review.mdc`

**我要维护文档**:
→ `workflows/documentation.mdc`

### 按技术栈查找规则

**Django开发**:
→ `django_split.mdc` + `lifecycle/development.mdc`

**Vue开发**:
→ `vue_component.mdc` + `lifecycle/development.mdc`

**测试编写**:
→ `lifecycle/testing.mdc` + `test_coverage.mdc`

## 🔄 规则维护

### 添加新规则

1. **确定规则分类**：

   - `principles/`: 核心原则（alwaysApply）
   - `workflows/`: 工作流程（按需加载）
   - `roles/`: 角色规则（按需加载）
   - `quality/`: 质量规则（按需加载）
   - `tech/`: 技术栈规则（按文件类型加载）
   - `tools/`: 工具规则（按需加载）

2. **使用模板创建规则**：

   - 参考 `RULE_TEMPLATE.mdc`
   - 包含完整的 frontmatter（description, globs, priority）
   - **不要设置 alwaysApply**（除非是核心原则）

3. **注册到意图路由**（如果是工作流程规则）：

   - 在 `workflows/intent-recognition.mdc` 中添加意图识别
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
- **Task-Master文档**: `@.cursor/rules/tools/taskmaster.mdc`
- **最佳实践**: https://github.com/PatrickJS/awesome-cursorrules
