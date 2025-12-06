# Task Master API配置说明

## 环境变量配置

API密钥存储在`.env`文件中，通过环境变量引用：

```bash
# 硅基流动
SILICONFLOW_API_KEY=sk-qcxlwgdycvwptcaipxbiomxxfdsalmtiwvktcravdcnfauit
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

## 模型配置

在`.taskmaster/config.json`中配置模型，使用OpenAI兼容的provider，通过baseURL指向硅基流动：

```json
{
  "models": {
    "main": {
      "provider": "openai",
      "modelId": "deepseek-chat",
      "baseURL": "${SILICONFLOW_BASE_URL}",
      "apiKey": "${SILICONFLOW_API_KEY}"
    }
  }
}
```

## MCP配置

在`.cursor/mcp.json`中配置Task Master MCP服务器，环境变量会自动传递：

```json
{
  "mcpServers": {
    "taskmaster": {
      "command": "npx",
      "args": ["-y", "task-master-ai", "mcp"],
      "env": {
        "SILICONFLOW_API_KEY": "${SILICONFLOW_API_KEY}",
        "SILICONFLOW_BASE_URL": "${SILICONFLOW_BASE_URL}"
      }
    }
  }
}
```

## 可用模型

✅ **硅基流动可用模型**:

- `deepseek-chat` - 推荐，性价比高
- `deepseek-coder` - 代码生成专用
- `Qwen/Qwen2.5-7B-Instruct` - 开源模型，便宜
- `meta-llama/Llama-3.1-8B-Instruct` - Meta开源模型

❌ **沉默AI** - 测试失败，暂不使用
