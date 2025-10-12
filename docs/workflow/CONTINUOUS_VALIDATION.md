# 工作流持续验证流程

> **目标**: 确保工作流文档和实际运行100%一致
> **方法**: 自动化验证 + 强制检查 + 实时报告

---

## 🎯 核心理念

**不满意85%，追求100%准确度**

- ❌ 纸上谈兵的文档
- ✅ 实际验证确认的文档
- ✅ 每次修改自动验证
- ✅ 持续监控准确性

---

## 🔄 验证流程

### 三层验证体系

```
┌─────────────────────────────────────────┐
│  第一层：本地验证（提交前）            │
│  - Git Hook自动触发                    │
│  - act语法检查                         │
│  - 结构完整性检查                      │
│  ⏱️  耗时: 10-30秒                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  第二层：CI自动验证（推送后）          │
│  - GitHub Actions自动触发              │
│  - 多维度验证                          │
│  - 文档一致性检查                      │
│  ⏱️  耗时: 1-2分钟                     │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  第三层：实际运行验证（定期）          │
│  - 创建测试PR                          │
│  - 记录实际触发的jobs                  │
│  - 对比文档更新报告                    │
│  ⏱️  耗时: 10-15分钟                   │
└─────────────────────────────────────────┘
```

---

## 🛠️ 使用方法

### 1. 本地验证

#### 自动验证（推荐）

修改工作流文件后，git commit会自动触发验证：

```bash
git add .github/workflows/push-validation.yml
git commit -m "feat: 添加hotfix分支支持"

# 自动运行验证
# 🔍 检测到工作流文件变更，启动验证...
# ✅ 工作流验证通过
```

#### 手动验证

```bash
# 快速验证（仅结构）
bash scripts/workflow-continuous-validation.sh quick

# 完整验证（结构+语法）
bash scripts/workflow-continuous-validation.sh full

# 自动模式（检测变更）
bash scripts/workflow-continuous-validation.sh auto
```

#### 跳过验证（不推荐）

```bash
export SKIP_WORKFLOW_VALIDATION=1
git commit -m "..."
```

### 2. CI自动验证

推送到远程后，GitHub Actions自动运行：

```yaml
# 自动触发条件：
- PR修改了.github/workflows/**
- Push到main/dev且修改了工作流
```

**查看结果：**

1. PR页面 → Checks标签
2. 查看"Workflow Validation Monitor"
3. 阅读Summary报告

### 3. 定期完整验证

**每周/每月执行一次：**

```bash
# 1. 创建测试分支
git checkout -b test/workflow-validation-$(date +%s)

# 2. 创建测试PR
gh pr create --base dev --title "test: workflow validation" \
  --body "定期验证工作流准确性"

# 3. 记录实际运行结果
gh pr checks [PR_NUMBER]

# 4. 对比文档，更新准确度报告
# 记录到 docs/workflow/VALIDATION_ACCURACY_REPORT.md

# 5. 清理测试分支
gh pr close [PR_NUMBER]
git branch -D test/workflow-validation-*
```

---

## 📊 准确度监控

### 准确度计算公式

```
准确度 = (实际一致项 / 文档声明总项) × 100%

实际一致项：
  - 工作流触发条件 ✓
  - Jobs数量 ✓/✗
  - 检查项内容 ✓
  - 验证级别 ✓
  - 覆盖率要求 ✓
  ...

目标：≥ 95%
```

### 当前准确度追踪

| 验证日期   | 验证方法        | 准确度 | 主要差异         |
| ---------- | --------------- | ------ | ---------------- |
| 2025-10-12 | PR #151实际运行 | 85%    | Jobs数量统计粒度 |
| TBD        | 定期验证        | TBD    | TBD              |

---

## 🔍 验证检查项

### 本地验证检查项

- [x] 工作流文件语法正确
- [x] 必要字段完整（name, on, jobs）
- [x] act可以解析
- [x] Jobs可以列出
- [x] 条件表达式语法正确

### CI自动验证检查项

- [x] 语法验证（act）
- [x] 结构验证
- [x] 文档更新提醒
- [x] 生成验证报告

### 定期完整验证检查项

- [ ] 实际触发的工作流数量
- [ ] 实际执行的jobs数量
- [ ] 每个job的运行时间
- [ ] 实际的检查项内容
- [ ] 条件跳过的jobs
- [ ] 覆盖率要求验证
- [ ] 文档一致性对比

---

## ⚙️ 配置文件

### scripts/workflow-continuous-validation.sh

主验证脚本，支持三种模式：

- `auto`: 自动检测变更
- `quick`: 快速结构验证
- `full`: 完整验证

### .husky/pre-commit-workflow-validation

Git Hook，在提交前自动验证工作流文件。

### .github/workflows/workflow-validation-monitor.yml

CI监控工作流，自动验证工作流变更。

---

## 🚨 故障排查

### 验证失败常见原因

1. **act语法检查失败**

   ```bash
   # 手动测试
   act -l -W .github/workflows/your-workflow.yml

   # 查看详细错误
   act push -W .github/workflows/your-workflow.yml -n
   ```

2. **结构验证失败**

   ```bash
   # 检查必要字段
   grep "^name:" .github/workflows/your-workflow.yml
   grep "^on:" .github/workflows/your-workflow.yml
   grep "^jobs:" .github/workflows/your-workflow.yml
   ```

3. **CI验证超时**
   - act验证服务容器时可能panic
   - 这是已知限制，不影响实际运行
   - 结构验证会通过

---

## 📈 持续改进

### 提高准确度的方法

1. **细化文档粒度**

   - 区分"stages"和"jobs"
   - 添加运行时间参考
   - 说明条件跳过逻辑

2. **增加验证频率**

   - 每次修改工作流立即验证
   - 每周定期完整验证
   - 每月对比准确度

3. **自动化文档更新**

   - 从实际运行结果生成文档
   - 自动对比差异
   - PR中自动提醒更新

4. **建立反馈循环**
   ```
   修改工作流 → 本地验证 → CI验证 → 实际运行
        ↑                                    ↓
        └────────── 更新文档 ←────────────┘
   ```

---

## 🎯 下一步计划

### 短期（1-2周）

- [ ] 部署持续验证流程
- [ ] 运行完整验证获取基线
- [ ] 修正文档达到95%准确度

### 中期（1个月）

- [ ] 自动化文档生成
- [ ] 建立准确度仪表板
- [ ] 集成到开发工作流

### 长期（持续）

- [ ] 机器学习辅助验证
- [ ] 自动发现差异并修正
- [ ] 实时准确度监控

---

## 📚 相关文档

- [工作流场景验证](./WORKFLOW_SCENARIO_VALIDATION.md)
- [工作流覆盖缺口修复](./WORKFLOW_COVERAGE_FIX.md)
- [工作流迁移映射](./workflow-migration-mapping.md)

---

## 💡 最佳实践

### DO ✅

- 每次修改工作流后立即验证
- 定期运行完整验证对比文档
- 记录验证结果并更新准确度
- 自动化所有可以自动化的验证

### DON'T ❌

- 不要跳过本地验证
- 不要相信"应该能工作"
- 不要让文档和实际脱节
- 不要满足于85%准确度

---

**目标**: 100%准确度
**方法**: 持续验证
**态度**: 不满意就改进

---

**文档维护者**: Claude 3.7 Sonnet (claude-sonnet-4-20250514)
**最后更新**: 2025-10-12
**验证状态**: 🚧 部署中
