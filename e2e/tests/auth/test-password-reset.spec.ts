// REQ-ID: REQ-2025-003-user-login
// 密码找回 E2E 测试
// 使用 Playwright 进行端到端测试
// TESTCASE-IDS: TC-AUTH_RESET-002

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

// 页面对象模式 - 发送密码重置邮件页
class PasswordResetRequestPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/forgot-password`, { waitUntil: 'domcontentloaded' });
    // 等待Vue组件渲染完成
    await this.page.waitForSelector(
      '.forgot-password-view, [data-testid="auth-card"], .auth-card, .password-reset-form',
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
    // 等待输入框出现（密码重置页面使用type="email"）
    await this.page.waitForSelector(
      'input[type="email"], input[placeholder*="邮箱"], input[placeholder*="email"]',
      { state: 'visible', timeout: 10000 }
    );
    const emailInput = await this.page
      .locator('input[type="email"], input[placeholder*="邮箱"], input[placeholder*="email"]')
      .first();
    await emailInput.fill(email);
  }

  async fillCaptcha(answer: string) {
    // 验证码输入框placeholder是"CODE"
    await this.page.fill('input[placeholder="CODE"]', answer);
  }

  async clickSendButton() {
    await this.page.click('button[type="submit"]');
  }

  async getSuccessMessage(): Promise<string | null> {
    return await this.page.textContent('.success-message');
  }

  async getErrorMessage(): Promise<string | null> {
    return await this.page.textContent('.error-message');
  }

  async waitForSuccessMessage() {
    await this.page.waitForSelector('.success-message', { timeout: 5000 });
  }
}

// 页面对象模式 - 重置密码页
class ResetPasswordPage {
  constructor(private page: Page) {}

  async goto(token: string) {
    await this.page.goto(`${BASE_URL}/reset-password?token=${token}`, {
      waitUntil: 'domcontentloaded',
    });
    // 等待Vue组件渲染完成
    await this.page.waitForSelector(
      '.reset-password-view, [data-testid="auth-card"], .auth-card, .reset-password-form',
      {
        state: 'visible',
        timeout: 15000,
      }
    );
    await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {
      // 如果网络空闲超时，继续执行
    });
  }

  async fillNewPassword(password: string) {
    // 等待密码输入框出现
    await this.page.waitForSelector('input[type="password"]', { state: 'visible', timeout: 10000 });
    const passwordInputs = await this.page.locator('input[type="password"]').all();
    if (passwordInputs.length > 0) {
      await passwordInputs[0].fill(password);
    }
  }

  async fillConfirmPassword(password: string) {
    // 等待确认密码输入框出现
    await this.page.waitForSelector('input[type="password"]', { state: 'visible', timeout: 10000 });
    const passwordInputs = await this.page.locator('input[type="password"]').all();
    if (passwordInputs.length > 1) {
      await passwordInputs[1].fill(password);
    }
  }

  async clickResetButton() {
    // 等待提交按钮出现
    await this.page.waitForSelector('button[type="submit"]', { state: 'visible', timeout: 10000 });
    await this.page.click('button[type="submit"]');
  }

  async getSuccessMessage(): Promise<string | null> {
    return await this.page.textContent('.success-message');
  }

  async getErrorMessage(): Promise<string | null> {
    return await this.page.textContent('.error-message');
  }

  async waitForSuccessMessage() {
    await this.page.waitForSelector('.success-message', { timeout: 5000 });
  }

  async waitForRedirect() {
    await this.page.waitForURL('**/login**', { timeout: 5000 });
  }
}

test.describe('密码找回流程 E2E 测试', () => {
  let passwordResetRequestPage: PasswordResetRequestPage;
  let resetPasswordPage: ResetPasswordPage;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    passwordResetRequestPage = new PasswordResetRequestPage(page);
    resetPasswordPage = new ResetPasswordPage(page);

    // 设置控制台错误监听器（必须在页面加载前设置）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();

    // Mock captcha API for all tests
    await page.route(`${API_BASE_URL}/api/auth/captcha/`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          captcha_id: 'test-captcha-id',
          captcha_image:
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=',
        }),
      });
    });
  });

  test('完整密码找回流程：从请求重置邮件到成功重置密码', async ({ page }) => {
    // Step 1: 请求密码重置邮件
    await page.route(`${API_BASE_URL}/api/auth/password/reset/send/`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: '密码重置邮件已发送，请查收',
        }),
      });
    });

    // 在goto之前设置验证码响应监听
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') && response.request().method() === 'GET',
      { timeout: 10000 }
    );

    await passwordResetRequestPage.goto();

    // 等待验证码组件加载
    await captchaResponsePromise;
    await page.waitForSelector('img[alt="验证码"]', { state: 'visible', timeout: 10000 });

    await passwordResetRequestPage.fillEmail('test@example.com');
    await passwordResetRequestPage.fillCaptcha(TEST_CAPTCHA_BYPASS);
    await passwordResetRequestPage.clickSendButton();
    await passwordResetRequestPage.waitForSuccessMessage();

    const successMessage = await passwordResetRequestPage.getSuccessMessage();
    expect(successMessage).toContain('密码重置邮件已发送');

    // Step 2: 模拟用户点击邮件中的重置链接，访问重置密码页面
    const resetToken = 'valid-reset-token';
    await page.route(`${API_BASE_URL}/api/auth/password/reset/`, async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          message: '密码重置成功',
        }),
      });
    });

    await resetPasswordPage.goto(resetToken);
    await resetPasswordPage.fillNewPassword('NewPassword123!');
    await resetPasswordPage.fillConfirmPassword('NewPassword123!');
    await resetPasswordPage.clickResetButton();
    await resetPasswordPage.waitForSuccessMessage();

    const resetSuccessMessage = await resetPasswordPage.getSuccessMessage();
    expect(resetSuccessMessage).toContain('密码重置成功');

    // Step 3: 验证自动跳转到登录页
    await resetPasswordPage.waitForRedirect();
    expect(page.url()).toContain('/login');
  });

  test('请求密码重置邮件失败（验证码错误）', async ({ page }) => {
    await page.route(`${API_BASE_URL}/api/auth/password/reset/send/`, async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '验证码错误',
          code: 'INVALID_CAPTCHA',
        }),
      });
    });

    // 在goto之前设置验证码响应监听
    const captchaResponsePromise = page.waitForResponse(
      response =>
        response.url().includes('/api/auth/captcha/') && response.request().method() === 'GET',
      { timeout: 10000 }
    );

    await passwordResetRequestPage.goto();

    // 等待验证码组件加载
    await captchaResponsePromise;
    await page.waitForSelector('img[alt="验证码"]', { state: 'visible', timeout: 10000 });

    await passwordResetRequestPage.fillEmail('test@example.com');
    // 使用非万能验证码的值测试错误场景
    await passwordResetRequestPage.fillCaptcha('WRON');
    await passwordResetRequestPage.clickSendButton();

    const errorMessage = await passwordResetRequestPage.getErrorMessage();
    expect(errorMessage).toContain('验证码错误');
  });

  test('重置密码失败（无效token）', async ({ page }) => {
    await page.route(`${API_BASE_URL}/api/auth/password/reset/`, async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '无效的重置链接',
          code: 'INVALID_TOKEN',
        }),
      });
    });

    await resetPasswordPage.goto('invalid-token');
    await resetPasswordPage.fillNewPassword('NewPassword123!');
    await resetPasswordPage.fillConfirmPassword('NewPassword123!');
    await resetPasswordPage.clickResetButton();

    const errorMessage = await resetPasswordPage.getErrorMessage();
    expect(errorMessage).toContain('无效');
  });

  test('重置密码失败（密码不匹配）', async ({ page }) => {
    await page.route(`${API_BASE_URL}/api/auth/password/reset/`, async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '两次输入的密码不一致',
          code: 'PASSWORD_MISMATCH',
        }),
      });
    });

    await resetPasswordPage.goto('valid-token');
    await resetPasswordPage.fillNewPassword('NewPassword123!');
    await resetPasswordPage.fillConfirmPassword('DifferentPassword123!');
    await resetPasswordPage.clickResetButton();

    const errorMessage = await resetPasswordPage.getErrorMessage();
    expect(errorMessage).toContain('不一致');
  });

  test('重置密码失败（弱密码）', async ({ page }) => {
    await page.route(`${API_BASE_URL}/api/auth/password/reset/`, async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          error: '密码长度至少为8位',
          code: 'WEAK_PASSWORD',
        }),
      });
    });

    await resetPasswordPage.goto('valid-token');
    await resetPasswordPage.fillNewPassword('weak');
    await resetPasswordPage.fillConfirmPassword('weak');
    await resetPasswordPage.clickResetButton();

    const errorMessage = await resetPasswordPage.getErrorMessage();
    expect(errorMessage).toContain('至少为8位');
  });

  test('无token参数访问重置密码页面，显示错误', async ({ page }) => {
    await resetPasswordPage.goto('');

    const errorMessage = await resetPasswordPage.getErrorMessage();
    expect(errorMessage).toContain('无效');
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });
});
