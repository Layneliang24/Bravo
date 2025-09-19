# CI工作流程图

## CI问题修复完整流程

```mermaid
flowchart TD
    A[开始CI修复任务] --> B[1. 查看FUCKING_CI.md了解已尝试方案]
    B --> C[2. 在FUCKING_CI.md新增记录项]
    C --> D[3. 在feature分支进行修复并提交]
    D --> E[4. 推送feature分支]
    E --> F[5. 创建feature到dev的PR]
    F --> G[6. 等待60秒]
    G --> H{PR工作流是否全部执行完毕?}
    H -->|否| G
    H -->|是| I{PR工作流是否完全通过?}
    I -->|否| J[记录失败原因到FUCKING_CI.md]
    J --> B
    I -->|是| K[7. 合并PR到dev分支]
    K --> L[8. 等待60秒]
    L --> M{Post Merge工作流是否全部执行完毕?}
    M -->|否| L
    M -->|是| N{Post Merge工作流是否完全通过?}
    N -->|否| O[记录失败原因到FUCKING_CI.md]
    O --> B
    N -->|是| P[9. 任务完成]

    style A fill:#e1f5fe
    style P fill:#c8e6c9
    style B fill:#fff3e0
    style C fill:#fff3e0
    style J fill:#ffebee
    style O fill:#ffebee
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style M fill:#f3e5f5
    style N fill:#f3e5f5
```

## 关键节点说明

### 📋 记录节点 (橙色)

- **步骤1**: 查看FUCKING_CI.md了解历史尝试
- **步骤2**: 记录新的修复方案

### 🔄 循环监控节点 (紫色)

- **步骤6**: 监控PR工作流状态
- **步骤8**: 监控Post Merge工作流状态
- 使用60秒间隔，避免频繁查询

### ❌ 失败处理节点 (红色)

- PR工作流失败 → 记录原因并重新开始
- Post Merge工作流失败 → 记录原因并重新开始

### ✅ 成功节点 (绿色)

- 所有工作流通过，任务完成

## 监控工具推荐

```bash
# 使用GitHub CLI监控PR状态
gh pr view <PR-NUMBER> --json statusCheckRollup

# 使用GitHub CLI监控工作流
gh run list --branch dev --limit 5

# 等待60秒（避免使用watch参数）
sleep 60
```

## 重要提醒

⚠️ **循环原则**: 任何工作流失败都回到步骤1，重新分析和规划
🕐 **时间间隔**: 严格遵守60秒监控间隔，保持动态对话
📝 **记录完整**: 每次失败都要在FUCKING_CI.md中详细记录原因和证据
🔧 **工具使用**: 优先使用GitHub CLI、act等工具，避免手动操作
