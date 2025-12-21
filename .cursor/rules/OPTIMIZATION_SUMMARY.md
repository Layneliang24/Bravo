# Cursor规则架构优化总结

> **日期**: 2025-01-15
> **目标**: 优化规则系统，避免冲突和规则遗忘

---

## ✅ 已完成的优化

### 1. 减少alwaysApply规则数量

**优化前**: 6个alwaysApply规则

- `v4-core.mdc` (priority: 1000) ✅ 保留
- `intent-recognition.mdc` (priority: 980) ✅ 保留
- `compliance.mdc` (priority: 960) ❌ 移除
- `documentation.mdc` (priority: 960) ❌ 移除
- `bug-investigation-priority.mdc` ❌ 移除
- `taskmaster-workflow.mdc` ❌ 移除

**优化后**: 2个alwaysApply规则

- `v4-core.mdc` (priority: 1000, alwaysApply: true) ✅ 核心宪法
- `intent-recognition.mdc` (priority: 980, alwaysApply: true) ✅ 路由层

**影响**: 减少了约66%的alwaysApply规则，显著降低上下文占用

---

### 2. 优化Glob Patterns

**优化前**: 多个规则使用过于宽泛的 `globs: **/*`

**优化后**:

- `documentation.mdc`: `globs: docs/**/*.md, scripts/**/*.{sh,py}` (精确匹配)
- `project-setup.mdc`: `globs: README.md, package.json, docker-compose.yml, Makefile` (精确匹配)
- `taskmaster-workflow.mdc`: `globs: .taskmaster/**/*.{json,md}` (精确匹配)
- `bug-investigation-priority.mdc`: 改为通过意图路由加载
- `compliance.mdc`: 改为通过意图路由在提交时加载

**影响**: 规则只在需要时加载，避免不必要的上下文占用

---

### 3. 调整优先级

**优化**:

- `compliance.mdc`: priority 960 → 950 (保持高优先级，但不alwaysApply)
- 其他规则保持原有优先级

**优先级层级**:

```
1000: v4-core (核心宪法，alwaysApply)
 980: intent-recognition (路由层，alwaysApply)
 950: compliance, pre-commit (提交前强制检查，按需加载)
 900: PRD设计、架构设计
 850: 测试、Task-Master
 800: 开发、任务执行
 700: CI/CD、部署
 600: 调试、代码审查
 500: 文档、工具使用
 400: 角色提示词
```

---

## 📊 优化效果

### Token占用估算

**优化前**（alwaysApply规则）:

- v4-core: ~8K tokens
- intent-recognition: ~15K tokens
- compliance: ~5K tokens
- documentation: ~3K tokens
- bug-investigation-priority: ~9K tokens
- taskmaster-workflow: ~15K tokens
- **总计**: ~55K tokens（总是加载）

**优化后**（alwaysApply规则）:

- v4-core: ~8K tokens
- intent-recognition: ~15K tokens
- **总计**: ~23K tokens（总是加载）

**节省**: ~32K tokens（58%减少）

### 按场景加载规则

**场景1：编写测试用例**

- 总是加载: v4-core, intent-recognition (~23K)
- 意图路由加载: test-case-writing, tester (~6K)
- **总计**: ~29K tokens

**场景2：提交代码**

- 总是加载: v4-core, intent-recognition (~23K)
- 意图路由加载: pre-commit, compliance (~8K)
- **总计**: ~31K tokens

**场景3：开发代码**

- 总是加载: v4-core, intent-recognition (~23K)
- Glob匹配加载: development-workflow, code-standards, developer (~10K)
- **总计**: ~33K tokens

---

## 🔍 仍需要优化的项目

### 1. 规则文件大小

**大文件**:

- `intent-recognition.mdc`: 713行（过大，建议拆分）
- `taskmaster-workflow.mdc`: 657行（建议拆分）

**建议**:

- 考虑将intent-recognition拆分为核心路由 + 各意图处理
- taskmaster-workflow可能需要拆分

### 2. Glob Patterns优化

**仍使用 `**/\*` 的规则\*\*:

- `v4-core.mdc` (必需，核心规则)
- `intent-recognition.mdc` (必需，路由规则)
- `debugging.mdc` (可能需要优化)

**建议**: 评估是否可以将debugging.mdc改为通过意图路由加载

### 3. 规则优先级验证

**需要验证**:

- 是否有相同优先级的规则冲突
- 优先级分配是否合理

---

## 📝 下一步优化建议

1. **拆分大文件**:

   - intent-recognition.mdc拆分为核心路由 + 意图处理器
   - taskmaster-workflow.mdc考虑拆分

2. **创建规则冲突检测脚本**:

   - 检查alwaysApply规则数量
   - 检查优先级冲突
   - 检查glob patterns优化

3. **文档化规则依赖关系**:
   - 明确规则之间的引用关系
   - 避免循环依赖

---

## ✅ 检查清单

- [x] 移除不必要的alwaysApply规则
- [x] 优化glob patterns
- [x] 调整优先级
- [ ] 拆分大文件（intent-recognition.mdc, taskmaster-workflow.mdc）
- [ ] 创建规则冲突检测脚本
- [ ] 验证规则优先级无冲突
