# E2E测试哲学

## 核心原则

**E2E测试应该直接使用真实API，而不是mock**

### 为什么？

1. **真实环境验证**：E2E测试的目的是验证整个系统（前端+后端+数据库）是否正常工作
2. **发现真实问题**：只有使用真实API才能发现实际的集成问题
3. **端到端覆盖**：mock会跳过后端逻辑，无法验证完整的用户流程

### 什么时候可以mock？

**仅在以下场景使用mock：**

1. **错误场景测试**：测试特定错误响应（400、500等），这些场景在真实环境中难以复现

   - 例如：测试"验证链接已过期"的场景
   - 例如：测试"网络错误"的场景

2. **外部依赖**：测试依赖第三方服务（如支付、邮件服务）的场景

   - 例如：测试邮件发送功能（避免真实发送邮件）

3. **性能测试**：需要模拟特定响应时间或大量数据的场景

### 当前测试配置

**所有测试文件已更新为使用容器名：**

```typescript
// Docker环境中使用容器名，本地开发使用localhost
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';
```

**已移除mock的测试：**

1. ✅ `test-captcha-refresh.spec.ts` - 验证码刷新测试（完全使用真实API）
2. ✅ `test-email-verification.spec.ts` - 注册成功场景（使用真实API）
3. ✅ `test-login-preview.spec.ts` - 验证码加载（使用真实API）

**保留mock的测试场景：**

1. ⚠️ `test-email-verification.spec.ts` - 错误场景（无效token、过期token）

   - **原因**：这些场景需要特定后端状态，难以在真实环境中复现
   - **建议**：如果后端支持测试模式，可以移除mock

2. ⚠️ `test-login-preview.spec.ts` - 预览API响应
   - **原因**：需要特定用户数据状态
   - **建议**：使用测试数据库，可以移除mock

### 运行测试

```bash
# 确保所有服务运行
docker-compose up -d

# 运行所有auth测试
docker-compose exec e2e npx playwright test e2e/tests/auth

# 运行特定测试
docker-compose exec e2e npx playwright test e2e/tests/auth/test-captcha-refresh.spec.ts
```

### 注意事项

1. **测试数据清理**：使用真实API的测试可能会创建数据，需要清理
2. **测试隔离**：每个测试应该使用唯一的数据（如唯一邮箱）
3. **服务依赖**：确保backend和frontend服务正常运行
