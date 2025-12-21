# V4合规引擎检查类型总结

本文档总结了V4合规引擎中实现的双向检查和单向检查。

---

## 🔄 双向检查（Bidirectional Checks）

双向检查确保两个方向的关联性都是正确的，即：

- **正向检查**：A → B（从源头检查目标）
- **反向检查**：B → A（从目标检查源头）

### 1. PRD ↔ 代码文件关联检查

**位置**: `prd_checker.py` → `_check_bidirectional_links()`

#### 正向检查（PRD → 代码）

- ✅ **检查PRD中列出的文件是否存在**

  - 检查 `test_files` 中声明的所有测试文件是否存在
  - 检查 `implementation_files` 中声明的所有实现文件是否存在
  - 如果文件不存在 → **错误**

- ✅ **检查文件中的REQ-ID是否匹配PRD的req_id**
  - 读取PRD中列出的每个文件，提取REQ-ID注释
  - 验证文件中的REQ-ID是否与PRD的req_id一致
  - 如果不匹配 → **错误**
  - 如果文件缺少REQ-ID注释 → **错误**

#### 反向检查（代码 → PRD）

- ✅ **检查代码文件是否在PRD的implementation_files列表中**

  - 位置: `code_checker.py` → `_check_file_in_prd_implementation_files()`
  - 当代码文件包含REQ-ID时，检查该文件是否在对应PRD的`implementation_files`列表中
  - 如果不在列表中 → **警告**

- ✅ **检查代码文件中的REQ-ID是否存在于PRD**
  - 位置: `code_checker.py` → `_check_prd_link()`
  - 验证代码文件中的REQ-ID对应的PRD文件是否存在
  - 如果PRD不存在 → **错误**

---

### 2. PRD ↔ 测试用例CSV关联检查

**位置**: `test_checker.py` → `_enforce_testcase_gate()`

#### 正向检查（代码 → CSV）

- ✅ **检查测试文件引用的TestCase-ID是否在CSV中存在**
  - 从测试代码中提取所有 `TESTCASE-IDS:` 注释中的用例ID
  - 从PRD对应的CSV文件中读取所有用例ID
  - 验证代码中引用的用例ID是否都在CSV中存在
  - 如果引用了不存在的用例ID → **错误**

#### 反向检查（CSV → 代码）

- ✅ **检查CSV中的用例是否都在测试代码中实现**
  - 位置: `test_checker.py` → `_enforce_testcase_gate()` 中的反向检查部分
  - 从CSV中读取所有用例ID
  - 从PRD声明的所有`test_files`中提取代码引用的用例ID
  - 验证CSV中的用例ID是否都在代码中实现
  - 如果CSV中有用例未在代码中实现 → **错误**（测试用例已评审通过时）或 **警告**（测试用例未评审时）
  - ⚠️ **特殊处理**：使用类变量 `_reverse_checked_req_ids` 确保每个REQ-ID只检查一次，避免重复报错

---

### 3. PRD ↔ Task-Master任务关联检查

**位置**: `prd_checker.py` → `_check_bidirectional_links()`

#### 正向检查（PRD → Task）

- ✅ **检查PRD的req_id是否在tasks.json中存在对应的任务组**
  - 从PRD的req_id查找`.taskmaster/tasks/tasks.json`中是否存在对应任务组
  - 如果不存在 → **警告**
  - 如果存在但任务组为空 → **警告**

#### 反向检查（Task → PRD）

- ⚠️ **未实现**：当前没有从tasks.json反向检查PRD的逻辑

---

## ➡️ 单向检查（One-way Checks）

单向检查只检查一个方向，确保某个方向的一致性。

### 1. 代码文件合规检查（代码 → 规范）

**位置**: `code_checker.py`

#### REQ-ID注释检查

- ✅ **代码文件必须包含REQ-ID注释**
  - 检查文件头部（前20行）是否包含REQ-ID注释
  - 如果缺少 → **错误**

#### 测试文件存在性检查

- ✅ **代码文件必须有关联的测试文件**
  - 位置: `code_checker.py` → `_check_test_link()`
  - 根据代码文件路径推断对应的测试文件路径
  - 检查测试文件是否存在（包括从git暂存区检查）
  - 如果不存在 → **警告**

#### Task关联检查

- ✅ **代码文件必须关联到Task-Master任务**
  - 位置: `code_checker.py` → `_check_task_link()`
  - 从代码文件的REQ-ID查找tasks.json中是否存在对应任务
  - 检查代码文件路径是否在任务的实现文件中
  - 如果未关联 → **警告**

---

### 2. PRD文件合规检查（PRD → 规范）

**位置**: `prd_checker.py`

#### 元数据完整性检查

- ✅ **必需字段检查**
  - 检查PRD frontmatter是否包含所有必需字段
  - 必需字段：`req_id`, `title`, `status`, `test_files`, `implementation_files`, `api_contract`, `testcase_file`, `testcase_status`, `deletable`
  - 如果缺少必需字段 → **错误**

#### PRD状态检查

- ✅ **状态有效性检查**

  - 检查status字段是否在有效状态列表中
  - 有效状态：`draft`, `review`, `approved`, `implementing`, `completed`, `archived`
  - 如果状态无效 → **错误**

- ✅ **状态转换规则检查**
  - `draft`状态不允许提交实现代码 → **错误**
  - `review`状态允许修改PRD，但不允许提交实现代码 → **警告**
  - `implementing/completed`状态要求测试用例必须评审通过 → **错误**

#### 文件结构检查

- ✅ **必需章节检查**

  - 检查PRD是否包含必需章节：`功能概述`, `用户故事`, `验收标准`, `测试用例`
  - 如果缺少必需章节 → **错误**

- ✅ **推荐章节检查**
  - 根据`implementation_files`中的文件类型，推荐添加相应章节（如`数据库设计`, `API接口定义`, `前端UI/UX设计`）
  - 如果缺少推荐章节 → **警告**

#### 内容详细度检查

- ✅ **章节内容检查**
  - 检查各章节内容是否符合要求（关键词、格式、最小项目数等）
  - 如果内容不足 → **警告**

---

### 3. 测试文件合规检查（测试 → 规范）

**位置**: `test_checker.py`

#### TestCase-ID格式检查

- ✅ **测试文件必须引用TestCase-ID**
  - 检查测试文件是否包含 `TESTCASE-IDS:` 注释
  - 如果缺少 → **错误**

#### PRD状态检查

- ✅ **PRD状态必须允许提交测试代码**
  - 检查PRD的status是否允许提交测试
  - `draft`/`review`状态不允许提交测试代码 → **错误**

#### 测试文件位置检查

- ✅ **测试文件必须在指定目录**
  - 根据测试类型（unit/integration/e2e）检查文件是否在正确目录
  - 如果位置不正确 → **警告**

---

### 4. 测试用例CSV合规检查（CSV → 规范）

**位置**: `testcase_checker.py`

#### 文件命名检查

- ✅ **CSV文件命名必须符合规范**
  - 格式：`{REQ-ID}-test-cases.csv`
  - 如果命名不符合 → **错误**

#### CSV内容格式检查

- ✅ **必需字段检查**
  - 检查CSV是否包含所有必需字段：`用例ID`, `用例名称`, `测试类型`, `优先级`, `关联REQ-ID`, `关联功能点`, `测试场景`, `前置条件`, `测试步骤`, `预期结果`
  - 如果缺少字段 → **错误**

#### 用例数据完整性检查

- ✅ **用例ID格式检查**

  - 格式：`TC-{MODULE}_{FEATURE}-{序号}` 或 `TC-{MODULE}-{序号}`
  - 如果格式不符合 → **警告**

- ✅ **用例ID唯一性检查**

  - 检查CSV中是否有重复的用例ID
  - 如果重复 → **错误**

- ✅ **关联REQ-ID一致性检查**

  - 检查每行的`关联REQ-ID`是否与文件名中的REQ-ID一致
  - 如果不一致 → **错误**

- ✅ **用例数量检查**
  - 检查CSV中用例数量是否满足最低要求（默认5个）
  - 检查P0用例数量是否满足最低要求（默认1个）
  - 如果数量不足 → **错误**

---

### 5. API契约一致性检查（代码 → 契约）

**位置**: `code_checker.py` → `_check_api_contract_consistency()`

#### 契约文件存在性检查

- ✅ **PRD必须声明api_contract字段**
  - 当后端API代码修改时，检查PRD是否声明了`api_contract`字段
  - 如果未声明 → **警告**

#### 契约文件格式检查

- ✅ **API契约文件格式验证**
  - 检查契约文件是否存在
  - 检查契约文件是否是有效的YAML格式
  - 检查契约文件是否包含`openapi`版本字段
  - 检查契约文件是否包含`paths`定义
  - 如果格式不正确 → **错误**

#### 一致性提醒

- ✅ **代码修改时提醒保持一致性**
  - 当后端API代码（views.py/serializers.py）修改时，提醒开发者确保代码与契约文件保持一致
  - 建议运行`python manage.py spectacular`验证 → **警告**

---

### 6. 删除授权检查（代码 → PRD）

**位置**: `code_checker.py` → `_check_deletion_authorization()`

#### 功能删除授权检查

- ✅ **删除功能代码必须获得PRD授权**
  - 检测到代码删除时，检查PRD的`deletable`字段是否为`true`
  - 如果`deletable=false`且检测到删除 → **错误**
  - 如果PRD未声明`deletable`字段且检测到删除 → **警告**

---

### 7. Task-Master任务合规检查（Task → 规范）

**位置**: `task_checker.py`, `task0_checker.py`

#### Task-0自检任务检查

- ✅ **每个REQ-ID必须有Task-0自检任务**
  - 检查tasks.json中每个REQ-ID的任务组是否包含Task-0
  - 如果缺少 → **错误**

#### 任务状态检查

- ✅ **任务状态有效性检查**
  - 检查任务状态是否在有效列表中
  - 如果状态无效 → **错误**

---

## 📊 检查类型统计

### 双向检查（3组）

1. ✅ **PRD ↔ 代码文件**（完全双向）
2. ✅ **PRD ↔ 测试用例CSV**（完全双向）
3. ⚠️ **PRD ↔ Task-Master**（仅正向，反向未实现）

### 单向检查（7类）

1. ✅ **代码文件合规检查**（代码 → 规范）
2. ✅ **PRD文件合规检查**（PRD → 规范）
3. ✅ **测试文件合规检查**（测试 → 规范）
4. ✅ **测试用例CSV合规检查**（CSV → 规范）
5. ✅ **API契约一致性检查**（代码 → 契约）
6. ✅ **删除授权检查**（代码 → PRD）
7. ✅ **Task-Master任务合规检查**（Task → 规范）

---

## 🔍 检查时机

### Pre-commit阶段（提交前检查）

所有检查器在pre-commit hook中执行，检查暂存的文件：

- PRD文件 → `prd_checker`
- 代码文件 → `code_checker`
- 测试文件 → `test_checker`
- 测试用例CSV → `testcase_checker`
- Task文件 → `task_checker`, `task0_checker`

### CI/CD阶段（持续集成检查）

在GitHub Actions中执行完整的合规检查，包括：

- 所有pre-commit检查
- 代码覆盖率检查
- API契约完整验证（使用`scripts/validate-api-contract.py`）

---

## 🎯 未来改进方向

### 待实现的双向检查

1. **Task-Master ↔ PRD反向检查**

   - 从tasks.json检查PRD是否存在
   - 检查任务描述是否与PRD一致

2. **API契约 ↔ 代码实现双向检查**

   - 正向：契约 → 代码（检查契约中定义的API是否都在代码中实现）
   - 反向：代码 → 契约（当前已实现）

3. **提交消息 ↔ PRD/Task关联检查**
   - 检查提交消息中的REQ-ID和Task-ID是否匹配
   - 检查提交消息格式是否符合规范

### 待增强的单向检查

1. **代码覆盖率检查**

   - 检查代码覆盖率是否达到要求（80%）

2. **依赖关系检查**
   - 检查PRD之间的依赖关系是否合理
   - 检查Task之间的依赖关系是否形成闭环

---

## 📚 相关文档

- [V4架构设计](../V4/AI-WORKFLOW-V4-PART1-ARCH.md)
- [V4合规引擎设计](../V4/AI-WORKFLOW-V4-PART5-COMPLIANCE.md)
- [API契约验证](API-CONTRACT-VALIDATION.md)
