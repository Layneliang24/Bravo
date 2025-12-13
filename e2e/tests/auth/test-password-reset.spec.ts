// REQ-ID: REQ-2025-003-user-login
// 密码找回 E2E 测试
// 使用 Playwright 进行端到端测试
// TESTCASE-IDS: TC-AUTH_RESET-002

import { test, expect, Page } from '@playwright/test';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3001';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://localhost:8000';

// 页面对象模式 - 发送密码重置邮件页
class PasswordResetRequestPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/forgot-password`);
    await this.page.waitForLoadState('networkidle');
  }

  async fillEmail(email: string) {
    await this.page.fill('input[type="email"]', email);
  }

  async fillCaptcha(answer: string) {
    await this.page.fill('input[placeholder*="验证码"]', answer);
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
    await this.page.goto(`${BASE_URL}/reset-password?token=${token}`);
    await this.page.waitForLoadState('networkidle');
  }

  async fillNewPassword(password: string) {
    const passwordInputs = await this.page.locator('input[type="password"]').all();
    if (passwordInputs.length > 0) {
      await passwordInputs[0].fill(password);
    }
  }

  async fillConfirmPassword(password: string) {
    const passwordInputs = await this.page.locator('input[type="password"]').all();
    if (passwordInputs.length > 1) {
      await passwordInputs[1].fill(password);
    }
  }

  async clickResetButton() {
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

  test.beforeEach(async ({ page }) => {
    passwordResetRequestPage = new PasswordResetRequestPage(page);
    resetPasswordPage = new ResetPasswordPage(page);

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

    await passwordResetRequestPage.goto();
    await passwordResetRequestPage.fillEmail('test@example.com');
    await passwordResetRequestPage.fillCaptcha('1234');
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

    await passwordResetRequestPage.goto();
    await passwordResetRequestPage.fillEmail('test@example.com');
    await passwordResetRequestPage.fillCaptcha('wrong');
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
});
