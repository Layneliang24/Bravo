// REQ-ID: REQ-2025-003-user-login
// 邮箱验证 E2E 测试
// 使用 Playwright 进行端到端测试

import { test, expect, Page } from '@playwright/test';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3001';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://localhost:8000';

// 页面对象模式 - 邮箱验证页
class EmailVerificationPage {
  constructor(private page: Page) {}

  async goto(token?: string) {
    const url = token ? `${BASE_URL}/verify-email?token=${token}` : `${BASE_URL}/verify-email`;
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
  }

  async getTitle(): Promise<string | null> {
    return await this.page.textContent('h1, .page-title, [data-testid="title"]');
  }

  async getMessage(): Promise<string | null> {
    return await this.page.textContent('.verification-message, .message, [data-testid="message"]');
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
    return await this.page.textContent(
      '.error-message, .verification-error-message, [data-testid="error-message"]'
    );
  }

  async clickResendButton(): Promise<void> {
    await this.page.click(
      'button:has-text("重新发送"), .resend-button, [data-testid="resend-button"]'
    );
  }

  async mockVerifyResponse(status: number, body: any) {
    await this.page.route(`${API_BASE_URL}/api/auth/email/verify/*`, async route => {
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
    await this.page.goto(`${BASE_URL}/register`);
    await this.page.waitForLoadState('networkidle');
  }

  async fillEmail(email: string) {
    await this.page.fill('input[type="email"]', email);
  }

  async fillPassword(password: string) {
    await this.page.fill('input[type="password"]', password);
  }

  async fillConfirmPassword(password: string) {
    await this.page.fill('input[type="password"]:nth-of-type(2)', password);
  }

  async fillCaptcha(captchaAnswer: string) {
    await this.page.fill('input[placeholder*="验证码"]', captchaAnswer);
  }

  async submit() {
    await this.page.click('button[type="submit"]');
  }

  async getSuccessMessage(): Promise<string | null> {
    return await this.page.textContent(
      '.success-message, .register-success, [data-testid="success-message"]'
    );
  }

  async mockRegisterResponse(status: number, body: any) {
    await this.page.route(`${API_BASE_URL}/api/auth/register/`, async route => {
      await route.fulfill({
        status,
        contentType: 'application/json',
        body: JSON.stringify(body),
      });
    });
  }

  async mockCaptchaResponse() {
    await this.page.route(`${API_BASE_URL}/api/auth/captcha/`, async route => {
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
    await this.page.route(`${API_BASE_URL}/api/auth/email/verify/send/`, async route => {
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

  test.beforeEach(async ({ page }) => {
    verificationPage = new EmailVerificationPage(page);
    registerPage = new RegisterPage(page);
  });

  test('成功验证邮箱，显示验证成功页面', async ({ page }) => {
    const validToken = 'valid-verification-token-12345';

    // Mock 验证 API 成功响应
    await verificationPage.mockVerifyResponse(200, {
      success: true,
      message: '邮箱验证成功',
    });

    await verificationPage.goto(validToken);
    await page.waitForTimeout(1000); // 等待API调用完成

    // 验证页面显示成功信息
    expect(await verificationPage.isSuccess()).toBe(true);
    const message = await verificationPage.getMessage();
    expect(message).toContain('成功');
  });

  test('验证链接无效，显示错误信息', async ({ page }) => {
    const invalidToken = 'invalid-token-12345';

    // Mock 验证 API 失败响应
    await verificationPage.mockVerifyResponse(400, {
      code: 'invalid_token',
      detail: '验证链接无效或已过期',
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
      code: 'token_expired',
      detail: '验证链接已过期，请重新发送验证邮件',
    });

    await verificationPage.goto(expiredToken);
    await page.waitForTimeout(1000); // 等待API调用完成

    // 验证页面显示过期提示
    expect(await verificationPage.isError()).toBe(true);
    const errorMessage = await verificationPage.getErrorMessage();
    expect(errorMessage).toContain('过期');
  });

  test('注册成功后，显示邮箱验证提示', async ({ page }) => {
    // Mock 注册 API 成功响应
    await registerPage.mockRegisterResponse(201, {
      success: true,
      message: '注册成功，请查收验证邮件',
      user: {
        id: 1,
        email: 'test@example.com',
      },
    });

    // Mock 验证码 API
    await registerPage.mockCaptchaResponse();

    await registerPage.goto();
    await registerPage.fillEmail('test@example.com');
    await registerPage.fillPassword('password123');
    await registerPage.fillConfirmPassword('password123');
    await registerPage.fillCaptcha('1234');
    await registerPage.submit();
    await page.waitForTimeout(1000); // 等待API调用完成

    // 验证显示邮箱验证提示
    const successMessage = await registerPage.getSuccessMessage();
    expect(successMessage).toContain('验证');
  });

  test('点击重新发送验证邮件按钮，触发发送API', async ({ page }) => {
    const expiredToken = 'expired-token-12345';

    // Mock 验证 API 过期响应
    await verificationPage.mockVerifyResponse(400, {
      code: 'token_expired',
      detail: '验证链接已过期，请重新发送验证邮件',
    });

    // Mock 重新发送验证邮件 API
    let sendEmailCalled = false;
    await page.route(`${API_BASE_URL}/api/auth/email/verify/send/`, async route => {
      sendEmailCalled = true;
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          message: '验证邮件已重新发送',
        }),
      });
    });

    await verificationPage.goto(expiredToken);
    await page.waitForTimeout(1000); // 等待API调用完成

    // 点击重新发送按钮
    await verificationPage.clickResendButton();
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
