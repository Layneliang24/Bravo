// REQ-ID: REQ-2025-003-user-login
// 邮箱验证 E2E 测试
// 使用 Playwright 进行端到端测试
// TESTCASE-IDS: TC-AUTH_EMAIL-002, TC-AUTH_EMAIL-007

import { expect, Page, test } from '@playwright/test';
import { ConsoleErrorListener } from '../_helpers/console-error-listener';

// 测试配置
// Docker环境中使用容器名，本地开发使用localhost
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

// 页面对象模式 - 邮箱验证页
class EmailVerificationPage {
  constructor(private page: Page) {}

  async goto(token?: string, withAuth = false) {
    const url = token ? `${BASE_URL}/verify-email?token=${token}` : `${BASE_URL}/verify-email`;
    await this.page.goto(url, { waitUntil: 'domcontentloaded' });

    // 如果需要模拟已登录状态
    if (withAuth) {
      await this.page.evaluate(() => {
        localStorage.setItem('auth_token', 'mock-auth-token');
        localStorage.setItem('refresh_token', 'mock-refresh-token');
      });
      await this.page.reload({ waitUntil: 'domcontentloaded' });
    }

    // 等待Vue组件渲染完成
    await this.page.waitForSelector(
      '.verify-email-view, .verification-loading, .verification-success, .verification-error',
      {
        state: 'visible',
        timeout: 15000,
      }
    );
    await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
      // 如果网络空闲超时，继续执行
    });
  }

  async getTitle(): Promise<string | null> {
    return await this.page.textContent('h1, .page-title, [data-testid="title"]');
  }

  async getMessage(): Promise<string | null> {
    // 等待消息元素出现
    await this.page
      .waitForSelector(
        '.verification-message, .message, [data-testid="message"], .success-message, .error-message',
        {
          state: 'visible',
          timeout: 10000,
        }
      )
      .catch(() => {
        // 如果找不到，返回null
      });
    return await this.page.textContent(
      '.verification-message, .message, [data-testid="message"], .success-message, .error-message'
    );
  }

  async isSuccess(): Promise<boolean> {
    const successIndicator = await this.page.$(
      '.success, .verification-success, [data-testid="success"]'
    );
    return successIndicator !== null;
  }

  async isError(): Promise<boolean> {
    const errorIndicator = await this.page.$('.error, .verification-error, [data-testid="error"]');
    return errorIndicator !== null;
  }

  async getErrorMessage(): Promise<string | null> {
    // 等待错误消息元素出现
    await this.page
      .waitForSelector(
        '.error-message, .verification-error .error-message, [data-testid="error-message"]',
        {
          state: 'visible',
          timeout: 10000,
        }
      )
      .catch(() => {
        // 如果找不到，尝试获取整个错误区域的内容
      });
    // 尝试多种选择器
    const errorText = await this.page
      .textContent(
        '.error-message, .verification-error .error-message, [data-testid="error-message"]'
      )
      .catch(() => {
        // 如果找不到，尝试获取整个错误区域
        return this.page.textContent('.verification-error');
      });
    return errorText;
  }

  async clickResendButton(): Promise<void> {
    // 等待重新发送按钮出现
    await this.page.waitForSelector(
      'button:has-text("重新发送"), .resend-button, [data-testid="resend-button"]',
      { state: 'visible', timeout: 10000 }
    );
    await this.page.click(
      'button:has-text("重新发送"), .resend-button, [data-testid="resend-button"]'
    );
  }

  async mockVerifyResponse(status: number, body: any) {
    // 使用通配符匹配所有verify请求
    await this.page.route('**/api/auth/email/verify/**', async route => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
      });
    });
  }
}

// 页面对象模式 - 注册页
class RegisterPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/register`, { waitUntil: 'domcontentloaded' });
    // 等待Vue组件渲染完成（注册页面使用不同的结构）
    await this.page.waitForSelector(
      '.register-view, .register-container, .register-form-wrapper, .register-form',
      {
        state: 'visible',
        timeout: 15000,
      }
    );
    await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
      // 如果网络空闲超时，继续执行
    });
  }

  async fillEmail(email: string) {
    // 等待输入框出现（使用桌面端布局）
    await this.page.waitForSelector('.desktop-layout input[type="email"]', {
      state: 'visible',
      timeout: 10000,
    });
    const emailInput = await this.page.locator('.desktop-layout input[type="email"]').first();
    await emailInput.fill(email);
  }

  async fillPassword(password: string) {
    // 等待密码输入框出现（使用桌面端布局）
    await this.page.waitForSelector('.desktop-layout input[type="password"]', {
      state: 'visible',
      timeout: 10000,
    });
    const passwordInputs = await this.page.locator('.desktop-layout input[type="password"]').all();
    if (passwordInputs.length > 0) {
      await passwordInputs[0].fill(password);
    }
  }

  async fillConfirmPassword(password: string) {
    const passwordInputs = await this.page.locator('.desktop-layout input[type="password"]').all();
    if (passwordInputs.length > 1) {
      await passwordInputs[1].fill(password);
    }
  }

  async fillCaptcha(captchaAnswer: string) {
    await this.page
      .locator('.desktop-layout input[placeholder*="验证码"]')
      .first()
      .fill(captchaAnswer);
  }

  async submit() {
    await this.page.locator('.desktop-layout button[type="submit"]').click();
  }

  async getSuccessMessage(): Promise<string | null> {
    return await this.page.textContent(
      '.success-message, .register-success, [data-testid="success-message"]'
    );
  }

  async mockRegisterResponse(status: number, body: any) {
    await this.page.route('**/api/auth/register/', async route => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
      });
    });
  }

  async mockCaptchaResponse() {
    await this.page.route('**/api/auth/captcha/', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          captcha_id: 'test-captcha-id',
          captcha_image:
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
          expires_in: 300,
        }),
      });
    });
  }

  async mockSendEmailVerificationResponse(status: number, body: any) {
    await this.page.route('**/api/auth/email/verify/send/', async route => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
      });
    });
  }
}

// 邮箱验证 E2E 测试套件
test.describe('邮箱验证功能测试', () => {
  let verificationPage: EmailVerificationPage;
  let registerPage: RegisterPage;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    verificationPage = new EmailVerificationPage(page);
    registerPage = new RegisterPage(page);

    // 设置控制台错误监听器（必须在页面加载前设置）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('成功验证邮箱，显示验证成功页面', async ({ page }) => {
    const validToken = 'valid-verification-token-12345';

    // ✅ 关键修复：必须在 goto 之前设置 mock
    await verificationPage.mockVerifyResponse(200, {
      success: true,
      message: '邮箱验证成功',
    });

    await verificationPage.goto(validToken);
    await page.waitForTimeout(2000); // 等待API调用完成和页面渲染

    // 验证页面显示成功信息
    expect(await verificationPage.isSuccess()).toBe(true);
    const message = await verificationPage.getMessage();
    expect(message).toContain('成功');
  });

  test('验证链接无效，显示错误信息', async ({ page }) => {
    const invalidToken = 'invalid-token-12345';

    // Mock 验证 API 失败响应
    await verificationPage.mockVerifyResponse(400, {
      error: '验证链接无效或已过期',
    });

    await verificationPage.goto(invalidToken);
    await page.waitForTimeout(1000); // 等待API调用完成

    // 验证页面显示错误信息
    expect(await verificationPage.isError()).toBe(true);
    const errorMessage = await verificationPage.getErrorMessage();
    expect(errorMessage).toContain('无效');
  });

  test('验证链接已过期，显示过期提示', async ({ page }) => {
    const expiredToken = 'expired-token-12345';

    // Mock 验证 API 过期响应
    await verificationPage.mockVerifyResponse(400, {
      error: '验证链接已过期，请重新发送验证邮件',
    });

    await verificationPage.goto(expiredToken);
    await page.waitForTimeout(1000); // 等待API调用完成

    // 验证页面显示过期提示
    expect(await verificationPage.isError()).toBe(true);
    const errorMessage = await verificationPage.getErrorMessage();
    expect(errorMessage).toContain('过期');
  });

  test('注册成功后，显示邮箱验证提示', async ({ page, request }) => {
    // ✅ E2E测试直接使用真实API，不mock
    // 注意：此测试会创建真实用户数据，测试后可能需要清理

    // 在goto之前设置验证码响应监听
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') &&
        response.request().method() === 'GET' &&
        response.status() === 200,
      { timeout: 15000 }
    );

    await registerPage.goto();

    // 等待验证码图片加载
    const captchaImage = page.locator('img[alt="验证码"]').first();
    await captchaResponsePromise;
    await expect(captchaImage).toBeVisible({ timeout: 15000 });

    // 使用万能验证码（测试环境专用）
    // 这解决了E2E测试中验证码的随机性问题，避免"调试地狱"
    // 注意：验证码是4位的，所以万能验证码也必须是4位
    const TEST_CAPTCHA_BYPASS = '6666';

    // 在提交之前设置注册API响应监听
    const registerResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/register/') && response.request().method() === 'POST',
      { timeout: 15000 }
    );

    await registerPage.fillEmail(`test-${Date.now()}@example.com`); // 使用唯一邮箱
    await registerPage.fillPassword('Test123456!');
    await registerPage.fillConfirmPassword('Test123456!');
    await registerPage.fillCaptcha(TEST_CAPTCHA_BYPASS);
    await registerPage.submit();

    // 等待注册API响应
    const registerResponse = await registerResponsePromise;
    const registerData = await registerResponse.json();

    // 如果注册失败，输出详细的调试信息
    if (![200, 201].includes(registerResponse.status())) {
      console.log('[TEST] 注册API失败:', {
        status: registerResponse.status(),
        data: registerData,
        url: registerResponse.url(),
      });
      // 如果注册失败，直接抛出错误，不要继续测试
      throw new Error(
        `注册失败: 状态码 ${registerResponse.status()}, 错误: ${JSON.stringify(registerData)}`
      );
    }

    // 验证注册成功（状态码应该是200或201）
    expect([200, 201]).toContain(registerResponse.status());

    // 等待Vue响应式更新完成（检查isRegistered状态）
    // 通过检查DOM中是否存在.email-verification-prompt元素来判断
    await page.waitForFunction(
      () => {
        const prompt = document.querySelector('.email-verification-prompt');
        return prompt !== null && prompt.offsetParent !== null; // 检查元素存在且可见
      },
      { timeout: 15000 }
    );

    // 等待注册成功界面出现（注册成功后，isRegistered会变为true，显示成功消息）
    await page.waitForSelector(
      '[data-testid="success-message"], .success-message, .register-success, .email-verification-prompt',
      { state: 'visible', timeout: 15000 }
    );
    await page.waitForTimeout(1000); // 等待动画完成

    // 验证显示邮箱验证提示
    const successMessage = await registerPage.getSuccessMessage();
    expect(successMessage).not.toBeNull();
    expect(successMessage).toContain('验证');
  });

  test('点击重新发送验证邮件按钮，触发发送API', async ({ page }) => {
    const expiredToken = 'expired-token-12345';

    // Mock 验证 API 过期响应
    await verificationPage.mockVerifyResponse(400, {
      error: '验证链接已过期，请重新发送验证邮件',
    });

    // Mock 重新发送验证邮件 API（在goto之前设置）
    // 注意：VerifyEmailView.vue中有两个方案：
    // 方案1：authStore.sendEmailVerification() → /api/auth/email/verify/send/ (需要认证)
    // 方案2：/api/auth/email/verify/resend/?token=xxx (POST，查询参数)
    // 需要同时Mock两个路径
    let sendEmailCalled = false;

    // Mock 方案1：需要认证的发送API
    await page.route('**/api/auth/email/verify/send/', async route => {
      sendEmailCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: '验证邮件已重新发送',
        }),
      });
    });

    // Mock 方案2：通过token重新发送API
    await page.route(
      url => url.href.includes('/api/auth/email/verify/resend/'),
      async route => {
        sendEmailCalled = true;
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            message: '验证邮件已重新发送，请查收您的邮箱',
          }),
        });
      }
    );

    // 访问页面并模拟已登录状态（重新发送需要认证）
    await verificationPage.goto(expiredToken, true);
    await page.waitForTimeout(1000); // 等待API调用完成

    // 在点击按钮之前设置响应监听（监听两个可能的路径）
    const sendEmailResponsePromise = Promise.race([
      page.waitForResponse(
        response =>
          response.url().includes('/api/auth/email/verify/send/') &&
          response.request().method() === 'POST',
        { timeout: 10000 }
      ),
      page.waitForResponse(
        response =>
          response.url().includes('/api/auth/email/verify/resend/') &&
          response.request().method() === 'POST',
        { timeout: 10000 }
      ),
    ]);

    // 点击重新发送按钮
    await verificationPage.clickResendButton();

    // 等待发送API响应（使用显式等待）
    try {
      await sendEmailResponsePromise;
    } catch (error) {
      // 如果响应等待失败，检查路由是否被调用
      console.log('[TEST] 发送API响应等待失败，检查路由是否被调用');
    }

    await page.waitForTimeout(1000); // 等待API调用完成

    // 验证发送API被调用
    expect(sendEmailCalled).toBe(true);
  });

  test('无token参数访问验证页面，显示错误', async ({ page }) => {
    await verificationPage.goto();
    await page.waitForTimeout(1000);

    // 验证页面显示错误或提示缺少token
    const message = await verificationPage.getMessage();
    const errorMessage = await verificationPage.getErrorMessage();
    expect(
      message?.includes('token') ||
        message?.includes('链接') ||
        errorMessage?.includes('token') ||
        errorMessage?.includes('链接')
    ).toBe(true);
  });
});
