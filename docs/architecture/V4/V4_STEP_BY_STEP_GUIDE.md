# V4架构分步实施指南

> **创建日期**: 2025-11-30
> **目标**: 在现有项目基础上逐步实施V4架构，避免破坏现有工作流

## 🎯 实施原则

1. **不覆盖现有配置**: 所有新配置与现有配置共存
2. **渐进式启用**: 先创建目录和文件，再逐步启用规则
3. **向后兼容**: 确保现有工作流不受影响
4. **测试验证**: 每个阶段完成后进行验证

## 📋 阶段概览

| 阶段     | 内容              | 时间   | 状态   |
| -------- | ----------------- | ------ | ------ |
| ✅ 阶段1 | 创建基础目录结构  | 5分钟  | 已完成 |
| ⏳ 阶段2 | 配置合规引擎      | 15分钟 | 进行中 |
| ⏸️ 阶段3 | Task-Master适配层 | 10分钟 | 待开始 |
| ⏸️ 阶段4 | Git Hooks集成     | 10分钟 | 待开始 |
| ⏸️ 阶段5 | CI/CD集成         | 10分钟 | 待开始 |
| ⏸️ 阶段6 | 创建示例和文档    | 5分钟  | 待开始 |

---

## ✅ 阶段1: 创建基础目录结构（已完成）

### 已创建的目录

```
docs/00_product/requirements/     # PRD需求文档
docs/01_guideline/api-contracts/   # API契约
backend/tests/regression/          # 回归测试
backend/tests/fixtures/            # 测试数据
e2e/tests/smoke/                   # 冒烟测试
e2e/tests/regression/             # E2E回归测试
e2e/tests/performance/             # 性能测试
.compliance/rules/                 # 合规规则定义
.compliance/checkers/              # 合规检查器
scripts/task-master/               # Task-Master适配层
scripts/compliance/                # 合规检查脚本
scripts/setup/                     # 安装脚本
.githooks/                         # Git Hooks（与.husky共存）
```

---

## ⏳ 阶段2: 配置合规引擎

### 2.1 创建全局配置文件

**文件**: `.compliance/config.yaml`

需要创建的内容：

- 引擎配置（版本、严格模式、审计日志）
- 规则加载配置
- 检查器配置
- 绕过机制配置
- 文件路径映射
- 排除路径

### 2.2 创建规则文件

需要创建的规则文件：

- `.compliance/rules/prd.yaml` - PRD规则
- `.compliance/rules/test.yaml` - 测试规则
- `.compliance/rules/code.yaml` - 代码规则
- `.compliance/rules/commit.yaml` - 提交规则
- `.compliance/rules/task.yaml` - 任务规则

### 2.3 创建检查器插件

需要创建的检查器：

- `.compliance/checkers/__init__.py`
- `.compliance/checkers/prd_checker.py`
- `.compliance/checkers/test_checker.py`
- `.compliance/checkers/code_checker.py`
- `.compliance/checkers/commit_checker.py`
- `.compliance/checkers/task_checker.py`

### 2.4 创建引擎核心

需要创建的核心文件：

- `.compliance/engine.py` - 规则引擎核心
- `.compliance/runner.py` - Pre-commit入口

### 2.5 创建审计日志

- `.compliance/audit.log` - 审计日志文件（空文件）

---

## ⏸️ 阶段3: Task-Master适配层

### 3.1 创建适配器

**文件**: `scripts/task-master/adapter.py`

功能：

- 读取Task-Master生成的tasks.json
- 转换为三层目录结构
- 创建task-{N}-{slug}/目录
- 生成task.md和subtask文件

### 3.2 创建状态同步脚本

**文件**: `scripts/task-master/sync_status.py`

功能：

- 同步任务状态到PRD元数据
- 更新追溯链
- 验证任务完成度

---

## ⏸️ 阶段4: Git Hooks集成

### 4.1 更新Pre-commit Hook

**文件**: `.husky/pre-commit`（现有文件，需要添加）

添加内容：

- 在现有检查后调用合规引擎
- 调用`.compliance/runner.py`

### 4.2 更新Commit-msg Hook

**文件**: `.husky/commit-msg`（现有文件，需要更新）

更新内容：

- 支持REQ-ID格式验证
- 格式：`[REQ-YYYY-NNN-slug] Task-X 描述`

### 4.3 更新Post-commit Hook

**文件**: `.husky/post-commit`（现有文件，需要添加）

添加内容：

- 记录提交到审计日志
- 更新追溯链

---

## ⏸️ 阶段5: CI/CD集成

### 5.1 在PR验证中添加合规检查

**文件**: `.github/workflows/on-pr.yml`（现有文件，需要添加）

添加内容：

- 添加合规验证步骤
- 验证PRD、测试、代码关联
- 验证追溯链完整性

### 5.2 添加自动回滚机制

**文件**: `.github/workflows/on-push-dev.yml`（现有文件，需要添加）

添加内容：

- 检测未授权的功能删除
- 自动回滚机制

---

## ⏸️ 阶段6: 创建示例和文档

### 6.1 创建示例PRD

**文件**: `docs/00_product/requirements/REQ-2025-EXAMPLE-demo/REQ-2025-EXAMPLE-demo.md`

内容：

- 完整的PRD模板
- 包含所有必需元数据
- 示例测试用例

### 6.2 创建使用指南

**文件**: `docs/architecture/V4/V4_USAGE_GUIDE.md`

内容：

- 如何创建PRD
- 如何使用Task-Master
- 如何执行开发流程

### 6.3 创建验证脚本

**文件**: `scripts/setup/verify_installation.sh`

功能：

- 验证所有目录是否存在
- 验证所有配置文件是否存在
- 验证Git Hooks是否正确配置

---

## 🔧 下一步操作

### 立即执行

1. **阶段2**: 创建合规引擎配置文件

   ```bash
   # 我将为您创建所有必需的配置文件
   ```

2. **验证阶段1**: 确认所有目录已创建
   ```bash
   ls -la docs/00_product/requirements/
   ls -la .compliance/
   ```

### 后续步骤

按照阶段顺序逐步实施，每个阶段完成后进行验证。

---

## ⚠️ 重要提醒

1. **不删除现有文件**: 所有新文件与现有文件共存
2. **测试每个阶段**: 每个阶段完成后运行验证脚本
3. **渐进式启用**: 先创建文件，再逐步启用规则
4. **备份重要配置**: 在修改现有文件前先备份
