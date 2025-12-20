# 规则文件分析报告

> **日期**: 2025-01-15
> **目标**: 检查规则文件是否符合职责单一、原子化原则，识别冗余和片面规则

---

## 📊 文件统计

### 文件数量和大小

- **总文件数**: 37个
- **总行数**: 6,477行
- **平均行数**: 175行
- **最大文件**: 
  - `intent-recognition.mdc`: 717行 (28KB)
  - `taskmaster-workflow.mdc`: 657行 (40KB)
  - `taskmaster-cli.mdc`: 487行 (33KB)
- **最小文件**: 
  - `v4-traceability.mdc`: 53行
  - `contract-testing.mdc`: 53行
  - `performance.mdc`: 20行

---

## 🔍 分析维度

### 1. 职责单一性检查

检查每个规则文件是否只负责一个明确的职责。

### 2. 原子化检查

检查规则文件是否足够小，是否可以被进一步拆分。

### 3. 冗余检查

检查是否有多个文件包含相同或相似的内容。

### 4. 片面性检查

检查是否有规则只覆盖部分场景，缺少完整的工作流程。

---

## 📋 详细分析

### 00-core/ (核心规则)

#### v4-core.mdc (208行)
- **职责**: V4架构核心设计原则
- **内容**: 
  - 核心信念（需求第一、代码即文档、浏览器验证）
  - 六条铁律（PRD先行、测试用例设计先行、测试代码先行、任务先行、修改PRD先行、不可绕过）
  - 追溯链要求
  - 产品文档是唯一真源
  - 契约驱动开发
  - 测试驱动开发 (TDD)
  - 五道防线保障
  - 目录结构强制规范
- **问题**: 
  - ⚠️ **职责不单一**：包含多个主题（核心信念、六条铁律、追溯链、TDD、契约驱动、五道防线、目录结构）
  - ⚠️ **与v4-traceability.mdc有重叠**：追溯链内容在两个文件中都有
  - ⚠️ **与development-workflow.mdc有重叠**：TDD内容在两个文件中都有
  - ⚠️ **与contract-testing.mdc有重叠**：契约驱动内容在两个文件中都有
- **建议**: 
  - 考虑拆分为：v4-principles.mdc（核心信念+六条铁律）+ v4-tdd.mdc（TDD工作流）+ v4-contract.mdc（契约驱动）
  - 追溯链内容应该只在v4-traceability.mdc中，v4-core.mdc只引用

#### intent-recognition.mdc (717行，28KB)
- **职责**: 意图识别与规则路由
- **内容**: 11种意图类型的识别和路由规则
  - PRD相关意图
  - 任务相关意图
  - 开发/实现相关意图
  - 测试相关意图
  - 提交/推送相关意图
  - 调试相关意图
  - API契约相关意图
  - 文档维护相关意图
  - 代码审查相关意图
  - 项目初始化相关意图
  - 架构相关意图
- **问题**:
  - ⚠️ **文件过大**：717行，28KB，包含所有意图类型的详细规则
  - ⚠️ **职责不单一**：既是路由层，又包含每个意图的详细规则
  - ⚠️ **不够原子化**：每个意图类型的规则可以独立成文件
  - ⚠️ **冗余啰嗦**：每个意图类型都有相似的格式和说明
- **建议**: 
  - 拆分为：intent-router.mdc（核心路由逻辑）+ intent-prd.mdc + intent-testing.mdc + intent-development.mdc等
  - 或者：保留intent-recognition.mdc作为路由表，详细规则移到对应的阶段目录

#### v4-traceability.mdc
- **职责**: 追溯链规则
- **内容**: 追溯链格式和实现
- **问题**: ✅ 职责单一，内容简洁

---

### 01-product/ (产品阶段)

#### prd-standards.mdc
- **职责**: PRD编写规范
- **内容**: PRD元数据标准、内容结构、角色切换
- **问题**: ✅ 职责单一

#### prd-refinement.mdc
- **职责**: PRD精化规则
- **内容**: 从raw文本到正式PRD的转换规则
- **问题**: ✅ 职责单一

---

### 02-testing/ (测试阶段)

#### test-case-standards.mdc
- **职责**: 测试用例编写规范
- **内容**: CSV格式、测试用例设计规则
- **问题**: ✅ 职责单一

#### test-case-review.mdc
- **职责**: 测试用例评审规则
- **内容**: 评审流程、评审标准
- **问题**: ✅ 职责单一

#### test-types.mdc
- **职责**: 测试类型规范
- **内容**: 单元测试、集成测试、E2E测试、回归测试
- **问题**: ✅ 职责单一

#### e2e-testing.mdc
- **职责**: E2E测试规则
- **内容**: E2E测试最佳实践、验证码测试等
- **问题**: ✅ 职责单一

#### contract-testing.mdc
- **职责**: 契约测试规则
- **内容**: API契约测试、Mock Server使用
- **问题**: ✅ 职责单一

#### golden-tests.mdc
- **职责**: 黄金测试保护规则
- **内容**: Golden Tests的保护机制
- **问题**: ✅ 职责单一

#### test-coverage.mdc
- **职责**: 测试覆盖率要求
- **内容**: 覆盖率标准、检查方法
- **问题**: ✅ 职责单一

---

### 03-taskmaster/ (任务管理)

#### task-generation.mdc
- **职责**: 任务生成规范
- **内容**: 如何解析PRD生成任务
- **问题**: ✅ 职责单一

#### taskmaster-cli.mdc
- **职责**: Task-Master CLI使用
- **内容**: CLI命令和参数
- **问题**: ✅ 职责单一

#### taskmaster-workflow.mdc (657行，40KB)
- **职责**: Task-Master工作流
- **内容**: 完整的工作流程、标签管理、进阶场景
- **问题**: 
  - ⚠️ **文件过大**：657行，40KB
  - ⚠️ **职责不单一**：包含工作流、标签管理、进阶场景、MCP vs CLI对比
  - ⚠️ **与taskmaster-cli.mdc有重叠**：都包含CLI命令说明
  - ⚠️ **冗余啰嗦**：包含大量示例和说明
- **建议**: 
  - 考虑拆分为：taskmaster-basic-workflow.mdc（基础循环）+ taskmaster-advanced.mdc（标签管理、进阶场景）
  - 或者精简内容，只保留核心工作流程

#### hamster-integration.mdc
- **职责**: Hamster集成
- **内容**: Hamster工具集成规则
- **问题**: ✅ 职责单一

---

### 04-development/ (开发阶段)

#### development-workflow.mdc (240行)
- **职责**: 开发工作流程
- **内容**: TDD流程、Docker容器化开发、REQ-ID注释、API契约遵循、代码质量、浏览器验证
- **问题**: 
  - ⚠️ **与v4-core.mdc有重叠**：TDD流程在两个文件中都有详细说明
  - ⚠️ **与task-execution.mdc有重叠**：都包含任务执行流程
  - ⚠️ **职责不够单一**：包含TDD、Docker、REQ-ID、API契约、代码质量、浏览器验证等多个主题
- **建议**: 
  - TDD流程应该只在v4-core.mdc中，development-workflow.mdc只引用
  - 或者拆分为：development-tdd.mdc + development-docker.mdc + development-standards.mdc

#### task-execution.mdc
- **职责**: 任务执行规则
- **内容**: 如何执行Task-Master任务
- **问题**: ✅ 职责单一

#### code-standards.mdc
- **职责**: 代码质量标准
- **内容**: 代码规范、命名约定
- **问题**: ✅ 职责单一

#### django-development.mdc
- **职责**: Django开发规范
- **内容**: Django特定的开发规则
- **问题**: ✅ 职责单一

#### vue-development.mdc
- **职责**: Vue开发规范
- **内容**: Vue/TS特定的开发规则
- **问题**: ✅ 职责单一

---

### 05-debugging/ (调试阶段)

#### debugging-methodology.mdc
- **职责**: 调试方法论
- **内容**: 3次失败原则、分层排查法
- **问题**: ✅ 职责单一

#### troubleshooting-checklist.mdc
- **职责**: 排查清单
- **内容**: PRD优先排查流程
- **问题**: ✅ 职责单一

---

### 06-cicd/ (CI/CD阶段)

#### pre-commit.mdc
- **职责**: Pre-commit规则
- **内容**: 四层检查体系
- **问题**: ✅ 职责单一

#### compliance.mdc
- **职责**: 合规检查
- **内容**: 合规警告主动修复
- **问题**: ✅ 职责单一

#### ci-workflow.mdc
- **职责**: CI工作流规则
- **内容**: CI流程规范
- **问题**: ✅ 职责单一

#### cd-workflow.mdc
- **职责**: CD部署规则
- **内容**: 部署流程规范
- **问题**: ✅ 职责单一

---

### 07-documentation/ (文档和配置)

#### documentation-standards.mdc
- **职责**: 文档规范
- **内容**: 禁止创建虚文档、文档格式要求
- **问题**: ✅ 职责单一

#### script-conventions.mdc
- **职责**: 脚本编写规范
- **内容**: Shell/Python脚本规范
- **问题**: ✅ 职责单一

---

### 08-project/ (项目公共)

#### project-setup.mdc
- **职责**: 项目初始化规则
- **内容**: 项目启动检查清单
- **问题**: ✅ 职责单一

---

### 09-roles/ (角色规则)

#### developer.mdc
- **职责**: 开发专家角色
- **内容**: 开发专家的职责和约束
- **问题**: ✅ 职责单一

#### tester.mdc
- **职责**: 测试专家角色
- **内容**: 测试专家的职责和约束
- **问题**: ✅ 职责单一

#### architect.mdc
- **职责**: 架构专家角色
- **内容**: 架构专家的职责和约束
- **问题**: ✅ 职责单一

#### prd-designer.mdc
- **职责**: PRD设计专家角色
- **内容**: PRD设计专家的职责和约束
- **问题**: ✅ 职责单一

---

### 1-quality/ (质量保障)

#### code-review.mdc
- **职责**: 代码审查规则
- **内容**: 代码审查检查清单
- **问题**: ✅ 职责单一

#### security.mdc
- **职责**: 安全规则
- **内容**: 安全开发规范
- **问题**: ✅ 职责单一

#### performance.mdc
- **职责**: 性能优化规则
- **内容**: 性能优化规范
- **问题**: ✅ 职责单一

---

### 10-tools/ (工具使用)

#### directory-guard.mdc
- **职责**: 目录守护工具
- **内容**: 目录保护规则
- **问题**: ✅ 职责单一

---

## ⚠️ 发现的问题

### 1. 文件过大问题（违反原子化原则）

| 文件 | 行数 | 大小 | 问题 |
|------|------|------|------|
| `intent-recognition.mdc` | 717行 | 28KB | 包含11种意图类型的详细规则，应该拆分 |
| `taskmaster-workflow.mdc` | 657行 | 40KB | 包含工作流、标签管理、进阶场景，应该拆分 |
| `taskmaster-cli.mdc` | 487行 | 33KB | CLI命令参考，内容详细但合理 |
| `test-types.mdc` | 394行 | 11KB | 包含TDD、四层测试体系、覆盖率等，可能可以拆分 |
| `prd-refinement.mdc` | 390行 | 7KB | PRD精化流程，内容详细但合理 |
| `troubleshooting-checklist.mdc` | 356行 | 11KB | 排查清单，内容详细但合理 |

**建议**: 
- `intent-recognition.mdc` 必须拆分（职责不单一）
- `taskmaster-workflow.mdc` 考虑拆分（内容过多）
- 其他文件虽然较大，但职责相对单一

### 2. 职责不单一问题

#### v4-core.mdc
- **问题**: 包含8个不同主题
  - 核心信念
  - 六条铁律
  - 追溯链要求（与v4-traceability.mdc重叠）
  - 产品文档是唯一真源
  - 契约驱动开发（与contract-testing.mdc重叠）
  - 测试驱动开发 (TDD)（与development-workflow.mdc重叠）
  - 五道防线保障
  - 目录结构强制规范
- **建议**: 拆分为多个文件

#### intent-recognition.mdc
- **问题**: 既是路由层，又包含每个意图的详细规则
- **建议**: 拆分为路由表 + 各意图详细规则

#### development-workflow.mdc
- **问题**: 包含TDD、Docker、REQ-ID、API契约、代码质量、浏览器验证等多个主题
- **建议**: 拆分为多个专门文件

### 3. 冗余内容问题

#### TDD内容重复
- `v4-core.mdc`: 包含TDD完整工作流（145-177行）
- `development-workflow.mdc`: 包含TDD开发流程（24-115行）
- `test-types.mdc`: 包含TDD三阶段循环（48-115行）
- `task-execution.mdc`: 包含TDD流程（117-132行）
- **问题**: TDD内容在4个文件中重复
- **建议**: 统一到一个文件（如v4-tdd.mdc），其他文件只引用

#### 追溯链内容重复
- `v4-core.mdc`: 包含追溯链要求（108-117行）
- `v4-traceability.mdc`: 包含追溯链格式和实现（完整文件）
- **问题**: 追溯链内容在两个文件中都有
- **建议**: v4-core.mdc只引用v4-traceability.mdc

#### 契约驱动内容重复
- `v4-core.mdc`: 包含契约驱动开发（133-143行）
- `contract-testing.mdc`: 包含V4契约驱动开发规则（完整文件）
- **问题**: 契约驱动内容在两个文件中都有
- **建议**: v4-core.mdc只引用contract-testing.mdc

#### REQ-ID注释要求重复
- `v4-core.mdc`: 提到REQ-ID注释（38行）
- `v4-traceability.mdc`: 包含REQ-ID注释格式（34-38行）
- `development-workflow.mdc`: 包含REQ-ID注释格式（102-125行）
- `task-execution.mdc`: 包含REQ-ID注释格式（179-202行）
- `compliance.mdc`: 包含REQ-ID注释修复方法（37-44行）
- **问题**: REQ-ID注释要求在5个文件中重复
- **建议**: 统一到v4-traceability.mdc，其他文件只引用

#### Docker容器化要求重复
- `v4-core.mdc`: 提到Docker（但内容较少）
- `development-workflow.mdc`: 包含Docker容器化开发（76-100行）
- `task-execution.mdc`: 包含Docker容器化开发约束（159-177行）
- `task-generation.mdc`: 包含Docker开发模式约束（48-52行）
- **问题**: Docker要求在4个文件中重复
- **建议**: 统一到一个文件（如development-docker.mdc），其他文件只引用

#### 测试用例设计流程重复
- `test-case-standards.mdc`: 包含测试用例设计流程（118-153行）
- `test-types.mdc`: 提到测试用例设计（但内容较少）
- `v4-core.mdc`: 提到测试用例设计先行（43-56行）
- **问题**: 测试用例设计流程在多个文件中重复
- **建议**: 统一到test-case-standards.mdc，其他文件只引用

#### 合规检查内容重复
- `pre-commit.mdc`: 包含合规警告主动修复（31-51行）
- `compliance.mdc`: 包含合规警告主动修复（完整文件）
- **问题**: 合规检查内容在两个文件中重复
- **建议**: 统一到compliance.mdc，pre-commit.mdc只引用

### 4. 片面性规则问题

#### test-case-review.mdc
- **问题**: 缺少frontmatter（description, globs, priority）
- **问题**: 内容只有184行，但缺少完整的评审流程说明
- **建议**: 补充frontmatter，完善评审流程

#### code-standards.mdc
- **问题**: 内容较简单（100行），只包含代码质量标准，缺少具体实施细节
- **建议**: 补充具体实施细节或合并到development-workflow.mdc

#### code-review.mdc
- **问题**: 内容过于简单（26行），只有检查清单，缺少审查流程和标准
- **建议**: 补充审查流程和标准

#### performance.mdc
- **问题**: 内容过于简单（20行），只有优化原则和检查清单，缺少具体优化方法
- **建议**: 补充具体优化方法或合并到其他文件

#### security.mdc
- **问题**: 内容较简单（67行），只包含安全扫描策略和工具，缺少具体安全开发规范
- **建议**: 补充具体安全开发规范

#### directory-guard.mdc
- **问题**: 内容过于简单（29行），只有禁止规则，缺少具体实施细节
- **建议**: 补充具体实施细节或合并到其他文件

---

## 📝 优化建议

### 1. 拆分大文件（原子化）

#### intent-recognition.mdc (717行 → 拆分)
**当前问题**: 包含11种意图类型的详细规则，职责不单一

**拆分方案**:
```
intent-recognition.mdc (核心路由，~100行)
  ├── intent-prd.mdc (PRD意图规则，~50行)
  ├── intent-testing.mdc (测试意图规则，~50行)
  ├── intent-development.mdc (开发意图规则，~50行)
  ├── intent-commit.mdc (提交意图规则，~50行)
  ├── intent-debugging.mdc (调试意图规则，~50行)
  └── ... (其他意图类型)
```

**或者**: 保留intent-recognition.mdc作为路由表（精简到~200行），详细规则移到对应的阶段目录

#### taskmaster-workflow.mdc (657行 → 拆分)
**当前问题**: 包含工作流、标签管理、进阶场景

**拆分方案**:
```
taskmaster-workflow.mdc (基础工作流，~200行)
  ├── taskmaster-advanced.mdc (标签管理、进阶场景，~300行)
  └── taskmaster-mcp-vs-cli.mdc (MCP vs CLI对比，~150行)
```

#### v4-core.mdc (208行 → 拆分)
**当前问题**: 包含8个不同主题

**拆分方案**:
```
v4-core.mdc (核心信念 + 六条铁律，~100行)
  ├── v4-tdd.mdc (TDD工作流，~80行) ← 从v4-core.mdc提取
  ├── v4-contract.mdc (契约驱动，~50行) ← 从v4-core.mdc提取
  └── v4-directory-structure.mdc (目录结构，~30行) ← 从v4-core.mdc提取
```

### 2. 消除冗余内容

#### TDD内容统一
**当前**: 4个文件包含TDD内容
- `v4-core.mdc`: TDD完整工作流
- `development-workflow.mdc`: TDD开发流程
- `test-types.mdc`: TDD三阶段循环
- `task-execution.mdc`: TDD流程

**优化方案**:
- 创建 `00-core/v4-tdd.mdc`，包含完整的TDD工作流
- 其他文件只引用，不重复内容

#### 追溯链内容统一
**当前**: 2个文件包含追溯链内容
- `v4-core.mdc`: 追溯链要求（108-117行）
- `v4-traceability.mdc`: 追溯链格式和实现（完整文件）

**优化方案**:
- `v4-core.mdc` 只保留一句话引用，详细内容在 `v4-traceability.mdc`

#### 契约驱动内容统一
**当前**: 2个文件包含契约驱动内容
- `v4-core.mdc`: 契约驱动开发（133-143行）
- `contract-testing.mdc`: V4契约驱动开发规则（完整文件）

**优化方案**:
- `v4-core.mdc` 只保留一句话引用，详细内容在 `contract-testing.mdc`

#### REQ-ID注释要求统一
**当前**: 5个文件包含REQ-ID注释要求
- `v4-core.mdc`: 提到REQ-ID注释
- `v4-traceability.mdc`: REQ-ID注释格式
- `development-workflow.mdc`: REQ-ID注释格式
- `task-execution.mdc`: REQ-ID注释格式
- `compliance.mdc`: REQ-ID注释修复方法

**优化方案**:
- 统一到 `v4-traceability.mdc`，其他文件只引用

#### Docker容器化要求统一
**当前**: 4个文件包含Docker要求
- `development-workflow.mdc`: Docker容器化开发
- `task-execution.mdc`: Docker容器化开发约束
- `task-generation.mdc`: Docker开发模式约束

**优化方案**:
- 创建 `00-core/containerization.mdc`，统一Docker开发规范
- 其他文件只引用

### 3. 补充片面规则

#### test-case-review.mdc
- **问题**: 缺少frontmatter
- **修复**: 添加完整的frontmatter

#### code-review.mdc
- **问题**: 内容过于简单（26行）
- **修复**: 补充审查流程、审查标准、审查记录

#### performance.mdc
- **问题**: 内容过于简单（20行）
- **修复**: 补充具体优化方法、性能测试工具、性能基准

#### security.mdc
- **问题**: 内容较简单（67行）
- **修复**: 补充具体安全开发规范、安全编码实践

#### directory-guard.mdc
- **问题**: 内容过于简单（29行）
- **修复**: 补充具体实施细节、违规处理流程

### 4. 职责单一化

#### development-workflow.mdc
**当前职责**: TDD流程、Docker、REQ-ID、API契约、代码质量、浏览器验证

**优化方案**:
```
development-workflow.mdc (开发工作流程，~100行)
  ├── development-tdd.mdc (TDD流程，引用v4-tdd.mdc)
  ├── development-docker.mdc (Docker开发，引用containerization.mdc)
  ├── development-standards.mdc (代码质量标准，引用code-standards.mdc)
  └── development-browser-verification.mdc (浏览器验证，~50行)
```

---

## 🔄 具体优化方案

### 优先级1: 必须优化（严重影响职责单一性）

1. **拆分intent-recognition.mdc** (717行)
   - 影响：职责不单一，文件过大
   - 方案：拆分为路由表 + 各意图详细规则

2. **拆分v4-core.mdc** (208行)
   - 影响：包含8个不同主题
   - 方案：拆分为核心原则 + TDD + 契约驱动 + 目录结构

3. **统一TDD内容**
   - 影响：4个文件重复TDD内容
   - 方案：创建v4-tdd.mdc，其他文件只引用

### 优先级2: 建议优化（有冗余但可接受）

4. **统一追溯链内容**
   - 影响：2个文件重复追溯链内容
   - 方案：v4-core.mdc只引用v4-traceability.mdc

5. **统一契约驱动内容**
   - 影响：2个文件重复契约驱动内容
   - 方案：v4-core.mdc只引用contract-testing.mdc

6. **统一REQ-ID注释要求**
   - 影响：5个文件重复REQ-ID注释要求
   - 方案：统一到v4-traceability.mdc

7. **统一Docker容器化要求**
   - 影响：4个文件重复Docker要求
   - 方案：创建containerization.mdc

### 优先级3: 可选优化（内容简单但可用）

8. **补充片面规则**
   - code-review.mdc: 补充审查流程
   - performance.mdc: 补充优化方法
   - security.mdc: 补充安全规范
   - directory-guard.mdc: 补充实施细节

---

## 📊 优化效果预估

### 文件数量变化
- **优化前**: 37个文件
- **优化后**: 约45-50个文件（拆分大文件，但消除冗余）

### 总行数变化
- **优化前**: 6,477行
- **优化后**: 约5,500-6,000行（消除冗余，但拆分后可能有少量新增说明）

### 职责单一性
- **优化前**: 约60%的文件职责单一
- **优化后**: 约90%的文件职责单一

### 冗余内容
- **优化前**: 约15-20%的内容重复
- **优化后**: 约5%的内容重复（必要的引用）

---

## ✅ 优化检查清单

### 职责单一性
- [ ] 每个文件只负责一个明确的职责
- [ ] 文件职责边界清晰，不重叠
- [ ] 相关主题通过引用关联，不重复内容

### 原子化
- [ ] 文件大小控制在300行以内（特殊情况可放宽到500行）
- [ ] 大文件已拆分为多个小文件
- [ ] 每个文件可以独立理解和维护

### 冗余消除
- [ ] TDD内容统一到一个文件
- [ ] 追溯链内容统一到一个文件
- [ ] 契约驱动内容统一到一个文件
- [ ] REQ-ID注释要求统一到一个文件
- [ ] Docker容器化要求统一到一个文件

### 片面性修复
- [ ] 所有规则都有完整的frontmatter
- [ ] 所有规则都有完整的工作流程
- [ ] 所有规则都有明确的输入和输出
- [ ] 所有规则都有参考文档链接
