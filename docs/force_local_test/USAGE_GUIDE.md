# 🛡️ Husky+Git-Guard 混合保护系统使用指南

## 🎯 系统概述

本系统整合了Husky和Git-Guard的优势，实现三层防护架构：

```
┌─────────────────────────────────────────────┐
│           🛡️ 三层防护架构                    │
├─────────────────────────────────────────────┤
│ 第一层: Git-Guard 命令级拦截（防绕过）        │
│ 第二层: Husky 代码质量检查（自动化）          │
│ 第三层: Passport 强制本地测试（准入）         │
└─────────────────────────────────────────────┘
```

## 🚀 快速启动（一次配置，永久生效）

### 1. 初始化保护系统

```bash
# 安装Husky hooks（仅需运行一次）
npm install

# 检查保护系统状态
bash scripts/protection-status.sh
```

### 2. 便捷命令

```bash
./test          # 生成本地测试通行证（四层验证）
./passport      # 检查通行证状态
./safe-push     # 安全推送（需要通行证）
```

## 📋 核心文件结构

### 防篡改核心脚本（`scripts-golden/`）

```
scripts-golden/
├── git-guard.sh              # Git命令拦截器（30KB）
├── local_test_passport.py    # 通行证生成器（19KB）
├── git-protection-monitor.sh # 保护监控器（15KB）
└── dependency-guard.sh       # 依赖安全检查（8KB）
```

### Husky集成（`.husky/`）

```
.husky/
└── pre-commit               # 三层检查：防篡改+通行证+代码质量
```

### 便捷脚本（根目录）

```
./test         # → scripts-golden/local_test_passport.py --generate-passport
./passport     # → scripts-golden/local_test_passport.py --check-status
./safe-push    # → scripts-golden/git-guard.sh git push
```

## 🔧 工作流程

### 提交流程（永久生效）

```bash
# 1. 写代码
git add .

# 2. Husky自动三层检查（永久生效，无需激活）
git commit -m "feat: 新功能"
# ✅ 防篡改依赖检查
# ✅ 通行证状态检查
# ✅ 代码质量检查
```

### 推送流程（永久保护）

```bash
# 1. 生成完整通行证
./test

# 2. 直接推送（Husky自动验证通行证）
git push
# ✅ 通行证验证（自动）
# ✅ 依赖安全检查（自动）
# ✅ Git完整性检查（自动）
```

## 🎫 通行证系统

### 四层验证

1. **语法验证**: YAML语法、Docker配置检查
2. **环境验证**: Docker服务启动、连通性测试
3. **功能验证**: API端点测试、数据库操作验证
4. **差异验证**: 环境配置对比、版本一致性

### 通行证状态

```bash
./passport --check-status    # 检查通行证状态
./passport --force-refresh   # 强制刷新通行证
```

## 🛡️ 安全特性

### 防绕过机制

- **命令拦截**: 所有git/pip/npm命令被Git-Guard拦截
- **防篡改**: 核心脚本存储在`scripts-golden/`，防止修改
- **完整性验证**: 通行证包含Git状态哈希，防止手工伪造

### 保护监控

- **自动恢复**: Git保护被删除时自动恢复
- **篡改检测**: 监控核心脚本完整性
- **日志记录**: 所有绕过尝试都会被记录

## 🔧 故障排除

### 常见问题

**Q: 重启终端后保护失效？**

```bash
# ✅ 不会失效！基于Git Hooks的永久保护
# 只需检查状态（可选）
bash scripts/protection-status.sh
```

**Q: 通行证验证失败？**

```bash
# 检查Docker环境
docker --version

# 重新生成通行证
./test --force-refresh
```

**Q: 代码质量检查失败？**

```bash
# 运行代码格式化
pre-commit run --all-files
```

### 紧急绕过（仅限紧急情况）

```bash
# 使用确认码绕过（会被记录）
export BYPASS_CONFIRMATION="I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS"
git push --no-verify
```

## 🎯 最佳实践

1. **日常开发**: 使用便捷命令`./test`、`./passport`、`./safe-push`
2. **提交前**: 确保所有代码质量检查通过
3. **推送前**: 生成完整的本地测试通行证
4. **团队合作**: 定期更新`scripts-golden/`中的防篡改脚本

## 📞 支持

- 📁 **文档**: `docs/force_local_test/`
- 🔧 **状态检查**: `bash scripts/protection-status.sh`
- 📊 **Hooks配置**: `.husky/pre-commit`, `.husky/pre-push`

---

_系统版本: Husky永久保护架构 v3.0 - 零维护成本_
