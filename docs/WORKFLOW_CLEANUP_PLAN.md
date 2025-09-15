# 🧹 工作流彻底清理方案

## 问题分析

- **28个workflow文件** - 太他妈多了！
- **功能严重重叠**：10个test文件，3个dev文件
- **虚假成功**：大量条件跳过导致测试没真正运行
- **持续叠加**：不断新增而不是修复现有

## 清理方案

### 🎯 保留核心4个文件：

1. **`pr-validation.yml`** - PR验证（feature → dev）
2. **`dev-merge.yml`** - Dev合并验证（合并后端到端测试）
3. **`main-release.yml`** - Main发布验证
4. **`regression-scheduled.yml`** - 定时回归测试

### 🗑️ 删除重复文件：

```bash
# Dev重复文件
on-merge-dev.yml              # 删除，保留optimized版本并重命名
on-merge-dev-optimized.yml    # 重命名为dev-merge.yml
on-push-dev.yml               # 删除，功能合并到dev-merge

# Test重复文件
test-backend.yml              # 删除，合并到core
test-frontend.yml             # 删除，合并到core
test-e2e.yml                  # 删除，合并到core
test-e2e-full.yml            # 删除，合并到core
test-e2e-smoke.yml           # 删除，合并到core
test-unit-backend.yml        # 删除，合并到core
test-unit-frontend.yml       # 删除，合并到core
test-integration.yml         # 删除，合并到core
test-regression.yml          # 删除，功能移到scheduled

# 其他冗余文件
branch-protection.yml         # 合并到core validation
cache-strategy.yml           # 合并到setup actions
setup-cache.yml              # 合并到setup actions
quality-*.yml (3个)          # 合并到core validation
```

### ✅ 最终结构：

```
.github/workflows/
├── pr-validation.yml        # PR验证（所有检查）
├── dev-merge.yml            # Dev合并验证
├── main-release.yml         # Main发布
└── regression-scheduled.yml # 定时回归
```

**从28个文件 → 4个文件**
