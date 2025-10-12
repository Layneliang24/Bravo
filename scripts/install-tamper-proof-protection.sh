#!/bin/bash
# 防篡改Git保护系统安装脚本
# 确保一次安装，持久保护

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_LOG="$PROJECT_ROOT/logs/protection-install.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "$1" | tee -a "$INSTALL_LOG"
}

# 创建日志目录
mkdir -p "$(dirname "$INSTALL_LOG")"
log "${BLUE}🛡️ 开始安装防篡改Git保护系统...${NC}"
log "📅 安装时间: $(date)"
log "📁 项目路径: $PROJECT_ROOT"
log ""

# 第1步：创建不可变备份
log "${YELLOW}第1步: 创建不可变保护文件备份${NC}"
bash "$PROJECT_ROOT/scripts/git-protection-monitor.sh" install
log "${GREEN}✅ 不可变备份创建完成${NC}"
log ""

# 第2步：设置智能alias（防止被覆盖）
log "${YELLOW}第2步: 设置智能防篡改alias${NC}"

# 创建智能alias函数，而不是简单的alias
SMART_ALIAS_FUNC='
# Git保护智能函数 - 防篡改设计
__git_protected() {
    local project_root="'"$PROJECT_ROOT"'"
    local guard_script="$project_root/scripts/git-guard.sh"
    local auto_fix_script="$project_root/scripts/auto-fix-git-protection.sh"

    # 自动修复检查（每次调用都检查）
    if [[ -f "$auto_fix_script" ]]; then
        bash "$auto_fix_script" 2>/dev/null || true
    fi

    # 调用保护脚本
    if [[ -f "$guard_script" ]]; then
        bash "$guard_script" "$@"
    else
        # 紧急回退到系统git
        echo "⚠️  警告: Git保护脚本丢失，使用系统git" >&2
        /mingw64/bin/git "$@" || /usr/bin/git "$@" || git "$@"
    fi
}

# 设置alias指向智能函数
alias git="__git_protected"

# 防止alias被意外删除的保护函数
__protect_git_alias() {
    if ! alias git 2>/dev/null | grep -q "__git_protected"; then
        alias git="__git_protected"
        echo "🔧 Git保护alias已自动恢复" >&2
    fi
}

# 在每个命令提示符显示前检查（轻量级）
if [[ "$PS1" ]]; then
    PROMPT_COMMAND="${PROMPT_COMMAND:+$PROMPT_COMMAND$'"'"'\n'"'"'}__protect_git_alias"
fi
'

# 添加到bashrc（去重处理）
log "📝 添加智能保护函数到 ~/.bashrc"
if [[ -f "$HOME/.bashrc" ]]; then
    # 移除旧的简单alias
    sed -i '/^alias git.*git-guard\.sh/d' "$HOME/.bashrc" 2>/dev/null || true
    sed -i '/^alias git.*git-interceptor/d' "$HOME/.bashrc" 2>/dev/null || true

    # 检查是否已经有智能函数
    if ! grep -q "__git_protected" "$HOME/.bashrc"; then
        echo "" >> "$HOME/.bashrc"
        echo "# Git防篡改保护系统 - 智能模式 ($(date))" >> "$HOME/.bashrc"
        echo "$SMART_ALIAS_FUNC" >> "$HOME/.bashrc"
        log "${GREEN}✅ 智能保护函数已添加到 ~/.bashrc${NC}"
    else
        log "${YELLOW}⚠️  智能保护函数已存在于 ~/.bashrc${NC}"
    fi
else
    log "${RED}❌ ~/.bashrc 不存在，请手动配置${NC}"
fi

# 激活当前会话的保护
eval "$SMART_ALIAS_FUNC"
log "${GREEN}✅ 当前会话保护已激活${NC}"
log ""

# 第3步：设置系统级监控
log "${YELLOW}第3步: 设置系统级监控${NC}"

# 创建定时检查脚本
cat > "$PROJECT_ROOT/scripts/periodic-protection-check.sh" << 'EOF'
#!/bin/bash
# 定期保护检查脚本（每分钟运行）

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITOR_SCRIPT="$PROJECT_ROOT/scripts/git-protection-monitor.sh"

# 静默检查和修复
if [[ -f "$MONITOR_SCRIPT" ]]; then
    bash "$MONITOR_SCRIPT" check >/dev/null 2>&1
fi
EOF
chmod +x "$PROJECT_ROOT/scripts/periodic-protection-check.sh"

# 设置crontab（如果可用）
if command -v crontab >/dev/null 2>&1; then
    CRON_JOB="* * * * * cd '$PROJECT_ROOT' && bash scripts/periodic-protection-check.sh"

    if ! crontab -l 2>/dev/null | grep -q "periodic-protection-check"; then
        (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab - 2>/dev/null && \
        log "${GREEN}✅ 定时监控已设置 (每分钟检查)${NC}" || \
        log "${YELLOW}⚠️  定时监控设置失败，将使用其他方式${NC}"
    else
        log "${YELLOW}⚠️  定时监控已存在${NC}"
    fi
else
    log "${YELLOW}⚠️  crontab不可用，跳过定时监控${NC}"
fi
log ""

# 第4步：创建保护状态检查工具
log "${YELLOW}第4步: 创建保护状态检查工具${NC}"

cat > "$PROJECT_ROOT/check-git-protection.sh" << 'EOF'
#!/bin/bash
# Git保护状态检查工具

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔍 Git保护系统状态检查"
echo "=========================="
echo ""

# 检查1: 当前alias状态
echo "1. 当前Git Alias状态:"
if alias git 2>/dev/null | grep -q "__git_protected"; then
    echo "   ✅ 智能保护函数已激活"
elif alias git 2>/dev/null | grep -q "git-guard"; then
    echo "   🟡 简单保护alias已激活"
else
    echo "   ❌ 保护alias未设置"
fi
echo ""

# 检查2: 保护脚本完整性
echo "2. 保护脚本完整性:"
if [[ -f "$PROJECT_ROOT/scripts/git-guard.sh" ]]; then
    echo "   ✅ 主保护脚本存在"
else
    echo "   ❌ 主保护脚本丢失"
fi

if [[ -f "$PROJECT_ROOT/scripts/git-protection-monitor.sh" ]]; then
    echo "   ✅ 监控脚本存在"
else
    echo "   ❌ 监控脚本丢失"
fi
echo ""

# 检查3: 备份状态
echo "3. 备份文件状态:"
if [[ -d "$PROJECT_ROOT/.git-protection-backup" ]]; then
    echo "   ✅ 备份目录存在"
    if [[ -f "$PROJECT_ROOT/.git-protection-backup/checksums.txt" ]]; then
        if sha256sum -c "$PROJECT_ROOT/.git-protection-backup/checksums.txt" >/dev/null 2>&1; then
            echo "   ✅ 文件完整性验证通过"
        else
            echo "   ⚠️  文件完整性验证失败"
        fi
    fi
else
    echo "   ❌ 备份目录不存在"
fi
echo ""

# 检查4: 系统级保护
echo "4. 系统级保护:"
if crontab -l 2>/dev/null | grep -q "protection-check"; then
    echo "   ✅ 定时监控已设置"
else
    echo "   ⚠️  定时监控未设置"
fi

if grep -q "__git_protected\|git-guard" "$HOME/.bashrc" 2>/dev/null; then
    echo "   ✅ ~/.bashrc配置存在"
else
    echo "   ❌ ~/.bashrc配置缺失"
fi
echo ""

# 检查5: 功能测试
echo "5. 功能测试:"
echo "   测试 --no-verify 拦截..."
if timeout 3 bash "$PROJECT_ROOT/scripts/git-guard.sh" commit --no-verify -m "test" 2>/dev/null | grep -q "检测到严重违规"; then
    echo "   ✅ --no-verify 拦截正常工作"
else
    echo "   ❌ --no-verify 拦截可能失效"
fi
echo ""

echo "🏁 状态检查完成"
echo ""
echo "📋 如发现问题，运行以下命令修复:"
echo "   bash scripts/install-tamper-proof-protection.sh"
EOF

chmod +x "$PROJECT_ROOT/check-git-protection.sh"
log "${GREEN}✅ 保护状态检查工具已创建: check-git-protection.sh${NC}"
log ""

# 第5步：创建用户教育文档
log "${YELLOW}第5步: 创建用户教育文档${NC}"

cat > "$PROJECT_ROOT/docs/git-protection-user-guide.md" << 'EOF'
# Git保护系统用户指南 🛡️

## 🎯 为什么需要Git保护

基于30轮CI修复的血泪教训，Git保护系统防止：
- ❌ `--no-verify` 绕过代码质量检查
- ❌ npm workspaces依赖漂移
- ❌ 架构违规问题扩散
- ❌ 恶意或意外的破坏性操作

## 🔧 如何正确使用

### ✅ 正常开发流程（推荐）
```bash
# 1. 创建feature分支
git checkout -b feature/your-feature

# 2. 正常开发和提交
git add .
git commit -m "your changes"  # 会通过正常检查

# 3. 推送并创建PR
git push origin feature/your-feature
```

### 🆘 紧急情况处理
```bash
# 临时禁用分支保护（谨慎使用）
export ALLOW_PROTECTED_BRANCH_OPERATIONS=true
git commit -m "emergency fix"

# 或使用紧急确认码
# 在提示时输入: HOTFIX_EMERGENCY_BYPASS
```

### 🚫 绝对不要做的事情

```bash
# ❌ 不要修改git alias
alias git='/usr/bin/git'  # 这会破坏保护

# ❌ 不要直接调用系统git
/mingw64/bin/git commit --no-verify  # 绕过保护

# ❌ 不要删除保护脚本
rm scripts/git-guard.sh  # 破坏保护系统
```

## 🔍 检查保护状态

```bash
# 检查保护是否正常工作
./check-git-protection.sh

# 查看拦截日志
cat logs/git-no-verify-attempts.log

# 测试拦截功能
git commit --no-verify -m "test"  # 应该被阻止
```

## 🛠️ 故障恢复

### 如果保护被意外破坏

```bash
# 自动修复
bash scripts/install-tamper-proof-protection.sh

# 或手动恢复
bash scripts/git-protection-monitor.sh restore
```

### 如果遇到误报

1. **检查是否在正确分支**:
   ```bash
   git branch  # 确保在feature分支，不是dev/main
   ```

2. **如果确实需要绕过**:
   ```bash
   # 设置环境变量（当前会话有效）
   export ALLOW_PROTECTED_BRANCH_OPERATIONS=true
   ```

3. **联系架构负责人**:
   - 如果规则需要调整
   - 如果遇到特殊情况

## 📊 系统组件说明

### 核心保护层
- `scripts/git-guard.sh` - 主拦截脚本
- `scripts/git-protection-monitor.sh` - 监控和恢复
- `scripts/auto-fix-git-protection.sh` - 自动修复

### 配置层
- `~/.bashrc` - 智能保护函数
- Crontab - 定时检查任务

### 备份层
- `.git-protection-backup/` - 不可变备份
- 文件完整性校验

## 🎓 最佳实践

1. **始终在feature分支开发**
2. **遇到阻止时先检查分支**
3. **不要尝试绕过保护系统**
4. **定期检查保护状态**
5. **有问题及时反馈**

---

💡 **记住**: 这个保护系统是为了帮助我们维护代码质量和项目稳定性，
不是为了阻碍开发效率。正确使用它会让开发更加顺畅！
EOF

log "${GREEN}✅ 用户教育文档已创建: docs/git-protection-user-guide.md${NC}"
log ""

# 安装完成总结
log "${GREEN}🎉 防篡改Git保护系统安装完成！${NC}"
log ""
log "${BLUE}📋 安装内容总结:${NC}"
log "   ✅ 智能防篡改alias函数"
log "   ✅ 不可变文件备份系统"
log "   ✅ 定时监控和自动修复"
log "   ✅ 完整性检查机制"
log "   ✅ 用户教育文档"
log ""
log "${YELLOW}🔄 后续步骤:${NC}"
log "   1. 重启终端或执行: source ~/.bashrc"
log "   2. 运行状态检查: ./check-git-protection.sh"
log "   3. 阅读用户指南: docs/git-protection-user-guide.md"
log ""
log "${RED}⚠️  重要提醒:${NC}"
log "   • 此保护系统现在具有自我修复能力"
log "   • 请不要尝试绕过或破坏保护机制"
log "   • 遇到问题请查看用户指南或联系架构负责人"
log ""

# 立即进行一次状态检查
log "${BLUE}🔍 正在进行首次状态检查...${NC}"
bash "$PROJECT_ROOT/check-git-protection.sh"
