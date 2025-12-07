# Pre-commit 优化指南

## 问题：为什么pre-commit总是要跑两遍？

### 根本原因

Pre-commit hooks的工作机制：

1. **第一遍**：检查文件，如果发现格式问题（如black、prettier、end-of-file-fixer），**自动修复**并返回非0退出码
2. **第二遍**：修复后的文件需要重新暂存并提交，再次运行检查确认通过

这是**pre-commit工具的正常行为**，不是bug。

### 为什么这样设计？

- **自动修复**：让开发者不需要手动运行格式化工具
- **确保一致性**：修复后的文件必须重新提交，确保仓库中都是格式化后的代码
- **防止遗漏**：如果直接通过，可能忘记提交修复后的文件

## 优化方案

### 方案1：提交前手动格式化（推荐）

在提交前手动运行格式化工具，避免pre-commit自动修复：

```bash
# 格式化Python代码
black backend/
isort backend/

# 格式化前端代码
prettier --write "frontend/**/*.{js,ts,tsx,vue,json,css}"

# 修复文件结尾
pre-commit run end-of-file-fixer --all-files

# 然后再提交
git add .
git commit -m "..."
```

### 方案2：配置IDE自动格式化

在VSCode/Cursor中配置保存时自动格式化：

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true
  }
}
```

### 方案3：使用pre-commit的缓存机制

Pre-commit会自动缓存已格式化的文件，但需要：

- 文件内容不变时，不会重新检查
- 第一次检查后，后续检查会更快

### 方案4：调整hook顺序（已实施）

在`.code-quality-config.yaml`中，快速检查（如`end-of-file-fixer`）已经放在前面，这样可以：

- 快速发现并修复简单问题
- 避免在复杂检查上浪费时间

## 当前配置分析

查看`.code-quality-config.yaml`，当前顺序：

1. ✅ `trailing-whitespace` - 快速检查
2. ✅ `end-of-file-fixer` - 快速修复
3. ✅ `black` - Python格式化
4. ✅ `prettier` - 前端格式化

这个顺序已经优化过了，但**自动修复机制**仍然需要两遍提交。

## 最佳实践

1. **开发时**：配置IDE自动格式化，保存时自动修复
2. **提交前**：运行`pre-commit run --all-files`检查所有文件
3. **提交时**：如果pre-commit修复了文件，重新添加并提交

## 时间成本分析

- **第一遍**：~30-60秒（检查+自动修复）
- **第二遍**：~10-20秒（验证修复后的文件）
- **总耗时**：~40-80秒

如果使用方案1（提交前手动格式化）：

- **手动格式化**：~10-20秒
- **提交检查**：~10-20秒
- **总耗时**：~20-40秒（节省50%时间）

## 建议

**立即实施**：

1. 配置IDE自动格式化（方案2）
2. 提交前运行格式化工具（方案1）

**长期优化**：

1. 考虑使用Git hooks直接调用格式化工具，而不是pre-commit
2. 或者接受pre-commit的两遍机制，作为代码质量保障
