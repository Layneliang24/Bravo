// 健康检查 E2E 测试
// 确保前端和后端服务都能正常启动和响应

import { test, expect } from '@playwright/test';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3001';
const API_URL = process.env.API_URL || 'http://localhost:8000';

// 健康检查测试套件
test.describe('服务健康检查', () => {
  test('前端服务应该能够正常访问', async ({ page }) => {
    // 访问前端主页
    await page.goto(BASE_URL);

    // 检查页面标题
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    // 检查页面是否加载完成
    await page.waitForLoadState('networkidle');

    // 检查是否有基本的HTML结构
    const body = await page.locator('body');
    expect(await body.count()).toBe(1);
  });

  test('后端API健康检查端点应该正常响应', async ({ page }) => {
    // 直接访问后端健康检查端点
    const response = await page.request.get(`${API_URL}/health/`);

    // 检查响应状态
    expect(response.status()).toBe(200);

    // 检查响应内容
    const responseText = await response.text();
    expect(responseText).toBeTruthy();
  });

  test('前端应该能够与后端API通信', async ({ page }) => {
    // 访问前端页面
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // 尝试通过前端调用后端API
    const apiResponse = await page.evaluate(async apiUrl => {
      try {
        const response = await fetch(`${apiUrl}/health/`);
        return {
          status: response.status,
          ok: response.ok,
          text: await response.text(),
        };
      } catch (error) {
        return {
          error: error.message,
        };
      }
    }, API_URL);

    // 检查API调用是否成功
    expect(apiResponse.error).toBeUndefined();
    expect(apiResponse.status).toBe(200);
    expect(apiResponse.ok).toBe(true);
  });

  test('页面加载时间应该在合理范围内', async ({ page }) => {
    const startTime = Date.now();

    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // 页面加载时间应该少于10秒
    expect(loadTime).toBeLessThan(10000);
  });

  test('应该能够处理网络错误', async ({ page }) => {
    // 模拟网络错误
    await page.route('**/*', route => route.abort());

    try {
      await page.goto(BASE_URL, { timeout: 5000 });
    } catch (error) {
      // 预期会失败
      expect(error).toBeTruthy();
    }

    // 恢复网络
    await page.unroute('**/*');
  });
});

// 基础功能测试套件
test.describe('基础功能测试', () => {
  test('主页应该显示基本内容', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // 检查页面是否有基本内容
    const bodyText = await page.textContent('body');
    expect(bodyText).toBeTruthy();
    expect(bodyText.length).toBeGreaterThan(0);
  });

  test('页面应该有正确的元数据', async ({ page }) => {
    await page.goto(BASE_URL);

    // 检查页面标题
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(0);

    // 检查是否有viewport meta标签
    const viewport = await page.getAttribute('meta[name="viewport"]', 'content');
    expect(viewport).toBeTruthy();
  });

  test('应该支持基本的键盘导航', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');

    // 使用Tab键导航
    await page.keyboard.press('Tab');

    // 检查是否有焦点元素
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeTruthy();
  });
});
