# ��� 改进后Husky架构执行流程详解

## ⏱️ 执行时序图

### Git Commit 完整时序

```mermaid
sequenceDiagram
    participant User as ��� 开发者
    participant Git as ��� Git
    participant PreHook as ��� .git/hooks/pre-commit
    participant HuskyScript as ��� .husky/pre-commit
    participant CodeQuality as ��� code-quality-check.sh
    participant PreCommit as ��� pre-commit工具
    participant CommitHook as ��� .git/hooks/commit-msg
    participant CommitScript as ��� .husky/commit-msg
    participant PostHook as ��� .git/hooks/post-commit
    participant PostScript as ��� .husky/post-commit

    User->>Git: git commit -m "feat: new feature"
    Git->>PreHook: 触发 pre-commit 钩子
    PreHook->>PreHook: PROJECT_ROOT=$(git rev-parse --show-toplevel)
    PreHook->>HuskyScript: exec bash .husky/pre-commit

    HuskyScript->>HuskyScript: ���️ 第一层: 依赖安全检查
    HuskyScript->>HuskyScript: pgrep -f "npm install|pip install"
    HuskyScript->>HuskyScript: ��� 第二层: 通行证验证 (可选)
    HuskyScript->>CodeQuality: bash scripts/code-quality-check.sh

    CodeQuality->>PreCommit: pre-commit run --config .code-quality-config.yaml
    PreCommit->>PreCommit: 执行 15+ 个检查项
    PreCommit-->>CodeQuality: ✅ 检查结果
    CodeQuality-->>HuskyScript: ✅ 代码质量通过
    HuskyScript-->>PreHook: ✅ 三层检查通过
    PreHook-->>Git: ✅ pre-commit 完成

    Git->>CommitHook: 触发 commit-msg 钩子
    CommitHook->>CommitScript: exec bash .husky/commit-msg "$1"
    CommitScript->>CommitScript: 读取提交消息
    CommitScript->>CommitScript: 正则验证格式
    CommitScript->>CommitScript: 检查长度限制
    CommitScript-->>CommitHook: ✅ 消息格式正确
    CommitHook-->>Git: ✅ commit-msg 完成

    Git->>Git: ��� 创建提交对象
    Git->>PostHook: 触发 post-commit 钩子
    PostHook->>PostScript: exec bash .husky/post-commit
    PostScript->>PostScript: python scripts/code_change_tracker.py --commit
    PostScript-->>PostHook: ✅ 变更跟踪完成
    PostHook-->>Git: ✅ post-commit 完成
    Git-->>User: ��� 提交成功!
```

### Git Push 完整时序

```mermaid
sequenceDiagram
    participant User as �� 开发者
    participant Git as ��� Git
    participant PushHook as ��� .git/hooks/pre-push
    participant PushScript as ���️ .husky/pre-push
    participant Passport as ��� local_test_passport.py
    participant DepGuard as ��� dependency-guard.sh
    participant GitGuard as ���️ git-guard.sh

    User->>Git: git push origin feature-branch
    Git->>PushHook: 触发 pre-push 钩子 (remote, url)
    PushHook->>PushScript: exec bash .husky/pre-push "$@"

    PushScript->>Passport: python scripts-golden/local_test_passport.py --check
    Passport->>Passport: 验证本地测试通行证
    Passport->>Passport: 检查测试覆盖率
    Passport->>Passport: 检查CI状态
    Passport-->>PushScript: ✅ 通行证有效

    PushScript->>DepGuard: bash scripts-golden/dependency-guard.sh
    DepGuard->>DepGuard: 扫描依赖安全漏洞
    DepGuard->>DepGuard: 检查依赖版本
    DepGuard-->>PushScript: ✅ 依赖安全

    PushScript->>GitGuard: bash scripts-golden/git-guard.sh
    GitGuard->>GitGuard: Git完整性检查
    GitGuard->>GitGuard: 防绕过机制验证
    GitGuard-->>PushScript: ✅ Git防护通过

    PushScript-->>PushHook: ✅ 所有安全检查通过
    PushHook-->>Git: ✅ pre-push 完成
    Git->>Git: ��� 执行推送到远程仓库
    Git-->>User: ��� 推送成功!
```

## ���️ 工具调用依赖图

```mermaid
graph TB
    subgraph "Git操作触发"
        A[git commit]
        B[git push]
        C[git checkout]
    end

    subgraph "钩子调用器层 (.git/hooks/)"
        D[pre-commit<br/>7行调用器]
        E[pre-push<br/>3行调用器]
        F[commit-msg<br/>3行调用器]
        G[post-commit<br/>3行调用器]
        H[post-checkout<br/>3行调用器]
    end

    subgraph "业务逻辑层 (.husky/)"
        I[pre-commit<br/>67行三层检查]
        J[pre-push<br/>60行安全验证]
        K[commit-msg<br/>44行格式验证]
        L[post-commit<br/>46行变更跟踪]
        M[post-checkout<br/>50行环境检查]
    end

    subgraph "工具脚本层 (scripts/)"
        N[code-quality-check.sh<br/>代码质量包装器]
        O[post_checkout_handler.py<br/>分支切换处理]
        P[code_change_tracker.py<br/>变更跟踪器]
    end

    subgraph "防篡改核心 (scripts-golden/)"
        Q[local_test_passport.py<br/>19KB 通行证系统]
        R[dependency-guard.sh<br/>8KB 依赖安全]
        S[git-guard.sh<br/>30KB Git防护]
        T[git-protection-monitor.sh<br/>15KB 保护监控]
    end

    subgraph "外部工具链"
        U[pre-commit工具<br/>Python生态]
        V[.code-quality-config.yaml<br/>15+检查规则]
        W[black/isort/flake8<br/>Python工具]
        X[prettier/eslint<br/>前端工具]
        Y[hadolint<br/>Docker工具]
    end

    A --> D
    B --> E
    A --> F
    A --> G
    C --> H

    D --> I
    E --> J
    F --> K
    G --> L
    H --> M

    I --> N
    I --> Q
    J --> Q
    J --> R
    J --> S
    L --> P
    M --> O

    N --> U
    U --> V
    V --> W
    V --> X
    V --> Y

    Q -.-> T
    R -.-> T
    S -.-> T

    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#e1f5fe
    style I fill:#f3e5f5
    style J fill:#f3e5f5
    style K fill:#f3e5f5
    style Q fill:#fff3e0
    style R fill:#fff3e0
    style S fill:#fff3e0
```

## ��� 性能分析与执行统计

### 执行时间分布

| 钩子              | 调用器开销 | 业务逻辑 | 工具链 | 总耗时 |
| ----------------- | ---------- | -------- | ------ | ------ |
| **pre-commit**    | <1ms       | 2-3ms    | 30-60s | ~60s   |
| **pre-push**      | <1ms       | 5-10ms   | 10-30s | ~30s   |
| **commit-msg**    | <1ms       | 1-2ms    | 0ms    | ~2ms   |
| **post-commit**   | <1ms       | 1-2ms    | 1-5s   | ~5s    |
| **post-checkout** | <1ms       | 2-5ms    | 1-10s  | ~10s   |

### 检查项目统计

- **代码质量检查**: 15+项 (格式化、语法、安全、规范)
- **安全验证**: 5项 (依赖、权限、通行证、防护、监控)
- **格式验证**: 3项 (提交消息、文件格式、命名规范)
- **环境检查**: 4项 (分支、依赖、配置、权限)

## ��� 关键设计原则

### 1. 责任分离

- **调用器**: 仅负责路径解析和脚本调用
- **业务逻辑**: 包含完整的检查和验证逻辑
- **工具脚本**: 提供可复用的功能模块
- **外部工具**: 专业的检查和格式化能力

### 2. 错误传播

```bash
# 调用器使用 exec 确保错误码正确传播
exec bash "$PROJECT_ROOT/.husky/pre-commit" "$@"
        ↓
# 业务脚本的 exit 代码直接传给 Git
exit 1  # 将阻止 git commit
```

### 3. 环境适配

```bash
# 动态获取项目根目录，支持各种环境
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
```

### 4. 参数传递

```bash
# 完整参数传递，保持钩子语义
exec bash "$SCRIPT" "$@"
```
