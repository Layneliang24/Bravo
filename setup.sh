#!/bin/bash
# 一键设置Git安全拦截器
echo "���️ 设置Git安全拦截器..."

# 设置alias
echo "alias git='bash \"$(pwd)/scripts/git-interceptor\"'" >> ~/.bashrc
source ~/.bashrc 2>/dev/null || true

echo "✅ Git安全拦截器已设置！"
echo "��� 请重启终端或运行：source ~/.bashrc"
echo "��� 现在所有Git操作都会被安全检查！"
