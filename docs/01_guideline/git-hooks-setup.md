# Git 钩子设置指南

## 概述

本项目包含自定义的 Git 钩子来帮助开发者避免常见问题。

## 安装钩子

### 自动安装（推荐）

```bash
# 运行安装脚本
bash scripts/install-hooks.sh
```

### 手动安装

如果需要手动安装，可以复制以下内容到 `.git/hooks/post-checkout`：

```bash
#!/bin/sh
# 文件：.git/hooks/post-checkout
# 参数：$1=前一个HEAD $2=当前HEAD $3=1(分支切换) 0(文件切换)

# 只在分支切换/创建时运行
[ "$3" = "1" ] || exit 0

# 获取当前分支名
current_branch=$(git branch --show-current)

# 跳过 main 和 dev 分支的检查
case "$current_branch" in
    main|dev)
        exit 0
        ;;
esac

# 获取 dev 分支的最新状态
git fetch origin dev:dev 2>/dev/null

# 检查当前分支是否基于最新的 dev
if ! git merge-base --is-ancestor dev HEAD; then
    echo "⚠️  警告：当前分支基底落后于 origin/dev"
    echo "   建议执行：git rebase dev"
    echo "   或者：git merge dev"
fi
```

然后设置执行权限：

```bash
chmod +x .git/hooks/post-checkout
```

## 钩子功能

### post-checkout 钩子

- **触发时机**：每次 `git checkout` 或 `git switch` 时
- **功能**：检查当前分支是否基于最新的 dev 分支
- **警告**：如果基于旧版本，会提示同步

## 注意事项

1. **本地钩子**：Git 钩子存储在 `.git/hooks/` 目录中，不会推送到远程仓库
2. **团队协作**：每个开发者需要单独安装钩子
3. **权限设置**：确保钩子文件有执行权限

## 故障排除

如果钩子不工作：

1. 检查文件是否存在：`ls -la .git/hooks/post-checkout`
2. 检查执行权限：`chmod +x .git/hooks/post-checkout`
3. 检查文件内容是否正确
4. 重新运行安装脚本：`bash scripts/install-hooks.sh`
