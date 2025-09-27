# 强制本地测试系统 - 常见问题FAQ

## 🚀 快速问题定位

### 问题分类索引

```
🎫 通行证相关问题 (Q1-Q8)
├─ Q1: 推送被拦截，要求通行证
├─ Q2: 通行证过期或失效
├─ Q3: 无法生成通行证
└─ Q4: 通行证验证异常

🐳 Docker环境问题 (Q5-Q10)
├─ Q5: Docker服务未启动
├─ Q6: docker-compose配置错误
├─ Q7: 容器启动失败
└─ Q8: 镜像拉取失败

⚡ 性能和超时问题 (Q9-Q12)
├─ Q9: 测试执行太慢
├─ Q10: 验证超时
├─ Q11: 内存不足
└─ Q12: 磁盘空间不足

🔧 安装和配置问题 (Q13-Q18)
├─ Q13: 自动安装失败
├─ Q14: Python环境问题
├─ Q15: Git拦截不生效
└─ Q16: Windows环境兼容性

🤝 团队协作问题 (Q17-Q20)
├─ Q17: 团队成员环境不一致
├─ Q18: 配置文件冲突
├─ Q19: 系统更新同步
└─ Q20: 权限和访问问题
```

---

## 🎫 通行证相关问题

### Q1: 推送时被拦截，提示需要通行证

**问题现象**:

```
🎫🎫🎫 本地测试通行证验证失败！🎫🎫🎫
❌ 检测到推送操作，但未找到有效的本地测试通行证！
```

**解决方案**:

```bash
# 方案1: 运行完整测试
make test
# 或者
./test

# 方案2: 快速测试 (推荐日常开发)
make test-quick
# 或者
./test --quick

# 方案3: 检查当前通行证状态
./passport --check
```

**根本原因**: 系统设计就是要求推送前必须通过本地测试，这是预期行为。

---

### Q2: 通行证过期或代码修改后失效

**问题现象**:

```
🚫 当前通行证状态：❌ 无效
💬 原因：通行证已过期 / 代码已修改，需要重新测试
```

**解决方案**:

```bash
# 强制重新生成通行证
./passport --force

# 或直接运行测试
./test --quick
```

**设计说明**:

- 通行证有效期1小时，防止推送过时代码
- 代码修改后自动失效，确保最新代码经过测试

---

### Q3: 本地测试无法通过，无法生成通行证

**问题现象**:

```
❌ 以下验证失败：语法验证 / 环境验证 / 功能验证
🚫 通行证生成失败
```

**解决方案**:

**Step 1: 分层诊断**

```bash
# 单独测试各层
./test --act-only      # 仅语法验证
./test --docker-only   # 仅环境验证

# 查看详细错误信息
./test --full 2>&1 | tee test_debug.log
```

**Step 2: 常见问题修复**

```bash
# Docker相关
docker info                    # 检查Docker状态
docker-compose config         # 验证配置
docker system prune -f        # 清理资源

# Python相关
python3 --version            # 检查Python版本
python3 scripts/local_test_passport.py --check  # 直接测试脚本
```

**Step 3: 使用快速模式绕过非关键验证**

```bash
# 快速模式跳过耗时的完整CI模拟
./test --quick
```

---

### Q4: 通行证文件损坏或格式错误

**问题现象**:

```
通行证文件格式损坏，需要重新生成
```

**解决方案**:

```bash
# 删除损坏的通行证文件
rm -f .git/local_test_passport.json

# 重新生成
./test --force
```

**预防措施**: 不要手动编辑 `.git/local_test_passport.json` 文件

---

## 🐳 Docker环境问题

### Q5: Docker服务未启动

**问题现象**:

```
❌ Docker服务异常
Cannot connect to the Docker daemon
```

**解决方案**:

**Windows**:

```bash
# 启动Docker Desktop
# 1. 双击桌面Docker Desktop图标
# 2. 等待Docker启动完成
# 3. 重新运行测试

# 验证Docker状态
docker info
```

**Linux**:

```bash
# 启动Docker服务
sudo systemctl start docker

# 设置自动启动
sudo systemctl enable docker

# 将用户添加到docker组
sudo usermod -aG docker $USER
```

---

### Q6: docker-compose配置错误

**问题现象**:

```
❌ docker-compose配置无效
ERROR: Invalid interpolation format
```

**解决方案**:

```bash
# 检查配置文件语法
docker-compose config

# 常见问题修复
# 1. 环境变量格式问题
sed -i 's/\${([^}]*)}/\${\1}/g' docker-compose.yml

# 2. 版本兼容性问题
# 删除过时的version字段
sed -i '/^version:/d' docker-compose.yml

# 3. 服务名称冲突
docker-compose down
docker-compose up -d
```

---

### Q7: 容器启动失败或崩溃

**问题现象**:

```
⚠️ MySQL服务启动超时
Container exited with code 1
```

**解决方案**:

```bash
# 查看容器日志
docker-compose logs mysql
docker-compose logs backend
docker-compose logs frontend

# 重新启动服务
docker-compose down
docker-compose up -d

# 清理并重建
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

**常见原因**:

- 端口冲突 (3306, 6379, 8000, 3000)
- 磁盘空间不足
- 内存不够

---

### Q8: Docker镜像拉取失败

**问题现象**:

```
Error pulling image: timeout
network timeout
```

**解决方案**:

**中国大陆用户**:

```bash
# 配置Docker镜像加速
mkdir -p ~/.docker
cat > ~/.docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF

# 重启Docker服务
# Windows: 重启Docker Desktop
# Linux: sudo systemctl restart docker
```

**其他地区用户**:

```bash
# 重试拉取
docker-compose pull

# 使用代理 (如果有)
docker-compose --env-file .env.proxy up -d
```

---

## ⚡ 性能和超时问题

### Q9: 测试执行太慢，影响开发效率

**问题现象**:

```
⏱️ 耗时：300秒+ (5分钟以上)
```

**解决方案**:

**日常开发使用快速模式**:

```bash
# 快速模式 (1-2分钟)
./test --quick

# 只在重要推送前使用完整模式
./test --full
```

**性能优化**:

```bash
# 1. 清理Docker缓存
docker system prune -f

# 2. 使用本地缓存
npm config set cache ~/.npm-cache
pip3 config set global.cache-dir ~/.pip-cache

# 3. 并行执行优化
export DOCKER_PARALLEL=true
```

**硬件优化建议**:

- 使用SSD硬盘
- 增加内存到16GB+
- 为Docker分配足够资源

---

### Q10: 验证过程超时

**问题现象**:

```
⏰ 功能测试超时（5分钟）
TimeoutExpired
```

**解决方案**:

```bash
# 1. 增加超时时间 (临时)
timeout 900 ./test --full  # 15分钟

# 2. 分步执行诊断
./test --act-only      # 先测试语法
./test --docker-only   # 再测试环境
./test --quick         # 最后快速功能测试

# 3. 检查系统资源
docker stats
htop
```

---

### Q11: 内存不足导致测试失败

**问题现象**:

```
OOMKilled
Container killed due to OOM
内存不足
```

**解决方案**:

```bash
# 1. 为Docker分配更多内存
# Docker Desktop → Settings → Resources → Memory (推荐8GB+)

# 2. 关闭其他应用
# 关闭浏览器、IDE等占用内存的应用

# 3. 清理内存
docker system prune -f --volumes
npm cache clean --force

# 4. 分批执行测试
./test --quick  # 使用轻量级测试
```

---

### Q12: 磁盘空间不足

**问题现象**:

```
No space left on device
磁盘使用率过高: 90%+
```

**解决方案**:

```bash
# 1. 清理Docker资源
docker system df              # 查看Docker磁盘使用
docker system prune -a -f     # 清理所有未使用资源
docker volume prune -f        # 清理卷

# 2. 清理系统缓存
npm cache clean --force
pip3 cache purge
rm -rf ~/.cache/*

# 3. 清理项目文件
rm -rf node_modules/
rm -rf logs/*.log
rm -rf test-results/
```

---

## 🔧 安装和配置问题

### Q13: 自动安装脚本执行失败

**问题现象**:

```
bash: scripts/setup_cursor_protection.sh: Permission denied
No such file or directory
```

**解决方案**:

```bash
# 1. 检查文件是否存在
ls -la scripts/setup_cursor_protection.sh

# 2. 添加执行权限
chmod +x scripts/setup_cursor_protection.sh

# 3. 重新运行安装
bash scripts/setup_cursor_protection.sh

# 4. 如果文件缺失，从Git重新获取
git checkout HEAD -- scripts/
```

---

### Q14: Python环境问题

**问题现象**:

```
python3: command not found
ModuleNotFoundError: No module named 'xxx'
```

**解决方案**:

**Windows**:

```bash
# 1. 检查Python安装
python --version   # Windows通常使用python而不是python3
py -3 --version    # Python Launcher

# 2. 如果未安装，下载安装Python 3.8+
# https://python.org/downloads/

# 3. 修复便捷命令
./passport --check  # 脚本会自动适配python/python3
```

**Linux/macOS**:

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS
brew install python3
```

---

### Q15: Git拦截不生效，仍能直接推送

**问题现象**:

```
git push 没有被拦截，直接推送成功了
```

**解决方案**:

**检查Git Guard是否安装**:

```bash
# 1. 检查别名设置
git config --list | grep alias

# 2. 手动测试拦截
bash scripts/git-guard.sh push origin test

# 3. 重新设置别名
git config alias.push '!bash scripts/git-guard.sh push'
```

**确保PATH优先级**:

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias git='bash "/path/to/project/scripts/git-guard.sh"'

# 重新加载配置
source ~/.bashrc
```

**Cursor特定设置**:

```json
// .vscode/settings.json
{
  "git.allowNoVerifyCommit": false,
  "terminal.integrated.shellArgs.windows": ["-l"]
}
```

---

### Q16: Windows环境兼容性问题

**问题现象**:

```
路径格式错误
CRLF换行符问题
权限错误
```

**解决方案**:

**路径问题**:

```bash
# Git Bash中路径转换
PROJECT_ROOT=$(cygpath -m "$PROJECT_ROOT")

# WSL中Windows路径访问
cd /mnt/c/path/to/project
```

**换行符问题**:

```bash
# 配置Git处理换行符
git config core.autocrlf true
git config core.safecrlf warn

# 批量转换现有文件
dos2unix scripts/*.sh
```

**权限问题**:

```bash
# WSL中修复权限
sudo chown -R $USER:$USER .
chmod +x scripts/*.sh scripts/*.py
```

---

## 🤝 团队协作问题

### Q17: 团队成员环境不一致

**问题现象**:

```
A成员可以正常使用，B成员报错
不同电脑上表现不同
```

**解决方案**:

**环境标准化**:

```bash
# 1. 生成环境信息
./test --check > my_environment.txt

# 2. 团队成员对比环境差异
diff member_a_env.txt member_b_env.txt

# 3. 统一环境配置
bash scripts/setup_cursor_protection.sh --team-sync
```

**版本对齐**:

```bash
# 确保所有人使用相同版本
git pull origin main
bash scripts/setup_cursor_protection.sh --update

# 检查关键工具版本
docker --version
python3 --version
git --version
```

---

### Q18: 配置文件冲突

**问题现象**:

```
.vscode/tasks.json 合并冲突
Makefile 冲突
```

**解决方案**:

```bash
# 1. 保留团队标准配置
git checkout --theirs .vscode/tasks.json

# 2. 或保留个人配置
git checkout --ours .vscode/tasks.json

# 3. 重新运行设置脚本合并
bash scripts/setup_cursor_protection.sh --merge-config

# 4. 手动合并后重新安装
bash scripts/setup_cursor_protection.sh --force
```

---

### Q19: 系统更新后其他成员没有同步

**问题现象**:

```
系统更新了，但团队其他成员还在用旧版本
新功能不可用
```

**解决方案**:

**自动同步机制**:

```bash
# 1. 确保安装了Git钩子
ls -la .git/hooks/post-merge

# 2. 手动安装钩子 (如果缺失)
bash scripts/setup_cursor_protection.sh --install-hooks

# 3. 通知团队成员更新
git commit -m "update: 请拉取最新版本并运行 bash scripts/setup_cursor_protection.sh --update"
```

**版本检查**:

```bash
# 创建版本检查脚本
echo "$(date): $(git rev-parse HEAD)" > .force_local_test_version

# 团队成员检查版本
cat .force_local_test_version
```

---

### Q20: 团队新成员首次使用困难

**问题现象**:

```
新成员不知道怎么使用
缺少培训和文档
```

**解决方案**:

**快速入门流程**:

```bash
# 1. 自动检测和引导
if [[ -f "scripts/setup_cursor_protection.sh" ]] && [[ ! -f ".force_local_test_setup_done" ]]; then
    echo "🎉 欢迎！检测到强制本地测试系统，正在引导设置..."
    bash scripts/setup_cursor_protection.sh --new-user
    touch .force_local_test_setup_done
fi

# 2. 创建新用户指南
cat > QUICK_START.md << 'EOF'
# 5分钟快速开始

1. 自动安装: `bash scripts/setup_cursor_protection.sh`
2. 运行测试: `make test`
3. 安全推送: `make safe-push`

详细文档: docs/CURSOR_PROTECTION_GUIDE.md
EOF
```

**培训检查清单**:

- [ ] 理解系统目的（防止跳过本地测试）
- [ ] 学会基本命令（test, passport, safe-push）
- [ ] 知道如何查看日志和排错
- [ ] 了解团队协作流程

---

## 🆘 紧急情况处理

### 紧急绕过系统（极度不推荐）

**场景**: 生产环境紧急修复，无法等待本地测试

**临时绕过方案**:

```bash
# 方案1: 环境变量绕过
export ALLOW_PUSH_WITHOUT_PASSPORT=true
git push origin hotfix/critical-fix
unset ALLOW_PUSH_WITHOUT_PASSPORT

# 方案2: 紧急确认码
# 推送时输入: EMERGENCY_PUSH_BYPASS_2024

# 方案3: 临时禁用拦截
mv scripts/git-guard.sh scripts/git-guard.sh.disabled
git push origin hotfix/critical-fix
mv scripts/git-guard.sh.disabled scripts/git-guard.sh
```

**⚠️ 重要提醒**:

- 所有绕过操作都会被详细记录
- 紧急修复后必须补充本地测试
- 建议尽快恢复正常流程

---

## 📞 获取更多帮助

### 文档资源

- [使用指南](../CURSOR_PROTECTION_GUIDE.md) - 详细使用说明
- [架构设计](./ARCHITECTURE.md) - 系统设计原理
- [技术实现](./IMPLEMENTATION.md) - 实现细节
- [调试指南](./DEBUG_GUIDE.md) - 高级故障排查

### 日志和诊断

```bash
# 查看详细日志
tail -50 logs/git-no-verify-attempts.log
tail -50 logs/local_test_passport.log

# 系统健康检查
bash scripts/system_health_check.sh

# 生成诊断报告
./test --check > diagnostic_report.txt 2>&1
```

### 社区支持

- 在项目Issue中报告问题
- 提供详细的错误信息和系统环境
- 包含相关日志文件

---

**💡 最佳实践提醒**:

- 优先使用 `--quick` 模式进行日常开发
- 定期清理Docker资源避免性能问题
- 遇到问题先查看日志和运行健康检查
- 团队协作时及时同步系统更新
