# 强制本地测试系统 (Force Local Test System)

## 🎯 系统目标

**彻底解决Cursor AI跳过本地测试直接推送GitHub的问题**

基于30轮修复血泪教训，设计了一套完整的强制本地测试机制，确保任何推送到远程仓库的代码都经过了严格的本地验证。

## 📁 文档结构

```
docs/force_local_test/
├── README.md                    # 本文件，系统概览
├── ARCHITECTURE.md              # 系统架构设计
├── IMPLEMENTATION.md            # 技术实现原理
├── FILES_STRUCTURE.md           # 文件组成和作用说明
├── CROSS_WINDOWS_DEPLOYMENT.md  # 跨Windows协作部署方案
├── DEBUG_GUIDE.md               # 调试和维护指南
└── FAQ.md                       # 常见问题和解决方案
```

## 🏗️ 系统核心组件

### 1. 通行证生成器 (Passport Generator)

- **文件**: `scripts/local_test_passport.py`
- **作用**: 执行四层验证，生成推送通行证
- **特性**: 1小时有效期，代码变更自动失效

### 2. Git拦截器 (Git Interceptor)

- **文件**: `scripts/git-guard.sh` (增强版)
- **作用**: 拦截所有推送操作，验证通行证
- **特性**: 多重拦截，详细日志记录

### 3. 一键测试脚本 (One-Click Test)

- **文件**: `scripts/one_click_test.sh`
- **作用**: 整合多种验证工具，便捷执行测试
- **特性**: 支持快速/完整测试模式

### 4. 自动部署器 (Auto Deployment)

- **文件**: `scripts/setup_cursor_protection.sh`
- **作用**: 自动设置保护系统，创建便捷命令
- **特性**: 跨Windows环境兼容

## 🔄 工作流程

```
代码修改 → 尝试推送 → 拦截检查 → 要求通行证 → 本地测试 → 获得通行证 → 允许推送
```

## 🛡️ 四层验证机制

1. **语法验证** - 使用act进行GitHub Actions语法检查
2. **环境验证** - Docker配置和服务依赖检查
3. **功能验证** - 完整的本地CI/CD模拟
4. **差异验证** - 环境配置差异和兼容性检查

## 🚀 快速开始

```bash
# 1. 自动设置系统
bash scripts/setup_cursor_protection.sh

# 2. 运行本地测试
make test
# 或者
./test

# 3. 获得通行证后推送
git push origin your-branch
```

## 📊 系统特性

- ✅ **强制执行**: 无通行证不允许推送
- ✅ **时效控制**: 通行证1小时有效期
- ✅ **变更检测**: 代码修改后自动失效
- ✅ **多重拦截**: `--no-verify`、强制推送等全部拦截
- ✅ **详细日志**: 所有操作完整记录
- ✅ **跨平台**: Windows环境完美兼容
- ✅ **便捷使用**: 多种调用方式
- ✅ **团队协作**: 自动部署和同步

## 📈 解决的问题

### 之前的痛点

- Cursor每次修改完直接推送
- 跳过本地测试和验证
- 远程CI频繁失败
- 30轮修复循环

### 现在的保障

- 强制本地验证通过才能推送
- 四层验证确保代码质量
- 提前发现问题，避免远程失败
- 一次性解决，长期受益

## 🔧 系统要求

- Windows 10/11
- Docker Desktop
- Git
- Python 3.x
- Node.js (可选，用于前端项目)
- act (可选，用于GitHub Actions验证)

## 📖 详细文档

请查看各个专项文档了解更多细节：

- [架构设计](./ARCHITECTURE.md) - 系统架构和设计原理
- [技术实现](./IMPLEMENTATION.md) - 具体实现细节和技术栈
- [文件结构](./FILES_STRUCTURE.md) - 所有文件的作用和关系
- [跨平台部署](./CROSS_WINDOWS_DEPLOYMENT.md) - 团队协作和自动部署
- [调试指南](./DEBUG_GUIDE.md) - 问题排查和维护方法
- [常见问题](./FAQ.md) - FAQ和解决方案

---

**💡 设计理念**:
_"Prevention is better than cure"_ - 与其在远程CI中反复修复，不如在本地一次性验证通过。
