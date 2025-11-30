# Task Master 配置指南

## ✅ 当前可用模式

### MCP模式（推荐，已配置完成）

在Cursor中直接使用Task Master工具，无需命令行：

- ✅ OpenRouter密钥已配置
- ✅ 可以直接使用
- ✅ 重启Cursor后生效

### CLI模式（需要额外配置）

命令行模式需要额外配置，见下方说明。

---

> **完成状态**: 2025-11-30
> **Task Master版本**: v0.36.0

---

## ✅ 已完成配置

### 1. Task Master初始化

```bash
✅ 项目结构创建完成
✅ 配置文件生成完成 (.taskmaster/config.json)
✅ MCP工具集成完成 (.cursor/mcp.json)
✅ 默认AI模型配置完成
```

### 2. 清理完成

```bash
✅ 删除不需要的编辑器配置 (AGENT.md, GEMINI.md, opencode.json)
✅ 保留核心配置 (.taskmaster/, .cursor/, CLAUDE.md)
```

---

## ⚠️ 待完成：配置API密钥

### 当前AI模型配置

| 角色         | 提供商     | 模型                       | SWE得分   | 成本   |
| ------------ | ---------- | -------------------------- | --------- | ------ |
| **Main**     | Anthropic  | claude-3-7-sonnet-20250219 | 62.3% ★★☆ | $3/$15 |
| **Research** | Perplexity | sonar-pro                  | N/A       | $3/$15 |
| **Fallback** | Anthropic  | claude-3-7-sonnet-20250219 | 62.3% ★★☆ | $3/$15 |

### 必需的API密钥

1. **ANTHROPIC_API_KEY** (必需)

   - 用途：主模型和备用模型
   - 获取：https://console.anthropic.com/
   - 格式：`sk-ant-api03-...`

2. **PERPLEXITY_API_KEY** (强烈推荐)

   - 用途：Research模式增强
   - 获取：https://www.perplexity.ai/settings/api
   - 格式：`pplx-...`

3. **OPENAI_API_KEY** (可选)
   - 用途：备选模型
   - 获取：https://platform.openai.com/api-keys
   - 格式：`sk-proj-...`

---

## 📝 配置步骤

### 方法1：在Cursor MCP配置中添加（推荐）

编辑 `.cursor/mcp.json`，找到 `task-master-ai` 节点，替换API密钥：

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-api03-YOUR_ACTUAL_KEY_HERE",
        "PERPLEXITY_API_KEY": "pplx-YOUR_ACTUAL_KEY_HERE",
        "OPENAI_API_KEY": "sk-proj-YOUR_ACTUAL_KEY_HERE"
      }
    }
  }
}
```

### 方法2：使用环境变量文件（CLI使用）

如果需要使用CLI命令（非Cursor），创建 `.env` 文件：

```bash
# 在项目根目录创建 .env 文件
echo "ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY" >> .env
echo "PERPLEXITY_API_KEY=pplx-YOUR_KEY" >> .env
echo "OPENAI_API_KEY=sk-proj-YOUR_KEY" >> .env
```

⚠️ **重要**：确保 `.env` 已在 `.gitignore` 中（已自动配置）

---

## 🚀 验证配置

配置完成后，重启Cursor并运行：

```bash
# 1. 验证API密钥状态
task-master models

# 2. 查看任务列表（应该能正常工作）
task-master list

# 3. 测试MCP工具（在Cursor中询问）
"请使用Task Master列出所有任务"
```

---

## 🎯 推荐的模型配置（V4方案）

根据[AI-WORKFLOW-V4-README.md](../architecture/V4/AI-WORKFLOW-V4-README.md)：

### Cursor主力开发

```bash
当前配置已是最佳实践：
- Main: Claude 3.7 Sonnet (平衡性能和成本)
- Research: Perplexity Sonar Pro (实时研究)
- Fallback: Claude 3.7 Sonnet (稳定性)
```

### 可选升级方案

**方案1：追求最高质量** (更贵)

```bash
task-master models --set-main claude-opus-4-5
task-master models --set-fallback claude-sonnet-4-5
```

**方案2：成本优化** (更便宜)

```bash
task-master models --set-main claude-3-5-sonnet-20241022
task-master models --set-fallback gpt-4o-mini
```

**方案3：使用免费模型** (零成本)

```bash
# 如果您有Claude Code/Gemini CLI/Codex CLI访问权
task-master models --set-main claude-code:sonnet
task-master models --set-research perplexity:sonar  # 仍需API key
```

---

## 📚 下一步

配置完成后，按照V4工作流开始：

1. **创建第一个PRD**

   ```bash
   mkdir -p docs/00_product/requirements/REQ-2025-001-test
   # 编写PRD文档，参考 .taskmaster/templates/example_prd.txt
   ```

2. **解析PRD生成任务**

   ```bash
   task-master parse-prd --input=docs/00_product/requirements/REQ-2025-001-test/REQ-2025-001-test.md
   ```

3. **分析复杂度**

   ```bash
   task-master analyze-complexity --research
   ```

4. **展开子任务**

   ```bash
   task-master expand --all --research
   ```

5. **开始开发**
   ```bash
   task-master next
   task-master show <id>
   # 开始编码...
   ```

---

## 🔗 相关文档

- [V4工作流完整指南](../architecture/V4/AI-WORKFLOW-V4-README.md)
- [Task Master深度集成](../architecture/V4/AI-WORKFLOW-V4-PART2-TM-ADAPTER.md)
- [PRD和TRD标准](../architecture/V4/AI-WORKFLOW-V4-PART3-PRD-TRD.md)
- [实施落地手册](../architecture/V4/AI-WORKFLOW-V4-PART6-IMPL.md)

---

**配置完成后，请通知AI助手继续验证Task Master功能！**
