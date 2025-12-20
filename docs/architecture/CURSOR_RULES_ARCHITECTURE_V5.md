# Cursor Rules Architecture V5 - 扁平化意图驱动架构

> **版本**: V5.0
> **状态**: 规划中 (Planning)
> **目标**: 基于11个核心领域重组规则，消除规则冲突，保持上下文清晰

---

## 🏗️ 架构概览

为了解决规则冲突和上下文遗忘问题，采用 **"扁平化目录 + 意图路由 + 核心强制"** 的架构设计的 V5 版本。

### 核心设计理念

1.  **数字前缀目录 (00-10)**：强制排序，确保心理模型清晰，避免目录深层嵌套。
2.  **意图路由 (Router)**：保留并增强 `intent-recognition.mdc`，将其作为规则系统的"大脑"，负责根据用户 prompt 动态加载特定领域的规则。
3.  **核心分离 (Core Split)**：
    - `00-core`：包含绝对不可违反的"宪法" (alwaysApply: true)。
    - 其他目录：默认按需加载 (alwaysApply: false)，由文件 glob 或意图路由触发。
4.  **角色解耦 (Roles)**：将角色提示语 (`09-roles`) 与具体规则分离，允许动态组合（例如：`架构师角色` + `测试规则`）。

---

## 📂 目录结构设计

新架构将 `.cursor/rules/` 扁平化为以下 11 个目录：

```
.cursor/rules/
├── 00-core/                  # 核心规则 (TDD, V4, 容器化, 意图识别)
├── 01-product/               # 产品 (PRD, 逻辑细节, 原型)
├── 02-testing/               # 测试 (用例, 黄金测试, 契约)
├── 03-taskmaster/            # 任务管理 (Task-Master规范, 任务生成)
├── 04-development/           # 开发 (编码规范, API文档, Tech Stack)
├── 05-debugging/             # 调试 (排查技巧, 调试规则)
├── 06-cicd/                  # CI/CD (通行证, 提交, 推送)
├── 07-docs-scripts/          # 文档与脚本 (配置规则, 脚本规范)
├── 08-common/                # 公共 (项目配置, 架构目录)
├── 09-roles/                 # 角色 (前端专家, 测试专家等)
└── 10-tools/                 # 工具 (MCP, 包管理)
```

---

## 📝 详细目录映射与规则定义

### 00-core/ (核心规则)

> **特点**: 优先级最高 (Priority: 1000)，部分规则 alwaysApply。

- `intent-recognition.mdc`: **关键路由**，监控用户意图并加载其他目录规则。
- `v4-core.mdc`: V4 架构五条铁律 (PRD先行, 测试先行等)。
- `containerization.mdc`: Docker 开发环境强制规则。
- `tdd-workflow.mdc`: 红-绿-重构核心流程。

### 01-product/ (产品)

> **特点**: 由 "PRD", "需求" 等词触发，或打开 `.md` (PRD目录) 时触发。

- `prd-standards.mdc`: PRD编写规范（Frontmatter, 章节结构）。
- `prototype-extraction.mdc`: 从原型提取代码的规则。
- `logic-details.mdc`: 业务逻辑描述规范。

### 02-testing/ (测试)

> **特点**: 由 "测试", "Test" 触发，或打开 `test_*.py`, `*.spec.ts` 触发。

- `test-case-standards.mdc`: 测试用例编写规范 (AAA模式)。
- `e2e-testing.mdc`: E2E测试规则。
- `golden-tests.mdc`: 黄金测试集保护规则。
- `contract-testing.mdc`: API契约测试规则。

### 03-taskmaster/ (任务管理)

> **特点**: 由 "任务", "Task", "parse-prd" 触发。

- `task-generation.mdc`: 如何解析PRD生成任务。
- `task-metadata.mdc`: 父子任务元数据填规范。
- `txt-generation.mdc`: 任务文本文件生成规则。

### 04-development/ (开发)

> **特点**: 由 "开发", "实现" 触发，或打开代码文件触发。

- `backend-django.mdc`: Django开发规范。
- `frontend-vue.mdc`: Vue/TS开发规范。
- `api-documentation.mdc`: 代码注释与文档生成。

### 05-debugging/ (调试)

> **特点**: 由 "报错", "调试", "Bug" 触发。

- `debug-protocol.mdc`: 3次失败原则，分层排查法。
- `troubleshooting-tips.mdc`: 常见问题快速修复。

### 06-cicd/ (CI/CD)

> **特点**: 由 "提交", "Commit", "Push" 触发。

- `git-passport.mdc`: 提交前通行证检查 (TaskID, REQ-ID)。
- `commit-standards.mdc`: 提交信息规范。

### 07-docs-scripts/ (文档与脚本)

> **特点**: 由 "文档", "脚本" 触发，或打开 `scripts/` 目录触发。

- `documentation-standards.mdc`: Markdown编写规范。
- `script-config.mdc`: Shell/Python脚本编写与配置规范。

### 08-common/ (公共)

> **特点**: 提供项目上下文，通常按需加载。

- `project-structure.mdc`: 项目目录结构说明。
- `project-background.mdc`: 项目背景知识。

### 09-roles/ (角色)

> **特点**: 纯提示词 (System Prompts)，不包含硬性技术约束。

- `frontend-expert.mdc`: "你是一名前端专家..."
- `backend-expert.mdc`
- `qa-engineer.mdc`
- `architect.mdc`

### 10-tools/ (工具)

> **特点**: 特定工具使用指南。

- `mcp-tools.mdc`: 如何使用已安装的 MCP 工具。
- `package-management.mdc`: npm/pip 使用规范 (容器内执行)。

---

## 🛡️ 冲突预防策略

为了防止 Cursor 上下文溢出或规则冲突，采取以下策略：

1.  **Glob 严格隔离**：

    - 02-testing 规则 **仅** 对 `*test*`, `*spec*` 文件生效，绝不污染正常开发文件。
    - 06-cicd 规则 **仅** 在意图识别到 "提交" 时加载，平时开发不加载。

2.  **Intent Router (大脑)**：

    - `00-core/intent-recognition.mdc` 是唯一 alwaysApply 的路由规则。
    - 它负责根据用户输入（如 "我要写测试"），显式在 Context 中提及："应用规则 @02-testing/test-case-standards.mdc"。
    - **原理**：Cursor 模型看到 @引用 时，会临时给予该文件更高的注意力权重。

3.  **规则原子化**：
    - 每个 `.mdc` 文件控制在 2KB 以内。
    - 避免一个巨型 `development.mdc`，拆分为 `backend-django.mdc` 和 `frontend-vue.mdc`。

## 🔄 迁移计划

1.  **创建目录结构**：创建 `00-core` 到 `10-tools` 文件夹。
2.  **移动与重命名**：
    - `principles/*` -> `00-core/`
    - `workflows/testing.mdc` -> `02-testing/test-case-standards.mdc`
    - `tech/django.mdc` -> `04-development/backend-django.mdc`
    - (以此类推...)
3.  **更新 Router**：修改 `intent-recognition.mdc` 中的引用路径，指向新的目录结构。
4.  **验证**：通过对话测试各场景（"生成任务", "写测试"）是否触发正确规则。
