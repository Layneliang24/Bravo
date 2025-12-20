# Task-0自动生成触发方式

> **文档日期**: 2025-01-15
> **说明**: 如何触发Task-0的自动生成

---

## 🎯 触发方式

### ⭐ 方式1：真正的自动生成（推荐）✅✅

**使用项目包装脚本 `scripts/task-master-parse-prd.sh`**：

该脚本在parse-prd成功后**自动生成Task-0**，无需额外命令：

```bash
# 使用包装脚本（真正的自动化）
bash scripts/task-master-parse-prd.sh \
  docs/00_product/requirements/REQ-2025-003-user-login/REQ-2025-003-user-login.md \
  --tag REQ-2025-003-user-login

# 输出示例：
# [步骤1/6] 检查PRD文件...
# [步骤2/6] 验证PRD状态...
# [步骤3/6] 执行task-master parse-prd...
# [步骤4/6] 记录PRD路径到tasks.json metadata...
# [步骤5/6] 自动生成Task-0...  ⭐ 自动执行，无需手动
# [步骤6/6] 更新PRD状态...
```

**或创建alias后使用**：

```bash
# 创建alias（可选，更便捷）
alias tm-parse='bash scripts/task-master-parse-prd.sh'

# 然后正常使用
tm-parse <prd-file> --tag <tag-name>
```

**优点**：

- ✅ **真正的自动化**：parse-prd后自动生成Task-0，无需手动执行额外命令
- ✅ 集成到现有工作流中
- ✅ 自动检测REQ-ID（从--tag参数或PRD文件路径）

### 方式2：手动执行（不推荐，仅备用）⚠️

如果必须使用原生`task-master parse-prd`命令，则需要手动运行：

```bash
# 1. 执行原生parse-prd
task-master parse-prd <prd-file> --tag <tag-name>

# 2. 手动生成Task-0（需要记住这一步）
python scripts/task-master/adapter.py <REQ-ID>
```

**不推荐的原因**：

- ❌ 需要手动执行额外命令
- ❌ 容易遗漏步骤
- ❌ 不是真正的自动化

### 方式3：集成到MCP工具（待实现）⚠️

**理想情况**：在MCP的`parse_prd`工具中自动调用

**当前状态**：❌ 未实现，但可以使用包装脚本实现相同效果

---

## 📋 完整工作流示例

### 新PRD的标准流程

```bash
# 步骤1: 解析PRD生成任务
task-master parse-prd \
  docs/00_product/requirements/REQ-2025-004-new-feature/REQ-2025-004-new-feature.md \
  --tag REQ-2025-004-new-feature

# 步骤2: 自动生成Task-0 ⭐
python scripts/task-master/adapter.py REQ-2025-004-new-feature

# 步骤3: 分析任务复杂度
task-master analyze-complexity --tag REQ-2025-004-new-feature --research

# 步骤4: 展开任务为子任务
task-master expand --all --tag REQ-2025-004-new-feature --research

# 步骤5: 查看任务列表
task-master list --tag REQ-2025-004-new-feature
```

### 验证Task-0已生成

```bash
# 查看tasks.json，确认Task-0已添加到第一位
cat .taskmaster/tasks/tasks.json | jq '.["REQ-2025-004-new-feature"].tasks[0]'

# 或使用task-master查看
task-master show 0 --tag REQ-2025-004-new-feature
```

---

## 🔧 adapter.py的工作原理

### 执行逻辑

1. **检查tasks.json是否存在**

   - 如果不存在，报错退出

2. **检查REQ-ID是否在tasks.json中**

   - 如果不存在，报错退出

3. **检查Task-0是否已存在**

   - 如果已存在（id=0），跳过生成并提示
   - 如果不存在，继续生成

4. **生成Task-0**

   - 创建固定格式的Task-0（包含3个固定子任务）
   - 使用中文标题和描述

5. **插入到tasks列表**

   - 将Task-0插入到tasks列表的**第一位**（id=0）

6. **更新tasks.json**
   - 保存更新后的tasks.json

### 安全机制

- ✅ **幂等性**：如果Task-0已存在，不会重复生成
- ✅ **不会覆盖**：如果Task-0已存在，保留原有Task-0
- ✅ **格式固定**：生成的Task-0格式固定，符合规范

---

## 🚀 自动化集成建议

### 方案A：创建包装脚本（已实现）✅

已创建 `scripts/task-master/generate-task0.sh`，可以直接使用：

```bash
bash scripts/task-master/generate-task0.sh REQ-2025-003-user-login
```

### 方案B：在parse-prd规则中提示（推荐）💡

在 `task-generation.mdc` 规则中添加提示：

```markdown
## 任务生成后必做

1. ✅ 执行 `python scripts/task-master/adapter.py {REQ-ID}` 生成Task-0
2. ✅ 执行 `task-master expand --all` 展开任务
```

### 方案C：集成到MCP工具（长期方案）🔮

修改MCP的`parse_prd`工具，在解析完成后自动调用adapter：

```python
# 伪代码
def parse_prd(prd_file, tag):
    # 1. 调用task-master parse-prd
    result = task_master.parse_prd(prd_file, tag)

    # 2. 提取REQ-ID
    req_id = extract_req_id_from_prd(prd_file)

    # 3. 自动生成Task-0
    generate_task0(req_id)  # 调用adapter.py

    return result
```

---

## 📝 使用检查清单

### 新PRD流程检查清单

- [ ] 创建PRD文档
- [ ] 运行 `task-master parse-prd` 生成任务
- [ ] ⭐ **运行 `python scripts/task-master/adapter.py {REQ-ID}` 生成Task-0**
- [ ] 运行 `task-master expand --all` 展开任务
- [ ] 验证Task-0已在任务列表的第一位
- [ ] 验证Task-0包含3个固定子任务

---

## ⚠️ 注意事项

### 1. REQ-ID必须存在

adapter.py需要REQ-ID已经存在于tasks.json中，所以必须在`parse-prd`**之后**执行。

### 2. 不会覆盖现有Task-0

如果Task-0已存在，adapter会跳过生成。如果需要重新生成，需要先手动删除Task-0。

### 3. 固定格式

生成的Task-0格式是固定的，包含3个固定子任务，不能自定义。

---

## 🔗 相关文档

- [Task-0固定检查任务说明](TASK0-FIXED-SUBTASKS.md)
- [Task-0生成时机说明](TASK0-GENERATION-TIMING.md)
- [Task-0生成和识别问题分析](TASK0-GENERATION-ISSUE.md)

---

## 💡 快速参考

```bash
# 一键生成Task-0（推荐）
python scripts/task-master/adapter.py REQ-2025-003-user-login

# 或使用Shell脚本
bash scripts/task-master/generate-task0.sh REQ-2025-003-user-login
```
