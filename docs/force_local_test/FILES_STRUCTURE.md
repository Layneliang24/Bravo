# 强制本地测试系统 - 文件组成说明

## 📁 完整文件结构

```
Bravo/
├── 🛠️ 核心脚本文件
│   ├── scripts/
│   │   ├── git-guard.sh                      # [核心] Git命令拦截器
│   │   ├── local_test_passport.py            # [核心] 通行证生成器
│   │   ├── one_click_test.sh                 # [核心] 一键测试脚本
│   │   ├── setup_cursor_protection.sh        # [部署] 自动安装脚本
│   │   └── (现有脚本...)                      # 项目原有脚本
│   │
├── 🎯 便捷命令文件
│   ├── test                                  # 便捷测试命令
│   ├── passport                              # 便捷通行证命令
│   ├── safe-push                             # 便捷推送命令
│   └── Makefile                              # Make命令集成
│
├── ⚙️ 配置文件
│   ├── .vscode/
│   │   ├── tasks.json                        # Cursor/VS Code任务配置
│   │   └── settings.json                     # 编辑器设置
│   └── .git/
│       └── local_test_passport.json          # [生成] 通行证文件
│
├── 📚 文档文件
│   ├── docs/
│   │   ├── CURSOR_PROTECTION_GUIDE.md        # 用户使用指南
│   │   └── force_local_test/                 # 设计文档目录
│   │       ├── README.md                     # 系统概览
│   │       ├── ARCHITECTURE.md               # 架构设计
│   │       ├── IMPLEMENTATION.md             # 技术实现
│   │       ├── FILES_STRUCTURE.md            # 本文件
│   │       ├── CROSS_WINDOWS_DEPLOYMENT.md   # 跨平台部署
│   │       ├── DEBUG_GUIDE.md                # 调试指南
│   │       └── FAQ.md                        # 常见问题
│   │
└── 📝 日志文件
    └── logs/
        ├── git-no-verify-attempts.log        # Git拦截日志
        └── local_test_passport.log           # 通行证操作日志
```

## 🔧 核心脚本文件详解

### 1. `scripts/git-guard.sh` [Git命令拦截器]

**作用**: 系统的核心组件，拦截所有Git命令并验证推送权限

**核心功能**:

```bash
# 主要检查项目
├── 通行证验证 (新增)
├── --no-verify 拦截
├── 强制推送拦截
├── 保护分支检查
├── 数据丢失操作防护
└── 宿主机依赖安装拦截
```

**关键代码段**:

```bash
# 通行证验证函数
check_local_test_passport() {
    local passport_file="$PROJECT_ROOT/.git/local_test_passport.json"
    # 验证通行证有效性
}

# 推送拦截逻辑
if [[ "$1" == "push" ]]; then
    if ! check_local_test_passport; then
        show_passport_warning "推送到远程仓库" "git $*"
    fi
fi
```

**输入**: Git命令参数 (`$@`)
**输出**: 允许执行或拦截并显示警告
**日志**: `logs/git-no-verify-attempts.log`

---

### 2. `scripts/local_test_passport.py` [通行证生成器]

**作用**: 执行四层验证并生成/管理推送通行证

**核心功能**:

```python
class LocalTestPassport:
    ├── run_act_validation()           # Layer 1: 语法验证
    ├── run_docker_validation()       # Layer 2: 环境验证
    ├── run_quick_tests()             # Layer 3: 功能验证
    ├── run_environment_diff_check()  # Layer 4: 差异验证
    ├── generate_passport()           # 通行证生成
    └── check_existing_passport()     # 通行证验证
```

**命令行接口**:

```bash
python local_test_passport.py              # 运行完整验证
python local_test_passport.py --check      # 检查通行证状态
python local_test_passport.py --force      # 强制重新生成
```

**输入**: 命令行参数，当前Git状态
**输出**: 通行证文件 `.git/local_test_passport.json`
**日志**: `logs/local_test_passport.log`

---

### 3. `scripts/one_click_test.sh` [一键测试脚本]

**作用**: 用户友好的测试入口，整合多种验证工具

**核心功能**:

```bash
# 测试模式
├── --quick    # 快速测试(1-2分钟)
├── --full     # 完整测试(5-10分钟)
├── --check    # 检查通行证状态
├── --act-only # 仅语法验证
└── --docker-only # 仅环境验证
```

**执行流程**:

```bash
检查前置条件 → 选择模式 → 运行验证 → 生成通行证 → 显示结果
```

**输入**: 模式参数
**输出**: 验证结果和通行证状态
**调用**: `local_test_passport.py`, Docker服务

---

### 4. `scripts/setup_cursor_protection.sh` [自动安装脚本]

**作用**: 一键设置整个保护系统，配置所有必要组件

**安装步骤**:

```bash
1. setup_git_guard()           # 设置Git拦截
2. create_convenience_commands() # 创建便捷命令
3. update_makefile()           # 更新Makefile
4. create_cursor_config()      # 创建Cursor配置
5. create_usage_guide()        # 生成使用指南
6. test_protection_system()    # 测试系统
```

**生成文件**:

- `test`, `passport`, `safe-push` 便捷命令
- `.vscode/tasks.json` Cursor任务配置
- `Makefile` 更新（添加测试命令）
- `docs/CURSOR_PROTECTION_GUIDE.md` 使用指南

---

## 🎯 便捷命令文件详解

### 1. `test` [便捷测试命令]

```bash
#!/bin/bash
# 直接调用一键测试脚本
bash scripts/one_click_test.sh "$@"
```

**使用示例**:

```bash
./test              # 完整测试
./test --quick      # 快速测试
./test --check      # 检查状态
```

---

### 2. `passport` [便捷通行证命令]

```bash
#!/bin/bash
# 跨平台Python调用
if command -v python3 &> /dev/null; then
    python3 scripts/local_test_passport.py "$@"
else
    python scripts/local_test_passport.py "$@"
fi
```

**使用示例**:

```bash
./passport --check  # 检查通行证
./passport --force  # 强制重新生成
```

---

### 3. `safe-push` [便捷推送命令]

```bash
#!/bin/bash
# 安全推送命令，自动验证通行证
bash scripts/git-guard.sh push "$@"
```

**使用示例**:

```bash
./safe-push origin feature/branch
```

---

### 4. `Makefile` [Make命令集成]

**新增的目标**:

```makefile
# Cursor AI保护系统相关命令
test:           # 运行本地测试
test-quick:     # 快速测试
test-check:     # 检查通行证状态
passport:       # 检查通行证
passport-force: # 强制重新生成
safe-push:      # 安全推送
setup-protection: # 设置保护系统
```

## ⚙️ 配置文件详解

### 1. `.vscode/tasks.json` [Cursor任务配置]

**任务列表**:

```json
{
  "tasks": [
    {
      "label": "🧪 本地测试（生成推送通行证）",
      "command": "bash",
      "args": ["scripts/one_click_test.sh"]
    },
    {
      "label": "⚡ 快速测试",
      "args": ["scripts/one_click_test.sh", "--quick"]
    },
    {
      "label": "🎫 检查通行证状态",
      "command": "python3",
      "args": ["scripts/local_test_passport.py", "--check"]
    }
  ]
}
```

**使用方式**: `Ctrl+Shift+P` → `Tasks: Run Task` → 选择任务

---

### 2. `.git/local_test_passport.json` [通行证文件]

**数据结构**:

```json
{
  "version": "1.0",
  "generated_at": "2024-12-07T10:30:00.000000",
  "expires_at": "2024-12-07T11:30:00.000000",
  "git_hash": "a1b2c3d4e5f6",
  "validation_layers": {
    "act_syntax": true,
    "docker_environment": true,
    "functional_tests": true,
    "environment_diff": true
  },
  "valid_for_push": true,
  "validation_signature": "sha256_hash_32chars"
}
```

**特性**:

- 1小时有效期
- Git状态绑定
- 加密签名验证
- 分层验证记录

## 📚 文档文件详解

### 1. `docs/CURSOR_PROTECTION_GUIDE.md` [用户使用指南]

**内容**:

- 快速开始指南
- 详细使用说明
- 故障排除方法
- 命令参考手册

**目标用户**: 开发者、新团队成员

---

### 2. `docs/force_local_test/` [设计文档目录]

| 文件名                        | 作用           | 目标读者         |
| ----------------------------- | -------------- | ---------------- |
| `README.md`                   | 系统概览和导航 | 所有人           |
| `ARCHITECTURE.md`             | 架构设计原理   | 架构师、维护者   |
| `IMPLEMENTATION.md`           | 技术实现细节   | 开发者           |
| `FILES_STRUCTURE.md`          | 文件组成说明   | 维护者           |
| `CROSS_WINDOWS_DEPLOYMENT.md` | 跨平台部署     | 运维、团队负责人 |
| `DEBUG_GUIDE.md`              | 调试维护指南   | 技术支持         |
| `FAQ.md`                      | 常见问题解答   | 用户             |

## 📝 日志文件详解

### 1. `logs/git-no-verify-attempts.log` [Git拦截日志]

**格式**:

```
[时间戳] | [操作类型] | [详细信息] | [命令]
```

**记录内容**:

- 所有被拦截的Git操作
- 通行证验证结果
- 绕过尝试记录
- 性能指标

---

### 2. `logs/local_test_passport.log` [通行证操作日志]

**记录内容**:

- 通行证生成过程
- 验证层执行结果
- 错误信息和警告
- 性能统计数据

## 🔗 文件依赖关系图

```
┌─────────────────┐
│   git-guard.sh  │ ◄────────────┐
└─────────┬───────┘              │
          │                      │
          ▼                      │
┌─────────────────┐              │
│local_test_      │              │
│passport.py      │              │
└─────────┬───────┘              │
          │                      │
          ▼                      │
┌─────────────────┐              │
│one_click_test.sh│              │
└─────────┬───────┘              │
          │                      │
          ▼                      │
┌─────────────────┐              │
│   便捷命令文件   │ ──────────────┘
│ (test/passport) │
└─────────────────┘
```

## 📊 文件使用频率

| 文件类型                     | 使用频率    | 用户类型   |
| ---------------------------- | ----------- | ---------- |
| `test`, `passport`           | 每日多次    | 所有开发者 |
| `git-guard.sh`               | 每次Git操作 | 自动执行   |
| `local_test_passport.py`     | 每次测试    | 自动执行   |
| `setup_cursor_protection.sh` | 一次性      | 新环境安装 |
| 使用指南                     | 初次使用    | 新用户     |
| 设计文档                     | 问题排查时  | 维护者     |

---

**文件管理原则**:

- **核心脚本**: 保持稳定，谨慎修改
- **便捷命令**: 简单包装，易于使用
- **配置文件**: 自动生成，用户可调整
- **文档文件**: 及时更新，保持同步
- **日志文件**: 自动轮转，定期清理
