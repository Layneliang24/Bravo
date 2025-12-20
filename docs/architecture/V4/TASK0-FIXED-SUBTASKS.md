# Task-0固定检查任务说明

> **文档日期**: 2025-01-15
> **说明**: Task-0的检查任务是固定的，不能修改

---

## ✅ Task-0的检查任务是固定的

**是的，Task-0的检查任务是固定的**，包含以下3个子任务：

### 固定子任务列表

| 子任务ID | 标题                | 说明                              | 对应检查器方法              |
| -------- | ------------------- | --------------------------------- | --------------------------- |
| **1**    | 验证PRD元数据完整性 | 检查PRD frontmatter和必需字段     | `_validate_prd_metadata()`  |
| **2**    | 检查测试目录存在    | 确保所有必需的测试目录存在        | `_check_test_directories()` |
| **3**    | 验证API契约文件     | 检查API契约文件是否存在且格式正确 | `_validate_api_contract()`  |

### 定义位置

**检查器定义**：`.compliance/checkers/task0_checker.py` (第1-9行)

```python
"""
Task-0职责（针对每个REQ-ID）：
1. Subtask-1: 验证PRD元数据完整性
2. Subtask-2: 检查测试目录存在
3. Subtask-3: 验证API契约文件
"""
```

**生成逻辑定义**：`scripts/task-master/adapter.py` (`_generate_task_0()` 方法)

---

## 📋 Task-0标准格式

### 任务结构

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
      "description": "检查PRD frontmatter和必需字段（test_files、implementation_files、testcase_file、testcase_status）",
      "status": "pending",
      "dependencies": []
    },
    {
      "id": 2,
      "title": "检查测试目录存在",
      "description": "确保所有必需的测试目录存在（backend/tests/unit/、backend/tests/integration/、e2e/tests/）",
      "status": "pending",
      "dependencies": []
    },
    {
      "id": 3,
      "title": "验证API契约文件",
      "description": "检查API契约文件是否存在且格式正确（OpenAPI 3.0格式，包含openapi和paths字段）",
      "status": "pending",
      "dependencies": []
    }
  ]
}
```

### 关键要求

- ✅ **id必须为0**（固定规则）
- ✅ **必须在tasks列表的第一位**（插入到第一位）
- ✅ **必须包含3个子任务**（固定，不能增加或减少）
- ✅ **子任务标题固定**（与task0_checker的检查逻辑对应）

---

## 🔍 为什么是固定的？

### 1. 与检查器逻辑对应

Task-0的子任务与`task0_checker.py`中的检查方法一一对应：

```python
# task0_checker.py中的检查方法
def _validate_prd_metadata(self, req_id: str) -> Dict[str, Any]:
    """Subtask-1: 验证PRD元数据完整性"""

def _check_test_directories(self) -> Dict[str, Any]:
    """Subtask-2: 检查测试目录是否存在"""

def _validate_api_contract(self, req_id: str) -> Dict[str, Any]:
    """Subtask-3: 验证API契约文件"""
```

### 2. V4架构核心要求

这3个检查对应V4架构的核心要求：

- **PRD元数据**：确保PRD完整性（PRD先行原则）
- **测试目录**：确保测试结构就绪（测试先行原则）
- **API契约**：确保API设计就绪（契约驱动开发）

### 3. 设计文档定义

根据`AI-WORKFLOW-V4-PART2-TM-ADAPTER.md`的设计：

> Task-0职责（针对每个REQ-ID）：
>
> 1. Subtask-1: 验证PRD元数据完整性
> 2. Subtask-2: 检查测试目录存在
> 3. Subtask-3: 验证API契约文件

---

## ⚠️ 不能修改的原因

### 1. 检查器依赖固定格式

`task0_checker.py`中的检查逻辑假设Task-0包含这3个固定子任务，如果修改会导致检查器无法正确验证。

### 2. 合规引擎依赖

合规引擎的检查逻辑依赖于Task-0的固定格式，修改会影响合规检查的准确性。

### 3. 项目标准

Task-0是V4架构的核心组件，其格式是项目标准的一部分，不应随意修改。

---

## 🎯 自动生成Task-0

### 使用adapter.py自动生成

修复后的`adapter.py`会自动生成符合固定格式的Task-0：

```bash
python scripts/task-master/adapter.py REQ-2025-003-user-login
```

**生成逻辑**：

1. 检查Task-0是否已存在（如果存在则跳过）
2. 生成固定格式的Task-0（包含3个固定子任务）
3. 将Task-0插入到tasks列表的第一位
4. 更新tasks.json

### 集成到工作流

**理想工作流**（待实现）：

```bash
# 1. 解析PRD
task-master parse-prd <prd-file> --tag <tag-name>

# 2. 自动生成Task-0（应该在parse-prd后自动调用）
python scripts/task-master/adapter.py <REQ-ID>

# 3. 展开任务
task-master expand --all --research
```

---

## 📝 总结

### Task-0固定检查任务

✅ **是的，Task-0的检查任务是固定的**

- 固定包含3个子任务
- 子任务标题和描述固定
- 不能增加、减少或修改子任务
- 与task0_checker的检查逻辑一一对应

### 自动生成

✅ **adapter.py已修复，支持自动生成Task-0**

- 适配标签化结构
- 自动插入到tasks列表第一位
- 生成固定格式的Task-0
- 如果已存在则跳过（避免重复）

### 使用方式

```bash
# 为指定REQ-ID生成Task-0
python scripts/task-master/adapter.py REQ-2025-003-user-login
```

---

## 🔗 相关文档

- [Task-0生成时机说明](TASK0-GENERATION-TIMING.md)
- [Task-0生成和识别问题分析](TASK0-GENERATION-ISSUE.md)
- [Task-0识别验证结果](TASK0-VERIFICATION-RESULT.md)
- [Task-0设计和实现分析](TASK0-DESIGN-ANALYSIS.md)
