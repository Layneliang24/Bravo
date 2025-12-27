# Cursor规则系统架构列表

> **版本**: V5
> **最后更新**: 2025-01-XX
> **规则总数**: 42个规则文件

---

## 📐 架构概览

### 三层架构设计

```
┌─────────────────────────────────────────────────┐
│  核心原则层 (AlwaysApply, 2个规则)             │
│  - v4-core.mdc (priority: 1000)                │
│  - intent-recognition.mdc (priority: 980)      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  意图路由层 (AlwaysApply, 1个规则)             │
│  - intent-recognition.mdc                       │
│  → 根据用户意图动态加载工作流程规则            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  工作流程层 (按需加载, 40个规则)               │
│  - 按阶段组织：产品→测试→任务→开发→...        │
│  - 通过意图路由或文件类型匹配触发              │
└─────────────────────────────────────────────────┘
```

### 目录结构

```
.cursor/rules/
├── 00-core/          (6个) - 核心原则
├── 01-product/       (2个) - 产品阶段
├── 02-testing/       (7个) - 测试阶段
├── 03-taskmaster/    (4个) - 任务管理阶段
├── 04-development/   (5个) - 开发阶段
├── 05-debugging/     (2个) - 调试阶段
├── 06-cicd/          (4个) - CI/CD阶段
├── 07-documentation/ (2个) - 文档维护
├── 08-project/       (1个) - 项目启动
├── 09-roles/         (4个) - 角色规则
├── 10-quality/       (3个) - 质量保障
├── 11-tools/         (1个) - 工具规则
├── README.md         - 规则索引文档
└── RULE_TEMPLATE.mdc - 规则模板
```

---

## 📋 详细规则列表

### 00-core/ 核心原则 (6个规则)

#### 1. v4-core.mdc

- **优先级**: 1000 (最高)
- **AlwaysApply**: ✅ 是
- **Globs**: `**/*`
- **核心内容**:
  - V4架构六条铁律
  - PRD先行、测试先行、任务先行、修改PRD先行、不可绕过
  - 追溯链要求
  - 产品文档是唯一真源
  - 契约驱动开发
  - 测试驱动开发(TDD)
  - 五道防线保障

#### 2. intent-recognition.mdc

- **优先级**: 980
- **AlwaysApply**: ✅ 是
- **Globs**: `**/*`
- **核心内容**:
  - 意图识别与规则路由机制
  - 13种意图类型定义（PRD、任务、开发、测试、提交、调试、API契约、文档、代码审查、项目初始化、架构、性能优化、安全）
  - 关键词匹配规则
  - 组合意图处理
  - 角色切换机制

#### 3. v4-traceability.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **核心内容**:
  - 追溯链格式：`REQ-ID → Task-ID → Test-File → Code-File → Commit → Deployment`
  - REQ-ID注释规范（Python/TypeScript/Vue）
  - 文件关联规则
  - 验证机制

#### 4. v4-tdd.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **核心内容**:
  - TDD三阶段循环（红→绿→重构）
  - 粒度与层级约定
  - 任务级别的TDD流程
  - 测试编写规范

#### 5. v4-directory-structure.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **核心内容**:
  - 目录结构强制规范
  - 文件组织规则
  - 命名约定

#### 6. v4-containerization.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **核心内容**:
  - Docker容器化开发规范
  - 开发环境要求
  - 容器内开发规则

---

### 01-product/ 产品阶段 (2个规则)

#### 1. prd-standards.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md`
- **触发意图**: PRD相关意图
- **核心内容**:
  - PRD设计标准
  - PRD元数据标准（req_id、status、priority等）
  - 关联文件字段（task_master_task、testcase_file等）
  - PRD状态流转
  - PRD内容结构要求
  - 数据库设计规范
  - API定义要求

#### 2. prd-refinement.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md`
- **触发意图**: PRD精化相关意图
- **核心内容**:
  - PRD精化规则
  - 原始需求处理流程
  - 需求分析步骤
  - 技术细节补充

---

### 02-testing/ 测试阶段 (7个规则)

#### 1. test-types.mdc

- **优先级**: 850
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/tests/**/*.py, frontend/**/__tests__/**/*.{ts,tsx,js,jsx}, e2e/tests/**/*.spec.ts`
- **触发意图**: 测试相关意图
- **核心内容**:
  - TDD三阶段循环（红→绿→重构）
  - 测试类型分类（unit、integration、e2e、regression）
  - 测试文件组织结构
  - 测试编写规范

#### 2. test-case-standards.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*-test-cases.csv`
- **触发意图**: 测试用例设计相关意图
- **核心内容**:
  - 测试用例CSV格式规范
  - 测试用例设计标准
  - 测试场景覆盖要求
  - 测试用例评审流程

#### 3. test-case-review.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*-test-cases.csv`
- **触发意图**: 测试用例评审相关意图
- **核心内容**:
  - 测试用例评审标准
  - 评审检查清单
  - 评审流程

#### 4. test-coverage.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 测试覆盖率相关意图
- **核心内容**:
  - 测试覆盖率要求（>= 80%）
  - 覆盖率检查方法
  - 覆盖率报告分析

#### 5. e2e-testing.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `e2e/tests/**/*.spec.ts`
- **触发意图**: E2E测试相关意图
- **核心内容**:
  - E2E测试编写规范
  - Playwright使用规范
  - E2E测试组织结构
  - 测试数据管理

#### 6. contract-testing.mdc

- **优先级**: 850
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: API契约相关意图
- **核心内容**:
  - API契约驱动开发
  - OpenAPI 3.0规范
  - 契约测试方法
  - Mock Server使用

#### 7. golden-tests.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 黄金测试相关意图
- **核心内容**:
  - 黄金测试保护机制
  - 快照测试规范
  - 回归测试要求

---

### 03-taskmaster/ 任务管理阶段 (4个规则)

#### 1. task-generation.mdc

- **优先级**: 800
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 任务生成相关意图
- **核心内容**:
  - Task-Master任务生成规则
  - PRD解析流程
  - 任务拆分标准
  - 任务结构规范

#### 2. taskmaster-workflow.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: Task-Master工作流相关意图
- **核心内容**:
  - Task-Master工作流程
  - 任务状态管理
  - 任务执行流程

#### 3. taskmaster-cli.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: Task-Master CLI相关意图
- **核心内容**:
  - Task-Master CLI命令使用
  - 命令参数说明
  - 常用操作流程

#### 4. hamster-integration.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: Hamster集成相关意图
- **核心内容**:
  - Hamster任务系统集成
  - 任务同步规则
  - Hamster CLI使用

---

### 04-development/ 开发阶段 (5个规则)

#### 1. development-workflow.mdc

- **优先级**: 750
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 开发相关意图
- **核心内容**:
  - TDD开发流程
  - Docker容器化开发
  - 代码文件REQ-ID注释
  - API实现遵循契约
  - 代码质量要求

#### 2. task-execution.mdc

- **优先级**: 700
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 任务执行相关意图
- **核心内容**:
  - 任务执行流程
  - 任务依赖检查
  - 任务完成标准
  - 代码提交规范

#### 3. code-standards.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 代码编写相关意图
- **核心内容**:
  - 代码质量标准
  - 代码风格规范
  - 命名约定
  - 代码组织规范

#### 4. django-development.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py`
- **触发意图**: Django开发相关意图
- **核心内容**:
  - Django开发规范
  - Django项目结构
  - Django最佳实践
  - Django测试规范

#### 5. vue-development.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: Vue开发相关意图
- **核心内容**:
  - Vue开发规范
  - TypeScript使用规范
  - Vue组件规范
  - 前端测试规范

---

### 05-debugging/ 调试阶段 (2个规则)

#### 1. debugging-methodology.mdc

- **优先级**: 600
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 调试相关意图
- **核心内容**:
  - 调试方法论
  - 问题定位流程
  - 日志分析规范
  - 调试工具使用

#### 2. troubleshooting-checklist.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 排查问题相关意图
- **核心内容**:
  - 排查检查清单
  - 常见问题解决方案
  - 系统性问题排查
  - 环境差异检查

---

### 06-cicd/ CI/CD阶段 (4个规则)

#### 1. pre-commit.mdc

- **优先级**: 950
- **AlwaysApply**: ❌ 否
- **Globs**: `**/*`
- **触发意图**: 提交代码相关意图
- **核心内容**:
  - Pre-commit四层检查体系
  - 依赖安全检查
  - 本地测试通行证验证
  - 代码质量检查
  - V4合规引擎检查
  - 合规警告主动修复

#### 2. compliance.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 合规检查相关意图
- **核心内容**:
  - 合规检查规则
  - 追溯链验证
  - PRD关联验证
  - 测试文件验证

#### 3. ci-workflow.mdc

- **优先级**: 650
- **AlwaysApply**: ❌ 否
- **Globs**: `.github/workflows/**/*.yml`
- **触发意图**: CI工作流相关意图
- **核心内容**:
  - CI工作流规范
  - GitHub Actions配置
  - CI检查流程
  - CI/CD集成规则

#### 4. cd-workflow.mdc

- **优先级**: 650
- **AlwaysApply**: ❌ 否
- **Globs**: `.github/workflows/**/*.yml`
- **触发意图**: CD工作流相关意图
- **核心内容**:
  - CD工作流规范
  - 部署流程
  - 部署验证
  - 回滚机制

---

### 07-documentation/ 文档维护 (2个规则)

#### 1. documentation-standards.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 文档维护相关意图
- **核心内容**:
  - 文档维护规则
  - 文档格式规范
  - 文档更新流程
  - 代码即文档原则

#### 2. script-conventions.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `scripts/**/*.sh, scripts/**/*.py`
- **触发意图**: 脚本编写相关意图
- **核心内容**:
  - 脚本编写规范
  - Shell脚本约定
  - Python脚本约定
  - 脚本命名规范

---

### 08-project/ 项目启动 (1个规则)

#### 1. project-setup.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 项目初始化相关意图
- **核心内容**:
  - 项目初始化规则
  - 环境配置检查
  - 目录结构确认
  - 技术栈确认
  - 开发环境设置

---

### 09-roles/ 角色规则 (4个规则)

#### 1. architect.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md, docs/01_guideline/api-contracts/**/*.yaml`
- **触发意图**: 架构相关意图
- **核心内容**:
  - 架构专家角色定义
  - PRD完整性验证
  - API契约设计验证
  - Task-0自检任务
  - 追溯链验证

#### 2. developer.mdc

- **优先级**: 800
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 开发相关意图
- **核心内容**:
  - 开发专家角色定义
  - TDD开发流程
  - 代码质量要求
  - 代码提交规范

#### 3. tester.mdc

- **优先级**: 850
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/tests/**/*.py, frontend/**/__tests__/**/*.{ts,tsx,js,jsx}, e2e/tests/**/*.spec.ts`
- **触发意图**: 测试相关意图
- **核心内容**:
  - 测试专家角色定义
  - 测试编写规范
  - 测试用例设计
  - 测试覆盖率要求

#### 4. prd-designer.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md`
- **触发意图**: PRD设计相关意图
- **核心内容**:
  - PRD设计专家角色定义
  - PRD设计标准
  - 需求分析流程
  - PRD精化规则

---

#### 1. code-review.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 代码审查相关意图
- **核心内容**:
  - 代码审查规则
  - 审查检查清单
  - 审查流程
  - 审查标准

#### 2. performance.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 性能优化相关意图
- **核心内容**:
  - 性能优化规则
  - 性能分析工具
  - 性能优化策略
  - 性能测试规范

#### 3. security.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 安全相关意图
- **核心内容**:
  - 安全规则
  - 安全审计标准
  - 安全漏洞检查
  - 安全最佳实践

---

### 10-quality/ 质量保障 (3个规则)

#### 1. code-review.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/**/*.py, frontend/**/*.{ts,tsx,js,jsx,vue}`
- **触发意图**: 代码审查相关意图
- **核心内容**:
  - 代码审查规则
  - 审查清单
  - 审查标准

#### 2. performance.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/**/*.{py}, frontend/**/*.{ts,tsx,js,jsx,vue}`
- **触发意图**: 性能优化相关意图
- **核心内容**:
  - 性能优化规则
  - 性能测试要求
  - 性能优化最佳实践

#### 3. security.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/**/*.py, frontend/**/*.{ts,tsx,js,jsx,vue}, .github/workflows/**/*.yml, ops/**/*.yml`
- **触发意图**: 安全检查相关意图
- **核心内容**:
  - 安全规则
  - 安全漏洞检查
  - 安全最佳实践

---

### 11-tools/ 工具规则 (1个规则)

#### 1. directory-guard.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 目录操作相关意图
- **核心内容**:
  - 目录守卫规则
  - 目录结构保护
  - 目录操作限制
  - 目录命名规范

---

## 🎯 规则优先级体系

### 优先级分层

| 优先级   | 规则类型   | 规则数量 | 说明                         |
| -------- | ---------- | -------- | ---------------------------- |
| **1000** | 核心原则   | 1个      | 最高优先级，总是生效         |
| **980**  | 意图路由   | 1个      | 路由层，总是生效             |
| **950**  | 提交前检查 | 1个      | Pre-commit强校验             |
| **900**  | 架构/PRD   | 3个      | 架构专家、PRD设计、PRD标准   |
| **850**  | 测试/契约  | 3个      | 测试专家、测试类型、契约测试 |
| **800**  | 开发/任务  | 2个      | 开发专家、任务生成           |
| **750**  | 开发工作流 | 1个      | 开发工作流                   |
| **700**  | 任务执行   | 1个      | 任务执行                     |
| **650**  | CI/CD      | 2个      | CI/CD工作流                  |
| **600**  | 调试       | 1个      | 调试方法论                   |
| **500**  | 质量/工具  | 4个      | 代码审查、性能、安全、工具   |

---

## 🔄 规则触发机制

### 1. AlwaysApply规则（2个）

这些规则总是生效，不依赖任何条件：

- `00-core/v4-core.mdc` (priority: 1000)
- `00-core/intent-recognition.mdc` (priority: 980)

### 2. 意图路由触发（推荐方式）

通过用户意图自动加载相应规则：

| 意图类型   | 触发关键词示例          | 加载的规则                                                    |
| ---------- | ----------------------- | ------------------------------------------------------------- |
| PRD设计    | "生成PRD"、"分析PRD"    | prd-standards.mdc + prd-designer.mdc + architect.mdc          |
| 任务生成   | "生成任务"、"parse-prd" | task-generation.mdc + taskmaster-workflow.mdc                 |
| 开发实现   | "实现功能"、"写代码"    | development-workflow.mdc + task-execution.mdc + developer.mdc |
| 测试编写   | "写测试"、"E2E"         | test-types.mdc + tester.mdc                                   |
| 提交代码   | "提交代码"、"commit"    | pre-commit.mdc + compliance.mdc + v4-traceability.mdc         |
| 调试问题   | "调试"、"排查问题"      | debugging-methodology.mdc + troubleshooting-checklist.mdc     |
| API契约    | "API契约"、"OpenAPI"    | contract-testing.mdc + architect.mdc                          |
| 文档维护   | "更新文档"、"写文档"    | documentation-standards.mdc                                   |
| 代码审查   | "代码审查"、"review"    | code-review.mdc                                               |
| 项目初始化 | "项目初始化"、"setup"   | project-setup.mdc                                             |
| 架构分析   | "架构"、"架构设计"      | architect.mdc + v4-core.mdc                                   |
| 性能优化   | "性能优化"、"优化性能"  | performance.mdc                                               |
| 安全检查   | "安全检查"、"安全漏洞"  | security.mdc                                                  |

### 3. 文件类型匹配触发（传统方式）

通过Globs模式匹配文件类型：

- 编辑 `.py` 文件 → 触发Django开发规则
- 编辑 `.vue` 文件 → 触发Vue开发规则
- 编辑 `**/tests/**/*.py` → 触发测试规则
- 编辑 `docs/00_product/requirements/**/*.md` → 触发PRD规则

---

## 📊 规则统计

### 按目录统计

| 目录             | 规则数量 | 占比     |
| ---------------- | -------- | -------- |
| 00-core          | 6个      | 14.3%    |
| 02-testing       | 7个      | 16.7%    |
| 04-development   | 5个      | 11.9%    |
| 03-taskmaster    | 4个      | 9.5%     |
| 06-cicd          | 4个      | 9.5%     |
| 09-roles         | 4个      | 9.5%     |
| 10-quality       | 3个      | 7.1%     |
| 01-product       | 2个      | 4.8%     |
| 05-debugging     | 2个      | 4.8%     |
| 07-documentation | 2个      | 4.8%     |
| 08-project       | 1个      | 2.4%     |
| 11-tools         | 1个      | 2.4%     |
| **总计**         | **42个** | **100%** |

### 按类型统计

| 规则类型     | 数量 | 说明               |
| ------------ | ---- | ------------------ |
| AlwaysApply  | 2个  | 总是生效的核心规则 |
| 角色规则     | 4个  | 定义AI角色职责     |
| 工作流程规则 | 36个 | 各阶段工作流程规则 |

---

## 🔗 规则依赖关系

### 核心依赖链

```
v4-core.mdc (核心原则)
  ↓
intent-recognition.mdc (意图路由)
  ↓
各阶段工作流程规则
  ├── 01-product/ (PRD设计)
  ├── 02-testing/ (测试)
  ├── 03-taskmaster/ (任务管理)
  ├── 04-development/ (开发)
  ├── 05-debugging/ (调试)
  ├── 06-cicd/ (CI/CD)
  └── ...
```

### 规则引用关系

- **v4-core.mdc** → 被所有规则引用（核心原则）
- **intent-recognition.mdc** → 引用所有工作流程规则（路由）
- **v4-tdd.mdc** → 被测试和开发规则引用
- **v4-traceability.mdc** → 被开发和CI/CD规则引用
- **v4-containerization.mdc** → 被开发规则引用

---

## 📝 规则编写规范

### Frontmatter格式

```yaml
---
description: 规则描述（一句话说明规则用途）
globs: **/*.py, **/*.ts        # 触发条件（Glob模式）
alwaysApply: true              # 是否总是应用（可选，默认false）
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

---

## ✅ 规则系统特点

### 1. 分层管理

- 核心原则层（alwaysApply）
- 意图路由层（alwaysApply）
- 工作流程层（按需加载）

### 2. 双重触发机制

- 意图路由（推荐，基于对话内容）
- 文件类型匹配（传统，基于文件类型）

### 3. 角色驱动

- 4个角色规则定义AI行为
- 自动角色切换机制

### 4. 优先级体系

- 12个优先级层级
- 确保规则加载顺序正确

### 5. 规则引用

- 规则间可相互引用
- 使用 `@.cursor/rules/...` 语法

---

## 📚 参考文档

- **规则索引**: `@.cursor/rules/README.md`
- **规则模板**: `@.cursor/rules/RULE_TEMPLATE.mdc`
- **V4架构文档**: `docs/architecture/V4/AI-WORKFLOW-V4-*.md`

---

## 🔄 更新日志

- **2025-01-XX**: 创建架构列表文档
- **V5架构**: 规则系统重组为阶段化目录结构
- **意图路由**: 新增13种意图类型支持
