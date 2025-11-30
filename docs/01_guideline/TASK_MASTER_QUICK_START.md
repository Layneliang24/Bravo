# Task Master 快速开始指南

## ✅ 已完成的配置

### 1. MCP模式（Cursor集成）- 推荐使用

Task Master已作为MCP工具集成到Cursor中，无需命令行操作。

**配置文件位置**：`.cursor/mcp.json`

**已配置的API密钥**：

- ✅ OpenRouter API Key（用于主模型）
- ✅ 硅基流动 API Key（用于备用模型）

**使用方法**：

1. **重启Cursor**（让MCP配置生效）
2. 在Cursor中直接调用Task Master工具：
   - `mcp_task-master-ai_parse_prd` - 解析PRD生成任务
   - `mcp_task-master-ai_get_tasks` - 查看任务列表
   - `mcp_task-master-ai_expand_task` - 展开任务为子任务
   - 更多工具见 `.cursor/rules/taskmaster/taskmaster.mdc`

**当前模型配置**：

- 主模型：OpenRouter - deepseek/deepseek-chat
- 备用模型：Anthropic Claude（需要单独充值）
- 研究模型：Perplexity Sonar（需要单独充值）

---

## ⚠️ CLI模式的问题和解决方案

### 问题1：OpenRouter账户限制

```
Error: This request requires more credits, or fewer max_tokens.
You requested up to 64000 tokens, but can only afford 2666.
```

**原因**：OpenRouter账户余额不足

**解决方案**：

1. 访问 https://openrouter.ai/settings/credits 充值
2. 或者配置其他免费/低成本模型（如硅基流动）

### 问题2：数据政策限制

```
Error: No endpoints found matching your data policy (Paid model training)
```

**原因**：OpenRouter隐私设置需要配置

**解决方案**：
访问 https://openrouter.ai/settings/privacy 配置数据使用政策

### 问题3：Schema验证错误（硅基流动）

DeepSeek-V3返回的JSON格式不完全符合Task Master预期的schema。

**临时解决方案**：使用MCP模式，或等待Task Master更新

---

## 🎯 推荐工作流程

### 第一次使用（推荐在MCP模式）

1. **重启Cursor**
2. 创建PRD文件：`.taskmaster/docs/your_project_prd.txt`
3. 在Cursor中调用：`mcp_task-master-ai_parse_prd`
4. 查看生成的任务：`mcp_task-master-ai_get_tasks`

### 后续开发

1. 展开任务：`mcp_task-master-ai_expand_task`
2. 更新任务：`mcp_task-master-ai_update_task`
3. 设置状态：`mcp_task-master-ai_set_task_status`

---

## 📝 配置文件说明

### `.cursor/mcp.json`（MCP模式，已配置）

存放Task Master MCP工具的API密钥。

**重要**：修改后需要重启Cursor才能生效。

### `.taskmaster/config.json`（模型配置）

存放AI模型的选择和参数配置。

**当前配置**：

```json
{
  "models": {
    "main": {
      "provider": "openrouter",
      "modelId": "deepseek/deepseek-chat",
      "maxTokens": 2000,
      "temperature": 0.2
    }
  }
}
```

### `.env`（CLI模式，可选）

CLI命令行模式需要的API密钥，MCP模式不需要此文件。

---

## 🔧 下一步

### 如果使用MCP模式（推荐）

1. 重启Cursor
2. 开始使用Task Master工具
3. 如需更多功能，查阅 `.cursor/rules/taskmaster/taskmaster.mdc`

### 如果必须使用CLI模式

1. 充值OpenRouter账户：https://openrouter.ai/settings/credits
2. 配置隐私策略：https://openrouter.ai/settings/privacy
3. 或者切换到其他提供商（需要更多配置）

---

## 🆘 遇到问题？

1. 检查Cursor是否已重启（MCP配置生效需要）
2. 检查API密钥是否正确配置在 `.cursor/mcp.json`
3. 查看Task Master日志获取详细错误信息
4. 参考 `docs/01_guideline/TASK_MASTER_PROVIDERS_CONFIG.md` 了解更多配置选项
