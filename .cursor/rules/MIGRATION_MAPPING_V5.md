# V5架构迁移映射表

> **基于**: `docs/architecture/CURSOR_RULES_ARCHITECTURE_V5.md` > **状态**: 执行中

---

## 📋 文件迁移映射

### 00-core/ (核心规则)

| 源文件                             | 目标文件                         | 说明                       |
| ---------------------------------- | -------------------------------- | -------------------------- |
| `principles/v4-core.mdc`           | `00-core/v4-core.mdc`            | V4核心宪法                 |
| `workflows/intent-recognition.mdc` | `00-core/intent-recognition.mdc` | 意图路由（大脑）           |
| `principles/v4-traceability.mdc`   | `00-core/v4-traceability.mdc`    | 追溯链规则                 |
| -                                  | `00-core/containerization.mdc`   | Docker容器化规则（需创建） |
| -                                  | `00-core/tdd-workflow.mdc`       | TDD工作流（需创建）        |

### 01-product/ (产品阶段)

| 源文件                         | 目标文件                              | 说明                   |
| ------------------------------ | ------------------------------------- | ---------------------- |
| `workflows/prd-design.mdc`     | `01-product/prd-standards.mdc`        | PRD编写规范            |
| `workflows/prd-refinement.mdc` | `01-product/prd-refinement.mdc`       | PRD精化规则            |
| -                              | `01-product/prototype-extraction.mdc` | 原型提取（需创建）     |
| -                              | `01-product/logic-details.mdc`        | 逻辑细节规范（需创建） |

### 02-testing/ (测试阶段)

| 源文件                              | 目标文件                             | 说明             |
| ----------------------------------- | ------------------------------------ | ---------------- |
| `workflows/testcase-design.mdc`     | `02-testing/test-case-standards.mdc` | 测试用例编写规范 |
| `workflows/testcase-review.mdc`     | `02-testing/test-case-review.mdc`    | 测试用例评审     |
| `workflows/e2e.mdc`                 | `02-testing/e2e-testing.mdc`         | E2E测试规则      |
| `quality/testing.mdc`               | `02-testing/test-types.mdc`          | 测试类型规范     |
| `quality/golden-tests.mdc`          | `02-testing/golden-tests.mdc`        | 黄金测试保护     |
| `quality/test-coverage.mdc`         | `02-testing/test-coverage.mdc`       | 测试覆盖率       |
| `principles/v4-contract-driven.mdc` | `02-testing/contract-testing.mdc`    | 契约测试         |

### 03-taskmaster/ (任务管理)

| 源文件                          | 目标文件                                | 说明                   |
| ------------------------------- | --------------------------------------- | ---------------------- |
| `workflows/task-generation.mdc` | `03-taskmaster/task-generation.mdc`     | 任务生成规范           |
| `tools/taskmaster.mdc`          | `03-taskmaster/taskmaster-cli.mdc`      | Task-Master CLI        |
| `tools/taskmaster-workflow.mdc` | `03-taskmaster/taskmaster-workflow.mdc` | Task-Master工作流      |
| `tools/taskmaster-hamster.mdc`  | `03-taskmaster/hamster-integration.mdc` | Hamster集成            |
| -                               | `03-taskmaster/task-metadata.mdc`       | 任务元数据（需创建）   |
| -                               | `03-taskmaster/txt-generation.mdc`      | 任务文本生成（需创建） |

### 04-development/ (开发阶段)

| 源文件                              | 目标文件                                  | 说明                    |
| ----------------------------------- | ----------------------------------------- | ----------------------- |
| `workflows/development.mdc`         | `04-development/development-workflow.mdc` | 开发工作流程            |
| `workflows/task-execution.mdc`      | `04-development/task-execution.mdc`       | 任务执行规则            |
| `tech/django.mdc`                   | `04-development/django-development.mdc`   | Django开发规范          |
| `tech/vue.mdc`                      | `04-development/vue-development.mdc`      | Vue开发规范             |
| `quality/code-standards.mdc`        | `04-development/code-standards.mdc`       | 代码质量标准            |
| `principles/v4-contract-driven.mdc` | `04-development/api-contracts.mdc`        | API契约规范（部分内容） |

### 05-debugging/ (调试阶段)

| 源文件                                     | 目标文件                                     | 说明       |
| ------------------------------------------ | -------------------------------------------- | ---------- |
| `workflows/debugging.mdc`                  | `05-debugging/debugging-methodology.mdc`     | 调试方法论 |
| `workflows/bug-investigation-priority.mdc` | `05-debugging/troubleshooting-checklist.mdc` | 排查清单   |

### 06-cicd/ (CI/CD阶段)

| 源文件                     | 目标文件                  | 说明                 |
| -------------------------- | ------------------------- | -------------------- |
| `tools/pre-commit.mdc`     | `06-cicd/pre-commit.mdc`  | Pre-commit规则       |
| `workflows/ci-cd.mdc`      | `06-cicd/ci-workflow.mdc` | CI工作流             |
| `workflows/deployment.mdc` | `06-cicd/cd-workflow.mdc` | CD部署规则           |
| `quality/compliance.mdc`   | `06-cicd/compliance.mdc`  | 合规检查             |
| -                          | `06-cicd/commit.mdc`      | 提交规则（需创建）   |
| -                          | `06-cicd/local-pass.mdc`  | 本地通行证（需创建） |

### 07-documentation/ (文档和配置)

| 源文件                        | 目标文件                                       | 说明               |
| ----------------------------- | ---------------------------------------------- | ------------------ |
| `workflows/documentation.mdc` | `07-documentation/documentation-standards.mdc` | 文档规范           |
| `tools/scripts.mdc`           | `07-documentation/script-conventions.mdc`      | 脚本编写规范       |
| -                             | `07-documentation/config-management.mdc`       | 配置管理（需创建） |

### 08-project/ (项目公共)

| 源文件                        | 目标文件                             | 说明               |
| ----------------------------- | ------------------------------------ | ------------------ |
| `workflows/project-setup.mdc` | `08-project/project-setup.mdc`       | 项目初始化         |
| -                             | `08-project/project-background.mdc`  | 项目背景（需创建） |
| -                             | `08-project/directory-structure.mdc` | 目录结构（需创建） |
| -                             | `08-project/naming-conventions.mdc`  | 命名约定（需创建） |

### 09-roles/ (角色规则)

| 源文件                   | 目标文件                    | 说明                       |
| ------------------------ | --------------------------- | -------------------------- |
| `roles/developer.mdc`    | `09-roles/developer.mdc`    | 开发专家                   |
| `roles/tester.mdc`       | `09-roles/tester.mdc`       | 测试专家                   |
| `roles/architect.mdc`    | `09-roles/architect.mdc`    | 架构专家                   |
| `roles/prd-designer.mdc` | `09-roles/prd-designer.mdc` | PRD设计专家                |
| -                        | `09-roles/devops.mdc`       | DevOps专家（需创建，可选） |

### 10-tools/ (工具使用)

| 源文件                      | 目标文件                         | 说明                  |
| --------------------------- | -------------------------------- | --------------------- |
| `tools/directory-guard.mdc` | `10-tools/directory-guard.mdc`   | 目录守护工具          |
| -                           | `10-tools/mcp-tools.mdc`         | MCP工具使用（需创建） |
| -                           | `10-tools/third-party-tools.mdc` | 第三方工具（需创建）  |

### 1-quality/ (质量保障 - 横向贯穿)

| 源文件                      | 目标文件                    | 说明     |
| --------------------------- | --------------------------- | -------- |
| `quality/security.mdc`      | `1-quality/security.mdc`    | 安全规则 |
| `quality/performance.mdc`   | `1-quality/performance.mdc` | 性能优化 |
| `workflows/code-review.mdc` | `1-quality/code-review.mdc` | 代码审查 |

---

## 📝 迁移步骤

1. ✅ 创建目录结构
2. ⏳ 移动文件到新目录
3. ⏳ 更新文件中的引用路径
4. ⏳ 更新intent-recognition.mdc中的引用
5. ⏳ 验证规则加载
6. ⏳ 删除旧目录

---

## ⚠️ 注意事项

- 保持文件内容不变，只移动位置
- 更新所有@引用路径
- 保持frontmatter中的globs和priority
- 验证迁移后规则正常工作
