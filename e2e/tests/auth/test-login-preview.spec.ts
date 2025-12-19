// REQ-ID: REQ-2025-003-user-login
// 登录预验证 E2E 测试
// 使用 Playwright 进行端到端测试
// TESTCASE-IDS: TC-AUTH_PREVIEW-003, TC-AUTH_PREVIEW-008, TC-AUTH_PREVIEW-009, TC-AUTH_PREVIEW-010, TC-AUTH_PREVIEW-011, TC-AUTH_PREVIEW-012

import { expect, Page, test } from '@playwright/test';
import { ConsoleErrorListener } from '../_helpers/console-error-listener';

// 测试配置
// Docker环境中使用容器名，本地开发使用localhost
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

// 万能验证码（测试环境专用）
// 后端在测试环境下，如果输入的验证码是此值，则直接通过验证
// 这解决了E2E测试中验证码的随机性问题，避免"调试地狱"
const TEST_CAPTCHA_BYPASS = '6666'; // 4位验证码

// 页面对象模式 - 登录页（带预验证）
class LoginPreviewPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    // 等待Vue组件渲染完成
    await this.page.waitForSelector('[data-testid="auth-card"], .auth-card, .login-form', {
      state: 'visible',
      timeout: 15000,
    });
    await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
      // 如果网络空闲超时，继续执行
    });
  }

  async fillEmail(email: string) {
    // 等待输入框出现（登录页面使用type="text"而不是type="email"）
    await this.page.waitForSelector(
      'input[type="text"], input[type="email"], input[placeholder*="username"], input[placeholder*="USERNAME"]',
      { state: 'visible', timeout: 10000 }
    );
    // 尝试多种选择器
    const emailInput = await this.page
      .locator(
        'input[type="text"], input[type="email"], input[placeholder*="username"], input[placeholder*="USERNAME"]'
      )
      .first();
    await emailInput.fill(email);
  }

  async fillPassword(password: string) {
    // 等待密码输入框出现
    await this.page.waitForSelector('input[type="password"]', { state: 'visible', timeout: 10000 });
    await this.page.fill('input[type="password"]', password);
  }

  async getCaptchaId(): Promise<string | null> {
    // 等待验证码加载（使用实际的类名选择器）
    await this.page.waitForSelector(
      '.captcha-container, .captcha-content, [data-testid="captcha"]',
      {
        timeout: 10000,
      }
    );
    // 从验证码组件获取 captcha_id（需要根据实际实现调整）
    // 如果组件没有data-captcha-id属性，可能需要从API响应中获取
    return await this.page
      .getAttribute('.captcha-container, [data-testid="captcha"]', 'data-captcha-id')
      .catch(() => null);
  }

  async fillCaptcha(captchaAnswer: string) {
    // 更新选择器以匹配新的LoginForm结构
    await this.page
      .locator('input[placeholder="CODE"], input[placeholder*="验证码"]')
      .first()
      .fill(captchaAnswer);
  }

  async blurPassword() {
    // 使用locator来blur
    const passwordInput = await this.page.locator('input[type="password"]').first();
    await passwordInput.blur();
  }

  async waitForPreviewLoading() {
    await this.page.waitForSelector('.loading', { timeout: 2000 }).catch(() => {});
  }

  async waitForPreviewUser() {
    await this.page.waitForSelector('.user-info', { timeout: 5000 }).catch(() => {});
  }

  async isPreviewVisible(): Promise<boolean> {
    // 预览组件在AuthCard中，通过头像图片判断
    const avatar = await this.page.$('img[alt="Avatar"]');
    return avatar !== null;
  }

  async getPreviewDisplayName(): Promise<string | null> {
    // 预览组件中的显示名称在AuthCard中，直接查找包含displayName的span元素
    // 根据AuthCard.vue，显示名称在 <span class="text-orange-600 font-bold"> 中
    const displayNameElement = await this.page.$('span.text-orange-600.font-bold');
    if (!displayNameElement) return null;
    return await displayNameElement.textContent();
  }

  async hasPreviewAvatar(): Promise<boolean> {
    // 预览组件在AuthCard中，查找头像图片
    const avatar = await this.page.$('img[alt="Avatar"]');
    return avatar !== null;
  }

  async hasPreviewDefaultAvatar(): Promise<boolean> {
    // AuthCard中的预览组件使用img标签，如果有默认头像会使用默认URL
    // 这里检查头像是否存在即可
    const avatar = await this.page.$('img[alt="Avatar"]');
    if (!avatar) return false;
    const src = await avatar.getAttribute('src');
    // 如果src包含默认头像URL，说明是默认头像
    return src?.includes('unsplash.com') || src?.includes('default') || false;
  }

  async mockPreviewResponse(response: any) {
    // 使用通配符匹配所有preview请求
    await this.page.route('**/api/auth/preview/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(response),
      });
    });
  }
}

// 登录预验证测试套件
test.describe('登录预验证功能测试', () => {
  let loginPage: LoginPreviewPage;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPreviewPage(page);

    // 设置控制台错误监听器（必须在页面加载前设置）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();

    // 在goto之前开始监听验证码API响应
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') && response.request().method() === 'GET',
      { timeout: 15000 }
    );

    await loginPage.goto();

    // 等待验证码组件加载完成（使用显式等待，而不是固定时间）
    await captchaResponsePromise;
    await page.waitForSelector('img[alt="验证码"]', { state: 'visible', timeout: 10000 });

    // 页面加载后，注入unhandledrejection监听器（确保捕获所有错误）
    try {
      await page.evaluate(() => {
        if (!(window as any).__unhandledRejectionListener) {
          (window as any).__unhandledRejectionListener = true;
          window.addEventListener('unhandledrejection', (event: any) => {
            if (!(window as any).__unhandledRejections) {
              (window as any).__unhandledRejections = [];
            }
            (window as any).__unhandledRejections.push({
              reason: event.reason?.toString() || 'Unknown error',
              timestamp: Date.now(),
            });
          });
        }
      });
    } catch (error) {
      // 如果注入失败，继续执行（可能页面还没完全加载）
      // 错误监听器已经通过page.on('pageerror')设置了
    }
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('TC-AUTH_PREVIEW-009: 成功预验证并显示用户头像（完整性测试）', async ({ page }) => {
    // ✅ 关键修复：在填写表单之前设置 mock
    await loginPage.mockPreviewResponse({
      valid: true,
      user: {
        display_name: 'Test User',
        avatar_url: 'https://example.com/avatar.jpg',
        default_avatar: false,
      },
    });

    // 填写表单
    await loginPage.fillEmail('test@example.com');
    await loginPage.fillPassword('password123');

    // 使用万能验证码（测试环境专用）
    await loginPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 触发预验证（密码失焦）
    await loginPage.blurPassword();

    // 等待预验证API响应（使用显式等待，而不是固定时间）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 验证预览组件显示（等待动画完成）
    await page.waitForSelector('img[alt="Avatar"]', { state: 'visible', timeout: 5000 });
    const isVisible = await loginPage.isPreviewVisible();
    expect(isVisible).toBe(true);

    // 验证头像真的显示（等待动画完成）
    const avatar = page.locator('img[alt="Avatar"]').first();
    await expect(avatar).toBeVisible({ timeout: 5000 });

    // 验证显示名称
    const displayName = await loginPage.getPreviewDisplayName();
    expect(displayName).toContain('Test User');
  });

  test('成功预验证但用户无头像，显示默认头像', async ({ page }) => {
    // Mock 预验证 API 响应（无头像）
    await loginPage.mockPreviewResponse({
      valid: true,
      user: {
        display_name: 'Test User',
        avatar_url: null,
        avatar_letter: 'T',
      },
    });

    // 填写表单
    await loginPage.fillEmail('test@example.com');
    await loginPage.fillPassword('password123');

    // 使用万能验证码（测试环境专用）
    await loginPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 触发预验证
    await loginPage.blurPassword();

    // 等待预验证API响应（使用显式等待）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );
    await loginPage.waitForPreviewUser();

    // 验证预览组件显示默认头像
    expect(await loginPage.isPreviewVisible()).toBe(true);
    expect(await loginPage.getPreviewDisplayName()).toBe('Test User');
    expect(await loginPage.hasPreviewDefaultAvatar()).toBe(true);
  });

  test('预验证失败，不显示用户预览', async ({ page }) => {
    // Mock 预验证 API 响应（无效）
    await loginPage.mockPreviewResponse({
      valid: false,
      user: null,
    });

    // 填写表单
    await loginPage.fillEmail('test@example.com');
    await loginPage.fillPassword('wrongpassword');

    // 使用万能验证码（测试环境专用）
    await loginPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 触发预验证
    await loginPage.blurPassword();

    // 等待预验证API响应（使用显式等待）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 验证预览组件不显示（或显示加载状态后消失）
    // 由于预验证失败，预览应该不显示用户信息
    const previewVisible = await loginPage.isPreviewVisible();
    // 如果预览可见，应该不包含用户信息
    if (previewVisible) {
      const displayName = await loginPage.getPreviewDisplayName();
      expect(displayName).toBeNull();
    }
  });

  test('频繁触发预验证，验证防抖功能', async ({ page }) => {
    let apiCallCount = 0;

    // Mock 预验证 API，记录调用次数
    await page.route('**/api/auth/preview/', async route => {
      apiCallCount++;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valid: true,
          user: {
            display_name: 'Test User',
            avatar_url: null,
            avatar_letter: 'T',
          },
        }),
      });
    });

    // 填写表单
    await loginPage.fillEmail('test@example.com');
    await loginPage.fillPassword('password123');

    // 使用万能验证码（测试环境专用）
    await loginPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 快速多次触发预验证（通过多次失焦）
    for (let i = 0; i < 5; i++) {
      await loginPage.blurPassword();
      await page.waitForTimeout(100); // 快速连续触发
    }

    // 等待最后一次API响应（防抖后应该只有一次调用）
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 验证 API 调用次数应该较少（由于防抖）
    // 理想情况下应该只有 1-2 次调用，而不是 5 次
    expect(apiCallCount).toBeLessThan(5);
  });

  test('TC-AUTH_PREVIEW-010: 登录预览-输入账号密码后即可显示头像（无需验证码）', async ({
    page,
  }) => {
    // Mock 预验证 API 响应
    let previewRequestData: any = null;

    await page.route('**/api/auth/preview/', async route => {
      const request = route.request();
      const postData = request.postDataJSON();
      previewRequestData = postData;

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valid: true,
          user: {
            display_name: 'Test User',
            avatar_url: 'https://example.com/avatar.jpg',
            default_avatar: false,
          },
        }),
      });
    });

    // 填写邮箱和密码（不输入验证码）
    await loginPage.fillEmail('test@example.com');
    await loginPage.fillPassword('password123');

    // 触发预验证（密码失焦）
    await loginPage.blurPassword();

    // 等待预验证API响应
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 验证预览API调用时captcha_answer为空或未提供
    expect(previewRequestData).toBeTruthy();
    expect(previewRequestData.email).toBe('test@example.com');
    expect(previewRequestData.password).toBe('password123');
    expect(previewRequestData.captcha_id).toBeTruthy();
    // 验证码答案应该为空或空字符串（根据PRD，预览时验证码可选）
    expect(
      previewRequestData.captcha_answer === '' || previewRequestData.captcha_answer === undefined
    ).toBe(true);

    // 验证头像预览组件显示
    await page.waitForSelector('img[alt="Avatar"]', { state: 'visible', timeout: 5000 });
    const isVisible = await loginPage.isPreviewVisible();
    expect(isVisible).toBe(true);

    // 验证显示名称
    const displayName = await loginPage.getPreviewDisplayName();
    expect(displayName).toContain('Test User');
  });

  test('TC-AUTH_PREVIEW-012: 429错误时显示用户友好提示且不清除头像', async ({ page }) => {
    // 先成功显示头像
    await page.route('**/api/auth/preview/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          valid: true,
          user: {
            display_name: 'Test User',
            avatar_url: null,
            avatar_letter: 'T',
          },
        }),
      });
    });

    // 填写邮箱和密码
    await loginPage.fillEmail('test@example.com');
    await loginPage.fillPassword('password123');

    // 触发预验证，显示头像
    await loginPage.blurPassword();
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 验证头像已显示
    const isPreviewVisibleBefore = await loginPage.isPreviewVisible();
    expect(isPreviewVisibleBefore).toBe(true);

    // 模拟429错误（频率限制）
    await page.route('**/api/auth/preview/', async route => {
      await route.fulfill({
        status: 429,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '请求过于频繁，请稍后再试',
          code: 'RATE_LIMIT_EXCEEDED',
        }),
      });
    });

    // 使用万能验证码触发验证码实时校验（会调用预览API）
    await loginPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 等待API响应
    await page.waitForResponse(
      response =>
        response.url().includes('/api/auth/preview/') && response.request().method() === 'POST',
      { timeout: 10000 }
    );

    // 等待错误提示显示
    await page.waitForTimeout(500);

    // 验证错误提示显示
    const errorMessage = page.locator(
      '.text-red-500.text-sm, [data-testid="captcha-error-message"]'
    );
    const errorVisible = await errorMessage.isVisible({ timeout: 5000 }).catch(() => false);
    expect(errorVisible).toBe(true);

    const errorText = await errorMessage.textContent();
    expect(errorText).toContain('请求过于频繁');

    // 验证头像仍然显示（不清除）
    const isPreviewVisibleAfter = await loginPage.isPreviewVisible();
    expect(isPreviewVisibleAfter).toBe(true);
  });
});
