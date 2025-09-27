# 🛡️ Cursor AI保护系统使用指南

## 🎯 目标

彻底解决Cursor AI跳过本地测试直接推送的问题，强制执行本地验证流程。

## 📋 核心原理

1. **拦截推送**：所有`git push`操作被拦截，检查本地测试通行证
2. **四层验证**：语法验证 → 环境验证 → 功能验证 → 差异验证
3. **通行证机制**：只有通过所有验证才能获得1小时有效期的推送通行证
4. **代码变更检测**：代码修改后通行证自动失效，需重新测试

## 🚀 快速开始

### 方式1：使用便捷命令

```bash
# 运行测试并生成通行证
./test

# 快速测试
./test --quick

# 检查通行证状态
./test --check

# 安全推送
./safe-push origin your-branch
```

### 方式2：使用Makefile命令

```bash
# 运行完整测试
make test

# 快速测试
make test-quick

# 检查通行证
make passport

# 安全推送
make safe-push
```

### 方式3：使用Cursor任务

1. 按 `Ctrl+Shift+P`
2. 输入 `Tasks: Run Task`
3. 选择：
   - `🧪 本地测试（生成推送通行证）`
   - `⚡ 快速测试`
   - `🎫 检查通行证状态`
   - `🚀 安全推送`

## 🔄 标准开发流程

```bash
# 1. 创建feature分支（如果还没有）
git checkout -b feature/your-feature

# 2. 进行代码修改
# ... 编码 ...

# 3. 运行本地测试获取通行证
make test
# 或者
./test

# 4. 等待验证完成，获取通行证

# 5. 提交代码
git add .
git commit -m "your commit message"

# 6. 安全推送（会自动验证通行证）
make safe-push
# 或者
git push origin feature/your-feature
```

## 🚨 被拦截了怎么办？

### 情况1：没有通行证

```
🎫🎫🎫 本地测试通行证验证失败！🎫🎫🎫
❌ 检测到推送操作，但未找到有效的本地测试通行证！
```

**解决**：运行 `make test` 或 `./test` 生成通行证

### 情况2：通行证过期

```
⚠️ 通行证已过期
```

**解决**：运行 `make test --force` 重新生成通行证

### 情况3：代码已修改

```
⚠️ 代码已修改，需要重新测试
```

**解决**：运行 `make test` 重新验证修改后的代码

### 情况4：紧急推送

如果确实需要紧急推送（极度不推荐）：

1. 环境变量绕过：

   ```bash
   export ALLOW_PUSH_WITHOUT_PASSPORT=true
   git push origin your-branch
   ```

2. 输入紧急确认码：`EMERGENCY_PUSH_BYPASS_2024`

## 🧪 测试模式说明

### 完整测试（默认）

- ✅ GitHub Actions语法验证
- ✅ Docker环境检查
- ✅ 完整功能测试（5-10分钟）
- ✅ 环境差异检查

### 快速测试（--quick）

- ✅ GitHub Actions语法验证
- ✅ Docker环境检查
- ✅ 基础功能检查（1-2分钟）
- ✅ 环境差异检查

### 单项测试

```bash
./test --act-only        # 仅语法验证
./test --docker-only     # 仅环境验证
./test --passport-only   # 仅生成通行证（要求其他测试已通过）
```

## 🛠️ 故障排除

### Python相关错误

```bash
# 确保Python3可用
python3 --version

# 如果Windows上没有python3命令
python --version  # 应该是3.x版本
```

### Docker相关错误

```bash
# 检查Docker状态
docker info

# 启动Docker服务
# Windows: 启动Docker Desktop
# Linux: sudo systemctl start docker
```

### Act相关错误

```bash
# 安装act（可选，用于GitHub Actions语法验证）
# Windows: choco install act-cli
# macOS: brew install act
# Linux: curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

## 📁 文件说明

- `scripts/local_test_passport.py` - 通行证生成器
- `scripts/git-guard.sh` - Git命令拦截器
- `scripts/one_click_test.sh` - 一键测试脚本
- `scripts/setup_cursor_protection.sh` - 保护系统安装脚本
- `test` - 便捷测试命令
- `passport` - 便捷通行证命令
- `safe-push` - 便捷推送命令

## 💡 最佳实践

1. **每次修改代码后都要重新测试**
2. **优先使用快速测试进行迭代开发**
3. **完整测试用于最终验证**
4. **保持Docker服务运行以提高测试速度**
5. **定期清理Docker镜像和容器**

## 🔧 自定义配置

### 修改通行证有效期

编辑 `scripts/local_test_passport.py`，找到：

```python
expire_time = current_time + timedelta(hours=1)  # 修改这里
```

### 添加自定义验证

在 `scripts/one_click_test.sh` 中添加你的验证逻辑。

### 修改拦截规则

编辑 `scripts/git-guard.sh` 来自定义Git命令拦截规则。

---

🎉 现在你可以放心让Cursor工作，再也不用担心它跳过本地测试直接推送了！
