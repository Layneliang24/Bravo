// REQ-ID: REQ-2025-003-user-login
// 登录预验证 E2E 测试
// 使用 Playwright 进行端到端测试

import { test, expect, Page } from '@playwright/test';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3001';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://localhost:8000';

// 页面对象模式 - 登录页（带预验证）
class LoginPreviewPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/login`);
    await this.page.waitForLoadState('networkidle');
  }

  async fillEmail(email: string) {
    await this.page.fill('input[type="email"]', email);
  }

  async fillPassword(password: string) {
    await this.page.fill('input[type="password"]', password);
  }

  async getCaptchaId(): Promise<string | null> {
    // 等待验证码加载
    await this.page.waitForSelector('[data-testid="captcha"]', {
      timeout: 5000,
    });
    // 从验证码组件获取 captcha_id（需要根据实际实现调整）
    return await this.page.getAttribute('[data-testid="captcha"]', 'data-captcha-id');
  }

  async fillCaptcha(captchaAnswer: string) {
    await this.page.fill('input[placeholder*="验证码"]', captchaAnswer);
  }

  async blurPassword() {
    await this.page.blur('input[type="password"]');
  }

  async waitForPreviewLoading() {
    await this.page.waitForSelector('.loading', { timeout: 2000 }).catch(() => {});
  }

  async waitForPreviewUser() {
    await this.page.waitForSelector('.user-info', { timeout: 5000 }).catch(() => {});
  }

  async isPreviewVisible(): Promise<boolean> {
    const preview = await this.page.$('.user-preview');
    return preview !== null;
  }

  async getPreviewDisplayName(): Promise<string | null> {
    return await this.page.textContent('.display-name');
  }

  async hasPreviewAvatar(): Promise<boolean> {
    const avatar = await this.page.$('.default-avatar img');
    return avatar !== null;
  }

  async hasPreviewDefaultAvatar(): Promise<boolean> {
    const defaultAvatar = await this.page.$('.default-avatar .avatar-letter');
    return defaultAvatar !== null;
  }

  async mockPreviewResponse(response: any) {
    await this.page.route(`${API_BASE_URL}/api/auth/preview/`, async route => {
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

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPreviewPage(page);
    await loginPage.goto();
  });

  test('成功预验证并显示用户头像', async ({ page }) => {
    // Mock 预验证 API 响应
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

    // 等待验证码加载并填写
    const captchaId = await loginPage.getCaptchaId();
    if (captchaId) {
      await loginPage.fillCaptcha('1234');
    }

    // 触发预验证（密码失焦）
    await loginPage.blurPassword();

    // 等待预验证完成
    await loginPage.waitForPreviewUser();

    // 验证预览组件显示
    expect(await loginPage.isPreviewVisible()).toBe(true);
    expect(await loginPage.getPreviewDisplayName()).toBe('Test User');
    expect(await loginPage.hasPreviewAvatar()).toBe(true);
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

    // 等待验证码加载并填写
    const captchaId = await loginPage.getCaptchaId();
    if (captchaId) {
      await loginPage.fillCaptcha('1234');
    }

    // 触发预验证
    await loginPage.blurPassword();

    // 等待预验证完成
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

    // 等待验证码加载并填写
    const captchaId = await loginPage.getCaptchaId();
    if (captchaId) {
      await loginPage.fillCaptcha('1234');
    }

    // 触发预验证
    await loginPage.blurPassword();

    // 等待一段时间，确保预验证完成
    await page.waitForTimeout(1000);

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
    await page.route(`${API_BASE_URL}/api/auth/preview/`, async route => {
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

    // 等待验证码加载并填写
    const captchaId = await loginPage.getCaptchaId();
    if (captchaId) {
      await loginPage.fillCaptcha('1234');
    }

    // 快速多次触发预验证（通过多次失焦）
    for (let i = 0; i < 5; i++) {
      await loginPage.blurPassword();
      await page.waitForTimeout(100); // 快速连续触发
    }

    // 等待防抖延迟（500ms）加上 API 调用时间
    await page.waitForTimeout(1000);

    // 验证 API 调用次数应该较少（由于防抖）
    // 理想情况下应该只有 1-2 次调用，而不是 5 次
    expect(apiCallCount).toBeLessThan(5);
  });
});
