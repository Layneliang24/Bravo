# 目录守卫系统使用指南

## 🎯 系统概述

目录守卫系统是一个三层防护机制，确保AI生成的文件、测试脚本和文档都放置在正确的目录位置，防止根目录混乱。

## 🛡️ 三层防护机制

### 第一层：Cursor AI规则（智能指引）

- **文件位置**：`.cursor/rules/directory_guard.mdc`
- **作用**：AI生成前读取规则，自动拒绝违规请求
- **规则**：禁止根目录新增.md、.txt、test\_\*.py等文件

### 第二层：本地提交钩子（强制拦截）

- **文件位置**：`.git/hooks/pre-commit`
- **作用**：本地commit前自动检查
- **拦截**：根目录违规文件无法提交

### 第三层：CI哨兵（远程验证）

- **文件位置**：`.github/workflows/dir_guard.yml`
- **作用**：PR阶段强制检查
- **结果**：违规文件导致CI失败

## 📁 文件放置规则

### ✅ 允许放置

| 文件类型 | 正确位置                    | 示例                                     |
| -------- | --------------------------- | ---------------------------------------- |
| 产品文档 | `docs/00_product/`          | `docs/00_product/feature_guide.md`       |
| 使用指南 | `docs/01_guideline/`        | `docs/01_guideline/api_usage.md`         |
| 测试报告 | `docs/02_test_report/`      | `docs/02_test_report/sprint1_report.md`  |
| 操作文档 | `docs/03_operate/`          | `docs/03_operate/deployment_guide.md`    |
| 后端测试 | `backend/apps/*/tests/`     | `backend/apps/user/tests/test_models.py` |
| 前端测试 | `frontend/src/**/*.spec.ts` | `frontend/src/components/Button.spec.ts` |

### ❌ 禁止放置

**根目录禁止**：

- `*.md`（除README.md、LICENSE）
- `*.txt`
- `test_*.py`
- `*_test.py`
- `*.keep`
- `*.example`

## 🚀 快速开始

### 1. 安装钩子

```bash
pre-commit install
```

### 2. 验证系统

```bash
./scripts/test_directory_guard.sh
```

### 3. 使用AI文档生成

通过Cursor命令面板：

```
> MCP: Generate onboarding guide
→ 自动生成到 docs/01_guideline/onboarding.md
```

## 🛠️ 误操作补救

### 一键清理

```bash
make move-clutter
```

### 手动移动

```bash
# 将根目录的.md文件移动到正确位置
mv *.md docs/00_product/
mv test_*.py backend/apps/tests/
```

## 🔧 自定义规则

### 添加新规则

1. **Cursor规则**：编辑`.cursor/rules/directory_guard.mdc`
2. **本地钩子**：编辑`.pre-commit-config.yaml`
3. **CI检查**：编辑`.github/workflows/dir_guard.yml`

### 修改文件类型

在以下文件中更新正则表达式：

- `.cursor/rules/directory_guard.mdc`
- `.pre-commit-config.yaml`
- `.github/workflows/dir_guard.yml`

## 📊 监控和验证

### 本地验证

```bash
# 测试目录守卫
./scripts/test_directory_guard.sh

# 检查文件状态
git status
```

### CI验证

每个PR会自动触发目录检查，违规文件会导致：

- ❌ CI状态失败
- 📋 PR评论提示
- 🔗 详细错误信息

## 🎯 最佳实践

### 开发流程

1. **创建新文档** → 直接放入`docs/`对应子目录
2. **编写测试** → 放入对应模块的`tests/`目录
3. **提交前检查** → 运行`git status`确认文件位置
4. **PR前验证** → 确保CI通过

### AI协作

- 使用`doc_writer`工具自动生成文档到正确位置
- 避免手动在根目录创建文件
- 利用Cursor规则自动指引

## 🚨 故障排除

### 常见问题

**Q: 文件被误拦截**
A: 检查文件扩展名和路径，使用`make move-clutter`补救

**Q: pre-commit钩子不生效**
A: 运行`pre-commit install`重新安装钩子

**Q: CI检查失败**
A: 查看CI日志，将违规文件移动到正确位置

**Q: 需要例外规则**
A: 在对应配置文件中添加例外规则，或联系管理员

## 📞 支持

- **问题反馈**：创建Issue并标记`directory-guard`
- **规则更新**：提交PR修改对应配置文件
- **紧急修复**：使用`make move-clutter`一键清理
