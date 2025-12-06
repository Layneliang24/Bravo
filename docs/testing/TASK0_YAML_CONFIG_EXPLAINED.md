# Task0.yaml配置文件作用机制 - 简明解释

> **日期**: 2025-12-03
> **作者**: Claude Sonnet 4.5

---

## 🎯 核心问题

**task0.yaml如何起作用？**

**简短回答**：task0.yaml通过**配置驱动**的方式控制Task0Checker的行为，引擎加载YAML配置并传递给检查器，检查器在运行时读取配置来控制检查逻辑。

---

## 🔄 三步流程

### 步骤1：引擎加载配置

```python
# .compliance/engine.py

def _load_rules(self):
    """加载所有规则文件"""
    for rule_file in Path(".compliance/rules").glob("*.yaml"):
        rule_name = rule_file.stem  # "task0"
        with open(rule_file, "r") as f:
            rules[rule_name] = yaml.safe_load(f)  # 解析YAML → Python字典

    # 结果：self.rules["task0"] = {...从task0.yaml解析的配置...}
```

**作用**：将YAML文件转换为Python字典，存储在`self.rules["task0"]`中。

---

### 步骤2：创建检查器实例

```python
# .compliance/engine.py

# 创建Task0Checker实例，传入配置
checkers["task0"] = Task0Checker(self.rules["task0"])

# 等价于：
Task0Checker({
    "name": "task0",
    "strict_mode": True,
    "task_master_checks": {
        "task_ordering": {"enabled": True, "level": "warning", ...},
        "task_expansion": {"enabled": True, "min_complexity_for_expansion": 5, ...},
        ...
    }
})
```

**作用**：将配置字典传递给检查器构造函数，检查器保存到`self.config`。

---

### 步骤3：检查器使用配置

```python
# .compliance/checkers/task0_checker.py

class Task0Checker:
    def __init__(self, config):
        self.config = config  # ⭐ 保存配置
        self.strict_mode = config.get("strict_mode", True)  # ⭐ 读取配置

    def _check_task_expansion(self, req_id):
        # ⭐ 从配置中读取参数
        task_master_config = self.config.get("task_master_checks", {})
        expansion_config = task_master_config.get("task_expansion", {})
        min_complexity = expansion_config.get("min_complexity_for_expansion", 5)

        # 使用配置的阈值
        if complexity >= min_complexity:  # 使用配置值，不是硬编码
            return {"level": expansion_config.get("level", "warning"), ...}
```

**作用**：检查器在运行时读取配置，控制检查行为。

---

## 📊 配置项映射表

| task0.yaml配置项                                                 | 检查器中的使用位置              | 作用                                 |
| ---------------------------------------------------------------- | ------------------------------- | ------------------------------------ |
| `strict_mode: true`                                              | `self.strict_mode`              | 控制是否严格模式（ERROR vs WARNING） |
| `task_master_checks.task_ordering.enabled`                       | `_check_task_ordering()`        | 控制是否执行任务排序检查             |
| `task_master_checks.task_ordering.level`                         | `_check_task_ordering()`        | 控制检查级别（warning/error/info）   |
| `task_master_checks.task_expansion.min_complexity_for_expansion` | `_check_task_expansion()`       | 控制复杂度阈值（默认5）              |
| `task_master_checks.task_expansion.level`                        | `_check_task_expansion()`       | 控制检查级别                         |
| `task_master_checks.task_files_generation.enabled`               | `_check_task_files_generated()` | 控制是否执行txt文件检查              |
| `task_master_checks.*.help`                                      | 所有检查方法                    | 提供帮助信息文本                     |

---

## 💡 实际例子

### 例子1：修改复杂度阈值

**需求**：只检查复杂度>=7的任务

**操作**：

```yaml
# .compliance/rules/task0.yaml
task_master_checks:
  task_expansion:
    min_complexity_for_expansion: 7 # 从5改为7
```

**执行流程**：

```
1. 引擎加载task0.yaml → 解析为字典
2. 创建Task0Checker实例 → 传入配置字典
3. _check_task_expansion()执行 → 读取min_complexity = 7
4. 只有复杂度>=7的任务会触发警告
```

**效果**：无需修改Python代码，只需改YAML配置。

---

### 例子2：禁用某个检查

**需求**：临时关闭任务排序检查

**操作**：

```yaml
# .compliance/rules/task0.yaml
task_master_checks:
  task_ordering:
    enabled: false # 关闭
```

**执行流程**：

```
1. 引擎加载配置 → enabled: false
2. Task0Checker.check()执行
3. 检查enabled状态 → 跳过_check_task_ordering()
```

**效果**：任务排序检查被跳过，其他检查正常执行。

---

### 例子3：修改检查级别

**需求**：将任务排序从WARNING改为ERROR（阻断提交）

**操作**：

```yaml
# .compliance/rules/task0.yaml
task_master_checks:
  task_ordering:
    level: "error" # 从warning改为error
```

**执行流程**：

```
1. 引擎加载配置 → level: "error"
2. _check_task_ordering()执行 → 发现问题
3. 返回结果 → {"level": "error", ...}
4. 引擎判断 → ERROR级别，阻断提交
```

**效果**：任务排序不符合TDD会**拒绝提交**，而不是只警告。

---

## 🔍 配置读取位置

### 在检查器中的读取方式

```python
# 方式1：直接读取顶层配置
self.strict_mode = self.config.get("strict_mode", True)

# 方式2：读取嵌套配置
task_master_config = self.config.get("task_master_checks", {})
expansion_config = task_master_config.get("task_expansion", {})
min_complexity = expansion_config.get("min_complexity_for_expansion", 5)

# 方式3：读取配置并设置默认值
level = expansion_config.get("level", "warning")  # 默认warning
```

---

## ✅ 配置驱动的优势

### 1. 无需改代码

**Before（硬编码）**：

```python
if complexity >= 5:  # 硬编码，改阈值需要改代码
    return warning
```

**After（配置驱动）**：

```python
min_complexity = config.get("min_complexity_for_expansion", 5)  # 从配置读取
if complexity >= min_complexity:  # 改配置即可
    return warning
```

### 2. 灵活调整

- ✅ 可以针对不同项目调整配置
- ✅ 可以临时启用/禁用检查项
- ✅ 可以调整检查级别和阈值
- ✅ 可以修改帮助信息文本

### 3. 易于维护

- ✅ 配置集中在一个文件
- ✅ 版本控制友好
- ✅ 易于理解和修改

---

## 📝 完整调用链

```
git commit
  ↓
.husky/pre-commit (第四层检查)
  ↓
docker-compose exec backend python .compliance/runner.py
  ↓
ComplianceEngine.__init__()
  ├─ _load_rules()
  │   └─ 读取 .compliance/rules/task0.yaml
  │       └─ yaml.safe_load() → Python字典
  │
  └─ _load_checkers()
      └─ Task0Checker(self.rules["task0"])  ⭐ 传入配置
          └─ self.config = config  ⭐ 保存配置
  ↓
engine.check_files(files)
  ↓
checker.check(files)
  ├─ 读取 self.config["strict_mode"]
  ├─ 读取 self.config["task_master_checks"]["task_ordering"]["enabled"]
  ├─ 读取 self.config["task_master_checks"]["task_expansion"]["min_complexity_for_expansion"]
  └─ 执行检查，使用配置参数
  ↓
返回检查结果
```

---

## 🎯 总结

**task0.yaml的作用**：

1. **定义规则**：在YAML中定义检查规则、参数、帮助信息
2. **引擎加载**：ComplianceEngine自动加载所有.yaml文件
3. **配置传递**：通过构造函数传递给检查器
4. **运行时读取**：检查器在运行时读取配置，控制行为

**核心价值**：

- ✅ **配置驱动**：修改配置即可调整行为，无需改代码
- ✅ **解耦设计**：配置和代码分离，易于维护
- ✅ **灵活控制**：可以启用/禁用、调整级别、修改阈值

---

**配置驱动设计，让检查器更加灵活和可维护！** 🎯

_文档模型：Claude Sonnet 4.5 (claude-sonnet-4-20250514)_
