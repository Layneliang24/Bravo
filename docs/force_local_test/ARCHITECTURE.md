# 强制本地测试系统 - 架构设计

## 🏗️ 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cursor AI 强制本地测试系统                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   Cursor    │───▶│  Git Guard   │───▶│  Local Tests    │    │
│  │             │    │ Interceptor  │    │   Validator     │    │
│  │ git push... │    │              │    │                 │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│         │                    │                     │            │
│         │            ┌───────▼─────────┐          │            │
│         │            │   Passport      │          │            │
│         │            │   Validator     │          │            │
│         │            │                 │          │            │
│         │            └─────────────────┘          │            │
│         │                    │                     │            │
│         └────────────────────▼─────────────────────┘            │
│                         Allow Push                              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        验证层架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: Syntax    │  Layer 2: Environment │  Layer 3: Function │
│  ┌─────────────────┐ │  ┌───────────────────┐ │ ┌──────────────┐ │
│  │ GitHub Actions  │ │  │ Docker Compose    │ │ │ CI/CD        │ │
│  │ Syntax Check    │ │  │ Configuration     │ │ │ Simulation   │ │
│  │ (act)           │ │  │ Validation        │ │ │              │ │
│  └─────────────────┘ │  └───────────────────┘ │ └──────────────┘ │
│                      │                        │                  │
│  Layer 4: Diff Check                                             │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Environment Configuration Differences Analysis              │ │
│  │ Cross-Platform Compatibility Validation                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 核心设计原理

### 1. 拦截器模式 (Interceptor Pattern)

```
User Input → Interceptor → Validation → Action/Block
```

**设计思路**:

- 在Git命令执行前进行拦截
- 透明代理所有git操作
- 只对推送操作进行额外验证

**实现方式**:

```bash
# 通过PATH优先级或别名机制
alias git='bash scripts/git-guard.sh'
```

### 2. 通行证机制 (Passport System)

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Generate  │───▶│   Validate  │───▶│    Allow    │
│  Passport   │    │  Passport   │    │    Push     │
└─────────────┘    └─────────────┘    └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
  Four Layer         Check Expiry         Git Push
  Validation         & Code Hash          Execution
```

**核心特性**:

- **时效性**: 1小时有效期，防止过时代码推送
- **唯一性**: 基于Git状态哈希，代码变更自动失效
- **安全性**: 加密签名，防止伪造
- **可追溯**: 完整日志记录

### 3. 四层验证架构 (Four-Layer Validation)

```
Layer 1: Syntax Validation
├─ act (GitHub Actions syntax)
├─ YAML/JSON format check
└─ Workflow file validation

Layer 2: Environment Validation
├─ Docker service status
├─ docker-compose configuration
├─ Service dependencies check
└─ Resource availability

Layer 3: Functional Validation
├─ Backend unit tests
├─ Frontend unit tests
├─ Integration tests
└─ E2E tests (optional)

Layer 4: Differential Validation
├─ Configuration file differences
├─ Environment-specific settings
├─ Cross-platform compatibility
└─ npm workspaces structure
```

## 🔄 数据流图

```
┌─────────────┐
│ Code Change │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ git push... │
└──────┬──────┘
       │
       ▼
┌─────────────┐    NO     ┌─────────────┐
│ Passport    │──────────▶│ Run Local   │
│ Valid?      │           │ Tests       │
└──────┬──────┘           └──────┬──────┘
       │YES                      │
       ▼                         ▼
┌─────────────┐           ┌─────────────┐
│ Allow Push  │           │ Generate    │
└─────────────┘           │ Passport    │
                          └──────┬──────┘
                                 │
                                 ▼
                          ┌─────────────┐
                          │ Allow Push  │
                          └─────────────┘
```

## 🛡️ 安全机制设计

### 1. 多重防护

```
┌─────────────────────────────────────┐
│            Security Layers          │
├─────────────────────────────────────┤
│ 1. Git Command Interception        │
│    ├─ --no-verify blocking         │
│    ├─ --force push blocking        │
│    └─ Protected branch blocking    │
│                                    │
│ 2. Passport Validation            │
│    ├─ Cryptographic signature     │
│    ├─ Timestamp verification      │
│    └─ Git state hash matching     │
│                                    │
│ 3. Emergency Bypass               │
│    ├─ Environment variable        │
│    ├─ Confirmation code           │
│    └─ Complete audit logging      │
│                                    │
│ 4. Audit Trail                   │
│    ├─ All operations logged       │
│    ├─ Bypass attempts recorded    │
│    └─ Performance metrics         │
└─────────────────────────────────────┘
```

### 2. 失效机制

```python
# 通行证失效条件
def is_passport_invalid():
    conditions = [
        current_time > expire_time,     # 时间过期
        git_hash != stored_hash,        # 代码变更
        signature_invalid(),            # 签名不匹配
        file_corrupted()               # 文件损坏
    ]
    return any(conditions)
```

## 🔗 组件交互关系

### 1. 核心组件关系图

```
┌─────────────────┐
│  Git Guard      │
│  (Interceptor)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐
│ Passport        │◄──▶│ One-Click Test  │
│ Generator       │    │ Script          │
└─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│ Local Test      │    │ Validation      │
│ Simulation      │    │ Layers          │
└─────────────────┘    └─────────────────┘
```

### 2. 文件依赖关系

```
scripts/
├── git-guard.sh                 # 主拦截器
│   ├── calls: local_test_passport.py
│   └── logs: git-no-verify-attempts.log
│
├── local_test_passport.py       # 通行证生成器
│   ├── calls: one_click_test.sh (optional)
│   └── generates: .git/local_test_passport.json
│
├── one_click_test.sh           # 一键测试
│   ├── calls: act, docker-compose
│   ├── calls: run_github_actions_simulation.sh
│   └── calls: local_test_passport.py
│
└── setup_cursor_protection.sh  # 自动部署
    ├── configures: git aliases
    ├── creates: convenience commands
    └── generates: .vscode/tasks.json
```

## 📊 性能设计考虑

### 1. 缓存机制

```
┌─────────────────┐
│ Performance     │
│ Optimizations   │
├─────────────────┤
│ ✓ Passport      │
│   Caching       │
│ ✓ Docker        │
│   Container     │
│   Reuse         │
│ ✓ Incremental   │
│   Validation    │
│ ✓ Fast/Full     │
│   Test Modes    │
└─────────────────┘
```

### 2. 执行时间优化

```
Fast Mode (1-2 minutes):
├─ Syntax validation only
├─ Basic environment check
├─ Quick function tests
└─ Essential validations

Full Mode (5-10 minutes):
├─ Complete CI simulation
├─ All test suites
├─ Comprehensive checks
└─ Full validation suite
```

## 🔧 扩展性设计

### 1. 插件架构

```python
class ValidationPlugin:
    def validate(self) -> bool:
        pass

    def get_name(self) -> str:
        pass

# 支持自定义验证插件
custom_plugins = [
    SecurityScanPlugin(),
    PerformanceTestPlugin(),
    CodeQualityPlugin()
]
```

### 2. 配置化设计

```json
{
  "validation_config": {
    "enabled_layers": ["syntax", "environment", "functional", "differential"],
    "passport_expiry_hours": 1,
    "fast_mode_timeout": 120,
    "full_mode_timeout": 600,
    "bypass_emergency_code": "EMERGENCY_PUSH_BYPASS_2024"
  }
}
```

## 🚀 部署架构

### 1. 自动部署流程

```
git clone → setup script → auto configure → ready to use
     │            │               │              │
     ▼            ▼               ▼              ▼
Repository  Protection       Git Aliases   Start Working
   Setup      System         & Commands     Immediately
```

### 2. 跨团队同步

```
Team Member A                Team Member B
     │                            │
     ▼                            ▼
Install System              git pull + setup
     │                            │
     ▼                            ▼
Push with Tests ────────────▶ Auto Deploy
     │                            │
     ▼                            ▼
Same Experience             Consistent Flow
```

---

**架构设计原则**:

- **简单性**: 复杂逻辑内部化，用户接口简单
- **可靠性**: 多重防护，失败时有明确反馈
- **可维护性**: 模块化设计，清晰的职责分离
- **可扩展性**: 插件化架构，支持自定义扩展
