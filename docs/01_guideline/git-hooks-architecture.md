# Git 钩子架构设计文档

## 📋 概述

本文档详细说明 Bravo 项目的 Git 钩子架构，包括本地钩子和服务器端钩子的区别、职责划分和部署方式。

## 🏗️ 架构总览

```
┌─────────────────────────────────────────────────────────────────┐
│                   Bravo Git 钩子防护体系                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  第一层：本地钩子（Husky 管理）                                │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 位置: .husky/                                          │   │
│  │ 管理: npm run prepare (Husky)                         │   │
│  │ 触发: 本地 Git 操作                                   │   │
│  │ 可绕过: ✗ 是（--no-verify）                           │   │
│  │                                                         │   │
│  │ 钩子:                                                  │   │
│  │  - pre-commit  → 代码质量检查                         │   │
│  │  - pre-push    → 测试通行证验证                       │   │
│  │  - commit-msg  → 提交消息格式                         │   │
│  └────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│              开发者可能使用 --no-verify 绕过                    │
│                            ↓                                     │
│  第二层：GitHub Actions（CI/CD）                               │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 位置: .github/workflows/                               │   │
│  │ 触发: PR 创建、推送到 dev/main                        │   │
│  │ 可绕过: ⚠️ 可能（分支规则配置）                       │   │
│  │                                                         │   │
│  │ 工作流:                                                │   │
│  │  - on-pr.yml         → PR 验证                        │   │
│  │  - push-validation.yml → 推送验证                     │   │
│  │  - branch-protection.yml → 分支保护                   │   │
│  └────────────────────────────────────────────────────────┘   │
│                            ↓                                     │
│  第三层：服务器端钩子（最后防线）⭐                           │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ 位置: server-hooks/ (部署到 Git 服务器)               │   │
│  │ 管理: 手动部署                                         │   │
│  │ 触发: 服务器接收推送                                  │   │
│  │ 可绕过: ✓ 否（服务器强制执行）                        │   │
│  │                                                         │   │
│  │ 钩子:                                                  │   │
│  │  - pre-receive → 全面检查（快速失败）                │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 🔍 详细对比

### 本地钩子 vs 服务器端钩子

| 维度         | 本地钩子 (.husky/)       | 服务器端钩子 (server-hooks/) |
| ------------ | ------------------------ | ---------------------------- |
| **运行位置** | 开发者本地机器           | Git 服务器                   |
| **触发时机** | 本地 Git 操作            | 服务器接收推送               |
| **管理工具** | Husky (npm)              | 手动部署                     |
| **安装方式** | `npm ci` (自动)          | 手动复制到服务器             |
| **可绕过性** | ✗ 可绕过 (`--no-verify`) | ✓ 不可绕过                   |
| **执行环境** | 开发者本地环境           | 服务器环境                   |
| **依赖**     | npm、Node.js、Python     | Git + Bash                   |
| **目的**     | 提高代码质量、加快反馈   | 强制执行规范、最后防线       |
| **适用场景** | 开发阶段                 | 所有推送                     |

## 📁 目录结构

```
Bravo/
├── .husky/                    # 本地钩子（Husky 管理）
│   ├── pre-commit            # 提交前检查
│   ├── pre-push              # 推送前检查
│   └── commit-msg            # 提交消息验证
│
├── .git/hooks/               # Git 原生钩子目录（本地）
│   ├── pre-commit           # → 调用 .husky/pre-commit
│   ├── pre-push             # → 调用 .husky/pre-push
│   └── pre-receive.sample   # 示例（本地不使用）
│
└── server-hooks/             # 服务器端钩子（需部署）
    ├── pre-receive          # 服务器端检查脚本
    ├── deploy.sh            # 部署脚本
    └── README.md            # 部署文档
```

## 🎯 职责划分

### 本地钩子职责（.husky/）

#### 1. pre-commit（提交前）

**目标**：快速反馈，提高代码质量

**检查项目**：

- ✅ 代码格式化（Black、Prettier）
- ✅ 语法检查（Flake8、ESLint）
- ✅ 类型检查（mypy）
- ✅ 安全检查（Bandit）
- ✅ 文件检查（YAML、JSON）
- ✅ 命名规范
- ✅ Docker 文件检查

**特点**：

- 🚀 快速执行（< 30 秒）
- 🔧 自动修复（格式化）
- 📊 详细反馈

#### 2. pre-push（推送前）

**目标**：确保测试通过

**检查项目**：

- ✅ 本地测试通行证验证
- ✅ 依赖安全检查
- ✅ Git 状态完整性

**特点**：

- 🎫 强制本地测试
- 🛡️ 防篡改检查

#### 3. commit-msg（提交消息）

**目标**：规范提交消息

**检查项目**：

- ✅ 提交消息格式
- ✅ 提交消息长度
- ✅ Conventional Commits 规范

### 服务器端钩子职责（server-hooks/）

#### pre-receive（接收推送前）

**目标**：最后防线，无法绕过

**检查项目**：

1. ✅ 分支保护（禁止直接推送到 main/dev）
2. ✅ 提交消息格式（最少 10 字符）
3. ✅ 禁止的文件（密钥、环境变量）
4. ✅ 大文件检查（> 10MB）
5. ✅ 代码质量标记（合并冲突、调试代码）
6. ✅ Docker 依赖管理规范
7. ✅ 本地测试通行证验证（警告）

**特点**：

- 🚀 快速失败（一旦失败立即终止）
- 🔒 无法绕过（服务器强制执行）
- 📊 详细日志（清晰的错误信息）

## 🔄 工作流程

### 正常开发流程

```bash
# 1. 开发者修改代码
vim backend/app.py

# 2. 提交代码（触发 pre-commit）
git commit -m "feat: add new feature"
# → 运行 .husky/pre-commit
# → 检查代码质量
# → 如果失败，提交被拒绝

# 3. 推送代码（触发 pre-push）
git push origin feature/new-feature
# → 运行 .husky/pre-push
# → 检查测试通行证
# → 如果失败，推送被拒绝

# 4. 服务器接收（触发 pre-receive）
# → 运行 server-hooks/pre-receive（服务器端）
# → 检查所有规范
# → 如果失败，推送被服务器拒绝
# → 如果成功，推送完成

# 5. GitHub Actions（触发 CI/CD）
# → 运行完整测试套件
# → 部署到环境
```

### 绕过本地钩子的情况

```bash
# 开发者使用 --no-verify 绕过本地钩子
git commit --no-verify -m "bypass checks"
git push --no-verify

# ❌ 推送到服务器时被 pre-receive 拒绝
# → 服务器端钩子无法绕过
# → 推送失败
# → 开发者必须修复问题
```

## 🚀 部署指南

### 本地钩子部署（自动）

```bash
# 克隆仓库后自动安装
git clone https://github.com/your-org/Bravo.git
cd Bravo

# npm ci 会自动运行 npm run prepare
npm ci

# Husky 会自动设置本地钩子
# .git/hooks/pre-commit → .husky/pre-commit
# .git/hooks/pre-push → .husky/pre-push
```

### 服务器端钩子部署（手动）

```bash
# 方案 1: 使用部署脚本（推荐）
cd server-hooks
./deploy.sh gitea /data/gitea/repositories/org/Bravo.git

# 方案 2: 手动部署
scp server-hooks/pre-receive user@server:/path/to/Bravo.git/hooks/
ssh user@server "chmod +x /path/to/Bravo.git/hooks/pre-receive"

# 详细步骤见 server-hooks/README.md
```

## 🔧 配置

### 本地钩子配置

**位置**：`.husky/pre-commit`, `.husky/pre-push`

**修改方式**：

```bash
# 编辑钩子文件
vim .husky/pre-commit

# 提交到仓库
git add .husky/pre-commit
git commit -m "chore: update pre-commit hook"
git push

# 团队成员拉取后自动生效
git pull
```

### 服务器端钩子配置

**位置**：`server-hooks/pre-receive`

**修改方式**：

```bash
# 1. 编辑钩子文件
vim server-hooks/pre-receive

# 2. 提交到仓库
git add server-hooks/pre-receive
git commit -m "chore: update server pre-receive hook"
git push

# 3. 重新部署到服务器
./server-hooks/deploy.sh gitea /path/to/repo.git
```

## 🛠️ 常见问题

### Q1: 为什么需要服务器端钩子？本地钩子不够吗？

**A**: 本地钩子可以被 `--no-verify` 绕过，开发者可能有意或无意地跳过检查。服务器端钩子是最后防线，无法绕过。

### Q2: 服务器端钩子可以用 Husky 管理吗？

**A**: 不可以。Husky 只管理**本地钩子**。服务器端钩子需要部署到 Git 服务器，服务器通常没有 npm、Node.js 环境。

### Q3: 本地的 .git/hooks/pre-receive 有什么用？

**A**: 在本地开发环境中，`pre-receive` 钩子**几乎不会被触发**。它只在服务器端接收推送时运行。本地应该使用 `pre-push` 钩子。

### Q4: 如果我是在 GitHub.com 托管，如何部署服务器端钩子？

**A**: GitHub.com 不支持自定义服务器端钩子。你需要：

- 使用 GitHub Actions 模拟服务器端检查
- 或者使用 GitHub Enterprise（支持 pre-receive 钩子）
- 或者使用分支保护规则 + Required Status Checks

### Q5: 本地钩子和服务器钩子的检查内容应该一样吗？

**A**: 不完全一样：

- **本地钩子**：快速反馈，轻量级检查，可以自动修复
- **服务器钩子**：最后防线，关键规范检查，快速失败

## 📚 相关文档

- [Git 钩子官方文档](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Husky 官方文档](https://typicode.github.io/husky/)
- [服务器端钩子部署指南](../../server-hooks/README.md)
- [项目开发规范](../memo.md)

## 🔄 更新历史

| 日期       | 版本  | 说明                                     |
| ---------- | ----- | ---------------------------------------- |
| 2025-10-12 | 1.0.0 | 初始版本，明确本地钩子和服务器钩子的区别 |

---

**维护人**: AI Assistant (Claude 3.5 Sonnet)
**更新时间**: 2025-10-12
