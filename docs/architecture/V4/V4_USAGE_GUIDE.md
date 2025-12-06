# V4架构使用指南

> **版本**: V4.0
> **更新日期**: 2025-11-30

## 📋 目录

- [1. 快速开始](#1-快速开始)
- [2. 创建PRD](#2-创建prd)
- [3. 使用Task-Master生成任务](#3-使用task-master生成任务)
- [4. 执行开发流程](#4-执行开发流程)
- [5. 提交和验证](#5-提交和验证)
- [6. 常见问题](#6-常见问题)

---

## 1. 快速开始

### 1.1 验证安装

运行验证脚本：

```bash
bash scripts/setup/verify_installation.sh
```

### 1.2 查看示例

查看示例PRD：

```bash
cat docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md
```

---

## 2. 创建PRD

### 2.1 PRD文件结构

PRD文件必须包含：

1. **Frontmatter（YAML格式）**

   - `req_id`: 需求ID（格式：REQ-YYYY-NNN-slug）
   - `title`: 需求标题
   - `status`: 状态（draft, refined, reviewed, approved, implementing, completed, archived）
   - `test_files`: 测试文件列表
   - `implementation_files`: 实现文件列表
   - `api_contract`: API契约文件路径（可选）
   - `deletable`: 是否可删除

2. **内容部分**
   - 功能概述
   - 用户故事
   - 功能需求
   - 测试用例
   - 技术实现
   - 验收标准

### 2.2 创建PRD步骤

1. **创建目录**

   ```bash
   mkdir -p docs/00_product/requirements/REQ-2025-001-your-feature
   ```

2. **创建PRD文件**

   ```bash
   touch docs/00_product/requirements/REQ-2025-001-your-feature/REQ-2025-001-your-feature.md
   ```

3. **编写PRD内容**

   - 参考示例PRD：`docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md`
   - 确保包含所有必需的Frontmatter字段
   - 详细描述功能需求和测试用例

4. **创建API契约（如果需要）**
   ```bash
   mkdir -p docs/01_guideline/api-contracts/REQ-2025-001-your-feature
   touch docs/01_guideline/api-contracts/REQ-2025-001-your-feature/api.yaml
   ```

---

## 3. 使用Task-Master生成任务

### 3.1 精化PRD

在Cursor中精化PRD，补充：

- 数据库表设计
- Redis缓存策略
- API接口定义（OpenAPI格式）
- 测试用例详情
- 前端UI/UX细节

### 3.2 运行Task-Master

```bash
# 在容器内执行
docker-compose exec backend bash

# 解析PRD生成任务
task-master parse-prd docs/00_product/requirements/REQ-2025-001-your-feature/REQ-2025-001-your-feature.md --tag=REQ-2025-001-your-feature

# 分析任务复杂度
task-master analyze-complexity --tag=REQ-2025-001-your-feature --research

# 展开所有任务为子任务
task-master expand --all --tag=REQ-2025-001-your-feature --research
```

### 3.3 运行适配器

```bash
# 转换Task-Master输出为三层结构
python scripts/task-master/adapter.py REQ-2025-001-your-feature
```

这将：

- 生成Task-0自检任务
- 创建三层目录结构
- 生成task.md和subtask文件
- 关联测试文件和实现文件

---

## 4. 执行开发流程

### 4.1 查看任务列表

```bash
task-master list --tag=REQ-2025-001-your-feature
```

### 4.2 查看下一个任务

```bash
task-master next --tag=REQ-2025-001-your-feature
```

### 4.3 执行任务

1. **查看任务详情**

   ```bash
   task-master show 0 --tag=REQ-2025-001-your-feature
   ```

2. **开始任务**

   ```bash
   task-master set-status --id=0 --status=in-progress --tag=REQ-2025-001-your-feature
   ```

3. **执行子任务**

   - 阅读子任务文件：`.taskmaster/tasks/REQ-2025-001-your-feature/task-0-self-check/subtask-1-validate-prd-metadata.md`
   - 按照TDD流程：先写测试，再写代码
   - 运行测试确保通过

4. **完成子任务**

   ```bash
   task-master set-status --id=0.1 --status=done --tag=REQ-2025-001-your-feature
   ```

5. **完成任务**
   ```bash
   task-master set-status --id=0 --status=done --tag=REQ-2025-001-your-feature
   ```

---

## 5. 提交和验证

### 5.1 提交格式

使用V4格式提交：

```bash
git commit -m "[REQ-2025-001-your-feature] Task-1 Subtask-2 实现登录API"
```

或传统格式（仍然支持）：

```bash
git commit -m "feat(auth): add user login functionality"
```

### 5.2 提交验证

提交时会自动执行：

1. **Pre-commit检查**

   - 代码质量检查
   - V4合规引擎检查（第四层）

2. **Commit-msg检查**

   - 验证提交消息格式
   - 支持V4格式和传统格式

3. **Post-commit处理**
   - 记录到审计日志
   - 同步任务状态到PRD元数据

### 5.3 PR验证

创建PR后，GitHub Actions会自动：

1. 运行合规验证
2. 验证追溯链
3. 运行测试套件
4. 检查代码质量

---

## 6. 常见问题

### Q1: 合规检查失败怎么办？

**A**: 查看错误信息，常见问题：

- PRD元数据不完整：检查Frontmatter字段
- 测试文件缺失：确保测试文件存在
- 提交消息格式错误：使用正确的格式

### Q2: Task-Master适配器失败？

**A**: 检查：

- tasks.json是否存在
- REQ-ID是否正确
- 是否在容器内执行

### Q3: 状态同步失败？

**A**: 检查：

- PRD文件是否存在
- PRD Frontmatter格式是否正确
- 是否在容器内执行

### Q4: 如何在容器内执行？

**A**: 使用docker-compose：

```bash
# 进入后端容器
docker-compose exec backend bash

# 执行命令
python scripts/task-master/adapter.py REQ-2025-001-your-feature
```

### Q5: 如何禁用合规检查？

**A**: 不推荐，但如果必须：

- 修改`.compliance/config.yaml`中的`strict_mode: false`
- 或临时移除合规引擎调用（不推荐）

---

## 📚 相关文档

- [V4架构总览](./AI-WORKFLOW-V4-README.md)
- [PART1核心架构](./AI-WORKFLOW-V4-PART1-ARCH.md)
- [PART2 Task-Master集成](./AI-WORKFLOW-V4-PART2-TM-ADAPTER.md)
- [PART3 PRD与TRD标准](./AI-WORKFLOW-V4-PART3-PRD-TRD.md)
- [PART4 TDD体系](./AI-WORKFLOW-V4-PART4-TDD-TEST.md)
- [PART5合规引擎](./AI-WORKFLOW-V4-PART5-COMPLIANCE.md)
- [PART6实施手册](./AI-WORKFLOW-V4-PART6-IMPL.md)

---

## 🎯 下一步

1. 创建你的第一个PRD
2. 使用Task-Master生成任务
3. 开始开发并体验完整工作流
4. 遇到问题时参考常见问题部分
