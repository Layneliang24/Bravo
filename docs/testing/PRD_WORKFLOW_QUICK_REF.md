# PRD工作流快速参考卡

> **版本**: V4.0
> **更新**: 2025-12-03

---

## 🎯 核心问题速查

### Q: 人类需求放哪里？

**A**: `.taskmaster/docs/{需求名}.txt`

```bash
# 示例
.taskmaster/docs/user-login-raw.txt
.taskmaster/docs/shopping-cart-raw.txt
```

---

### Q: Cursor精化的PRD放哪里？

**A**: `docs/00_product/requirements/{REQ-ID}/{REQ-ID}.md`

```bash
# 示例
docs/00_product/requirements/REQ-2025-001-user-login/REQ-2025-001-user-login.md
docs/00_product/requirements/REQ-2025-002-shopping-cart/REQ-2025-002-shopping-cart.md
```

---

### Q: Parse命令是什么？

**A**: `task-master parse-prd --input=<文件路径>`

```bash
# 快速模式（无状态检查）
task-master parse-prd --input=.taskmaster/docs/需求.txt

# 严格模式（检查status=approved）
task-master parse-prd --input=docs/00_product/requirements/REQ-YYYY-NNN/REQ-YYYY-NNN.md
```

---

## 📁 路径速查表

| 文件类型     | 路径模式                                                     | 示例                                                        |
| ------------ | ------------------------------------------------------------ | ----------------------------------------------------------- |
| **原始需求** | `.taskmaster/docs/{名称}.txt`                                | `.taskmaster/docs/login-raw.txt`                            |
| **精化PRD**  | `docs/00_product/requirements/{REQ-ID}/{REQ-ID}.md`          | `docs/00_product/requirements/REQ-2025-001/REQ-2025-001.md` |
| **API契约**  | `docs/01_guideline/api-contracts/{REQ-ID}/{REQ-ID}-api.yaml` | `docs/01_guideline/api-contracts/REQ-2025-001/api.yaml`     |
| **任务文件** | `.taskmaster/tasks/tasks.json`                               | `.taskmaster/tasks/tasks.json`                              |

---

## 🔄 两种模式速查

### 快速开发模式

```bash
# 1. 创建原始需求
echo "需要用户登录功能" > .taskmaster/docs/login.txt

# 2. Cursor精化（同一文件）
# （补充技术细节）

# 3. Parse（无状态检查）
task-master parse-prd --input=.taskmaster/docs/login.txt

# 4. 开发
task-master list
task-master next
```

**特点**：

- ✅ 快速、灵活
- ❌ 无审核、无合规检查

---

### 严格流程模式

```bash
# 1. 创建标准PRD
mkdir -p docs/00_product/requirements/REQ-2025-001-login
vim docs/00_product/requirements/REQ-2025-001-login/REQ-2025-001-login.md

# 2. Cursor编写PRD（包含YAML frontmatter）
# status: draft

# 3. 审核流程
# status: draft → review → approved

# 4. Parse（检查status=approved）
task-master parse-prd --input=docs/00_product/requirements/REQ-2025-001-login/REQ-2025-001-login.md

# 5. Parse成功，status自动更新
# status: approved → implementing

# 6. 开发（受V4合规保护）
task-master list
task-master next
```

**特点**：

- ✅ 审核流程、合规检查
- ❌ 流程相对复杂

---

## 🛡️ PRD状态机速查

| 状态             | 能否Parse     | 能否提交代码      | 转换方式    |
| ---------------- | ------------- | ----------------- | ----------- |
| **draft**        | ❌            | ❌                | 人工        |
| **review**       | ❌            | ❌（实现代码）    | 人工        |
| **approved**     | ✅            | ⚠️（建议先parse） | 人工        |
| **implementing** | ❌（已parse） | ✅                | **自动** ⭐ |
| **completed**    | ❌            | ✅                | 人工        |
| **archived**     | ❌            | ⚠️                | 人工        |

**唯一自动转换**：`approved → implementing`（由parse-prd触发）

---

## 🎯 快速决策

### 我应该用哪种模式？

**用快速模式**（.taskmaster/docs/）：

- ✅ 个人开发
- ✅ 快速原型
- ✅ 探索式开发

**用严格模式**（docs/00_product/）：

- ✅ 团队协作
- ✅ 正式项目
- ✅ 需要审核

**用混合模式**：

- ✅ 先快速探索
- ✅ 评估可行性
- ✅ 正式立项后迁移

---

## 🔧 常用命令速查

```bash
# Parse PRD
task-master parse-prd --input=<文件路径>

# 查看任务
task-master list

# 下一个任务
task-master next

# 分析复杂度
task-master analyze-complexity --research

# 展开任务
task-master expand --all --research

# 生成txt文件
task-master generate

# 查看任务详情
task-master show <id>

# 更新任务状态
task-master set-status --id=<id> --status=done
```

---

## ⚠️ 常见错误速查

| 错误      | 原因                 | 解决                 |
| --------- | -------------------- | -------------------- |
| Parse拒绝 | status不是approved   | 修改status为approved |
| 提交拒绝  | status是draft        | 完成审核流程         |
| 找不到PRD | 路径不对             | 检查REQ-ID和路径     |
| 重复parse | status是implementing | 已parse过，无需重复  |

---

**快速参考完成！** 📚

_Claude Sonnet 4.5 (claude-sonnet-4-20250514)_
