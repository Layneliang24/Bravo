// REQ-ID: REQ-2025-003-user-login
// 验证码测试辅助函数
// 目的：提供验证码相关的测试辅助功能

import { Page, APIRequestContext } from '@playwright/test';

const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';
const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

export interface CaptchaData {
  id: string;
  answer: string;
  image: string;
}

export class CaptchaHelper {
  constructor(
    private page: Page,
    private request: APIRequestContext
  ) {}

  /**
   * 获取验证码并返回答案（测试专用）
   * 注意：实际实现需要后端提供测试端点来获取验证码答案
   */
  async getCaptchaWithAnswer(): Promise<CaptchaData> {
    // 1. 从API获取验证码
    const captchaResponse = await this.request.get(`${API_BASE_URL}/api/auth/captcha/`);
    const captchaData = await captchaResponse.json();

    // 2. 从测试API获取答案（如果存在）
    // 注意：这需要后端提供测试端点
    let answer: string | null = null;

    try {
      const answerResponse = await this.request.get(
        `${API_BASE_URL}/api/test/captcha/answer/?captcha_id=${captchaData.captcha_id}`
      );
      if (answerResponse.ok()) {
        const answerData = await answerResponse.json();
        answer = answerData.answer;
      }
    } catch (e) {
      // 如果测试端点不存在，返回null
      console.warn('测试端点不存在，无法获取验证码答案');
    }

    return {
      id: captchaData.captcha_id,
      answer: answer || 'TEST', // 如果无法获取答案，返回测试值
      image: captchaData.captcha_image,
    };
  }

  /**
   * 验证captcha_id是否正确传递
   */
  async verifyCaptchaIdFlow(expectedId: string): Promise<boolean> {
    // 监听注册请求
    let submittedId: string | null = null;

    this.page.on('request', async request => {
      if (request.url().includes('/api/auth/register/')) {
        try {
          const postData = request.postDataJSON();
          submittedId = postData?.captcha_id || null;
        } catch (e) {
          // 忽略解析错误
        }
      }
    });

    await this.page.click('button:has-text("创建账户"), button[type="submit"]');
    await this.page.waitForTimeout(1000);

    return submittedId === expectedId;
  }

  /**
   * 从页面获取当前验证码ID（通过控制台日志或网络请求）
   */
  async getCurrentCaptchaId(): Promise<string | null> {
    // 方法1: 从网络请求中提取
    const captchaIds: string[] = [];

    this.page.on('response', async response => {
      if (response.url().includes('/api/auth/captcha/')) {
        try {
          const data = await response.json();
          if (data.captcha_id) {
            captchaIds.push(data.captcha_id);
          }
        } catch (e) {
          // 忽略解析错误
        }
      }
    });

    // 等待验证码加载
    await this.page.waitForTimeout(2000);

    return captchaIds.length > 0 ? captchaIds[0] : null;
  }

  /**
   * 填写验证码输入框
   */
  async fillCaptchaInput(answer: string): Promise<void> {
    await this.page.fill('input[placeholder*="验证码"], input[placeholder*="4位验证码"]', answer);
  }

  /**
   * 刷新验证码
   */
  async refreshCaptcha(): Promise<string | null> {
    // 点击验证码区域刷新
    const captchaArea = this.page
      .locator('div[style*="160px"][style*="64px"].cursor-pointer')
      .first();
    await captchaArea.click();
    await this.page.waitForTimeout(1500);

    // 获取新的验证码ID
    return await this.getCurrentCaptchaId();
  }
}
