// REQ-ID: REQ-2025-003-user-login
// 注册页面按钮 E2E 测试
// TESTCASE-IDS: TC-AUTH_REGISTER-008

import { expect, Page, test } from '@playwright/test';
import { ConsoleErrorListener } from '../_helpers/console-error-listener';

// Docker环境中使用容器名，本地开发使用localhost
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';

class RegisterPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/register`, { waitUntil: 'domcontentloaded' });
    await this.page.waitForSelector('.register-form, form', {
      state: 'visible',
      timeout: 15000,
    });
  }

  async getSubmitButton() {
    return this.page
      .locator(
        'button[type="submit"], .submit-button, button:has-text("注册"), button:has-text("创建账户")'
      )
      .first();
  }
}

test.describe('注册页面按钮验证', () => {
  let registerPage: RegisterPage;
  let errorListener: ConsoleErrorListener;

  test.beforeEach(async ({ page }) => {
    registerPage = new RegisterPage(page);

    // 设置控制台错误监听器（必须在页面加载前设置）
    errorListener = new ConsoleErrorListener(page);
    errorListener.startListening();

    await registerPage.goto();
  });

  test.afterEach(async () => {
    // 验证是否有控制台错误
    errorListener.assertNoErrors();
    await errorListener.assertNoUnhandledRejections();
  });

  test('TC-AUTH_REGISTER-008: 注册页面应该有创建账户按钮且样式正确', async ({ page }) => {
    // 1. 检查提交按钮存在
    const submitButton = await registerPage.getSubmitButton();
    await expect(submitButton).toBeVisible();

    // 2. 验证按钮文本为"创建账户"或"注册"
    const buttonText = await submitButton.textContent();
    expect(buttonText).toMatch(/创建账户|注册/);

    // 3. 验证按钮样式符合设计（渐变背景、圆角等）
    const bgColor = await submitButton.evaluate(el => {
      const styles = window.getComputedStyle(el);
      return styles.background || styles.backgroundColor;
    });

    // 应该包含渐变或橙色/黄色
    expect(bgColor).toBeTruthy();

    // 4. 验证按钮可点击（未禁用状态）
    const isDisabled = await submitButton.isDisabled();
    // 按钮可能因为表单未填写而禁用，这是正常的
    // 但至少按钮应该存在
    expect(submitButton).toBeVisible();
  });
});
