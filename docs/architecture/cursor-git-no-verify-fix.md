# Cursor IDE --no-verify 问题解决方案

## 🚨 问题描述

Cursor IDE会自动在git commit命令中添加`--no-verify`参数，这会跳过所有pre-commit hooks，包括：
- 代码质量检查
- npm workspaces架构检查  
- 安全扫描
- 格式化检查

这违反了项目的架构治理规范，基于30轮修复血泪教训必须彻底阻止。

## 🛡️ 多层防护方案

### 方案1：Cursor设置配置 ⭐ (推荐先试)

#### 1.1 禁用Cursor的自动--no-verify

在Cursor中打开设置：
```
File → Preferences → Settings (或 Ctrl+,)
搜索: git verify
```

寻找以下设置项：
- `git.alwaysSignOff`: false  
- `git.allowNoVerifyCommit`: false
- `git.useEditorAsCommitInput`: false
- `scm.alwaysShowActions`: true

#### 1.2 自定义Cursor的Git配置

在项目根目录创建 `.vscode/settings.json` (Cursor会读取这个)：
```json
{
  "git.allowNoVerifyCommit": false,
  "git.alwaysSignOff": false,
  "git.useEditorAsCommitInput": true,
  "scm.inputFontFamily": "monospace",
  "git.confirmSync": true,
  "git.confirmNoVerifyCommit": true
}
```

#### 1.3 强制使用pre-commit hooks

```json
{
  "git.postCommitCommand": "none",
  "git.showPushSuccessNotification": true,
  "git.allowForcePush": false,
  "terminal.integrated.defaultProfile.windows": "Git Bash"
}
```

### 方案2：Git Alias劫持 🔧 (最可靠)

运行我们的保护脚本：
```bash
bash scripts/setup-git-no-verify-protection.sh
```

选择方案1 (Git Alias方案)，这会：
- 重定向 `git commit` 到检查函数
- 拦截所有 `--no-verify` 尝试
- 记录违规行为到日志文件

### 方案3：PATH劫击 💪 (最强力)

如果前两个方案都无效，使用PATH劫持：
```bash
bash scripts/setup-git-no-verify-protection.sh
```

选择方案3，这会：
- 在PATH最前面放置git包装脚本
- 拦截所有git命令
- 彻底阻止--no-verify

## 🧪 验证保护是否生效

### 测试命令
```bash
# 这应该被拦截
git commit --no-verify -m "test commit"

# 预期输出
🚨 检测到--no-verify违规！
❌ 禁止使用--no-verify跳过检查
💡 请修复检查问题而非绕过检查
```

### 检查保护状态
```bash
bash scripts/setup-git-no-verify-protection.sh
# 选择选项4查看当前保护状态
```

### 查看违规日志
```bash
tail -f logs/git-no-verify-attempts.log
```

## 🔍 故障排除

### 问题1：Cursor仍然能够使用--no-verify

**可能原因**：
- Cursor使用绝对路径调用git
- Cursor绕过了shell环境

**解决方案**：
1. 使用方案3的PATH劫持
2. 修改系统级git配置
3. 使用更底层的拦截

### 问题2：Git Alias不生效

**检查Alias设置**：
```bash
git config --get alias.commit
```

**重新设置**：
```bash
git config alias.commit '!f() { 
    if echo "$@" | grep -q "\-\-no-verify\|\-n"; then 
        echo "🚨 --no-verify被拦截！"; 
        exit 1; 
    fi; 
    command git commit "$@"; 
}; f'
```

### 问题3：Windows环境问题

**Git Bash配置**：
确保使用Git Bash作为默认终端：
```json
{
  "terminal.integrated.defaultProfile.windows": "Git Bash"
}
```

**PowerShell配置**：
如果必须使用PowerShell，添加function：
```powershell
function git {
    if ($args[0] -eq "commit" -and ($args -contains "--no-verify" -or $args -contains "-n")) {
        Write-Host "🚨 检测到--no-verify违规！" -ForegroundColor Red
        Write-Host "❌ 禁止使用--no-verify跳过检查" -ForegroundColor Red
        return 1
    }
    & git.exe @args
}
```

## 📊 监控和报告

### 违规统计
```bash
# 统计违规次数
wc -l logs/git-no-verify-attempts.log

# 最近的违规
tail -10 logs/git-no-verify-attempts.log
```

### 周期性检查
添加到crontab或Windows任务计划：
```bash
# 每天检查是否有新的违规尝试
0 9 * * * cd /path/to/project && python scripts/architecture_health_check.py
```

## 🎯 最终目标

通过这些方案的组合使用，确保：
- ✅ Cursor无法使用--no-verify绕过检查
- ✅ 所有git commit都会经过pre-commit hooks
- ✅ npm workspaces架构检查得到执行
- ✅ 违规行为被记录和监控

**记住：预防大于治疗，架构治理不容妥协！** 🛡️
