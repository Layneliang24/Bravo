# Task0和PRD检查增强 - 快速参考

> **版本**: V2.0
> **更新日期**: 2025-12-03

---

## 🎯 核心变化

### Task0新增3项检查

| 检查项   | 级别    | 说明                    |
| -------- | ------- | ----------------------- |
| 任务排序 | WARNING | TDD流程：测试→编码→验证 |
| 任务展开 | WARNING | 复杂度>=5建议展开       |
| txt文件  | INFO    | Task Master文件生成     |

### PRD新增5项检查

| 检查项      | 级别    | 说明          |
| ----------- | ------- | ------------- |
| 验收标准    | ERROR   | 必需，至少3条 |
| 业务背景    | WARNING | 建议包含      |
| 数据库设计  | WARNING | 后端项目建议  |
| API接口定义 | WARNING | API项目建议   |
| 前端UI/UX   | WARNING | 前端项目建议  |

---

## 📋 PRD模板（新标准）

```markdown
---
req_id: REQ-YYYY-NNN-description
title: 功能标题
status: approved
test_files:
  - backend/tests/unit/test_xxx.py
implementation_files:
  - backend/apps/xxx/models.py
  - frontend/src/views/Xxx.vue
api_contract: docs/01_guideline/api-contracts/REQ-XXX/api.yaml
deletable: false
---

# 功能概述

简要说明功能是什么

# 业务背景 ⭐ 新增

为什么需要这个功能，解决什么问题

# 用户故事

作为...，我希望...，以便...

# 验收标准 ⭐ 新增（必需）

1. 可测试的标准1
2. 可测试的标准2
3. 可测试的标准3

# 数据库设计 ⭐ 新增（后端项目）

## 表名

| 字段 | 类型 | 说明 | 约束 |
| ---- | ---- | ---- | ---- |
| id   | UUID | 主键 | PK   |

# API接口定义 ⭐ 新增（API项目）

## GET /api/xxx

**请求**：...
**响应**：...

# 前端UI/UX设计 ⭐ 新增（前端项目）

## 页面结构

- 页面：Xxx.vue
- 组件：...

## 交互流程

1. 用户操作 → 系统响应

# 测试用例

TC-001: ...
```

---

## 🔧 Task Master最佳实践

### 任务结构（符合TDD）

```json
{
  "subtasks": [
    {
      "id": 1,
      "title": "编写测试用例", // ⭐ 第一步：测试
      "description": "TDD红色阶段"
    },
    {
      "id": 2,
      "title": "实现功能", // ⭐ 第二步：编码
      "description": "实现核心逻辑"
    },
    {
      "id": 3,
      "title": "运行测试验证", // ⭐ 第三步：验证
      "description": "TDD绿色阶段"
    }
  ]
}
```

### 任务展开命令

```bash
# 1. 分析复杂度
task-master analyze-complexity --research

# 2. 展开单个任务
task-master expand --id=1 --research

# 3. 批量展开
task-master expand --all --research

# 4. 生成txt文件
task-master generate
```

---

## ⚠️ 常见错误和修复

### 错误1：缺少验收标准

```
❌ 缺少必需章节: 验收标准

修复：在PRD中添加
# 验收标准
1. 用户可以...
2. 系统能够...
3. 数据正确...
```

### 错误2：任务未展开

```
⚠️ 任务 1 复杂度较高(8/10)，建议展开

修复：
task-master expand --id=1 --research
```

### 错误3：任务排序不符合TDD

```
⚠️ 建议第一个子任务应该是"编写测试"

修复：调整子任务顺序，确保：
1. 第一个子任务：编写测试
2. 中间子任务：实现功能
3. 最后子任务：运行测试验证
```

---

## 📊 检查级别说明

| 级别        | 说明         | 是否阻断      |
| ----------- | ------------ | ------------- |
| **ERROR**   | 基础质量要求 | ✅ 阻断提交   |
| **WARNING** | 最佳实践建议 | ⚠️ 警告但允许 |
| **INFO**    | 辅助信息     | ℹ️ 仅提示     |

---

## 🎯 快速检查清单

### 提交前自查

**PRD检查**：

- [ ] 包含所有必需章节
- [ ] 验收标准至少3条
- [ ] 根据项目类型添加相应章节
  - [ ] 后端项目：数据库设计
  - [ ] API项目：API接口定义
  - [ ] 前端项目：UI/UX设计

**Task Master检查**：

- [ ] 复杂任务已展开为子任务
- [ ] 第一个子任务是"编写测试"
- [ ] 已运行 `task-master generate`

---

**快速参考完成！** 📚

_Claude Sonnet 4.5 (claude-sonnet-4-20250514)_
