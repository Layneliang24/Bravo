# Cursor规则系统重构方案

## 📋 问题分析

### 当前问题

1. **命名不规范**：

   - 混用 kebab-case：`task-generation.mdc`, `prd-design.mdc`
   - 根目录文件命名不一致：`code_quality.mdc`, `django_split.mdc`, `compliance_workflow.mdc`
   - 缺少统一的命名规范

2. **文件夹分类混乱**：

   - `lifecycle/` - 概念模糊，包含工作流程、阶段、工具等混合内容
   - `v4/` - 应该属于核心原则，不应该单独分类
   - `roles/` - 这个分类合理
   - `taskmaster/` - 应该属于工具类
   - 根目录技术栈规则散乱

3. **组织逻辑不清晰**：
   - 按"生命周期"分类过于主观
   - 没有明确的分类维度
   - 历史规则和新规则混在一起

## 🎯 重构目标

### 1. 统一命名规范

**规则**：所有规则文件使用 `kebab-case`，格式为 `{category}-{name}.mdc`

**示例**：

- ✅ `workflow-prd-design.mdc`
- ✅ `workflow-task-generation.mdc`
- ✅ `principle-v4-core.mdc`
- ✅ `tech-django.mdc`
- ✅ `quality-code-standards.mdc`
- ❌ `task-generation.mdc` (缺少分类前缀)
- ❌ `code_quality.mdc` (使用下划线)

### 2. 按规则类型分类

**新的目录结构**：

```
.cursor/rules/
├── README.md                    # 规则索引和导航
├── principles/                  # 核心原则（最高优先级）
│   ├── v4-core.mdc             # V4架构核心原则
│   ├── v4-traceability.mdc     # 追溯链规则
│   ├── v4-contract-driven.mdc  # 契约驱动规则
│   └── docker-first.mdc        # Docker优先原则
├── workflows/                   # 工作流程规则
│   ├── prd-design.mdc          # PRD设计流程
│   ├── task-generation.mdc    # 任务生成流程
│   ├── task-execution.mdc     # 任务执行流程
│   ├── development.mdc        # 开发流程
│   ├── testing.mdc            # 测试流程
│   ├── debugging.mdc          # 调试流程
│   ├── code-review.mdc        # 代码审查流程
│   ├── ci-cd.mdc              # CI/CD流程
│   └── deployment.mdc         # 部署流程
├── roles/                       # 角色定义（保留）
│   ├── developer.mdc          # 开发专家
│   ├── tester.mdc             # 测试专家
│   ├── architect.mdc          # 架构专家
│   └── prd-designer.mdc       # PRD设计专家
├── tools/                       # 工具相关规则
│   ├── taskmaster.mdc         # Task-Master工具
│   ├── taskmaster-workflow.mdc # Task-Master工作流
│   ├── git-hooks.mdc          # Git Hooks规则
│   └── pre-commit.mdc         # Pre-commit规则
├── tech/                        # 技术栈特定规则
│   ├── django.mdc             # Django开发规则
│   ├── vue.mdc                # Vue开发规则
│   └── typescript.mdc         # TypeScript规则
└── quality/                     # 质量保证规则
    ├── code-standards.mdc     # 代码质量标准
    ├── test-coverage.mdc      # 测试覆盖率
    ├── security.mdc           # 安全规则
    ├── compliance.mdc         # 合规检查
    └── golden-tests.mdc       # 黄金测试保护
```

### 3. 分类维度说明

#### principles/ - 核心原则

- **特点**：最高优先级，alwaysApply: true
- **内容**：架构原则、设计原则、开发理念
- **示例**：V4五条铁律、Docker优先、TDD原则

#### workflows/ - 工作流程

- **特点**：按开发阶段组织，有明确的执行顺序
- **内容**：PRD设计→任务生成→开发→测试→部署
- **触发**：根据文件类型和操作阶段自动触发

#### roles/ - 角色定义

- **特点**：AI角色切换，根据任务类型自动切换
- **内容**：不同角色的职责、工作方式、Prompt模板
- **触发**：根据任务类型和上下文自动切换

#### tools/ - 工具相关

- **特点**：针对特定工具的使用规则
- **内容**：Task-Master、Git Hooks、Pre-commit等工具的使用规范
- **触发**：编辑相关工具配置文件时触发

#### tech/ - 技术栈

- **特点**：针对特定技术栈的编码规范
- **内容**：Django、Vue、TypeScript等技术的开发规范
- **触发**：编辑对应技术栈的文件时触发

#### quality/ - 质量保证

- **特点**：代码质量、测试、安全等质量相关规则
- **内容**：代码标准、测试覆盖率、安全扫描、合规检查
- **触发**：代码审查、测试、提交时触发

## 📝 迁移计划

### 阶段1：创建新目录结构

```bash
mkdir -p .cursor/rules/{principles,workflows,tools,tech,quality}
```

### 阶段2：文件迁移映射

| 原路径                          | 新路径        | 新文件名                  |
| ------------------------------- | ------------- | ------------------------- |
| `lifecycle/prd-design.mdc`      | `workflows/`  | `prd-design.mdc`          |
| `lifecycle/task-generation.mdc` | `workflows/`  | `task-generation.mdc`     |
| `lifecycle/task-execution.mdc`  | `workflows/`  | `task-execution.mdc`      |
| `lifecycle/development.mdc`     | `workflows/`  | `development.mdc`         |
| `lifecycle/testing.mdc`         | `workflows/`  | `testing.mdc`             |
| `lifecycle/debugging.mdc`       | `workflows/`  | `debugging.mdc`           |
| `lifecycle/pre-commit.mdc`      | `tools/`      | `pre-commit.mdc`          |
| `lifecycle/ci-cd.mdc`           | `workflows/`  | `ci-cd.mdc`               |
| `lifecycle/deployment.mdc`      | `workflows/`  | `deployment.mdc`          |
| `lifecycle/supplementary.mdc`   | `workflows/`  | `code-review.mdc`         |
| `v4/v4-core-principles.mdc`     | `principles/` | `v4-core.mdc`             |
| `v4/v4-traceability.mdc`        | `principles/` | `v4-traceability.mdc`     |
| `v4/v4-contract-driven.mdc`     | `principles/` | `v4-contract-driven.mdc`  |
| `taskmaster/taskmaster.mdc`     | `tools/`      | `taskmaster.mdc`          |
| `taskmaster/dev_workflow.mdc`   | `tools/`      | `taskmaster-workflow.mdc` |
| `taskmaster/hamster.mdc`        | `tools/`      | `taskmaster-hamster.mdc`  |
| `code_quality.mdc`              | `quality/`    | `code-standards.mdc`      |
| `test_coverage.mdc`             | `quality/`    | `test-coverage.mdc`       |
| `security_scan.mdc`             | `quality/`    | `security.mdc`            |
| `compliance_workflow.mdc`       | `quality/`    | `compliance.mdc`          |
| `golden_test_protection.mdc`    | `quality/`    | `golden-tests.mdc`        |
| `django_split.mdc`              | `tech/`       | `django.mdc`              |
| `vue_component.mdc`             | `tech/`       | `vue.mdc`                 |
| `directory_guard.mdc`           | `tools/`      | `directory-guard.mdc`     |
| `project_startup.mdc`           | `workflows/`  | `project-setup.mdc`       |

### 阶段3：更新文件内容

1. **更新frontmatter**：

   - 更新 `description` 以反映新分类
   - 保持 `globs` 和 `priority` 不变
   - 更新 `alwaysApply` 如果需要

2. **更新内部引用**：

   - 更新所有 `@.cursor/rules/...` 引用
   - 更新 README.md 中的路径引用

3. **更新README.md**：
   - 更新目录结构说明
   - 更新分类说明
   - 更新快速导航

### 阶段4：验证和测试

1. 验证所有规则文件路径正确
2. 验证所有引用链接有效
3. 测试规则触发是否正常
4. 更新验证报告

## 🎨 命名规范详细说明

### 文件命名规则

1. **格式**：`{category}-{name}.mdc` 或 `{name}.mdc`（如果分类已通过目录体现）
2. **大小写**：全部小写，使用 kebab-case
3. **长度**：文件名不超过50个字符
4. **语义化**：文件名应该清晰表达规则内容

### 分类前缀规则

- `principle-` - 核心原则（可选，目录已体现）
- `workflow-` - 工作流程（可选，目录已体现）
- `role-` - 角色定义（可选，目录已体现）
- `tool-` - 工具相关（可选，目录已体现）
- `tech-` - 技术栈（可选，目录已体现）
- `quality-` - 质量保证（可选，目录已体现）

**建议**：由于已通过目录分类，文件名可以省略分类前缀，直接使用语义化名称。

## 📊 优先级重新规划

| 优先级 | 规则类型                       | 说明                        |
| ------ | ------------------------------ | --------------------------- |
| 1000   | `principles/`                  | 核心原则，alwaysApply: true |
| 950    | `tools/pre-commit.mdc`         | Pre-commit规则              |
| 900    | `roles/architect.mdc`          | 架构专家角色                |
| 850    | `roles/tester.mdc`             | 测试专家角色                |
| 800    | `roles/developer.mdc`          | 开发专家角色                |
| 750    | `workflows/development.mdc`    | 开发流程                    |
| 700    | `workflows/task-execution.mdc` | 任务执行流程                |
| 650    | `workflows/ci-cd.mdc`          | CI/CD流程                   |
| 600    | `workflows/debugging.mdc`      | 调试流程                    |
| 550    | `workflows/deployment.mdc`     | 部署流程                    |
| 500    | `tech/`, `quality/`            | 技术栈和质量规则            |

## ✅ 实施检查清单

- [ ] 创建新目录结构
- [ ] 迁移所有规则文件
- [ ] 更新所有文件frontmatter
- [ ] 更新所有内部引用
- [ ] 更新README.md
- [ ] 更新.cursorrules中的引用
- [ ] 验证所有规则触发正常
- [ ] 更新验证报告
- [ ] 删除旧目录和文件
- [ ] 提交变更并记录迁移历史

## 🔄 向后兼容

为了保持向后兼容，可以考虑：

1. **保留旧路径的符号链接**（如果系统支持）
2. **在README中说明迁移路径**
3. **在旧文件中添加重定向说明**

## 📚 参考

- Cursor Rules最佳实践：https://github.com/PatrickJS/awesome-cursorrules
- 项目V4架构文档：`docs/architecture/V4/`

## 📋 问题分析

### 当前问题

1. **命名不规范**：

   - 混用 kebab-case：`task-generation.mdc`, `prd-design.mdc`
   - 根目录文件命名不一致：`code_quality.mdc`, `django_split.mdc`, `compliance_workflow.mdc`
   - 缺少统一的命名规范

2. **文件夹分类混乱**：

   - `lifecycle/` - 概念模糊，包含工作流程、阶段、工具等混合内容
   - `v4/` - 应该属于核心原则，不应该单独分类
   - `roles/` - 这个分类合理
   - `taskmaster/` - 应该属于工具类
   - 根目录技术栈规则散乱

3. **组织逻辑不清晰**：
   - 按"生命周期"分类过于主观
   - 没有明确的分类维度
   - 历史规则和新规则混在一起

## 🎯 重构目标

### 1. 统一命名规范

**规则**：所有规则文件使用 `kebab-case`，格式为 `{category}-{name}.mdc`

**示例**：

- ✅ `workflow-prd-design.mdc`
- ✅ `workflow-task-generation.mdc`
- ✅ `principle-v4-core.mdc`
- ✅ `tech-django.mdc`
- ✅ `quality-code-standards.mdc`
- ❌ `task-generation.mdc` (缺少分类前缀)
- ❌ `code_quality.mdc` (使用下划线)

### 2. 按规则类型分类

**新的目录结构**：

```
.cursor/rules/
├── README.md                    # 规则索引和导航
├── principles/                  # 核心原则（最高优先级）
│   ├── v4-core.mdc             # V4架构核心原则
│   ├── v4-traceability.mdc     # 追溯链规则
│   ├── v4-contract-driven.mdc  # 契约驱动规则
│   └── docker-first.mdc        # Docker优先原则
├── workflows/                   # 工作流程规则
│   ├── prd-design.mdc          # PRD设计流程
│   ├── task-generation.mdc    # 任务生成流程
│   ├── task-execution.mdc     # 任务执行流程
│   ├── development.mdc        # 开发流程
│   ├── testing.mdc            # 测试流程
│   ├── debugging.mdc          # 调试流程
│   ├── code-review.mdc        # 代码审查流程
│   ├── ci-cd.mdc              # CI/CD流程
│   └── deployment.mdc         # 部署流程
├── roles/                       # 角色定义（保留）
│   ├── developer.mdc          # 开发专家
│   ├── tester.mdc             # 测试专家
│   ├── architect.mdc          # 架构专家
│   └── prd-designer.mdc       # PRD设计专家
├── tools/                       # 工具相关规则
│   ├── taskmaster.mdc         # Task-Master工具
│   ├── taskmaster-workflow.mdc # Task-Master工作流
│   ├── git-hooks.mdc          # Git Hooks规则
│   └── pre-commit.mdc         # Pre-commit规则
├── tech/                        # 技术栈特定规则
│   ├── django.mdc             # Django开发规则
│   ├── vue.mdc                # Vue开发规则
│   └── typescript.mdc         # TypeScript规则
└── quality/                     # 质量保证规则
    ├── code-standards.mdc     # 代码质量标准
    ├── test-coverage.mdc      # 测试覆盖率
    ├── security.mdc           # 安全规则
    ├── compliance.mdc         # 合规检查
    └── golden-tests.mdc       # 黄金测试保护
```

### 3. 分类维度说明

#### principles/ - 核心原则

- **特点**：最高优先级，alwaysApply: true
- **内容**：架构原则、设计原则、开发理念
- **示例**：V4五条铁律、Docker优先、TDD原则

#### workflows/ - 工作流程

- **特点**：按开发阶段组织，有明确的执行顺序
- **内容**：PRD设计→任务生成→开发→测试→部署
- **触发**：根据文件类型和操作阶段自动触发

#### roles/ - 角色定义

- **特点**：AI角色切换，根据任务类型自动切换
- **内容**：不同角色的职责、工作方式、Prompt模板
- **触发**：根据任务类型和上下文自动切换

#### tools/ - 工具相关

- **特点**：针对特定工具的使用规则
- **内容**：Task-Master、Git Hooks、Pre-commit等工具的使用规范
- **触发**：编辑相关工具配置文件时触发

#### tech/ - 技术栈

- **特点**：针对特定技术栈的编码规范
- **内容**：Django、Vue、TypeScript等技术的开发规范
- **触发**：编辑对应技术栈的文件时触发

#### quality/ - 质量保证

- **特点**：代码质量、测试、安全等质量相关规则
- **内容**：代码标准、测试覆盖率、安全扫描、合规检查
- **触发**：代码审查、测试、提交时触发

## 📝 迁移计划

### 阶段1：创建新目录结构

```bash
mkdir -p .cursor/rules/{principles,workflows,tools,tech,quality}
```

### 阶段2：文件迁移映射

| 原路径                          | 新路径        | 新文件名                  |
| ------------------------------- | ------------- | ------------------------- |
| `lifecycle/prd-design.mdc`      | `workflows/`  | `prd-design.mdc`          |
| `lifecycle/task-generation.mdc` | `workflows/`  | `task-generation.mdc`     |
| `lifecycle/task-execution.mdc`  | `workflows/`  | `task-execution.mdc`      |
| `lifecycle/development.mdc`     | `workflows/`  | `development.mdc`         |
| `lifecycle/testing.mdc`         | `workflows/`  | `testing.mdc`             |
| `lifecycle/debugging.mdc`       | `workflows/`  | `debugging.mdc`           |
| `lifecycle/pre-commit.mdc`      | `tools/`      | `pre-commit.mdc`          |
| `lifecycle/ci-cd.mdc`           | `workflows/`  | `ci-cd.mdc`               |
| `lifecycle/deployment.mdc`      | `workflows/`  | `deployment.mdc`          |
| `lifecycle/supplementary.mdc`   | `workflows/`  | `code-review.mdc`         |
| `v4/v4-core-principles.mdc`     | `principles/` | `v4-core.mdc`             |
| `v4/v4-traceability.mdc`        | `principles/` | `v4-traceability.mdc`     |
| `v4/v4-contract-driven.mdc`     | `principles/` | `v4-contract-driven.mdc`  |
| `taskmaster/taskmaster.mdc`     | `tools/`      | `taskmaster.mdc`          |
| `taskmaster/dev_workflow.mdc`   | `tools/`      | `taskmaster-workflow.mdc` |
| `taskmaster/hamster.mdc`        | `tools/`      | `taskmaster-hamster.mdc`  |
| `code_quality.mdc`              | `quality/`    | `code-standards.mdc`      |
| `test_coverage.mdc`             | `quality/`    | `test-coverage.mdc`       |
| `security_scan.mdc`             | `quality/`    | `security.mdc`            |
| `compliance_workflow.mdc`       | `quality/`    | `compliance.mdc`          |
| `golden_test_protection.mdc`    | `quality/`    | `golden-tests.mdc`        |
| `django_split.mdc`              | `tech/`       | `django.mdc`              |
| `vue_component.mdc`             | `tech/`       | `vue.mdc`                 |
| `directory_guard.mdc`           | `tools/`      | `directory-guard.mdc`     |
| `project_startup.mdc`           | `workflows/`  | `project-setup.mdc`       |

### 阶段3：更新文件内容

1. **更新frontmatter**：

   - 更新 `description` 以反映新分类
   - 保持 `globs` 和 `priority` 不变
   - 更新 `alwaysApply` 如果需要

2. **更新内部引用**：

   - 更新所有 `@.cursor/rules/...` 引用
   - 更新 README.md 中的路径引用

3. **更新README.md**：
   - 更新目录结构说明
   - 更新分类说明
   - 更新快速导航

### 阶段4：验证和测试

1. 验证所有规则文件路径正确
2. 验证所有引用链接有效
3. 测试规则触发是否正常
4. 更新验证报告

## 🎨 命名规范详细说明

### 文件命名规则

1. **格式**：`{category}-{name}.mdc` 或 `{name}.mdc`（如果分类已通过目录体现）
2. **大小写**：全部小写，使用 kebab-case
3. **长度**：文件名不超过50个字符
4. **语义化**：文件名应该清晰表达规则内容

### 分类前缀规则

- `principle-` - 核心原则（可选，目录已体现）
- `workflow-` - 工作流程（可选，目录已体现）
- `role-` - 角色定义（可选，目录已体现）
- `tool-` - 工具相关（可选，目录已体现）
- `tech-` - 技术栈（可选，目录已体现）
- `quality-` - 质量保证（可选，目录已体现）

**建议**：由于已通过目录分类，文件名可以省略分类前缀，直接使用语义化名称。

## 📊 优先级重新规划

| 优先级 | 规则类型                       | 说明                        |
| ------ | ------------------------------ | --------------------------- |
| 1000   | `principles/`                  | 核心原则，alwaysApply: true |
| 950    | `tools/pre-commit.mdc`         | Pre-commit规则              |
| 900    | `roles/architect.mdc`          | 架构专家角色                |
| 850    | `roles/tester.mdc`             | 测试专家角色                |
| 800    | `roles/developer.mdc`          | 开发专家角色                |
| 750    | `workflows/development.mdc`    | 开发流程                    |
| 700    | `workflows/task-execution.mdc` | 任务执行流程                |
| 650    | `workflows/ci-cd.mdc`          | CI/CD流程                   |
| 600    | `workflows/debugging.mdc`      | 调试流程                    |
| 550    | `workflows/deployment.mdc`     | 部署流程                    |
| 500    | `tech/`, `quality/`            | 技术栈和质量规则            |

## ✅ 实施检查清单

- [ ] 创建新目录结构
- [ ] 迁移所有规则文件
- [ ] 更新所有文件frontmatter
- [ ] 更新所有内部引用
- [ ] 更新README.md
- [ ] 更新.cursorrules中的引用
- [ ] 验证所有规则触发正常
- [ ] 更新验证报告
- [ ] 删除旧目录和文件
- [ ] 提交变更并记录迁移历史

## 🔄 向后兼容

为了保持向后兼容，可以考虑：

1. **保留旧路径的符号链接**（如果系统支持）
2. **在README中说明迁移路径**
3. **在旧文件中添加重定向说明**

## 📚 参考

- Cursor Rules最佳实践：https://github.com/PatrickJS/awesome-cursorrules
- 项目V4架构文档：`docs/architecture/V4/`
