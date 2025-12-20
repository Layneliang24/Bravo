# Task-0生成和识别问题分析

> **分析日期**: 2025-01-15
> **问题**: 为什么看不到Task-0？

---

## 🔍 问题诊断

### 当前状态

1. **tasks.json中没有Task-0**

   - 检查`.taskmaster/tasks/tasks.json`
   - `REQ-2025-003-user-login`标签下只有task id 1-19
   - **没有task id 0（Task-0）**

2. **adapter.py从未被调用**

   - `scripts/task-master/adapter.py`存在，但从未执行
   - adapter.py的`_generate_task_0()`方法从未运行

3. **设计不匹配**
   - adapter.py期望：`.taskmaster/tasks/{REQ-ID}/tasks.json`
   - 实际情况：`.taskmaster/tasks/tasks.json`（标签化结构）

---

## 📋 Task-0应该如何生成？

### 设计意图（PART2文档）

根据`AI-WORKFLOW-V4-PART2-TM-ADAPTER.md`的设计：

```
Task-Master工作流：
1. parse-prd → 生成tasks.json（原始任务）
2. expand → 生成子任务
3. adapter.py → 生成Task-0 + 三层目录结构
```

**关键点**：

- Task-0应该由**适配层（adapter.py）**生成
- Task-0应该被插入到tasks列表的**第一位**（id=0）
- Task-0应该作为**强制性自检任务**

### 实际情况

1. **Task-Master直接解析PRD** → 生成tasks.json（**没有Task-0**）
2. **adapter.py未被调用** → Task-0没有被生成
3. **tasks.json中缺少Task-0** → 合规检查器无法找到Task-0

---

## 🎯 为什么adapter.py没有被调用？

### 原因分析

1. **工作流程缺失**

   - 设计文档中提到应该在parse-prd后调用adapter
   - 但实际工作流中**没有这一步**
   - 用户或MCP工具只执行了`parse-prd`，没有执行`adapter.py`

2. **路径不匹配**

   - adapter.py期望：`.taskmaster/tasks/{REQ-ID}/tasks.json`
   - 实际情况：`.taskmaster/tasks/tasks.json`（标签化）
   - adapter.py的设计是基于**旧的目录结构**，不匹配当前的**标签化结构**

3. **集成不完整**
   - adapter.py是独立脚本，没有被集成到Task-Master工作流中
   - MCP工具和CLI命令都没有调用adapter

---

## 🔧 Task-0如何被Task-Master识别？

### 当前识别逻辑（task0_checker.py）

```python
def _find_tasks_by_req_id(self, tasks_data: dict, req_id: str) -> list:
    """从tasks.json中查找与REQ-ID相关的任务"""
    related_tasks = []

    # 遍历所有tag
    for tag_name, tag_data in tasks_data.items():
        tasks = tag_data.get("tasks", [])

        for task in tasks:
            # 检查任务标题、描述、details中是否包含REQ-ID
            task_text = " ".join([task.get("title", ""), ...])
            if req_id in task_text:
                related_tasks.append(task)

    return related_tasks
```

**问题**：

- 这个方法查找的是**任务文本中包含REQ-ID的任务**
- 它**不会**专门查找Task-0（id=0）
- 如果Task-0的标题/描述不包含REQ-ID，就找不到

### 正确的识别方式

Task-0应该：

1. **id必须为0**（固定规则）
2. **在对应REQ-ID的tag下**
3. **作为第一个任务**（在tasks列表的第一位）

**识别逻辑应该是**：

```python
# 直接从REQ-ID的tag下查找id=0的任务
req_tag = tasks_data.get(req_id, {})
tasks = req_tag.get("tasks", [])
task_0 = next((t for t in tasks if t.get("id") == 0), None)
```

---

## ✅ 解决方案

### 方案1：手动添加Task-0到tasks.json（快速修复）

**步骤**：

1. 直接在tasks.json的REQ-ID tag下，tasks列表的**第一位**添加Task-0：

```json
{
  "REQ-2025-003-user-login": {
    "tasks": [
      {
        "id": 0,
        "title": "Task-0: 自检与验证",
        "description": "验证PRD元数据完整性、检查测试目录存在、验证API契约文件",
        "status": "pending",
        "priority": "high",
        "dependencies": [],
        "subtasks": [
          {
            "id": 1,
            "title": "验证PRD元数据完整性",
            "description": "检查PRD frontmatter和必需字段",
            "status": "pending"
          },
          {
            "id": 2,
            "title": "检查测试目录存在",
            "description": "确保所有必需的测试目录存在",
            "status": "pending"
          },
          {
            "id": 3,
            "title": "验证API契约文件",
            "description": "检查API契约文件是否存在且格式正确",
            "status": "pending"
          }
        ]
      },
      {
        "id": 1,
        "title": "后端：数据库模型扩展与迁移",
        ...
      }
    ]
  }
}
```

### 方案2：修改adapter.py适配标签化结构（长期方案）

**需要修改**：

1. **修改路径逻辑**：

   ```python
   # 旧代码
   self.tasks_json_path = self.root_dir / ".taskmaster" / "tasks" / req_id / "tasks.json"

   # 新代码（适配标签化结构）
   self.tasks_json_path = self.root_dir / ".taskmaster" / "tasks" / "tasks.json"
   ```

2. **修改读取逻辑**：

   ```python
   # 读取tasks.json（标签化结构）
   with open(self.tasks_json_path, "r", encoding="utf-8") as f:
       all_tasks_data = json.load(f)

   # 获取对应REQ-ID的tag数据
   req_tag_data = all_tasks_data.get(self.req_id, {})
   original_tasks = req_tag_data.get("tasks", [])
   ```

3. **修改写入逻辑**：

   ```python
   # 更新对应REQ-ID的tag
   all_tasks_data[self.req_id]["tasks"] = enhanced_tasks  # 包含Task-0
   all_tasks_data[self.req_id]["metadata"]["updated_at"] = datetime.now().isoformat()

   # 写回tasks.json
   with open(self.tasks_json_path, "w", encoding="utf-8") as f:
       json.dump(all_tasks_data, f, indent=2, ensure_ascii=False)
   ```

4. **修复编码问题**：
   ```python
   # 在print中使用UTF-8编码
   import sys
   sys.stdout.reconfigure(encoding='utf-8')
   ```

### 方案3：集成到Task-Master工作流（最佳方案）

**理想工作流**：

```bash
# 1. 解析PRD
task-master parse-prd --input="docs/00_product/requirements/REQ-2025-003-user-login/REQ-2025-003-user-login.md"

# 2. 自动调用adapter生成Task-0（应该在parse-prd内部完成，或作为post-hook）
python scripts/task-master/adapter.py REQ-2025-003-user-login

# 3. 展开任务
task-master expand --all --research
```

**或者更理想的**：

- parse-prd命令**自动生成Task-0**
- 不需要单独的adapter.py脚本
- Task-0作为parse-prd的**内置步骤**

---

## 🔍 为什么现在看不到Task-0？

### 根本原因

1. **Task-0从未被生成**

   - adapter.py存在但从未被调用
   - parse-prd命令不生成Task-0（Task-Master原生不支持）

2. **设计演进导致的不匹配**

   - adapter.py设计时：期望独立的tasks.json文件（每个REQ-ID一个）
   - 现在实际：标签化结构（所有REQ-ID在一个tasks.json中）

3. **工作流缺失**
   - 设计文档中提到的adapter步骤没有被实际执行
   - 用户/MCP工具只执行了parse-prd，跳过了adapter步骤

---

## 💡 建议的解决步骤

### 立即解决（手动添加）

1. **手动在tasks.json中添加Task-0**（使用方案1）
2. **验证task0_checker能否识别**（可能需要修改识别逻辑）

### 长期解决（代码修复）

1. **修改adapter.py适配标签化结构**（方案2）
2. **修复编码问题**
3. **集成到工作流**（方案3，可选）

### 或者（更简单的方案）

**直接在Task-Master的parse-prd命令中内置Task-0生成逻辑**，不需要单独的adapter.py脚本。

---

## 📝 Task-0的标准格式

根据设计文档和task0_checker的实现，Task-0应该：

```json
{
  "id": 0, // ⭐ 必须是0
  "title": "Task-0: 自检与验证",
  "description": "验证PRD元数据完整性、检查测试目录存在、验证API契约文件",
  "status": "pending",
  "priority": "high",
  "dependencies": [],
  "subtasks": [
    {
      "id": 1,
      "title": "验证PRD元数据完整性",
      "status": "pending"
    },
    {
      "id": 2,
      "title": "检查测试目录存在",
      "status": "pending"
    },
    {
      "id": 3,
      "title": "验证API契约文件",
      "status": "pending"
    }
  ]
}
```

**关键要求**：

- ✅ id必须为0
- ✅ 必须在tasks列表的**第一位**
- ✅ 必须包含3个subtasks（PRD元数据、测试目录、API契约）

---

## 🎯 下一步行动

### 选项A：手动添加Task-0（推荐，快速）

我可以帮您：

1. 读取当前的tasks.json
2. 在REQ-2025-003-user-login的tasks列表开头添加Task-0
3. 保存更新后的tasks.json

### 选项B：修复adapter.py（长期方案）

我可以帮您：

1. 修复adapter.py适配标签化结构
2. 修复编码问题
3. 运行adapter.py生成Task-0

**您希望我采用哪种方案？**
