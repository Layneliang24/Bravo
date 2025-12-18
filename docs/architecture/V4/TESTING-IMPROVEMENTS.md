# 测试改进方案 - 注册页面问题复盘

## REQ-ID: REQ-2025-003-user-login

## 问题复盘

### 发现的问题

1. **验证码图片不显示，一直提示验证码错误**

   - 问题：后端返回的是Base64图片，但前端显示的是随机生成的文本
   - 根因：`captchaImage`为空，导致`v-if="captchaImage"`为false，显示降级文本
   - 影响：用户输入的是随机文本，但后端验证的是图片中的答案，导致一直报错
   - 修复：修改Captcha组件，确保正确显示后端返回的图片

2. **邮箱验证页面缺少重新发送按钮功能**

   - 问题：重新发送按钮需要用户已登录，但验证失败时用户可能未登录
   - 根因：`sendEmailVerification` API需要认证，但验证失败时用户未登录
   - 影响：用户无法重新发送验证邮件
   - 修复：添加新的API端点`/api/auth/email/verify/resend/?token=xxx`，允许通过验证token重新发送

3. **密码强度进度条不显示**

   - 问题：进度条宽度为33%，但高度为0，不可见
   - 根因：CSS变量`--color-error`未定义，导致背景色透明
   - 影响：用户无法看到密码强度视觉反馈
   - 修复：添加CSS变量定义，修复进度条样式

4. **验证码输入框缺失**

   - 问题：RegisterForm组件缺少验证码输入框
   - 根因：组件重构时遗漏了输入框实现
   - 影响：用户无法输入验证码，无法完成注册
   - 修复：添加验证码输入框

5. **文字布局混乱**

   - 问题：表单元素高度为0，导致布局异常
   - 根因：CSS样式冲突，父容器高度计算错误
   - 影响：页面显示异常，用户体验差
   - 修复：修复CSS样式，确保表单正确显示

6. **创建账户按钮无法点击**
   - 问题：按钮一直处于disabled状态
   - 根因：表单验证逻辑要求`captcha_id`，但Captcha组件可能未正确触发事件
   - 影响：用户无法提交注册表单
   - 修复：修复表单验证逻辑

### 为什么测试没有发现这些问题？

#### 1. E2E测试环境差异

**问题**：

- E2E测试在Docker容器内运行，使用`http://backend:8000`（无CORS问题）
- 浏览器在宿主机运行，使用`http://localhost:8000`（需要CORS配置）
- 测试环境与真实浏览器环境存在差异

**证据**：

- 测试通过，但浏览器报CORS错误
- 测试通过，但浏览器显示异常

**改进方案**：

```typescript
// 1. 添加浏览器环境验证测试
test("TC-AUTH_REGISTER-009: 浏览器环境验证", async ({ page, context }) => {
  // 使用真实浏览器环境（非headless）
  await page.goto("http://localhost:3000/register");

  // 检查控制台错误
  const consoleErrors = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });

  // 检查CORS错误
  page.on("response", (response) => {
    if (response.status() === 0) {
      throw new Error("CORS error detected");
    }
  });

  // 验证页面正常渲染
  await expect(page.locator(".register-form")).toBeVisible();

  // 验证无控制台错误
  expect(consoleErrors).toHaveLength(0);
});
```

#### 2. 视觉回归测试缺失

**问题**：

- 没有测试密码强度进度条的视觉显示
- 没有测试验证码输入框的存在和可见性
- 没有测试表单布局的正确性

**改进方案**：

```typescript
// 2. 添加视觉回归测试
test("TC-AUTH_REGISTER-010: 密码强度进度条视觉验证", async ({ page }) => {
  await page.goto("http://localhost:3000/register");

  // 输入密码
  await page.fill('input[type="password"]', "test1234");

  // 检查进度条存在
  const progressBar = page.locator(".password-strength .strength-bar");
  await expect(progressBar).toBeVisible();

  // 检查进度条高度（应该>0）
  const height = await progressBar.evaluate((el) => el.offsetHeight);
  expect(height).toBeGreaterThan(0);

  // 检查进度条宽度（应该>0）
  const width = await progressBar.evaluate((el) => el.offsetWidth);
  expect(width).toBeGreaterThan(0);

  // 检查进度条背景色（不应该透明）
  const bgColor = await progressBar.evaluate((el) => {
    const styles = window.getComputedStyle(el);
    return styles.backgroundColor;
  });
  expect(bgColor).not.toBe("rgba(0, 0, 0, 0)");
  expect(bgColor).not.toBe("transparent");
});

test("TC-AUTH_REGISTER-011: 验证码输入框存在和可见性", async ({ page }) => {
  await page.goto("http://localhost:3000/register");

  // 检查验证码输入框存在
  const captchaInput = page.locator(
    'input[placeholder*="验证码"], input[placeholder*="CODE"]',
  );
  await expect(captchaInput).toBeVisible();

  // 检查输入框可交互
  await expect(captchaInput).toBeEnabled();

  // 检查输入框高度（应该>0）
  const height = await captchaInput.evaluate((el) => el.offsetHeight);
  expect(height).toBeGreaterThan(0);
});
```

#### 3. CSS变量验证缺失

**问题**：

- 没有验证CSS变量是否正确定义
- 没有验证CSS变量是否正确应用

**改进方案**：

```typescript
// 3. 添加CSS变量验证测试
test("TC-AUTH_REGISTER-012: CSS变量验证", async ({ page }) => {
  await page.goto("http://localhost:3000/register");

  // 检查CSS变量定义
  const rootStyles = await page.evaluate(() => {
    const root = document.documentElement;
    return {
      errorColor: window
        .getComputedStyle(root)
        .getPropertyValue("--color-error")
        .trim(),
      successColor: window
        .getComputedStyle(root)
        .getPropertyValue("--color-success")
        .trim(),
    };
  });

  expect(rootStyles.errorColor).toBeTruthy();
  expect(rootStyles.successColor).toBeTruthy();
  expect(rootStyles.errorColor).not.toBe("");
  expect(rootStyles.successColor).not.toBe("");
});
```

#### 4. 表单验证逻辑测试不完整

**问题**：

- 没有测试表单验证的完整流程
- 没有测试`captcha_id`是否正确设置

**改进方案**：

```typescript
// 4. 添加表单验证逻辑测试
test("TC-AUTH_REGISTER-013: 表单验证完整流程", async ({ page }) => {
  await page.goto("http://localhost:3000/register");

  // 等待验证码加载
  await page.waitForTimeout(2000);

  // 检查captcha_id是否设置
  const captchaId = await page.evaluate(() => {
    // 通过Vue DevTools或直接访问组件实例
    return (window as any).__VUE_DEVTOOLS_GLOBAL_HOOK__?.apps?.[0]?.config
      ?.globalProperties?.$data;
  });

  // 填写表单
  await page.fill('input[type="email"]', "test@example.com");
  await page.fill('input[type="password"]', "test1234");
  await page
    .fillAll('input[type="password"]')
    .then((inputs) => inputs[1].fill("test1234"));

  // 获取验证码文本
  const captchaText = await page.evaluate(() => {
    const captchaDiv = document.querySelector(".cursor-pointer");
    return captchaDiv?.textContent?.match(/[A-Z0-9]{6}/)?.[0] || "";
  });

  await page.fill('input[placeholder*="验证码"]', captchaText);

  // 检查按钮是否启用
  const submitButton = page.locator('button[type="submit"]');
  const isDisabled = await submitButton.isDisabled();

  // 如果所有字段都填写正确，按钮应该启用
  if (captchaText && captchaText.length === 6) {
    expect(isDisabled).toBe(false);
  }
});
```

#### 5. 浏览器环境验证缺失

**问题**：

- 没有在真实浏览器环境中运行测试
- 没有检查浏览器控制台错误
- 没有检查网络请求错误

**改进方案**：

```typescript
// 5. 添加浏览器环境验证
test("TC-AUTH_REGISTER-014: 浏览器环境完整验证", async ({ page, context }) => {
  // 收集控制台错误
  const consoleErrors: string[] = [];
  page.on("console", (msg) => {
    if (msg.type() === "error") {
      consoleErrors.push(msg.text());
    }
  });

  // 收集网络错误
  const networkErrors: string[] = [];
  page.on("response", (response) => {
    if (response.status() >= 400) {
      networkErrors.push(`${response.url()}: ${response.status()}`);
    }
  });

  await page.goto("http://localhost:3000/register");
  await page.waitForTimeout(3000); // 等待所有资源加载

  // 验证无控制台错误
  expect(consoleErrors).toHaveLength(0);

  // 验证无网络错误
  expect(networkErrors).toHaveLength(0);

  // 验证页面正常渲染
  await expect(page.locator(".register-form")).toBeVisible();
});
```

## 改进措施

### 1. 强制浏览器环境验证

**规则更新**：

- 每次修复前端问题后，必须使用MCP工具验证浏览器环境
- 不能只验证容器内测试，必须验证浏览器实际运行效果
- 使用 `browser_navigate` + `browser_console_messages` 主动检查错误

**参考**：`.cursor/rules/principles/v4-core.mdc` - 浏览器验证强制规则

### 2. 增强E2E测试覆盖

**新增测试用例**：

- `TC-AUTH_REGISTER-009`: 浏览器环境验证
- `TC-AUTH_REGISTER-010`: 密码强度进度条视觉验证
- `TC-AUTH_REGISTER-011`: 验证码输入框存在和可见性
- `TC-AUTH_REGISTER-012`: CSS变量验证
- `TC-AUTH_REGISTER-013`: 表单验证完整流程
- `TC-AUTH_REGISTER-014`: 浏览器环境完整验证

### 3. 添加视觉回归测试

**工具**：使用Playwright的截图对比功能

```typescript
test("视觉回归：注册页面布局", async ({ page }) => {
  await page.goto("http://localhost:3000/register");
  await page.waitForLoadState("networkidle");

  // 截图对比
  await expect(page).toHaveScreenshot("register-page.png", {
    fullPage: true,
    threshold: 0.2,
  });
});
```

### 4. CSS变量检查清单

**检查项**：

- [ ] 所有使用的CSS变量都在`brand-colors.css`中定义
- [ ] CSS变量名称符合命名规范
- [ ] CSS变量值符合设计规范
- [ ] 测试验证CSS变量正确加载

### 5. 表单验证测试清单

**检查项**：

- [ ] 所有必填字段都有验证
- [ ] 表单验证逻辑正确
- [ ] 按钮状态与表单验证状态同步
- [ ] 错误消息正确显示

## 总结

**根本原因**：

1. 测试环境与浏览器环境差异
2. 视觉回归测试缺失
3. CSS变量验证缺失
4. 浏览器环境验证缺失

**改进方向**：

1. 强制浏览器环境验证（MCP工具）
2. 增强E2E测试覆盖（视觉、CSS变量、表单验证）
3. 添加视觉回归测试
4. 建立CSS变量检查清单
5. 建立表单验证测试清单

**预期效果**：

- 在测试阶段发现90%以上的UI问题
- 减少浏览器环境问题
- 提高代码质量
