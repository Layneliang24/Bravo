#!/bin/bash
# 安装项目钩子脚本

echo "🔧 安装 Git 钩子..."

# 创建钩子目录（如果不存在）
mkdir -p .git/hooks

# 安装 post-checkout 钩子
cat > .git/hooks/post-checkout << 'EOF'
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
EOF

# 设置执行权限
chmod +x .git/hooks/post-checkout

echo "✅ post-checkout 钩子安装完成"
echo "💡 现在每次切换分支时会自动检查是否基于最新的 dev 分支"
