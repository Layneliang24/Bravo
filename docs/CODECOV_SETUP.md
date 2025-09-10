# Codecov 配置指南

## 问题描述

当前遇到 Codecov 速率限制错误：
```
429 - {"message":"Rate limit reached. Please upload with the Codecov repository upload token to resolve issue. Expected time to availability: 2193s."}
```

## 解决方案

### 方案 1：配置 Codecov Token（推荐）

1. **获取 Token**：
   - 访问 [Codecov.io](https://codecov.io)
   - 登录 GitHub 账户
   - 选择 `Layneliang24/Bravo` 仓库
   - 在 Settings > General 中找到 "Repository Upload Token"

2. **配置 GitHub Secrets**：
   - 在 GitHub 仓库中，进入 Settings > Secrets and variables > Actions
   - 添加新的 Secret：
     - Name: `CODECOV_TOKEN`
     - Value: 从 Codecov 复制的 token

3. **更新工作流配置**：
   ```yaml
   - name: Upload Coverage to Codecov
     uses: codecov/codecov-action@v3
     with:
       token: ${{ secrets.CODECOV_TOKEN }}
       files: ./coverage-frontend.lcov,./coverage-backend.xml
       flags: unittests
       name: codecov-umbrella
       fail_ci_if_error: true
   ```

### 方案 2：临时禁用（当前方案）

当前已配置 `continue-on-error: true` 和 `fail_ci_if_error: false`，这样：
- CI 不会因为 Codecov 上传失败而中断
- 覆盖率报告仍会生成并保存为 artifacts
- 可以稍后手动上传到 Codecov

### 方案 3：使用其他覆盖率服务

可以考虑使用：
- **Coveralls**
- **Code Climate**
- **SonarCloud**

## 当前状态

- ✅ 覆盖率报告正常生成
- ✅ 报告保存为 GitHub Actions artifacts
- ⚠️ Codecov 上传因速率限制失败（已配置忽略错误）
- 🔄 等待速率限制解除或配置 token

## 下一步

1. **短期**：继续使用当前配置，CI 正常运行
2. **长期**：配置 Codecov token 以获得完整功能
3. **备选**：考虑迁移到其他覆盖率服务

## 相关文件

- `.github/workflows/gate.yml` - 主要测试工作流
- `.github/workflows/ci.yml` - CI 工作流
- `codecov.yml` - Codecov 配置文件
- `docs/CODECOV_SETUP.md` - 本说明文档
