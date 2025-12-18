// REQ-ID: REQ-2025-003-user-login
// 验证码测试辅助函数
// 用于E2E测试中获取验证码答案

import { APIRequestContext } from '@playwright/test';

/**
 * 通过后端API获取验证码答案（测试环境专用）
 * 注意：生产环境不应该暴露此API
 */
export async function getCaptchaAnswer(
  request: APIRequestContext,
  captchaId: string,
  apiBaseUrl: string
): Promise<string | null> {
  try {
    // 尝试通过测试API获取验证码答案
    // 如果API不存在，返回null
    const response = await request.get(`${apiBaseUrl}/api/auth/captcha/${captchaId}/answer/`, {
      headers: {
        'X-Test-Environment': 'true', // 标识这是测试环境请求
      },
    });

    if (response.ok()) {
      const data = await response.json();
      return data.answer || null;
    }
  } catch (error) {
    // API不存在或请求失败，返回null
    console.warn('[CaptchaHelper] Failed to get captcha answer from API:', error);
  }

  return null;
}

/**
 * 从验证码API响应中提取captcha_id
 */
export function extractCaptchaIdFromResponse(responseData: any): string | null {
  return responseData?.captcha_id || null;
}
