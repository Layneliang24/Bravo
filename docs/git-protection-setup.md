# Git --no-verify 保护系统使用指南

## 🎯 目标

防止任何人在任何环境中使用`--no-verify`绕过项目检查，确保代码质量和架构一致性。

## 🛡️ 多层防护体系

### 1. Git Hooks 保护（核心层）
- **文件**: `.git/hooks/pre-commit`, `.git/hooks/commit-msg`  
- **特点**: 跟随项目，无法简单绕过
- **覆盖**: 所有git commit操作

### 2. Shell 别名保护（用户层）
- **文件**: `~/.bashrc` 中的git别名
- **特点**: 拦截命令行git调用
- **覆盖**: 终端中的git命令

### 3. IDE 配置保护（工具层）
- **文件**: `.vscode/settings.json`
- **特点**: 限制Cursor IDE行为
- **覆盖**: IDE内的git操作

### 4. Pre-commit 检查（流程层）
- **文件**: `.pre-commit-config.yaml`
- **特点**: 代码质量检查
- **覆盖**: 提交前检查流程

## 📋 新环境设置

在新电脑或新克隆的项目中：

```bash
# 1. 克隆项目后立即运行
./scripts/setup-git-protection.sh

# 2. 重启终端或执行
source ~/.bashrc

# 3. 测试保护是否生效
./test-git-protection.sh
```

## 🧪 测试命令

```bash
# 测试--no-verify拦截
git commit --no-verify -m "should be blocked"

# 测试-n短参数拦截  
git commit -n -m "should also be blocked"

# 查看拦截日志
cat logs/git-no-verify-attempts.log
```

## 🔧 故障排除

### 问题：新环境中--no-verify没有被拦截

**解决方案**：
1. 检查Git Hooks权限：`ls -la .git/hooks/pre-commit`
2. 重新运行设置脚本：`./scripts/setup-git-protection.sh`
3. 运行测试验证：`./test-git-protection.sh`

### 问题：Shell别名不生效

**解决方案**：
1. 重启终端或执行：`source ~/.bashrc`
2. 检查别名：`alias | grep git`
3. 手动添加：`alias git='bash "$(pwd)/scripts/git-guard.sh"'`

## 📊 监控和审计

所有违规尝试会记录到：
- `logs/git-no-verify-attempts.log`

定期检查此日志了解绕过尝试情况。
