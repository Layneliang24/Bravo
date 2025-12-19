// REQ-ID: REQ-2025-003-user-login
// 登录预览UI细节 E2E 测试
// 使用 Playwright 进行端到端测试
// TESTCASE-IDS: TC-AUTH_UI-015, TC-AUTH_UI-016

import { expect, Page, test } from '@playwright/test';
import { ConsoleErrorListener } from '../_helpers/console-error-listener';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

// 万能验证码（测试环境专用）
const TEST_CAPTCHA_BYPASS = '6666';

// 页面对象模式 - 登录页（预览UI细节）
class LoginPreviewUIPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
    await this.page.waitForSelector('[data-testid="auth-card"], .auth-card', {
      state: 'visible',
      timeout: 15000,
    });
    await this.page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  }

  async fillEmail(email: string) {
    const emailInput = await this.page.locator('input[type="text"], input[type="email"]').first();
    await emailInput.fill(email);
  }

  async fillPassword(password: string) {
    const passwordInput = await this.page.locator('input[type="password"]').first();
    await passwordInput.fill(password);
  }

  async fillCaptcha(captcha: string) {
    const captchaInput = await this.page
      .locator('input[placeholder="CODE"], input[placeholder*="验证码"]')
      .first();
    await captchaInput.fill(captcha);
  }

  async getPreviewComponent() {
    return this.page
      .locator('[data-testid="user-preview"], .user-preview, .preview-avatar')
      .first();
  }

  async getPreviewAvatar() {
    return this.page
      .locator('[data-testid="preview-avatar"], .preview-avatar img, .preview-avatar .avatar')
      .first();
  }

  async getPreviewText() {
    return this.page
      .locator('[data-testid="preview-text"], .preview-text, .preview-message')
      .first();
  }

  async getScanningRing() {
    return this.page.locator('[data-testid="scanning-ring"], .scanning-ring, .avatar-ring').first();
  }
}

test.describe('登录预览UI细节验证', () => {
  let previewPage: LoginPreviewUIPage;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    previewPage = new LoginPreviewUIPage(page);
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();
    await page.setViewportSize({ width: 1200, height: 800 });
    await previewPage.goto();
  });

  test.afterEach(async () => {
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('TC-AUTH_UI-015: 头像预览转圈动画应该以头像中心为旋转中心', async ({ page }) => {
    // 1. 打开登录页
    await previewPage.goto();

    // 2. 输入有效账号密码触发预览
    await previewPage.fillEmail('test@example.com');
    await previewPage.fillPassword('SecurePass123');
    await previewPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 等待预览出现
    const previewComponent = await previewPage.getPreviewComponent();
    await expect(previewComponent).toBeVisible({ timeout: 5000 });

    // 3. 检查扫描圆环的旋转中心
    const scanningRing = await previewPage.getScanningRing();
    const avatar = await previewPage.getPreviewAvatar();

    if (await scanningRing.isVisible().catch(() => false)) {
      const ringBox = await scanningRing.boundingBox();
      const avatarBox = await avatar.boundingBox();

      if (ringBox && avatarBox) {
        // 计算头像中心
        const avatarCenterX = avatarBox.x + avatarBox.width / 2;
        const avatarCenterY = avatarBox.y + avatarBox.height / 2;

        // 计算圆环中心
        const ringCenterX = ringBox.x + ringBox.width / 2;
        const ringCenterY = ringBox.y + ringBox.height / 2;

        // 4. 验证圆环围绕头像中心旋转（允许±5px误差）
        expect(Math.abs(ringCenterX - avatarCenterX)).toBeLessThan(5);
        expect(Math.abs(ringCenterY - avatarCenterY)).toBeLessThan(5);

        // 验证动画流畅（检查CSS transform-origin）
        const transformOrigin = await scanningRing.evaluate(el => {
          return getComputedStyle(el).transformOrigin;
        });

        // transform-origin应该接近中心（50% 50%）
        expect(transformOrigin).toMatch(/50%/);
      }
    }
  });

  test('TC-AUTH_UI-016: 头像预览文案应该显示Account Verified而非Login Successful', async ({
    page,
  }) => {
    // 1. 打开登录页
    await previewPage.goto();

    // 2. 输入有效账号密码触发预览
    await previewPage.fillEmail('test@example.com');
    await previewPage.fillPassword('SecurePass123');
    await previewPage.fillCaptcha(TEST_CAPTCHA_BYPASS);

    // 等待预览出现
    const previewComponent = await previewPage.getPreviewComponent();
    await expect(previewComponent).toBeVisible({ timeout: 5000 });

    // 3. 检查预览区域的文案
    const previewText = await previewPage.getPreviewText();
    const textContent = await previewText.textContent();

    // 4. 验证显示Account Verified而非Login Successful
    expect(textContent).toContain('Account Verified');
    expect(textContent).not.toContain('Login Successful');
  });
});
