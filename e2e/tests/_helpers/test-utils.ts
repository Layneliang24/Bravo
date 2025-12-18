// REQ-ID: REQ-2025-003-user-login
// 测试工具函数集合
// 目的：提供通用的测试辅助功能

import { Page } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

/**
 * 等待并捕获网络响应
 * 注意：必须在页面加载之前调用此函数，以便设置监听器
 */
export async function waitForResponse(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = 10000
): Promise<any> {
  const responses: any[] = [];
  let handler: ((response: any) => Promise<void>) | null = null;

  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      if (handler) {
        page.removeListener('response', handler);
      }
      if (responses.length > 0) {
        resolve(responses[0]);
      } else {
        reject(new Error(`Timeout waiting for response matching ${urlPattern}`));
      }
    }, timeout);

    handler = async (response: any) => {
      const url = response.url();
      const matches =
        typeof urlPattern === 'string' ? url.includes(urlPattern) : urlPattern.test(url);

      if (matches) {
        try {
          const data = await response.json();
          responses.push(data);
          if (responses.length === 1) {
            // 第一个响应到达时立即resolve
            clearTimeout(timeoutId);
            if (handler) {
              page.removeListener('response', handler);
            }
            resolve(data);
          }
        } catch (e) {
          // 忽略解析错误，继续等待
        }
      }
    };

    page.on('response', handler);
  });
}

/**
 * 等待并捕获多个网络响应
 */
export async function waitForResponses(
  page: Page,
  urlPattern: string | RegExp,
  count: number = 1,
  timeout: number = 5000
): Promise<any[]> {
  const responses: any[] = [];

  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      page.removeListener('response', handler);
      if (responses.length >= count) {
        resolve(responses);
      } else {
        reject(new Error(`Timeout: Expected ${count} responses, got ${responses.length}`));
      }
    }, timeout);

    const handler = async (response: any) => {
      const url = response.url();
      const matches =
        typeof urlPattern === 'string' ? url.includes(urlPattern) : urlPattern.test(url);

      if (matches) {
        try {
          const data = await response.json();
          responses.push(data);
          if (responses.length >= count) {
            clearTimeout(timeoutId);
            page.removeListener('response', handler);
            resolve(responses);
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    };

    page.on('response', handler);
  });
}

/**
 * 等待并捕获网络请求
 */
export async function waitForRequest(
  page: Page,
  urlPattern: string | RegExp,
  timeout: number = 5000
): Promise<any> {
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      page.removeListener('request', handler);
      reject(new Error(`Timeout waiting for request matching ${urlPattern}`));
    }, timeout);

    const handler = async (request: any) => {
      const url = request.url();
      const matches =
        typeof urlPattern === 'string' ? url.includes(urlPattern) : urlPattern.test(url);

      if (matches) {
        clearTimeout(timeoutId);
        page.removeListener('request', handler);
        try {
          const postData = request.postDataJSON();
          resolve(postData);
        } catch (e) {
          resolve(null);
        }
      }
    };

    page.on('request', handler);
  });
}

/**
 * 填写注册表单
 */
export async function fillRegisterForm(
  page: Page,
  options: {
    email?: string;
    password?: string;
    passwordConfirm?: string;
    captchaAnswer?: string;
  }
): Promise<void> {
  const {
    email = `test-${Date.now()}@example.com`,
    password = 'Test123456',
    passwordConfirm = 'Test123456',
    captchaAnswer = 'TEST',
  } = options;

  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);

  const confirmPasswordInput = page.locator('input[type="password"]').nth(1);
  await confirmPasswordInput.waitFor({ state: 'visible', timeout: 5000 });
  await confirmPasswordInput.fill(passwordConfirm);

  // 验证码输入框的placeholder是"CODE"，需要等待输入框出现
  const captchaInput = page
    .locator(
      'input[placeholder*="CODE"], input[placeholder*="验证码"], input[placeholder*="4位验证码"]'
    )
    .first();
  await captchaInput.waitFor({ state: 'visible', timeout: 10000 });
  await captchaInput.fill(captchaAnswer);
}

/**
 * 等待表单验证完成（按钮启用）
 */
export async function waitForFormValid(page: Page, timeout: number = 5000): Promise<boolean> {
  const submitButton = page.locator('button:has-text("创建账户"), button[type="submit"]');

  try {
    await submitButton.waitFor({ state: 'visible', timeout });

    // 等待按钮启用
    let attempts = 0;
    const maxAttempts = 10;

    while (attempts < maxAttempts) {
      const isDisabled = await submitButton.isDisabled();
      if (!isDisabled) {
        return true;
      }
      await page.waitForTimeout(500);
      attempts++;
    }

    return false;
  } catch (e) {
    return false;
  }
}

/**
 * 获取当前页面的验证码ID（从网络响应中）
 */
export async function getCaptchaIdFromPage(page: Page): Promise<string | null> {
  try {
    const captchaData = await waitForResponse(page, '/api/auth/captcha/', 5000);
    return captchaData?.captcha_id || null;
  } catch (e) {
    return null;
  }
}
