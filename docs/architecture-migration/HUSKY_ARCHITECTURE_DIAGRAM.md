# 🏗️ 改进后的标准Husky架构流程与调用拓扑图

## 🎯 整体架构概览

```mermaid
graph TD
    A[Git操作] --> B{触发钩子}
    B -->|git commit| C[.git/hooks/pre-commit]
    B -->|git commit| D[.git/hooks/commit-msg]
    B -->|git push| E[.git/hooks/pre-push]
    B -->|git commit完成| F[.git/hooks/post-commit]
    B -->|git checkout| G[.git/hooks/post-checkout]

    C --> C1[调用器: 7行]
    D --> D1[调用器: 3行]
    E --> E1[调用器: 3行]
    F --> F1[调用器: 3行]
    G --> G1[调用器: 3行]

    C1 --> C2[.husky/pre-commit: 67行]
    D1 --> D2[.husky/commit-msg: 44行]
    E1 --> E2[.husky/pre-push: 60行]
    F1 --> F2[.husky/post-commit: 46行]
    G1 --> G2[.husky/post-checkout: 50行]

    style A fill:#e1f5fe
    style C2 fill:#f3e5f5
    style D2 fill:#f3e5f5
    style E2 fill:#f3e5f5
    style F2 fill:#e8f5e8
    style G2 fill:#e8f5e8
```

## 🔧 详细调用链拓扑图

### 1. Pre-commit 三层检查架构

```mermaid
graph TD
    A[git commit] --> B[.git/hooks/pre-commit]
    B --> C[PROJECT_ROOT=git rev-parse]
    C --> D[exec bash .husky/pre-commit]

    D --> E[🛡️ 第一层: 依赖安全检查]
    D --> F[🎫 第二层: 本地测试通行证]
    D --> G[📋 第三层: 代码质量检查]

    E --> E1[检查包管理命令进程]
    E1 --> E2{pgrep npm/pip/yarn}
    E2 -->|运行中| E3[❌ 退出]
    E2 -->|无进程| E4[✅ 通过]

    F --> F1[scripts-golden/local_test_passport.py]
    F1 --> F2[--check参数]
    F2 --> F3[检查通行证状态]

    G --> G1[scripts/code-quality-check.sh]
    G1 --> G2[--all-files --verbose]
    G2 --> G3[pre-commit工具]
    G3 --> G4[.code-quality-config.yaml]

    G4 --> H1[🔧 trim-whitespace]
    G4 --> H2[🔧 fix-end-of-files]
    G4 --> H3[🔧 check-yaml/json]
    G4 --> H4[🐍 black格式化]
    G4 --> H5[🐍 isort导入排序]
    G4 --> H6[🐍 flake8检查]
    G4 --> H7[🐍 mypy类型检查]
    G4 --> H8[🐍 bandit安全检查]
    G4 --> H9[💎 prettier前端格式化]
    G4 --> H10[⚡ eslint前端检查]
    G4 --> H11[🐳 hadolint Docker检查]
    G4 --> H12[📏 naming-conventions检查]
    G4 --> H13[🛡️ root-clutter守卫]

    style D fill:#f3e5f5
    style G1 fill:#fff3e0
    style G4 fill:#e8f5e8
```

### 2. Pre-push 通行证与安全验证

```mermaid
graph TD
    A[git push] --> B[.git/hooks/pre-push]
    B --> C[PROJECT_ROOT=git rev-parse]
    C --> D[exec bash .husky/pre-push]

    D --> E[🎫 通行证验证]
    D --> F[🔒 依赖安全检查]
    D --> G[🛡️ Git防护检查]

    E --> E1[scripts-golden/local_test_passport.py]
    E1 --> E2[--check完整验证]
    E2 --> E3{通行证有效?}
    E3 -->|无效| E4[❌ 推送被拒绝]
    E3 -->|有效| E5[✅ 通过验证]

    F --> F1[scripts-golden/dependency-guard.sh]
    F1 --> F2[检查依赖安全]
    F2 --> F3[扫描危险依赖]

    G --> G1[scripts-golden/git-guard.sh]
    G1 --> G2[Git完整性检查]
    G2 --> G3[防止绕过机制]

    style D fill:#f3e5f5
    style E1 fill:#fff3e0
    style F1 fill:#fff3e0
    style G1 fill:#fff3e0
```

### 3. Commit-msg 消息格式验证

```mermaid
graph TD
    A[git commit -m] --> B[.git/hooks/commit-msg]
    B --> C[exec bash .husky/commit-msg]
    C --> D[读取提交消息 $1]

    D --> E[正则表达式验证]
    E --> F{格式检查}
    F -->|匹配| G[长度检查]
    F -->|不匹配| H[❌ 格式错误提示]

    G --> I{< 500字符?}
    I -->|是| J[✅ 验证通过]
    I -->|否| K[❌ 消息过长]

    H --> L[显示格式规范]
    L --> M[feat|fix|docs等类型说明]
    M --> N[示例消息展示]

    style C fill:#f3e5f5
    style E fill:#e8f5e8
```

### 4. Post-hooks 监控与跟踪

```mermaid
graph TD
    A[Git操作完成] --> B{后置钩子}

    B -->|commit完成| C[.git/hooks/post-commit]
    B -->|checkout完成| D[.git/hooks/post-checkout]

    C --> C1[exec bash .husky/post-commit]
    D --> D1[exec bash .husky/post-checkout]

    C1 --> C2[scripts/code_change_tracker.py]
    C2 --> C3[--commit参数]
    C3 --> C4[跟踪代码变更]

    D1 --> D2[scripts/post_checkout_handler.py]
    D2 --> D3[分支切换处理]
    D3 --> D4[环境检查]
    D4 --> D5[依赖提醒]

    style C1 fill:#e8f5e8
    style D1 fill:#e8f5e8
```

## 🗂️ 关键组件说明

### Git钩子调用器 (.git/hooks/)

```bash
#!/usr/bin/env sh
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
exec bash "$PROJECT_ROOT/.husky/[hook-name]" "$@"
```

- **作用**: 轻量级调用器，动态获取项目路径
- **优势**: 跨平台兼容，路径自适应

### 实际逻辑脚本 (.husky/)

- **pre-commit**: 67行三层检查逻辑
- **pre-push**: 60行通行证和安全验证
- **commit-msg**: 44行消息格式验证
- **post-\***: 后置监控和处理

### 工具链脚本 (scripts/)

- **code-quality-check.sh**: 代码质量检查包装器
- **post_checkout_handler.py**: 分支切换处理器
- **code_change_tracker.py**: 代码变更跟踪器

### 防篡改脚本 (scripts-golden/)

- **local_test_passport.py**: 通行证生成和验证
- **dependency-guard.sh**: 依赖安全检查
- **git-guard.sh**: Git防护机制

## 🔄 流程优化对比

| 阶段         | 迁移前流程                | 迁移后流程             |
| ------------ | ------------------------- | ---------------------- |
| **开发**     | 修改.husky/ → 手动sync    | 修改.husky/ ✨         |
| **提交**     | Git → .git/hooks/直接执行 | Git → 调用器 → .husky/ |
| **团队协作** | 需要记住同步命令          | 标准化流程             |
| **维护**     | 双重配置维护              | 单一配置维护           |

## ⚡ 性能与可靠性

- **调用开销**: 调用器仅增加~1ms延迟
- **错误处理**: exec确保错误码正确传递
- **路径解析**: 动态路径解析，支持各种环境
- **权限管理**: 自动继承执行权限

---

_架构设计: 标准Husky + 复杂业务逻辑的最佳实践_
