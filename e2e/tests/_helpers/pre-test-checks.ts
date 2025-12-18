// REQ-ID: REQ-2025-003-user-login
// 测试前检查工具
// 目的：在运行测试前验证环境配置和系统状态

import { Page, APIRequestContext } from '@playwright/test';

const API_BASE_URL = process.env.TEST_API_BASE_URL || 'http://backend:8000';
const BASE_URL = process.env.TEST_BASE_URL || 'http://frontend:3000';

export interface PreTestCheck {
  name: string;
  passed: boolean;
  message: string;
}

export async function runPreTestChecks(
  page: Page,
  request: APIRequestContext
): Promise<PreTestCheck[]> {
  const checks: PreTestCheck[] = [];

  // 1. 检查后端服务可用性
  try {
    const healthResponse = await request.get(`${API_BASE_URL}/api/auth/captcha/`);
    checks.push({
      name: '后端服务',
      passed: healthResponse.ok(),
      message: healthResponse.ok() ? '后端服务可用' : `后端服务不可用: ${healthResponse.status()}`,
    });
  } catch (error) {
    checks.push({
      name: '后端服务',
      passed: false,
      message: `后端服务连接失败: ${error}`,
    });
  }

  // 2. 检查前端页面加载
  try {
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'domcontentloaded', timeout: 10000 });
    const formExists = (await page.locator('form.register-form').count()) > 0;
    checks.push({
      name: '注册页面',
      passed: formExists,
      message: formExists ? '注册页面加载成功' : '注册页面加载失败',
    });
  } catch (error) {
    checks.push({
      name: '注册页面',
      passed: false,
      message: `注册页面加载失败: ${error}`,
    });
  }

  // 3. 检查验证码API
  try {
    const captchaResponse = await request.get(`${API_BASE_URL}/api/auth/captcha/`);
    const captchaData = await captchaResponse.json();
    checks.push({
      name: '验证码API',
      passed: captchaResponse.ok() && !!captchaData.captcha_id,
      message: captchaResponse.ok() && !!captchaData.captcha_id ? '验证码API正常' : '验证码API异常',
    });
  } catch (error) {
    checks.push({
      name: '验证码API',
      passed: false,
      message: `验证码API调用失败: ${error}`,
    });
  }

  // 4. 检查组件实例数量（响应式布局）
  try {
    await page.goto(`${BASE_URL}/register`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);

    const visibleForms = await page.locator('form.register-form:visible').count();
    const captchaImages = await page.locator('img[alt="验证码"]:visible').count();

    checks.push({
      name: '组件实例',
      passed: visibleForms === 1 && captchaImages === 1,
      message:
        visibleForms === 1 && captchaImages === 1
          ? '组件实例数量正确'
          : `组件实例数量异常: 表单${visibleForms}个, 验证码${captchaImages}个`,
    });
  } catch (error) {
    checks.push({
      name: '组件实例',
      passed: false,
      message: `组件实例检查失败: ${error}`,
    });
  }

  // 报告检查结果
  const failedChecks = checks.filter(c => !c.passed);
  if (failedChecks.length > 0) {
    console.error('⚠️ 测试前检查失败:');
    failedChecks.forEach(check => {
      console.error(`  ❌ ${check.name}: ${check.message}`);
    });
  } else {
    console.log('✅ 所有测试前检查通过');
  }

  return checks;
}
