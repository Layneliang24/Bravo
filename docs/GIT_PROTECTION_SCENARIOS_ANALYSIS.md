# Git保护机制拦截场景全面分析

## 📊 拦截场景分类

### 🛡️ **类别A：保护分支操作**（最高优先级）

| 场景        | Git命令               | 当前验证方式                     | 位置             |
| ----------- | --------------------- | -------------------------------- | ---------------- |
| 1. 添加文件 | `git add`             | 确认码 `HOTFIX_EMERGENCY_BYPASS` | git-guard.sh:320 |
| 2. 提交更改 | `git commit`          | 确认码 `HOTFIX_EMERGENCY_BYPASS` | git-guard.sh:327 |
| 3. 挑选提交 | `git cherry-pick`     | 确认码 `HOTFIX_EMERGENCY_BYPASS` | git-guard.sh:331 |
| 4. 撤销提交 | `git revert`          | 确认码 `HOTFIX_EMERGENCY_BYPASS` | git-guard.sh:334 |
| 5. 应用补丁 | `git apply`           | 确认码 `HOTFIX_EMERGENCY_BYPASS` | git-guard.sh:337 |
| 6. 恢复暂存 | `git stash pop/apply` | 确认码 `HOTFIX_EMERGENCY_BYPASS` | git-guard.sh:341 |
| 7. 手动合并 | `git merge`           | 询问确认 + 确认码                | git-guard.sh:345 |

### 🚨 **类别B：危险Git操作**（高优先级）

| 场景               | Git命令                  | 当前验证方式                       | 位置             |
| ------------------ | ------------------------ | ---------------------------------- | ---------------- |
| 8. --no-verify绕过 | `git commit --no-verify` | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:359 |
| 9. 推送--no-verify | `git push --no-verify`   | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:574 |
| 10. 强制推送       | `git push -f/--force`    | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:591 |
| 11. 硬重置         | `git reset --hard`       | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:596 |
| 12. 清理文件       | `git clean -fd`          | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:600 |
| 13. 丢弃更改       | `git checkout .`         | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:604 |
| 14. 强制删除分支   | `git branch -D`          | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:609 |
| 15. 交互式变基     | `git rebase -i`          | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:613 |
| 16. 删除标签       | `git tag -d`             | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:617 |

### 🎫 **类别C：推送验证**（需要通行证）

| 场景                       | Git命令                | 当前验证方式                       | 位置             |
| -------------------------- | ---------------------- | ---------------------------------- | ---------------- |
| 17. 推送到远程（无通行证） | `git push`             | **加密密码验证** ✓                 | git-guard.sh:624 |
| 18. 推送到dev分支          | `git push origin dev`  | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:635 |
| 19. 推送到main分支         | `git push origin main` | 确认码 `I_UNDERSTAND_THE_RISKS...` | git-guard.sh:638 |

### 🚫 **类别D：质量检查绕过**

| 场景             | 命令                  | 当前验证方式                 | 位置             |
| ---------------- | --------------------- | ---------------------------- | ---------------- |
| 20. SKIP环境变量 | `SKIP=xxx git commit` | 确认码 `QUALITY_BYPASS_2024` | git-guard.sh:448 |
| 21. 其他绕过变量 | `--skip-hooks` 等     | 确认码 `QUALITY_BYPASS_2024` | git-guard.sh:373 |

### 🐳 **类别E：宿主机依赖安装**

| 场景              | 命令               | 当前验证方式                  | 位置             |
| ----------------- | ------------------ | ----------------------------- | ---------------- |
| 22. npm/yarn/pnpm | `npm install`      | 确认码 `DOCKER_NATIVE_BYPASS` | git-guard.sh:99  |
| 23. pip安装       | `pip install`      | 确认码 `DOCKER_NATIVE_BYPASS` | git-guard.sh:104 |
| 24. 系统包管理    | `apt/brew install` | 确认码 `DOCKER_NATIVE_BYPASS` | git-guard.sh:110 |

---

## ⚠️ **为什么输入确认码后还是失败？**

### **问题1：超时机制**

```bash
# git-guard.sh 第305行
response=$(read_with_timeout "确认码: ")
if [[ "$response" != "I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS" ]]; then
    echo "❌ 操作被取消"
    exit 1
fi
```

**`read_with_timeout` 有30秒超时**：

- AI输入确认码 → 但需要30秒内完成
- 超时后 `read_with_timeout` 返回 exit 1
- 导致 `response` 为空
- 不等于确认码，所以失败

### **问题2：确认码太长**

```
I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS  # 46个字符
```

容易输入错误或超时。

### **问题3：密码验证未初始化**

```bash
# 场景17使用加密密码验证
if ! bash "$PROJECT_ROOT/scripts-golden/encrypted_auth_system.sh" --verify; then
    echo "❌ 加密验证失败"
    exit 1
fi
```

如果未初始化密码系统（`.auth-config` 不存在），会失败。

---

## 🎯 **统一改为密码验证的方案**

### **优点**

1. ✅ **一致性**：所有场景使用同一验证方式
2. ✅ **安全性**：只有知道密码的人能通过
3. ✅ **用户友好**：输入短密码比长确认码简单
4. ✅ **AI无法绕过**：30秒超时 + 真实密码验证

### **需要修改的文件**

1. `scripts-golden/git-guard.sh` - 主保护脚本
2. `scripts/git-interceptor` - 简化版拦截脚本
3. 所有`show_*_warning`函数

### **修改策略**

```bash
# 当前：确认码验证
response=$(read_with_timeout "确认码: ")
if [[ "$response" != "I_UNDERSTAND_THE_RISKS_OF_BYPASSING_CHECKS" ]]; then
    exit 1
fi

# 改为：密码验证
if ! bash "$PROJECT_ROOT/scripts-golden/encrypted_auth_system.sh" --verify "场景描述" "Git操作"; then
    exit 1
fi
```

---

## 📋 **初始化密码系统**

首次使用需要初始化：

```bash
bash scripts-golden/encrypted_auth_system.sh --init
```

设置一个主密码（8位以上，包含数字、字母、符号）。

---

## ✅ **验证流程**

1. **用户初始化密码** → `.auth-config` 文件生成
2. **触发拦截** → 调用加密验证系统
3. **输入密码** → 30秒超时保护
4. **SHA256验证** → 密码哈希匹配
5. **通过/拒绝** → 记录到日志

---

生成时间：2025-10-19 23:30
