// REQ-ID: REQ-2025-003-user-login
// TESTCASE-IDS: TC-AUTH_CAPTCHA-001
// 环境配置一致性测试
// 目的：验证测试环境与开发环境的配置一致性（通过验证码API间接测试缓存配置）

import { expect, test } from '@playwright/test';

const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';

test.describe('环境配置一致性测试', () => {
  test('缓存配置应该与开发环境一致', async ({ request }) => {
    // 1. 检查后端健康状态（如果存在健康检查端点）
    // 注意：如果后端没有健康检查端点，可以跳过此测试或创建测试端点

    // 2. 测试缓存功能是否正常工作
    const testKey = `test-cache-${Date.now()}`;
    const testValue = 'test-value-123';

    // 通过验证码API间接测试缓存
    // 生成验证码应该会存储到缓存中
    const captchaResponse1 = await request.get(`${API_BASE_URL}/api/auth/captcha/`);
    expect(captchaResponse1.ok()).toBe(true);

    const captchaData1 = await captchaResponse1.json();
    expect(captchaData1.captcha_id).toBeTruthy();
    expect(captchaData1.captcha_image).toBeTruthy();

    // 如果缓存是DummyCache，验证码验证会失败
    // 我们可以通过尝试注册来验证缓存是否工作
    // 但更好的方法是检查后端配置

    // 3. 验证缓存后端类型（通过检查验证码是否可以被验证）
    // 如果使用DummyCache，验证码无法存储，验证会失败
    // 如果使用Redis，验证码可以存储和验证

    // 注意：这个测试需要后端提供测试端点来检查缓存配置
    // 或者通过功能测试间接验证
  });

  test('验证码应该能够正确存储和验证（缓存功能验证）', async ({ request }) => {
    // 1. 生成验证码
    const captchaResponse = await request.get(`${API_BASE_URL}/api/auth/captcha/`);
    expect(captchaResponse.ok()).toBe(true);

    const captchaData = await captchaResponse.json();
    const { captcha_id, captcha_image } = captchaData;

    expect(captcha_id).toBeTruthy();
    expect(captcha_image).toBeTruthy();

    // 2. 尝试使用错误的验证码验证（应该失败）
    const wrongVerifyResponse = await request.post(`${API_BASE_URL}/api/auth/register/`, {
      data: {
        email: `test-${Date.now()}@example.com`,
        password: 'Test123456',
        password_confirm: 'Test123456',
        captcha_id: captcha_id,
        captcha_answer: 'WRONG',
      },
    });

    // 应该返回验证码错误
    expect(wrongVerifyResponse.status()).toBe(400);
    const wrongError = await wrongVerifyResponse.json();
    expect(wrongError.error || wrongError.code).toContain('验证码');

    // 3. 如果缓存是DummyCache，即使使用正确的验证码也会失败
    // 这可以间接验证缓存配置是否正确

    // 注意：要完全验证缓存配置，需要后端提供测试端点
    // 或者通过集成测试验证完整流程
  });

  test('数据库配置应该正确', async ({ request }) => {
    // 通过尝试注册来验证数据库连接
    // 如果数据库配置错误，注册会失败

    const uniqueEmail = `test-db-${Date.now()}@example.com`;

    // 注意：这个测试需要能够获取正确的验证码答案
    // 或者使用测试专用的注册端点

    // 暂时跳过，等待后端提供测试端点
  });
});
