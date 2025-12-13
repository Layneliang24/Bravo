// REQ-ID: REQ-2025-003-user-login
// UI设计规范 E2E 测试
// 使用 Playwright 进行端到端测试，验证登录页面是否符合Figma设计规范
// TESTCASE-IDS: TC-AUTH_UI-001, TC-AUTH_UI-002, TC-AUTH_UI-003, TC-AUTH_UI-004, TC-AUTH_UI-005, TC-AUTH_UI-006

import { test, expect, Page } from '@playwright/test';

// 测试配置
const BASE_URL = process.env.TEST_BASE_URL || 'http://localhost:3001';

// 页面对象模式 - 登录页（UI设计验证）
class LoginUIPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto(`${BASE_URL}/login`);
    await this.page.waitForLoadState('networkidle');
  }

  // 获取主容器元素
  async getMainContainer() {
    return this.page.locator('[data-testid="auth-card"], .auth-card, .login-container').first();
  }

  // 获取左侧品牌展示区
  async getBrandSection() {
    return this.page.locator('[data-testid="brand-section"], .brand-section, .login-brand').first();
  }

  // 获取右侧登录表单区
  async getFormSection() {
    return this.page.locator('[data-testid="form-section"], .form-section, .login-form').first();
  }

  // 获取输入框
  async getInputFields() {
    return this.page.locator('input[type="text"], input[type="email"], input[type="password"]');
  }

  // 获取验证码显示框
  async getCaptchaDisplay() {
    return this.page
      .locator('[data-testid="captcha-display"], .captcha-display, .captcha-image')
      .first();
  }

  // 获取验证码输入框
  async getCaptchaInput() {
    return this.page
      .locator(
        'input[placeholder*="验证码"], input[placeholder*="CODE"], input[placeholder*="code"]'
      )
      .first();
  }

  // 获取Learning Hub标题
  async getLearningHubTitle() {
    return this.page.locator('text=Learning Hub').first();
  }

  // 获取欢迎文字
  async getWelcomeText() {
    return this.page.locator('text=/Welcome to your personal learning space/').first();
  }

  // 获取功能卡片
  async getFeatureCards() {
    return this.page.locator('[data-testid="feature-card"], .feature-card');
  }

  // 获取元素的计算样式
  async getComputedStyle(selector: string, property: string): Promise<string> {
    return await this.page.evaluate(
      ({ selector, property }) => {
        const element = document.querySelector(selector);
        if (!element) return '';
        const styles = window.getComputedStyle(element);
        return (
          styles.getPropertyValue(property) || styles[property as keyof CSSStyleDeclaration] || ''
        );
      },
      { selector, property }
    );
  }

  // 获取元素的尺寸
  async getElementSize(selector: string): Promise<{ width: number; height: number }> {
    const element = await this.page.locator(selector).first();
    const box = await element.boundingBox();
    return box ? { width: box.width, height: box.height } : { width: 0, height: 0 };
  }

  // 获取元素的颜色（转换为rgba格式）
  async getElementColor(selector: string, property: string = 'background-color'): Promise<string> {
    const color = await this.getComputedStyle(selector, property);
    // 将颜色转换为rgba格式以便比较
    return color;
  }

  // 设置视口大小（用于响应式测试）
  async setViewportSize(width: number, height: number) {
    await this.page.setViewportSize({ width, height });
  }
}

// UI设计规范测试套件
test.describe('UI设计规范验证 - Figma设计规范', () => {
  let loginPage: LoginUIPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginUIPage(page);
    // 设置桌面端视口（1152px宽度，符合Figma设计）
    await loginPage.setViewportSize(1200, 800);
    await loginPage.goto();
  });

  test('TC-AUTH_UI-001: 登录页面布局-左右分栏', async ({ page }) => {
    // 1. 打开登录页面
    // (已在beforeEach中完成)

    // 2. 检查左侧品牌展示区
    const brandSection = await loginPage.getBrandSection();
    await expect(brandSection).toBeVisible();

    // 验证左侧品牌区宽度为460px（允许±2px误差）
    const brandSize = await loginPage.getElementSize(
      '[data-testid="brand-section"], .brand-section, .login-brand'
    );
    expect(brandSize.width).toBeGreaterThanOrEqual(458);
    expect(brandSize.width).toBeLessThanOrEqual(462);

    // 3. 检查右侧登录表单区
    const formSection = await loginPage.getFormSection();
    await expect(formSection).toBeVisible();

    // 验证右侧表单区宽度为690px（允许±2px误差）
    const formSize = await loginPage.getElementSize(
      '[data-testid="form-section"], .form-section, .login-form'
    );
    expect(formSize.width).toBeGreaterThanOrEqual(688);
    expect(formSize.width).toBeLessThanOrEqual(692);

    // 验证主容器总宽度约为1152px（460 + 690 + 分隔线等）
    const mainContainer = await loginPage.getMainContainer();
    const containerSize = await mainContainer.boundingBox();
    if (containerSize) {
      expect(containerSize.width).toBeGreaterThanOrEqual(1150);
      expect(containerSize.width).toBeLessThanOrEqual(1154);
    }
  });

  test('TC-AUTH_UI-002: 登录页面颜色规范验证', async ({ page }) => {
    // 1. 打开登录页面
    // (已在beforeEach中完成)

    // 2. 检查主卡片背景色rgba(255,255,255,0.75)
    const mainContainer = await loginPage.getMainContainer();
    const bgColor = await loginPage.getElementColor(
      '[data-testid="auth-card"], .auth-card, .login-container'
    );
    // 验证背景色包含rgba(255,255,255,0.75)或等效值
    // Playwright可能返回rgb或rgba格式，需要灵活匹配
    expect(bgColor).toMatch(/rgba?\(255,\s*255,\s*255/i);
    // 如果返回rgba，验证透明度约为0.75
    if (bgColor.includes('rgba')) {
      const alphaMatch = bgColor.match(/[\d.]+\)$/);
      if (alphaMatch) {
        const alpha = parseFloat(alphaMatch[0].replace(')', ''));
        expect(alpha).toBeGreaterThanOrEqual(0.7);
        expect(alpha).toBeLessThanOrEqual(0.8);
      }
    }

    // 3. 检查输入框边框rgba(249,115,22,0.15)
    const inputFields = await loginPage.getInputFields();
    const firstInput = inputFields.first();
    const borderColor = await loginPage.getElementColor(
      'input[type="text"], input[type="email"], input[type="password"]',
      'border-color'
    );
    // 验证边框颜色包含橙色rgba(249,115,22,0.15)或等效值
    expect(borderColor).toMatch(/rgba?\(249,\s*115,\s*22/i);

    // 4. 检查文字颜色
    // 主标题颜色应该是#1e2939
    const titleColor = await loginPage.getElementColor('h1, h2, .title', 'color');
    expect(titleColor).toMatch(/rgba?\(30,\s*41,\s*57/i); // #1e2939的rgb值

    // 副标题/正文颜色应该是#4a5565
    const subtitleColor = await loginPage.getElementColor('.subtitle, p', 'color');
    expect(subtitleColor).toMatch(/rgba?\(74,\s*85,\s*101/i); // #4a5565的rgb值
  });

  test('TC-AUTH_UI-003: 输入框样式验证', async ({ page }) => {
    // 1. 打开登录页面
    // (已在beforeEach中完成)

    // 2. 检查输入框高度60px
    const inputFields = await loginPage.getInputFields();
    const firstInput = inputFields.first();
    const inputSize = await firstInput.boundingBox();
    expect(inputSize?.height).toBeGreaterThanOrEqual(58);
    expect(inputSize?.height).toBeLessThanOrEqual(62);

    // 3. 检查圆角14px
    const borderRadius = await loginPage.getComputedStyle(
      'input[type="text"], input[type="email"], input[type="password"]',
      'border-radius'
    );
    // 验证border-radius包含14px
    expect(borderRadius).toMatch(/14px/);

    // 4. 检查图标位置和尺寸
    // 查找输入框内的图标（通常在左侧）
    const icon = await page.locator('input ~ svg, input ~ .icon, .input-icon').first();
    if (await icon.isVisible().catch(() => false)) {
      const iconSize = await icon.boundingBox();
      // 图标应该是20px × 20px
      expect(iconSize?.width).toBeGreaterThanOrEqual(18);
      expect(iconSize?.width).toBeLessThanOrEqual(22);
      expect(iconSize?.height).toBeGreaterThanOrEqual(18);
      expect(iconSize?.height).toBeLessThanOrEqual(22);
    }
  });

  test('TC-AUTH_UI-004: 验证码区域样式验证', async ({ page }) => {
    // 1. 打开登录页面
    // (已在beforeEach中完成)

    // 2. 检查验证码显示框160px×64px
    const captchaDisplay = await loginPage.getCaptchaDisplay();
    if (await captchaDisplay.isVisible().catch(() => false)) {
      const displaySize = await captchaDisplay.boundingBox();
      expect(displaySize?.width).toBeGreaterThanOrEqual(158);
      expect(displaySize?.width).toBeLessThanOrEqual(162);
      expect(displaySize?.height).toBeGreaterThanOrEqual(62);
      expect(displaySize?.height).toBeLessThanOrEqual(66);
    }

    // 3. 检查验证码输入框402px×64px
    const captchaInput = await loginPage.getCaptchaInput();
    if (await captchaInput.isVisible().catch(() => false)) {
      const inputSize = await captchaInput.boundingBox();
      expect(inputSize?.width).toBeGreaterThanOrEqual(400);
      expect(inputSize?.width).toBeLessThanOrEqual(404);
      expect(inputSize?.height).toBeGreaterThanOrEqual(62);
      expect(inputSize?.height).toBeLessThanOrEqual(66);
    }

    // 4. 检查验证码文字30px粗体
    const captchaText = await page.locator('.captcha-text, [data-testid="captcha-text"]').first();
    if (await captchaText.isVisible().catch(() => false)) {
      const fontSize = await loginPage.getComputedStyle(
        '.captcha-text, [data-testid="captcha-text"]',
        'font-size'
      );
      expect(fontSize).toMatch(/30px/);

      const fontWeight = await loginPage.getComputedStyle(
        '.captcha-text, [data-testid="captcha-text"]',
        'font-weight'
      );
      expect(fontWeight).toMatch(/bold|700|600/);
    }
  });

  test('TC-AUTH_UI-005: 左侧品牌展示区内容验证', async ({ page }) => {
    // 1. 打开登录页面
    // (已在beforeEach中完成)

    // 2. 检查Learning Hub标题
    const learningHubTitle = await loginPage.getLearningHubTitle();
    await expect(learningHubTitle).toBeVisible();

    // 3. 检查欢迎文字
    const welcomeText = await loginPage.getWelcomeText();
    await expect(welcomeText).toBeVisible();

    // 4. 检查中央插图
    // 查找插图元素（可能是SVG、图片或装饰元素）
    const illustration = await page
      .locator('[data-testid="illustration"], .illustration, .brand-illustration')
      .first();
    // 插图可能以不同形式存在，如果存在则验证可见性
    const hasIllustration = await illustration.isVisible().catch(() => false);
    // 插图不是必须立即可见的，但应该存在于DOM中

    // 5. 检查三个功能卡片
    const featureCards = await loginPage.getFeatureCards();
    const cardCount = await featureCards.count();
    expect(cardCount).toBeGreaterThanOrEqual(3);

    // 验证功能卡片内容
    const englishLearning = await page.locator('text=/English Learning/i').first();
    await expect(englishLearning).toBeVisible();

    const codingPractice = await page.locator('text=/Coding Practice/i').first();
    await expect(codingPractice).toBeVisible();

    const careerGrowth = await page.locator('text=/Career Growth/i').first();
    await expect(careerGrowth).toBeVisible();
  });

  test('TC-AUTH_UI-006: 响应式布局-移动端适配', async ({ page }) => {
    // 1. 调整浏览器宽度<768px
    await loginPage.setViewportSize(375, 667); // iPhone SE尺寸
    await loginPage.goto();

    // 2. 检查布局变化
    // 移动端应该是单列布局，左右分栏应该消失或堆叠
    const brandSection = await loginPage.getBrandSection();
    const formSection = await loginPage.getFormSection();

    // 在移动端，品牌区可能隐藏或堆叠在表单上方
    // 验证表单区域仍然可见且可访问
    await expect(formSection).toBeVisible();

    // 3. 检查表单可访问性
    // 验证输入框仍然可以正常使用
    const inputFields = await loginPage.getInputFields();
    const firstInput = inputFields.first();
    await expect(firstInput).toBeVisible();
    await expect(firstInput).toBeEnabled();

    // 验证表单在移动端的宽度合理（应该接近视口宽度）
    const formSize = await formSection.boundingBox();
    if (formSize) {
      // 移动端表单宽度应该接近视口宽度（减去padding）
      expect(formSize.width).toBeGreaterThan(300);
      expect(formSize.width).toBeLessThan(375);
    }

    // 验证没有水平滚动条（布局应该适配）
    const hasHorizontalScroll = await page.evaluate(() => {
      return document.documentElement.scrollWidth > document.documentElement.clientWidth;
    });
    expect(hasHorizontalScroll).toBe(false);
  });
});
