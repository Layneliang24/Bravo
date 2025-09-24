#!/bin/bash
# Git安全拦截器一键安装
echo "���️ 安装Git安全拦截器..."

# 方法1: 设置shell别名 (推荐)
echo "alias git='bash \"\$(pwd)/scripts/git-interceptor\"'" >> ~/.bashrc

# 方法2: 设置Git别名到项目配置
git config --local alias.add "!bash scripts/git-interceptor add"
git config --local alias.commit "!bash scripts/git-interceptor commit"
git config --local alias.push "!bash scripts/git-interceptor push"

echo "✅ 安装完成！重启终端或运行: source ~/.bashrc"
