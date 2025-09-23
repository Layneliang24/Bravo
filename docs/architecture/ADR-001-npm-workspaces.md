# ADR-001: npm workspaces依赖管理架构

**状态**: 已接受 ✅  
**日期**: 2024-12-23  
**决策者**: 架构团队  
**血泪教训**: 基于30轮CI修复的惨痛经历

---

## 🎯 问题背景

### 历史问题
2024年项目经历了**30轮CI修复的恶性循环**，根本原因是npm依赖管理的架构混乱：

- **39个文件**中存在npm workspaces架构违规
- **5种环境配置** × **33个工作流** = 复杂度失控
- **新旧依赖管理模式并存**导致不可预测的依赖漂移

### 核心问题
```bash
# ❌ 问题模式：各种破坏性的npm调用
cd frontend && npm ci                    # 重新评估整个workspace
npm install -g some-tool                 # 版本不固定
working-directory: ./frontend + npm ci   # 工作流违规
```

这些看似无害的命令会**重新评估整个npm workspaces依赖树**，导致：
- deduped依赖被重新分配
- 共享依赖从根目录移动到子目录
- 其他workspace无法访问依赖
- 神秘的构建失败

---

## 🏗️ 架构决策

### 核心原则

#### 1. **单一入口原则**
```bash
✅ 正确：根目录统一管理
npm ci --prefer-offline --no-audit     # 只在根目录执行

❌ 错误：子目录分散管理  
cd frontend && npm ci                   # 破坏workspace结构
cd e2e && npm install                   # 导致依赖漂移
```

#### 2. **workspace优先原则**
```json
// package.json
{
  "workspaces": ["frontend", "e2e"],
  "scripts": {
    "build:frontend": "cd frontend && npm run build",  // ✅ 只构建，不安装
    "test:e2e": "cd e2e && npm run test"              // ✅ 只测试，不安装
  }
}
```

#### 3. **工具统一原则**
```bash
✅ 正确：项目内工具管理
npx playwright install --with-deps      # 使用项目依赖
npx @lhci/cli autorun                   # 避免全局安装

❌ 错误：全局工具安装
npm install -g playwright              # 版本不可控
npm install -g @lhci/cli               # 环境差异风险
```

---

## 📋 实施标准

### GitHub Actions工作流标准

```yaml
# ✅ 正确的工作流模式
- name: Install Dependencies
  run: npm ci --prefer-offline --no-audit  # 根目录统一安装

- name: Build Frontend  
  run: npm run build:frontend              # 通过scripts执行

- name: Run Tests
  run: npm run test:frontend               # 通过scripts执行
```

```yaml
# ❌ 禁止的工作流模式
- name: Install Frontend Dependencies
  working-directory: ./frontend           # ❌ 禁止
  run: npm ci

- name: Build Frontend
  run: cd frontend && npm ci && npm run build  # ❌ 禁止
```

### package.json Scripts标准

```json
{
  "scripts": {
    // ✅ 安全的scripts模式
    "install:all": "npm ci --prefer-offline --no-audit",
    "e2e:install": "npx playwright install --with-deps",
    "deps:check": "npm audit --audit-level=high",
    
    // ❌ 危险的scripts模式（已修复）
    // "install:all": "npm install && cd frontend && npm install && cd ../e2e && npm install",
    // "e2e:install": "cd e2e && npm install && npx playwright install --with-deps",
  }
}
```

### 本地开发标准

```bash
# ✅ 开发者应该使用的命令
npm ci --prefer-offline --no-audit      # 安装所有依赖
npm run dev:frontend                     # 启动前端开发
npm run test:e2e                        # 运行E2E测试

# ❌ 开发者不应该使用的命令
cd frontend && npm ci                    # 会破坏依赖结构
make install                            # 旧的Makefile方式（已修复）
```

---

## 🛡️ 防护机制

### 1. 自动化检查

#### Pre-commit Hook
```python
# scripts/check_npm_workspaces.py
# 检查所有文件中的npm workspaces违规模式
```

#### GitHub Actions检查
```yaml
- id: npm-workspaces-guard
  name: NPM Workspaces Architecture Guard
  entry: scripts/check_npm_workspaces.py
```

### 2. Issue模板
- 架构违规专用issue模板：`.github/ISSUE_TEMPLATE/architecture-violation.yml`
- 标准化违规报告和修复流程

### 3. 文档和培训
- 新人onboarding必读本ADR
- Code Review checklist包含架构检查
- 错误提示包含正确修复方案

---

## 🎯 成功标准

### 量化指标
- **架构合规率**: 100%（0个npm workspaces违规）
- **CI修复效率**: 单次修复成功率 > 90%
- **问题响应时间**: < 15分钟修复验证
- **新人培训时间**: < 1天掌握规范

### 质性指标
- 杜绝"30轮修复"的恶性循环
- 开发者构建体验一致性
- CI/CD流程可预测性

---

## 🚨 常见违规模式

### 模式1: 子目录npm ci
```bash
# ❌ 违规
cd frontend && npm ci
cd e2e && npm install

# ✅ 修复  
npm ci --prefer-offline --no-audit
```

### 模式2: 工作流working-directory
```yaml
# ❌ 违规
- working-directory: ./frontend
  run: npm ci

# ✅ 修复
- run: npm ci --prefer-offline --no-audit
```

### 模式3: 全局工具安装
```bash
# ❌ 违规
npm install -g @lhci/cli

# ✅ 修复
# 添加到devDependencies，使用npx执行
npx @lhci/cli autorun
```

### 模式4: package.json scripts违规
```json
// ❌ 违规
"install:all": "npm install && cd frontend && npm install"

// ✅ 修复  
"install:all": "npm ci --prefer-offline --no-audit"
```

---

## 🔄 维护和演进

### 定期审查
- **每月架构健康检查**：确保0违规状态
- **季度工具链review**：评估是否需要架构升级
- **年度最佳实践更新**：根据npm生态演进调整

### 演进策略
- **向后兼容**：新规范不破坏现有功能
- **渐进式改进**：优先修复高影响问题
- **知识传承**：确保团队理解架构决策背景

---

## 📚 相关资源

- [npm workspaces官方文档](https://docs.npmjs.com/cli/v7/using-npm/workspaces)
- [30轮修复血泪史总结](../FAQ.md#30轮修复血泪史)
- [架构违规检查脚本](../../scripts/check_npm_workspaces.py)
- [Pre-commit配置](../../.pre-commit-config.yaml)

---

## 🏆 决策理由

**为什么选择npm workspaces单一入口模式？**

1. **技术原理**: npm workspaces使用全局依赖解析，任何子目录操作都会重新评估整个依赖图谱
2. **历史教训**: 30轮修复证明了混合模式的不可持续性  
3. **行业最佳实践**: 符合npm官方推荐和大型项目标准
4. **维护成本**: 统一标准显著降低认知负担和错误概率

**这不是教条主义，而是基于血泪教训的务实选择。** 🎯
