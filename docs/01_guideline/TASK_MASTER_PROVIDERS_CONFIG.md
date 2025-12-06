# Task Master 多提供商配置指南

> **适用场景**: 配置OpenRouter和硅基流动等多个AI提供商
> **更新时间**: 2025-11-30

---

## 📊 提供商对比

| 提供商         | 内置支持 | 需要baseURL | API密钥环境变量      | 优势                 |
| -------------- | -------- | ----------- | -------------------- | -------------------- |
| **Anthropic**  | ✅       | ❌          | `ANTHROPIC_API_KEY`  | 官方Claude，最稳定   |
| **OpenRouter** | ✅       | ❌          | `OPENROUTER_API_KEY` | 聚合多模型，价格优惠 |
| **Perplexity** | ✅       | ❌          | `PERPLEXITY_API_KEY` | 实时搜索增强         |
| **硅基流动**   | ❌       | ✅          | `OPENAI_API_KEY`     | 国内快速访问         |
| **OpenAI**     | ✅       | ❌          | `OPENAI_API_KEY`     | GPT系列              |

---

## 🎯 配置方案

### 方案1: OpenRouter（推荐，简单）

**优势**:

- ✅ 不需要配置URL
- ✅ 支持70+个模型（DeepSeek、Qwen、Llama等）
- ✅ 价格比官方便宜
- ✅ 国内访问较快

**配置步骤**:

**Step 1: 在 `.cursor/mcp.json` 中配置密钥**

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-YOUR_KEY",
        "PERPLEXITY_API_KEY": "pplx-YOUR_KEY",
        "OPENROUTER_API_KEY": "sk-or-v1-YOUR_OPENROUTER_KEY" // ← 添加这个
      }
    }
  }
}
```

**Step 2: 设置模型**

```bash
# 使用DeepSeek V3（性价比高）
task-master models --set-main deepseek/deepseek-chat-v3-0324 --openrouter

# 使用Qwen Max（通义千问旗舰版）
task-master models --set-main qwen/qwen-max --openrouter

# 使用Llama 3.3 70B
task-master models --set-main meta-llama/llama-3.3-70b-instruct --openrouter

# 查看所有OpenRouter可用模型
task-master models | grep openrouter
```

---

### 方案2: 硅基流动（国内优化）

**优势**:

- ✅ 国内服务器，延迟低
- ✅ 支持国产模型（DeepSeek、Qwen等）
- ✅ 价格实惠

**配置步骤**:

**Step 1: 在 `.cursor/mcp.json` 中配置密钥**

```json
{
  "mcpServers": {
    "task-master-ai": {
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-YOUR_KEY",
        "PERPLEXITY_API_KEY": "pplx-YOUR_KEY",
        "OPENAI_API_KEY": "sk-YOUR_SILICONFLOW_KEY" // ← 硅基流动密钥
      }
    }
  }
}
```

**Step 2: 设置模型（需要指定URL）**

```bash
# 使用DeepSeek V3
task-master models --set-main deepseek-ai/DeepSeek-V3 \
  --openai-compatible \
  --baseURL https://api.siliconflow.cn/v1

# 使用Qwen2.5-72B
task-master models --set-main Qwen/Qwen2.5-72B-Instruct \
  --openai-compatible \
  --baseURL https://api.siliconflow.cn/v1

# 使用Qwen2.5-7B（更便宜）
task-master models --set-main Qwen/Qwen2.5-7B-Instruct \
  --openai-compatible \
  --baseURL https://api.siliconflow.cn/v1
```

---

## 🆚 方案对比

### OpenRouter vs 硅基流动

| 维度         | OpenRouter                   | 硅基流动                 |
| ------------ | ---------------------------- | ------------------------ |
| **配置难度** | ⭐⭐⭐⭐⭐ 简单（不需要URL） | ⭐⭐⭐☆☆ 中等（需要URL） |
| **国内访问** | ⭐⭐⭐⭐☆ 较快               | ⭐⭐⭐⭐⭐ 很快          |
| **模型选择** | ⭐⭐⭐⭐⭐ 70+模型           | ⭐⭐⭐⭐☆ 30+模型        |
| **价格**     | ⭐⭐⭐⭐☆ 较便宜             | ⭐⭐⭐⭐⭐ 很便宜        |
| **稳定性**   | ⭐⭐⭐⭐⭐ 很稳定            | ⭐⭐⭐⭐☆ 稳定           |

---

## 💡 推荐配置

### 最佳实践配置

```json
{
  "task-master-ai": {
    "env": {
      // 主力模型
      "ANTHROPIC_API_KEY": "sk-ant-YOUR_KEY",

      // 研究增强
      "PERPLEXITY_API_KEY": "pplx-YOUR_KEY",

      // 备用/成本优化
      "OPENROUTER_API_KEY": "sk-or-v1-YOUR_KEY"
    }
  }
}
```

**模型设置**:

```bash
# 主模型：Claude（高质量）
task-master models --set-main claude-3-7-sonnet-20250219

# 研究模型：Perplexity（实时搜索）
task-master models --set-research sonar-pro

# 备用模型：OpenRouter DeepSeek（成本优化）
task-master models --set-fallback deepseek/deepseek-chat-v3-0324 --openrouter
```

---

## 🔧 验证配置

### 1. 检查API密钥状态

```bash
task-master models
```

看到以下输出说明配置成功：

```
🔑 API Key Status:
┌───────────────┬────────────────────┬─────────────────────────┐
│ Provider      │ CLI Key (.env)     │ MCP Key (mcp.json)      │
│ Anthropic     │ ❌ Missing         │ ✅ Found                │
│ Perplexity    │ ❌ Missing         │ ✅ Found                │
│ Openrouter    │ ❌ Missing         │ ✅ Found                │
└───────────────┴────────────────────┴─────────────────────────┘
```

### 2. 测试任务生成

```bash
# 创建测试PRD
echo "# 测试需求\n实现一个简单的Hello World功能" > test_prd.txt

# 测试解析（会调用配置的模型）
task-master parse-prd --input=test_prd.txt
```

---

## 📚 获取API密钥

### OpenRouter

1. 访问: https://openrouter.ai/
2. 注册/登录账号
3. 进入 Settings → API Keys
4. 创建新密钥（格式: `sk-or-v1-...`）
5. 充值余额（最低$5）

### 硅基流动

1. 访问: https://siliconflow.cn/
2. 注册/登录账号
3. 进入控制台 → API密钥
4. 创建新密钥（格式: `sk-...`）
5. 充值余额

### Anthropic

1. 访问: https://console.anthropic.com/
2. 注册/登录账号
3. 进入 API Keys
4. 创建新密钥（格式: `sk-ant-api03-...`）
5. 充值余额（最低$5）

### Perplexity

1. 访问: https://www.perplexity.ai/settings/api
2. 注册Pro账号（$20/月）
3. 获取API密钥（格式: `pplx-...`）

---

## ⚠️ 常见问题

### Q1: 硅基流动配置后还是用不了？

**A**: 确保：

1. `.cursor/mcp.json`中配置了`OPENAI_API_KEY`
2. 设置模型时使用了`--openai-compatible --baseURL https://api.siliconflow.cn/v1`
3. 模型ID正确（如`deepseek-ai/DeepSeek-V3`）

### Q2: OpenRouter配置简单，为什么还要用硅基流动？

**A**:

- **国内项目**: 硅基流动延迟更低
- **成本敏感**: 硅基流动某些模型更便宜
- **备用方案**: 多个提供商互为备份

### Q3: 可以同时配置多个提供商吗？

**A**: ✅ 可以！Task Master支持配置多个提供商，通过`--set-main/research/fallback`指定不同角色使用不同提供商。

---

## 🎯 总结

**简单配置（推荐初学者）**:

```json
{
  "ANTHROPIC_API_KEY": "...",
  "OPENROUTER_API_KEY": "..." // 不需要URL，简单！
}
```

**高级配置（国内优化）**:

```bash
# 主模型用硅基流动（需要命令行配置URL）
task-master models --set-main deepseek-ai/DeepSeek-V3 \
  --openai-compatible \
  --baseURL https://api.siliconflow.cn/v1
```

**最佳实践**:

- 主模型: Claude/OpenRouter DeepSeek（质量优先）
- 研究模型: Perplexity（实时搜索）
- 备用模型: 硅基流动/OpenRouter（成本优化）

---

**配置完成后，重启Cursor即可使用！**
