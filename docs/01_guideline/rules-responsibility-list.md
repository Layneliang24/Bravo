# Cursor规则职责范围和作用列表

> **版本**: V1.0
> **最后更新**: 2025-01-XX
> **规则总数**: 42个规则文件

---

## 📋 规则组织结构

本项目Cursor规则系统采用**分层管理 + 意图路由**策略，共42个规则文件，分为12个目录。

### 三层架构

```
核心原则层 (AlwaysApply, 2个规则)
  ↓
意图路由层 (AlwaysApply, 1个规则)
  ↓
工作流程层 (按需加载, 39个规则)
```

---

## 📚 规则详细列表

### 00-core/ 核心原则 (6个规则)

#### 1. v4-core.mdc

- **优先级**: 1000 (最高)
- **AlwaysApply**: ✅ 是
- **Globs**: `**/*`
- **职责范围**:
  - V4架构五条铁律（PRD先行、测试先行、任务先行、修改PRD先行、不可绕过）
  - 追溯链要求规范
  - 产品文档是唯一真源原则
  - 契约驱动开发原则
  - 测试驱动开发(TDD)原则
  - 五道防线保障体系
- **作用**: 定义项目的核心约束和不可违反的铁律，是所有其他规则的基础

#### 2. behavior-guidelines.mdc

- **优先级**: 990
- **AlwaysApply**: ✅ 是
- **Globs**: `**/*`
- **职责范围**:
  - AI行为准则（禁止创建虚文档、禁止随意创建脚本、不要过度解释）
  - 规则优先级约束
  - 规则执行优先级说明
- **作用**: 约束AI的行为方式，确保AI遵循正确的开发习惯

#### 3. intent-recognition.mdc

- **优先级**: 980
- **AlwaysApply**: ✅ 是
- **Globs**: `**/*`
- **职责范围**:
  - 意图识别与规则路由机制
  - 13种意图类型定义（PRD、任务、开发、测试、提交、调试、API契约、文档、代码审查、项目初始化、架构、性能优化、安全）
  - 关键词匹配规则
  - 组合意图处理
  - 角色切换机制
  - 意图识别失败降级机制
- **作用**: 根据用户意图动态加载相应的工作流程规则，实现智能路由

#### 4. v4-traceability.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **职责范围**:
  - 追溯链格式定义：`REQ-ID → Task-ID → Test-File → Code-File → Commit → Deployment`
  - REQ-ID注释规范（Python/TypeScript/Vue）
  - 文件关联规则
  - 追溯链验证机制
- **作用**: 确保代码变更可以追溯到原始需求，实现全生命周期追溯

#### 5. v4-tdd.mdc

- **优先级**: 950
- **AlwaysApply**: ❌ 否
- **Globs**: `**/*`
- **职责范围**:
  - TDD三阶段循环（红→绿→重构）详解
  - 粒度与层级约定（Task-Master场景）
  - 任务级别的TDD流程
  - 测试编写规范
- **作用**: 强制执行测试驱动开发流程，确保测试先行

#### 6. v4-directory-structure.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **职责范围**:
  - 目录结构强制规范
  - 文件组织规则
  - 命名约定
  - 目录层级要求
- **作用**: 确保项目目录结构符合V4架构规范

#### 7. v4-containerization.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **职责范围**:
  - Docker容器化开发规范
  - 开发环境要求（纯容器化，不使用本地环境）
  - 容器内开发规则
  - 服务端口映射规范
- **作用**: 确保开发环境一致，所有操作在容器内进行

---

### 01-product/ 产品阶段 (2个规则)

#### 1. prd-standards.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md`
- **触发意图**: PRD相关意图
- **职责范围**:
  - PRD设计标准和要求
  - PRD元数据标准（req_id、status、priority等）
  - PRD关联文件字段（task_master_task、testcase_file等）
  - PRD状态流转规则
  - PRD内容结构要求（功能概述、用户故事、验收标准等）
  - 数据库设计规范
  - API定义要求
- **作用**: 确保PRD文档符合V4标准，包含所有必需信息

#### 2. prd-refinement.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md`
- **触发意图**: PRD精化相关意图
- **职责范围**:
  - PRD精化规则和流程
  - 原始需求处理流程（从`.taskmaster/docs/`到标准PRD）
  - 需求分析步骤
  - 技术细节补充要求
- **作用**: 指导如何将原始需求精化为标准PRD文档

---

### 02-testing/ 测试阶段 (7个规则)

#### 1. test-types.mdc

- **优先级**: 850
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/tests/**/*.py, frontend/**/__tests__/**/*.{ts,tsx,js,jsx}, e2e/tests/**/*.spec.ts`
- **触发意图**: 测试相关意图
- **职责范围**:
  - TDD三阶段循环在测试中的应用（红→绿→重构）
  - 四层测试体系定义（unit、integration、e2e、regression）
  - 测试文件组织结构
  - 测试编写规范
  - 测试代码与CSV用例的对应规则
  - E2E测试环境差异验证（强制）
  - 系统状态验证测试（新增）
- **作用**: 定义测试类型和测试编写规范，确保测试覆盖完整

#### 2. test-case-standards.mdc

- **优先级**: 880
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*-test-cases.csv`
- **触发意图**: 测试用例设计相关意图
- **职责范围**:
  - 测试用例CSV格式规范
  - 测试用例设计标准
  - 用例ID命名规范（TC-{MODULE}\_{FEATURE}-{序号}）
  - 测试场景覆盖要求
  - 优先级定义（P0/P1/P2/P3）
  - 测试用例设计流程
  - PRD元数据更新要求
- **作用**: 确保测试用例设计完整、规范、可追溯

#### 3. test-case-review.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*-test-cases.csv`
- **触发意图**: 测试用例评审相关意图
- **职责范围**:
  - 测试用例评审标准
  - 评审检查清单（完整性、优先级、可追溯性、可执行性）
  - 评审流程和要求
- **作用**: 确保测试用例经过评审，质量符合要求

#### 4. test-coverage.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/tests/**/*.py, frontend/src/**/*.{spec.ts,spec.tsx,test.ts,test.tsx,test.js}, e2e/tests/**/*.spec.ts`
- **触发意图**: 测试覆盖率相关意图
- **职责范围**:
  - 测试覆盖率要求（后端≥85%，前端≥80%，E2E≥70%）
  - 分类覆盖率要求（单元测试≥90%，集成测试≥75%，API测试≥85%）
  - 覆盖率检查方法和工具
  - 覆盖率报告分析
- **作用**: 确保测试覆盖率符合要求

#### 5. e2e-testing.mdc

- **优先级**: 520
- **AlwaysApply**: ❌ 否
- **Globs**: `e2e/tests/**/*.spec.ts`
- **触发意图**: E2E测试相关意图
- **职责范围**:
  - E2E测试编写规范
  - Playwright使用规范
  - E2E测试组织结构
  - 测试数据管理
  - 验证码测试最佳实践（万能验证码、Mock网络请求）
  - 禁止事项（不要尝试识别真正的验证码）
- **作用**: 确保E2E测试稳定可靠，符合最佳实践

#### 6. contract-testing.mdc

- **优先级**: 850
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/01_guideline/api-contracts/**/*.yaml, backend/apps/**/*.py, frontend/src/api/**/*.{ts,js}`
- **触发意图**: API契约相关意图
- **职责范围**:
  - API契约驱动开发原则
  - OpenAPI 3.0规范要求
  - 契约测试方法
  - Mock Server使用（Prism）
  - 前后端并行开发流程
- **作用**: 确保前后端通过API契约并行开发，接口符合规范

#### 7. golden-tests.mdc

- **优先级**: 950
- **AlwaysApply**: ❌ 否
- **Globs**: `tests-golden/**/*, **/tests-golden/**/*`
- **触发意图**: 黄金测试相关意图
- **职责范围**:
  - 黄金测试保护机制（禁止AI修改）
  - 黄金测试选择标准
  - 保护机制说明（Git钩子、CI检查、分支保护）
  - 紧急情况处理流程
- **作用**: 保护核心业务逻辑测试不被误修改

---

### 03-taskmaster/ 任务管理阶段 (4个规则)

#### 1. task-generation.mdc

- **优先级**: 800
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 任务生成相关意图
- **职责范围**:
  - Task-Master任务生成规则
  - PRD解析流程
  - 任务拆分标准
  - 任务结构规范
  - 任务ID命名规范
- **作用**: 确保任务生成符合规范，结构清晰

#### 2. taskmaster-workflow.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: Task-Master工作流相关意图
- **职责范围**:
  - Task-Master工作流程
  - 任务状态管理
  - 任务执行流程
  - 任务状态同步规则
- **作用**: 定义Task-Master任务管理的完整工作流

#### 3. taskmaster-cli.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: Task-Master CLI相关意图
- **职责范围**:
  - Task-Master CLI命令使用规范
  - 命令参数说明
  - 常用操作流程
- **作用**: 指导如何正确使用Task-Master CLI工具

#### 4. hamster-integration.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: Hamster集成相关意图
- **职责范围**:
  - Hamster任务系统集成规则
  - 任务同步规则
  - Hamster CLI使用规范
- **作用**: 定义Hamster任务系统的集成和使用规范

---

### 04-development/ 开发阶段 (5个规则)

#### 1. development-workflow.mdc

- **优先级**: 750
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 开发相关意图
- **职责范围**:
  - TDD开发流程
  - Docker容器化开发要求
  - 代码文件REQ-ID注释要求
  - API实现遵循契约要求
  - 代码质量要求
  - 开发环境规范
- **作用**: 定义开发阶段的工作流程和质量要求

#### 2. task-execution.mdc

- **优先级**: 700
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 任务执行相关意图
- **职责范围**:
  - 任务执行流程
  - 任务依赖检查
  - 任务完成标准
  - 代码提交规范
  - 任务状态更新规则
- **作用**: 定义任务执行的标准流程和要求

#### 3. code-standards.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 代码编写相关意图
- **职责范围**:
  - 代码质量标准
  - 代码风格规范
  - 命名约定
  - 代码组织规范
  - 代码可读性要求
- **作用**: 确保代码质量符合项目标准

#### 4. django-development.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py`
- **触发意图**: Django开发相关意图
- **职责范围**:
  - Django开发规范
  - Django项目结构要求
  - Django最佳实践
  - Django测试规范
  - Django模型、视图、序列化器规范
- **作用**: 定义Django后端的开发规范

#### 5. vue-development.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: Vue开发相关意图
- **职责范围**:
  - Vue开发规范
  - TypeScript使用规范
  - Vue组件规范
  - 前端测试规范
  - Vue最佳实践
- **作用**: 定义Vue前端的开发规范

---

### 05-debugging/ 调试阶段 (2个规则)

#### 1. debugging-methodology.mdc

- **优先级**: 600
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 调试相关意图
- **职责范围**:
  - 调试方法论
  - 问题定位流程
  - 日志分析规范
  - 调试工具使用
  - 抽象层次识别
- **作用**: 提供系统化的调试方法和流程

#### 2. troubleshooting-checklist.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 排查问题相关意图
- **职责范围**:
  - 排查检查清单
  - 常见问题解决方案
  - 系统性问题排查方法
  - 环境差异检查
  - 多维验证策略
- **作用**: 提供完整的问题排查检查清单和方法

---

### 06-cicd/ CI/CD阶段 (4个规则)

#### 1. pre-commit.mdc

- **优先级**: 950
- **AlwaysApply**: ❌ 否
- **Globs**: `**/*`
- **触发意图**: 提交代码相关意图
- **职责范围**:
  - Pre-commit四层检查体系
  - 依赖安全检查
  - 本地测试通行证验证
  - 代码质量检查
  - V4合规引擎检查
  - 合规警告主动修复
  - 禁止使用`--no-verify`
- **作用**: 在提交前进行全面的合规和质量检查

#### 2. compliance.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 合规检查相关意图
- **职责范围**:
  - 合规检查规则
  - 追溯链验证
  - PRD关联验证
  - 测试文件验证
  - 合规警告主动修复工作流程
- **作用**: 确保代码符合V4合规要求

#### 3. ci-workflow.mdc

- **优先级**: 650
- **AlwaysApply**: ❌ 否
- **Globs**: `.github/workflows/**/*.yml`
- **触发意图**: CI工作流相关意图
- **职责范围**:
  - CI工作流规范
  - GitHub Actions配置要求
  - CI检查流程
  - CI/CD集成规则
  - 测试执行要求
- **作用**: 定义CI持续集成的工作流规范

#### 4. cd-workflow.mdc

- **优先级**: 650
- **AlwaysApply**: ❌ 否
- **Globs**: `.github/workflows/**/*.yml`
- **触发意图**: CD工作流相关意图
- **职责范围**:
  - CD工作流规范
  - 部署流程要求
  - 部署验证规则
  - 回滚机制
  - 环境管理规范
- **作用**: 定义CD持续部署的工作流规范

#### 5. version-control.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 版本控制相关意图
- **职责范围**:
  - Git提交消息格式规范
  - 分支管理规范
  - PR流程规范
  - 版本控制最佳实践
- **作用**: 确保版本控制操作符合规范

---

### 07-documentation/ 文档维护 (2个规则)

#### 1. documentation-standards.mdc

- **优先级**: 960
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/**/*.md, scripts/**/*.{sh,py}`
- **触发意图**: 文档维护相关意图
- **职责范围**:
  - 文档维护规则
  - 文档格式规范
  - 文档更新流程
  - 代码即文档原则
  - 禁止创建虚文档规则
  - 允许的文档类型定义
- **作用**: 确保文档质量，避免创建无用文档

#### 2. script-conventions.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: `scripts/**/*.sh, scripts/**/*.py`
- **触发意图**: 脚本编写相关意图
- **职责范围**:
  - 脚本编写规范
  - Shell脚本约定
  - Python脚本约定
  - 脚本命名规范
  - 禁止创建临时脚本规则
- **作用**: 确保脚本代码质量，避免脚本滥用

---

### 08-project/ 项目启动 (1个规则)

#### 1. project-setup.mdc

- **优先级**: 默认
- **AlwaysApply**: ❌ 否
- **Globs**: 通过意图路由触发
- **触发意图**: 项目初始化相关意图
- **职责范围**:
  - 项目初始化规则
  - 环境配置检查
  - 目录结构确认
  - 技术栈确认
  - 开发环境设置
- **作用**: 指导项目初始化的标准流程

---

### 09-roles/ 角色规则 (4个规则)

#### 1. architect.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md, docs/01_guideline/api-contracts/**/*.yaml`
- **触发意图**: 架构相关意图
- **职责范围**:
  - 架构专家角色定义
  - PRD完整性验证
  - API契约设计验证
  - Task-0自检任务
  - 追溯链验证
  - 架构设计原则
- **作用**: 定义架构专家的职责和行为规范

#### 2. developer.mdc

- **优先级**: 800
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/apps/**/*.py, frontend/src/**/*.{ts,tsx,vue,js,jsx}`
- **触发意图**: 开发相关意图
- **职责范围**:
  - 开发专家角色定义
  - TDD开发流程
  - 代码质量要求
  - 代码提交规范
  - 任务执行规范
- **作用**: 定义开发专家的职责和行为规范

#### 3. tester.mdc

- **优先级**: 850
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/tests/**/*.py, frontend/**/__tests__/**/*.{ts,tsx,js,jsx}, e2e/tests/**/*.spec.ts`
- **触发意图**: 测试相关意图
- **职责范围**:
  - 测试专家角色定义
  - 测试编写规范
  - 测试用例设计
  - 测试覆盖率要求
  - 测试策略质疑机制
- **作用**: 定义测试专家的职责和行为规范

#### 4. prd-designer.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `docs/00_product/requirements/**/*.md`
- **触发意图**: PRD设计相关意图
- **职责范围**:
  - PRD设计专家角色定义
  - PRD设计标准
  - 需求分析流程
  - PRD精化规则
- **作用**: 定义PRD设计专家的职责和行为规范

---

### 10-quality/ 质量保障 (3个规则)

#### 1. code-review.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/**/*.py, frontend/**/*.{ts,tsx,js,jsx,vue}`
- **触发意图**: 代码审查相关意图
- **职责范围**:
  - 代码审查规则
  - 审查检查清单
  - 审查流程
  - 审查标准
- **作用**: 定义代码审查的标准和流程

#### 2. performance.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/**/*.{py}, frontend/**/*.{ts,tsx,js,jsx,vue}`
- **触发意图**: 性能优化相关意图
- **职责范围**:
  - 性能优化规则
  - 性能测试要求
  - 性能优化最佳实践
  - 性能分析工具使用
- **作用**: 定义性能优化的标准和最佳实践

#### 3. security.mdc

- **优先级**: 500
- **AlwaysApply**: ❌ 否
- **Globs**: `backend/**/*.py, frontend/**/*.{ts,tsx,js,jsx,vue}, .github/workflows/**/*.yml, ops/**/*.yml`
- **触发意图**: 安全检查相关意图
- **职责范围**:
  - 安全规则
  - 安全漏洞检查
  - 安全最佳实践
  - 安全审计标准
- **作用**: 确保代码安全性，防止安全漏洞

---

### 11-tools/ 工具规则 (1个规则)

#### 1. directory-guard.mdc

- **优先级**: 900
- **AlwaysApply**: ❌ 否
- **Globs**: `./**/*.{md,txt}, ./**/*test*.py, ./**/*_test.py`
- **触发意图**: 目录操作相关意图
- **职责范围**:
  - 目录守卫规则
  - 根目录禁止新增文件类型
  - 文件放置规则（文档、测试、脚本等）
  - 允许的根目录文件列表
  - 违规处理机制
- **作用**: 保护项目目录结构，防止文件随意放置

---

## 🎯 规则优先级体系

### 优先级分层

| 优先级   | 规则类型        | 规则数量 | 说明                                 |
| -------- | --------------- | -------- | ------------------------------------ |
| **1000** | 核心原则        | 1个      | 最高优先级，总是生效                 |
| **990**  | 行为准则        | 1个      | AI行为约束，总是生效                 |
| **980**  | 意图路由        | 1个      | 路由层，总是生效                     |
| **950**  | 提交前检查/保护 | 3个      | Pre-commit强校验、TDD、黄金测试保护  |
| **900**  | 架构/PRD/目录   | 4个      | 架构专家、PRD设计、PRD标准、目录守卫 |
| **880**  | 测试用例设计    | 1个      | 测试用例标准                         |
| **850**  | 测试/契约       | 3个      | 测试专家、测试类型、契约测试         |
| **800**  | 开发/任务       | 2个      | 开发专家、任务生成                   |
| **750**  | 开发工作流      | 1个      | 开发工作流                           |
| **700**  | 任务执行        | 1个      | 任务执行                             |
| **650**  | CI/CD           | 2个      | CI/CD工作流                          |
| **600**  | 调试            | 1个      | 调试方法论                           |
| **500**  | 质量/工具       | 4个      | 代码审查、性能、安全、测试覆盖率     |

---

## 🔄 规则触发机制

### 1. AlwaysApply规则（2个）

这些规则总是生效，不依赖任何条件：

- `00-core/v4-core.mdc` (priority: 1000)
- `00-core/behavior-guidelines.mdc` (priority: 990)
- `00-core/intent-recognition.mdc` (priority: 980)

### 2. 意图路由触发（推荐方式）

通过用户意图自动加载相应规则，即使文件还没打开也会生效。

### 3. 文件类型匹配触发（传统方式）

通过Globs模式匹配文件类型，编辑特定文件时触发。

---

## 📊 规则统计

### 按目录统计

| 目录             | 规则数量 | 占比     |
| ---------------- | -------- | -------- |
| 00-core          | 7个      | 16.7%    |
| 02-testing       | 7个      | 16.7%    |
| 04-development   | 5个      | 11.9%    |
| 03-taskmaster    | 4个      | 9.5%     |
| 06-cicd          | 5个      | 11.9%    |
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
| AlwaysApply  | 3个  | 总是生效的核心规则 |
| 角色规则     | 4个  | 定义AI角色职责     |
| 工作流程规则 | 35个 | 各阶段工作流程规则 |

---

## 🔗 规则依赖关系

### 核心依赖链

```
v4-core.mdc (核心原则)
  ↓
behavior-guidelines.mdc (行为准则)
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

---

## 📚 参考文档

- **规则索引**: `@.cursor/rules/README.md`
- **规则架构列表**: `@.cursor/rules/ARCHITECTURE_LIST.md`
- **规则模板**: `@.cursor/rules/RULE_TEMPLATE.mdc`
- **V4架构文档**: `docs/architecture/V4/AI-WORKFLOW-V4-*.md`

---

## 🔄 更新日志

- **2025-01-XX**: 创建规则职责列表文档
- **V5架构**: 规则系统重组为阶段化目录结构
- **意图路由**: 新增13种意图类型支持
