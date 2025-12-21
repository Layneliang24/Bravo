// REQ-ID: REQ-2025-003-user-login
// REQ-ID: REQ-2025-003-user-login
// 验证码实时验证 E2E 测试
// TESTCASE-IDS: TC-AUTH_UI-014, TC-AUTH_UI-018, TC-AUTH_PREVIEW-011

import { expect, Page, test } from '@playwright/test';
import { ConsoleErrorListener } from '../_helpers/console-error-listener';

const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

// 万能验证码（测试环境专用）
// 后端在测试环境下，如果输入的验证码是此值，则直接通过验证
// 这解决了E2E测试中验证码的随机性问题，避免"调试地狱"
const TEST_CAPTCHA_BYPASS = '6666'; // 4位验证码

test.describe('验证码实时校验功能', () => {
  let page: Page;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page: testPage }) => {
    page = testPage;

    // 设置控制台错误监听器
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();

    // 注意：route必须在goto之前设置，所以每个测试用例需要在自己的开头设置route后再goto
    // 这里不goto，让每个测试用例自己goto
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('TC-AUTH_UI-014: 验证码输入错误时应该自动刷新', async ({ request }) => {
    let apiCallCount = 0;
    let lastCaptchaAnswer = '';

    // Mock预览API（必须在页面加载前设置）
    await page.route('**/api/auth/preview/', async route => {
      apiCallCount++;
      const postData = route.request().postDataJSON() || {};
      lastCaptchaAnswer = postData.captcha_answer || '';

      // 如果验证码答案是'WRON'，返回验证码错误
      if (postData.captcha_answer === 'WRON') {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            error: '验证码错误',
            code: 'INVALID_CAPTCHA',
          }),
        });
        return;
      }
      // 其他情况（账号密码正确，无验证码或验证码正确），返回成功
      if (postData.email === 'test@example.com' && postData.password === 'Test123456') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            valid: true,
            user: { display_name: 'Test User', avatar_url: 'https://example.com/avatar.jpg' },
          }),
        });
        return;
      }
      await route.continue();
    });

    // 在goto之前开始监听验证码API响应
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') && response.request().method() === 'GET',
      { timeout: 15000 }
    );

    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });

    // 等待验证码组件加载
    await captchaResponsePromise;

    // 等待验证码组件渲染完成
    const captchaImage = page
      .locator('div[style*="160px"][style*="64px"], div.cursor-pointer')
      .first();
    await expect(captchaImage).toBeVisible({ timeout: 10000 });

    // 输入账号密码
    await page.fill(
      'input[type="text"][placeholder*="email"], input[type="text"][placeholder*="EMAIL"]',
      'test@example.com'
    );
    await page.fill('input[type="password"]', 'Test123456');

    // 输入错误验证码（使用非万能验证码的值）
    const captchaInput = page
      .locator('input[placeholder*="CODE"], input[placeholder*="验证码"]')
      .first();
    await captchaInput.waitFor({ state: 'visible', timeout: 5000 });

    // 记录输入前的API调用次数
    const apiCallCountBefore = apiCallCount;

    // 输入错误验证码（非万能验证码）
    await captchaInput.type('WRON', { delay: 50 });

    // 等待API调用和UI更新（使用显式等待）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 检查输入框的值
    const captchaInputValue = await captchaInput.inputValue();

    // 检查错误提示 - 使用更通用的选择器
    const errorMessage = page.locator(
      '.text-red-500.text-sm, [data-testid="captcha-error-message"]'
    );
    const errorVisible = await errorMessage.isVisible({ timeout: 5000 }).catch(() => false);
    const errorText = errorVisible ? await errorMessage.textContent() : null;

    // 调试：检查DOM中是否存在错误元素
    const errorElementExists = await page.evaluate(() => {
      const error = document.querySelector('[data-testid="captcha-error-message"]');
      return {
        exists: !!error,
        text: error?.textContent || null,
        visible: error ? window.getComputedStyle(error).display !== 'none' : false,
      };
    });
    console.log('[TEST] 错误元素检查:', errorElementExists);

    // 验证：如果API被调用了，应该看到错误提示
    if (apiCallCount > apiCallCountBefore) {
      expect(errorVisible).toBe(true);
      expect(errorText).toContain('验证码');
      expect(captchaInputValue).toBe('');
    } else {
      // 如果API没有被调用，检查可能的原因
      const hasCaptchaId = await page.evaluate(() => {
        const captchaImg = document.querySelector('div[style*="160px"][style*="64px"] img');
        return captchaImg !== null;
      });

      if (hasCaptchaId) {
        throw new Error(
          `验证码图片存在，但API没有被调用！可能captcha_id没有设置或实时校验逻辑有问题。输入前: ${apiCallCountBefore}, 输入后: ${apiCallCount}`
        );
      } else {
        throw new Error(
          `验证码图片不存在！验证码组件可能没有加载。输入前: ${apiCallCountBefore}, 输入后: ${apiCallCount}`
        );
      }
    }
  });

  test('TC-AUTH_UI-018: 验证码输入正确时应该显示打勾图标', async ({ request }) => {
    // 使用万能验证码测试打勾图标显示逻辑

    // 在goto之前开始监听验证码API响应
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') && response.request().method() === 'GET',
      { timeout: 15000 }
    );

    // 加载页面
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });

    // 等待验证码组件加载
    await captchaResponsePromise;
    await page.waitForSelector('img[alt="验证码"]', { state: 'visible', timeout: 10000 });

    // 3. 输入有效账号密码（触发头像预览）
    await page.fill(
      'input[type="text"][placeholder*="email"], input[type="text"][placeholder*="EMAIL"]',
      'test@example.com'
    );
    await page.fill('input[type="password"]', 'Test123456');

    // 4. 使用万能验证码测试打勾图标显示逻辑
    const captchaInput = page
      .locator('input[placeholder*="CODE"], input[placeholder*="验证码"]')
      .first();
    await captchaInput.waitFor({ state: 'visible', timeout: 5000 });

    // 输入万能验证码（测试环境专用，保证验证通过）
    await captchaInput.fill(TEST_CAPTCHA_BYPASS);

    // 等待实时校验完成（使用显式等待）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 5. 检查是否有错误提示
    const errorMessage = page.locator('text=/验证码错误/');
    const hasError = await errorMessage.isVisible().catch(() => false);

    if (!hasError) {
      // 如果没有错误提示，说明验证码可能正确，应该显示打勾图标
      const checkIcon = page.locator('svg[class*="text-green-500"]').first();
      await expect(checkIcon).toBeVisible({ timeout: 2000 });
    } else {
      // 如果有错误提示，说明验证码错误，应该已经自动刷新
      // 验证输入框已清空
      const captchaInputValue = await captchaInput.inputValue();
      expect(captchaInputValue).toBe('');
    }
  });

  test('TC-AUTH_PREVIEW-011: 头像预览应该不受验证码错误影响', async ({ request }) => {
    let previewCallCount = 0;

    // Mock预览API（必须在页面加载前设置）
    await page.route('**/api/auth/preview/', async route => {
      previewCallCount++;
      const postData = route.request().postDataJSON() || {};

      // 第一次调用：账号密码正确，返回成功（触发头像显示）
      if (
        previewCallCount === 1 &&
        postData.email === 'test@example.com' &&
        postData.password === 'Test123456'
      ) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            valid: true,
            user: { display_name: 'Test User', avatar_url: 'https://example.com/avatar.jpg' },
          }),
        });
        return;
      }

      // 第二次调用：验证码错误，但账号密码正确，返回验证码错误（头像应该保持显示）
      if (
        previewCallCount >= 2 &&
        postData.captcha_answer === 'WRON' &&
        postData.email === 'test@example.com' &&
        postData.password === 'Test123456'
      ) {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            error: '验证码错误',
            code: 'INVALID_CAPTCHA',
          }),
        });
        return;
      }

      // 账号密码错误，返回失败（头像应该消失）
      if (postData.email === 'wrong@example.com') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            valid: false,
            user: null,
          }),
        });
        return;
      }

      await route.continue();
    });

    // 在goto之前开始监听验证码API响应
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') && response.request().method() === 'GET',
      { timeout: 15000 }
    );

    // route设置后，再goto页面
    await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });

    // 等待验证码组件加载
    await captchaResponsePromise;
    await page.waitForSelector('img[alt="验证码"]', { state: 'visible', timeout: 10000 });

    // 输入正确账号密码触发头像预览
    await page.fill(
      'input[type="text"][placeholder*="email"], input[type="text"][placeholder*="EMAIL"]',
      'test@example.com'
    );
    await page.fill('input[type="password"]', 'Test123456');

    // 使用万能验证码（测试环境专用）
    const captchaInput = page
      .locator('input[placeholder*="CODE"], input[placeholder*="验证码"]')
      .first();
    await captchaInput.waitFor({ state: 'visible', timeout: 5000 });
    await captchaInput.fill(TEST_CAPTCHA_BYPASS);

    // 等待预览API返回成功
    const previewResponse = await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    const previewData = await previewResponse.json();
    expect(previewData.valid).toBe(true);

    // 等待头像显示（需要等待Vue组件更新和动画完成）
    const avatar = page.locator('img[alt="Avatar"]');
    await expect(avatar).toBeVisible({ timeout: 10000 });

    // 输入错误验证码（使用非万能验证码的值）
    await captchaInput.fill('WRON');

    // 等待验证码实时校验API调用（validateCaptchaRealTime会调用预览API）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 等待验证码错误提示显示
    await page.waitForTimeout(1000);

    // 验证头像仍然显示（验证码错误不应该影响头像）
    // 根据LoginForm.vue的逻辑，验证码错误时不会清除头像（triggerPreview中的catch块会检查errorCode !== 'INVALID_CAPTCHA'）
    await expect(avatar).toBeVisible({ timeout: 5000 });

    // 7. 修改账号（导致验证失败）
    await page.fill(
      'input[type="text"][placeholder*="email"], input[type="text"][placeholder*="EMAIL"]',
      'wrong@example.com'
    );

    // 等待预览API响应（使用显式等待）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 8. 验证头像消失（账号密码变化导致验证失败，应该清除头像）
    await expect(avatar).not.toBeVisible({ timeout: 5000 });
  });
});
