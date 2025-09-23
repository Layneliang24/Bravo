#!/bin/bash
# Git --no-verify 多层保护安装脚本
# 用于新环境快速配置完整的保护体系

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "🛡️ 设置Git --no-verify 多层保护系统..."
echo "📁 项目根目录: $PROJECT_ROOT"

# 1. 安装Git Hooks
echo ""
echo "1. 📋 安装Git Hooks保护..."
if [ ! -f "$PROJECT_ROOT/.git/hooks/pre-commit" ]; then
    cp "$PROJECT_ROOT/scripts/git-guard.sh" "$PROJECT_ROOT/.git/hooks/pre-commit"
    chmod +x "$PROJECT_ROOT/.git/hooks/pre-commit"
    echo "✅ pre-commit hook已安装"
else
    echo "⚠️  pre-commit hook已存在，跳过"
fi

# 2. 创建commit-msg hook检查
echo ""
echo "2. 📝 安装commit-msg检查..."
cat > "$PROJECT_ROOT/.git/hooks/commit-msg" << 'EOF'
#!/bin/bash
# 检查提交信息中是否包含绕过标志

COMMIT_MSG_FILE="$1"
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# 检查提交信息中的可疑内容
if echo "$COMMIT_MSG" | grep -qi "no.verify\|skip.hook\|bypass"; then
    echo ""
    echo "🚨 警告：提交信息中包含可疑的绕过标志"
    echo "📋 提交信息: $COMMIT_MSG"
    echo ""
    echo "如果这是正常的功能描述，请忽略此警告"
    echo "如果试图记录绕过行为，这可能违反项目规范"
fi
EOF
chmod +x "$PROJECT_ROOT/.git/hooks/commit-msg"
echo "✅ commit-msg hook已安装"

# 3. 设置Shell别名（可选）
echo ""
echo "3. 🔧 设置Shell别名保护（可选）..."
BASHRC_ALIAS="alias git='bash \"$PROJECT_ROOT/scripts/git-guard.sh\"'"

if [ -f "$HOME/.bashrc" ]; then
    if ! grep -q "git-guard.sh" "$HOME/.bashrc"; then
        echo "$BASHRC_ALIAS" >> "$HOME/.bashrc"
        echo "✅ 已添加git alias到~/.bashrc"
    else
        echo "⚠️  ~/.bashrc中已存在git别名"
    fi
else
    echo "⚠️  ~/.bashrc不存在，跳过Shell别名设置"
fi

# 4. 创建测试脚本
echo ""
echo "4. 🧪 创建保护测试脚本..."
cat > "$PROJECT_ROOT/test-git-protection.sh" << 'EOF'
#!/bin/bash
# 测试Git --no-verify保护是否生效

echo "🧪 测试Git --no-verify保护系统..."
echo ""

cd "$(dirname "$0")"

# 测试1: Git Hooks保护
echo "1. 测试Git Hooks保护..."
echo "test content" > test-protection-file.txt
git add test-protection-file.txt 2>/dev/null || true

echo "尝试--no-verify提交..."
if git commit --no-verify -m "test protection" 2>&1 | grep -q "检测到试图绕过"; then
    echo "✅ Git Hooks保护生效"
    git reset HEAD~1 2>/dev/null || true
    rm -f test-protection-file.txt 2>/dev/null || true
else
    echo "❌ Git Hooks保护可能失效"
fi

# 测试2: Shell别名保护（如果存在）
echo ""
echo "2. 测试Shell别名保护..."
if alias git 2>/dev/null | grep -q "git-guard.sh"; then
    echo "✅ Shell别名保护已激活"
else
    echo "⚠️  Shell别名保护未激活（需要重启终端或source ~/.bashrc）"
fi

# 测试3: IDE配置检查
echo ""
echo "3. 检查IDE配置..."
if [ -f ".vscode/settings.json" ] && grep -q '"git.allowNoVerifyCommit": false' ".vscode/settings.json"; then
    echo "✅ Cursor IDE配置已设置"
else
    echo "⚠️  Cursor IDE配置可能需要调整"
fi

echo ""
echo "🎯 保护系统测试完成！"
EOF
chmod +x "$PROJECT_ROOT/test-git-protection.sh"
echo "✅ 测试脚本已创建: test-git-protection.sh"

# 5. 创建文档
echo ""
echo "5. 📚 创建使用文档..."
cat > "$PROJECT_ROOT/docs/git-protection-setup.md" << 'EOF'
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
EOF
echo "✅ 使用文档已创建: docs/git-protection-setup.md"

# 完成安装
echo ""
echo "🎉 Git --no-verify 多层保护系统安装完成！"
echo ""
echo "📋 后续步骤："
echo "1. 重启终端或执行: source ~/.bashrc"
echo "2. 运行测试: ./test-git-protection.sh"
echo "3. 查看文档: docs/git-protection-setup.md"
echo ""
echo "⚡ 此保护系统现在将跟随项目，在任何克隆此项目的环境中都能快速激活！"
